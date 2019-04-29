import time, logging, os
from PyQt4 import QtCore
from mido import MidiFile, MidiTrack, Message, MetaMessage
from mido import second2tick, bpm2tempo, tempo2bpm
from pyano.IOPi import IOPi

GPIO_ENABLED = False
PRINT_NOTES = True

# TODO: update play_file, octave_adjust, and play_note to be more like hero mode


#---WORKER THREAD: MIDI PLAYER------------------------------------------

class PlayerThread(QtCore.QThread):
    
    # this gets ran when the thread is created (when player btn is clicked on main menu page)
    def __init__(self, parent = None):
        # this is ran when on_player_click is ran in gui thread
        
        # set MainWindow (gui thread) as parent of PlayerThread
        super(self.__class__, self).__init__(parent)
        self.midi_file_list = []
        self.next_check = False
        self.back_check = False
        self.pause_check = False
        self.stop_check = False
        self.current_song = 0 # current_song is the index of the highlighted_file that is set when play btn is presed
        
        # IO setup
        if GPIO_ENABLED:
            # get busses from i2c addresses
            self.bus1 = IOPi(0x21)
            self.bus2 = IOPi(0x20)
            # set all 4 port directions to output (0x00)
            self.bus1.set_port_direction(0, 0x00)
            self.bus1.set_port_direction(1, 0x00)
            self.bus2.set_port_direction(0, 0x00)
            self.bus2.set_port_direction(1, 0x00)
            # initialize all outputs to 0
            self.clear_outputs()
    
    # this gets ran when the thread is activated (when play btn is clicked on player page)
    def run(self):  
        
        # play each file in midi_file_list starting from the index position of the highlighted file
        file_count = len(self.midi_file_list)
        
        while self.current_song < file_count:
            logging.info("PLAYING: " + self.midi_file_list[self.current_song])
            
            # disable buttons (for when next file plays automatically)
            # clicking next & back buttons do this already
            self.emit(QtCore.SIGNAL("playerBtnsEnabled(bool)"), False)
                        
            self.play_file() # plays self.current_song
        
            if self.stop_check:
                self.emit(QtCore.SIGNAL("resetPlayerGUI()"))
                self.clear_outputs()
                return # exit if stop btn is pressed
            
            # make sure all outputs are low before playing the next song
            self.clear_outputs()
            
        self.emit(QtCore.SIGNAL("resetPlayerGUI()"))
            
            
    def play_file(self):
        
        # MAKE THIS MORE LIKE HERO MODE
        # ADD OCTAVE ADJUST CODE TO THIS FUNCTION
        
        # use mido library to create mid object which is all the song/file data
        midi_file = self.midi_file_list[self.current_song]
        mid = MidiFile(os.getcwd() + '/midi-files/' + midi_file)  # mid is the current mido MIDI file playing
        
        # filter out files that are not MIDI type 1
        # type 0 (single track): all messages are saved in one track
        # type 1 (synchronous): all tracks start at the same time
        # type 2 (asynchronous): each track is independent of the others
        if mid.type != 1:
            logging.error('ERROR: file contains unsupported midi type')
            self.emit(QtCore.SIGNAL("playerNextFile()"))
            self.current_song += 1
            return
        
        # variable inits
        self.off_check = False
        progress = 0
        message_count = 0 # used to keep track of progress of a song
        current_message = 0 # used to keep track of the progress of a song
        notes = set()  # testing note range of each MIDI file - build set of all unique notes & find min and max for key shifting

        is_custom = False
        for msg in mid:
            if msg.type == 'text' and msg.text == 'custom pyano file':
                logging.info('Custom pyano file')
                is_custom = True
                break
        
        # go through midi file for processing
        for msg in mid:
            # adjust octave range & count messages for song progress bar
            if msg.type == 'note_on' or msg.type == 'note_off':
                # if we made it this far then the message must be note_on/off type
                # adjust octave will also check for on/off commands - if none are present the file is un-playable
                self.adjust_octave(msg, notes)
                message_count += 1 # message count is really only counting on/off messages
                
        # skip midi file if it does not have off commands
        if self.off_check == False:
            logging.error("ERROR: file does not contain any off commands")
            self.current_song += 1
            self.emit(QtCore.SIGNAL("playerNextFile()"))
            return
        
        # testing note range of each MIDI file
        min_note = min([int(i) for i in notes]) # the min and max values are strings from the midi file and need to be converted to ints
        max_note = max([int(i) for i in notes])
        range_notes = max_note - min_note
        
        #~ if range_notes <= 25:
            #~ adjust_value = min_value - 1
        #~ else:
            #~ adjust_value = 83 # 59, 71, 83
            
        if not is_custom and range_notes <= 25:
            adjust_value = min_note - 1 # adjust the lowest note in the song to the first note on the piano
        else:
            adjust_value = 59 # adjust to play middle C plus 2 octaves on the piano 
        
        #~ print("All Notes: {}".format(notes))
        print("Min Note: {} Max Note: {}".format(min_note, max_note))
        print("Range:", range_notes)
        
        # get the length of MIDI file in seconds
        file_length = (round(mid.length, 2))
        
        # enable skip & back btns after song processing completes
        self.emit(QtCore.SIGNAL("playerBtnsEnabled(bool)"), True)
        
        # go through midi file and actually play notes          
        for msg in mid:
            
            # is there better way to have all same code in and out of pause check??
            if self.pause_check:
                self.emit(QtCore.SIGNAL("hideAllIndicators()"))
                self.clear_outputs()
                
                while self.pause_check: 
                    # stop/next/back are all same as when not paused except in here they also reset the pause_check 
                    
                    if self.stop_check:
                        self.pause_check = False
                        self.emit(QtCore.SIGNAL("resetPlayerGUI()"))
                        return
                
                    if self.next_check:
                        self.current_song +=1
                        self.next_check = False
                        self.pause_check = False
                        return
                        
                    if self.back_check:
                        # file_length < 20 sec fixes not being able to go back a file when playing a really short file
                        if progress < 5 or file_length < 20: 
                            self.current_song -= 1
                            self.emit(QtCore.SIGNAL("playerLastFile()"))
                        # otherwise just return to main while loop and restart file from beginning 
                        self.back_check = False
                        self.pause_check = False
                        return
                        
                    time.sleep(0.2)
                    
            if self.stop_check:
                self.emit(QtCore.SIGNAL("hideAllIndicators()"))
                self.emit(QtCore.SIGNAL("resetPlayerGUI()"))
                self.clear_outputs()
                return
        
            if self.next_check:
                self.current_song +=1
                self.next_check = False
                self.emit(QtCore.SIGNAL("hideAllIndicators()"))
                self.clear_outputs()
                return
                
            if self.back_check:
                # file_length < 20 sec fixes not being able to go back a file when playing a really short file
                if progress < 5 or file_length < 20: 
                    self.current_song -= 1
                    self.emit(QtCore.SIGNAL("playerLastFile()"))
                # otherwise just return to main while loop and restart file from beginning 
                self.back_check = False
                self.emit(QtCore.SIGNAL("hideAllIndicators()"))
                self.clear_outputs()
                return
     
            if not msg.is_meta and msg.type != 'program_change' and msg.type != 'control_change':
                
                # if we made it this far then the message must be note_on/off type
                
                # msg.time = elapsed (delta) time from previous event to this event
                time.sleep(msg.time) 
                self.play_note(msg, adjust_value)

                    
                # song progress
                current_message += 1
                progress_old = progress
                progress = int((current_message / message_count)*100) # save progress of the song as an int
                if progress_old != progress: # only emit the progress value when it updates
                    self.emit(QtCore.SIGNAL("updatePlayerProgress(int)"), progress)
                        
        # this runs after each file naturally reaches the end (next btn was NOT pressed)
        self.emit(QtCore.SIGNAL("playerNextFile()"))
        self.current_song += 1
    
    # CHANGE NAME
    def adjust_octave(self, msg, notes):
        
        # extract the note from the message
        msg_data = str(msg)
        temp1 = msg_data.find('note_')
        temp2 = msg_data.find('channel')
        status = msg_data[temp1 + 5:temp2]  # status = on or off
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as midi
        
        # add note to set of notes (for checking note range of each midi file)
        notes.add(note)
        
        # check if the midi file has on/off commands
        if status == 'off ':
            self.off_check = True
            
        return
    
    def play_note(self, msg, adjust_value):
        
        self.solenoid2key = {'1': 'z', '2': 's', '3': 'x', '4': 'd', '5': 'c', '6': 'v',
                             '7': 'g', '8': 'b', '9': 'h', '10': 'n', '11': 'j', '12': 'm',
                             '13': 'q', '14': '2', '15': 'w', '16': '3', '17': 'e', '18': 'r',
                             '19': '5', '20': 't', '21': '6', '22': 'y', '23': '7', '24': 'u'}
        
        # extract note and status from message
        status = msg.type[len('note_'):]
        msg_data = str(msg)
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
        note = int(note) - adjust_value # adjust notes to playable range

        # adjust for notes that are still outside the range of the piano
        #~ while note > 24:
            #~ note = note - 24
            
        try:
            key = self.solenoid2key[str(note)]
            
            # print/update GUI with note and status
            if PRINT_NOTES:
                print("Note {} {}".format(note, status))
            
            # turn solenoids on or off based on status variable
            # and show indicators
            if status == 'on':
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'player', key, 'on')
                if GPIO_ENABLED:
                    if note < 17:
                        self.bus1.write_pin(note, 1)
                        pass
                    else:
                        note -= 16
                        self.bus2.write_pin(note, 1)
                        pass
            elif status == 'off': 
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'player', key, 'off')
                if GPIO_ENABLED:
                    if note < 17:
                        self.bus1.write_pin(note, 0)
                        pass
                    else:
                        note -= 16
                        self.bus2.write_pin(note, 0)
                        pass
        except:
            pass
                
        return
    
    # function that sets all i2c pins to 0         
    def clear_outputs(self):
        if GPIO_ENABLED:
            logging.info('CLEARING OUTPUTS')
            self.bus1.write_port(0, 0x00)
            self.bus1.write_port(1, 0x00)
            self.bus2.write_port(0, 0x00)
            self.bus2.write_port(1, 0x00)

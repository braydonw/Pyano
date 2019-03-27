import time
import logging
from PyQt4 import QtGui, QtCore, uic
from mido import MidiFile, MidiTrack, Message, MetaMessage, second2tick, bpm2tempo, tempo2bpm

import os # REMOVE?

#---WORKER THREAD: MIDI PLAYER------------------------------------------

##### ADD WAY TO START FROM HIGHLIGHTED FILE IN GUI, NOT AT BEGGINING OF FILELIST
##### MAKE PAUSE AND STOP BUTTONS WORK WITH PLAYBACK

##### NEED MAKER TO GIVE FILES ALL META DATA THAT WE DISPLAY ON GUI


class PlayerThread(QtCore.QThread):
    
    # this gets ran when the thread is created (when player btn is clicked on main menu page)
    def __init__(self, parent = None):
        super(PlayerThread, self).__init__(parent)
        self.midi_file_list = []
        self.next_check = False
        self.back_check = False
        self.pause_check = False
        self.stop_check = False
        # CHANGE TO CURRENT_INDEX
        self.current_song = 0 # current_song is the index of the highlighted_file that is set when play btn is presed
    
    # this gets ran when the thread is activated (when play btn is clicked on player page)
    def run(self):  
        
        # play each file in midi_file_list starting from the index position of the highlighted file
        file_count = len(self.midi_file_list) # remember to -1 for index
        
        #~ for midi_file in self.midi_file_list: # midi_file is a string of the current MIDI file name
        for midi_file in self.midi_file_list[self.current_song:]: # slice midi_file_list playback
            if self.stop_check:
                return # exit if stop btn is pressed
            
            print(os.getcwd())
            mid = MidiFile(midi_file)  # mid is the current mido MIDI file playing
            logging.info("Playing file: {}".format(midi_file))
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "")
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Playing: {}".format(midi_file))
            self.play_file(mid)
            
            # reset GUI btn-click checks after each file
            self.pause_check = False
            self.next_check = False
            self.back_check = False
            off_check = False
            #~ self.progress = 0 # DOES THIS GET TAKEN CARE OF BY ADAN'S CODE???
            
            # update GUI elements to show new song
            if not self.stop_check:
                self.emit(QtCore.SIGNAL("playerNextFile()"))
        
    def play_file(self, mid):
        
        progress = 0
        message_count = 0 #used to keep track of progress of a song
        current_message = 0 #used to keep track of the progress of a song
        notes = set()  # testing note range of each MIDI file - build set of all unique notes & find min and max for key shifting
        
        # filter out files that are not MIDI type 1
        if mid.type == 0:
            # type 0 (single track): all messages are saved in one track
            logging.info("MIDI Type: 0 (currently unsupported)")
            #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type: 0 (currently unsupported)")
            return
        elif mid.type == 1:
            # type 1 (synchronous): all tracks start at the same time
            logging.info("MIDI Type: 1")
            #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type: 1")
        elif mid.type == 2:
            # type 2 (asynchronous): each track is independent of the others
            logging.info("MIDI Type: 2 (currently unsupported)")
            #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type: 2 (currently unsupported)")
            return
        else:
            logging.info("MIDI Type Error")
            return

        # get the length of MIDI file in seconds
        # MAKE DYNAMIC FOR SEC, MIN, ETC?
        file_length = (round(mid.length, 2))
        logging.info("Length: {}s".format(file_length))
        self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Length: {}s".format(file_length))
        
        # go through the MIDI file and collect note values
        # WHAT DOES PLAY NOTES TEST DO EXACTLY?? RENAME TO OCTAVE ADJUST OR SOMETHING
        for msg in mid:
            # ADDED THIS TO PRINT TEMPO AFTER FILE LENGTH IN S
            if msg.is_meta:
                msg_data = str(msg)
                if msg.type == 'set_tempo':
                    temp1 = msg_data.find('tempo=')
                    temp2 = msg_data.find('time=')
                    tempo = msg_data[temp1 + 6:temp2]
                    self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "BPM: {}".format(round(tempo2bpm(int(tempo)))))
            # THIS IS WHAT WAS IN HERE BEFORE    
            if not msg.is_meta:
                if msg.type != 'program_change' and msg.type != 'control_change':
                    # if we made it this far then the message must be note_on/off type
                    self.play_note_test(msg, notes)
                    message_count += 1

        # skip this midi file if it does not have off commands
        if off_check == False:
            print()
            print("---------------------------------------------------------------------")
            print()
            print("This file cannot be played becuase it does not contain 'off' commands")
            print()
            print("---------------------------------------------------------------------")
            return
        
        # testing note range of each MIDI file
        min_value = min([int(i) for i in notes]) # the min and max values are strings from the MIDI file and need to be converted to ints
        max_value = max([int(i) for i in notes])
        range_notes = max_value - min_value
        adjust_value = min_value - 1 # the number that needs to be subtracted from every note to make it playable
        
        print("All Notes: {}".format(notes))
        print("Min Note: {} Max Note: {}".format(min_value, max_value))
        print("Range: ", range_notes)
        
        # go through MIDI File and actually play notes          
        for msg in mid:
            
            #~ if msg.is_meta:
                #~ if msg.type == 'set_tempo':
                    #~ print(msg)
            
            if self.stop_check:
                return
            
            if self.pause_check:
                logging.info("*P A U S E D*")
                time.sleep(0.2)
            while self.pause_check: # do not continue while pause variable is true
                # this block needs to be in here so that skipping while paused is pausible
                #~ if self.next_check: #skip the rest of this song if the skip variable is true
                    #~ logging.info("*S K I P*")
                    #~ return
                    
                    #~ ### WHAT IS CURRENT_SONG???
                    #~ ### GET PROGRESS WORKING
                    
                #~ if self.back_check:
                    #~ logging.info("*B A C K*")
                    #~ if progress > 5: #only decrement by 1 if progress is greater than 5%
                         #~ current_song = current_song - 1
                    #~ else: #decrement by 2 if progress is 5% or less
                        #~ current_song = current_song - 2
                    #~ return
                time.sleep(0.2)
        
            if self.next_check == True: #skip the rest of this song if the skip variable is true
                logging.info("*S K I P*")
                return
                
            if self.back_check:
                logging.info("*B A C K*")
                if progress > 5: #only decrement by 1 if progress is greater than 5%
                     current_song = current_song - 1
                else: #decrement by 2 if progress is 5% or less
                    current_song = current_song - 2
                return
     
            if not msg.is_meta:
                if msg.type != 'program_change' and msg.type != 'control_change':
                    # if we made it this far then the message must be note_on/off type
                    time.sleep(msg.time) # MUST GO BERFORE PLAY_NOTE FUNCTION
                    self.play_note(msg, notes, adjust_value)
                    
                    # song progress
                    current_message += 1
                    progress_old = progress
                    #print("Current Message: ", current_message) #I was using this for debugging 
                    progress = int((current_message / message_count)*100) #saves the progress of the song as an intger value
                    #comment the next 2 lines if you don't want to see the progress in terminal
                    if progress_old != progress: #only print the progress when it updates
                        #~ print ("{} % complete" .format(progress)) #output progress for debugging
                        self.emit(QtCore.SIGNAL("updatePlayerProgress(int)"), progress)


    def play_note_test(self, msg, notes):
        msg_data = str(msg)
        temp1 = msg_data.find('note_')
        temp2 = msg_data.find('channel')
        status = msg_data[temp1 + 5:temp2]  # status = on or off
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
        notes.add(note)  # testing note range of each MIDI file
        
        #check if the midi file has off commands
        global off_check
        
        if status == 'off ':
            off_check = True
            
        return
    
    def play_note(self, msg, notes, adjust_value):
        msg_data = str(msg)
        temp1 = msg_data.find('note_')
        temp2 = msg_data.find('channel')
        status = msg_data[temp1 + 5:temp2]  # status = on or off (redundant: just use msg.type == 'note_on')
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
        note = int(note) - adjust_value #adjust notes to playable range

        #adjust for notes that are still outside the range of the piano
        while note > 24:
            note = note - 24

        #print to terminal for debug purposes
        #~ print("Note {} {}".format(note, status))
        #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Note {} {}".format(note, status))
        
        # google easier way? use dictionaries??
        #Output to solenoids
        if status == 'off ':
            pass
                
        if status == 'on ':
            print("Note {} {}".format(note, status))
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Note {} {}".format(note, status))
            pass
            
       
         
        return

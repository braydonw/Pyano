# cleanup imports and only keep what is used / needed in this file
import time
import logging
from PyQt4 import QtCore
from mido import MidiFile, MidiTrack, Message, MetaMessage, second2tick, bpm2tempo, tempo2bpm
import os # REMOVE?
from pyano.IOPi import IOPi #Library for IOPI Plus expansion board


#---WORKER THREAD: MIDI PLAYER------------------------------------------

class PlayerThread(QtCore.QThread):
    
    # this gets ran when the thread is created (when player btn is clicked on main menu page)
    def __init__(self, parent = None):
        super(PlayerThread, self).__init__(parent)
        self.midi_file_list = []
        self.next_check = False
        self.back_check = False
        self.pause_check = False
        self.stop_check = False
        self.current_song = 0 # current_song is the index of the highlighted_file that is set when play btn is presed
        
        #~ #IO setup
        #~ bus1 = IOPi(0x20) #address for first bus
        #~ bus2 = IOPi(0x21) #address for second bus

        #~ bus1.set_port_direction(0, 0x00) #set channels 1-8 on bus 1 to output
                                         #~ #first variable is the port (0 or1)
                                         #~ #second variable is bit by bit assignment (0 = out, 1 = in)
        #~ bus1.set_port_direction(1, 0x00) #set channes 9-16 on bus 1 to output
        #~ bus2.set_port_direction(0, 0x00) #set channels 1-8 on bus 2 to output
        #~ bus2.set_port_direction(1, 0xC0) #set channels 9-15 on bus 2 to output
                                         #~ #pin 16 is set to input for hardware control
                                         
        #~ #Initialize all outputs to 0
        #~ self.clear_outputs()
    
    # this gets ran when the thread is activated (when play btn is clicked on player page)
    def run(self):  
        
        # play each file in midi_file_list starting from the index position of the highlighted file
        file_count = len(self.midi_file_list)
        
        while self.current_song < file_count:
            self.play_file() # plays self.current_song
        
            if self.stop_check:
                return # exit if stop btn is pressed
            
            # ???
            
            
            # make sure all outputs are low before playing the next song
            #~ self.clear_outputs()
            
            
    def play_file(self):
        
        self.off_check = False
        #~ self.on_check = False
        
        # disable skip & back btns until the song starts playing
        # could combine player_next_enabled & player_back_enabled into 1 function
        self.emit(QtCore.SIGNAL("playerNextEnabled(bool)"), False)
        self.emit(QtCore.SIGNAL("playerBackEnabled(bool)"), False)
        
        # use mido library to create mid object which is all the song/file data
        midi_file = self.midi_file_list[self.current_song]
        mid = MidiFile(midi_file)  # mid is the current mido MIDI file playing
        self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "")
        self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Playing: {}".format(midi_file))
        
        # filter out files that are not MIDI type 1
        if mid.type == 0:
            # type 0 (single track): all messages are saved in one track
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type: 0 (unsupported)")
            self.emit(QtCore.SIGNAL("playerNextFile()"))
            self.current_song += 1
            return
        elif mid.type == 1:
            # type 1 (synchronous): all tracks start at the same time
            #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type: 1")
            pass
        elif mid.type == 2:
            # type 2 (asynchronous): each track is independent of the others
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type: 2 (unsupported)")
            self.emit(QtCore.SIGNAL("playerNextFile()"))
            self.current_song += 1
            return
        else:
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "MIDI Type Error")
            self.emit(QtCore.SIGNAL("playerNextFile()"))
            self.current_song += 1
            return
            
        progress = 0
        message_count = 0 # used to keep track of progress of a song
        current_message = 0 # used to keep track of the progress of a song
        notes = set()  # testing note range of each MIDI file - build set of all unique notes & find min and max for key shifting

        # get the length of MIDI file in seconds
        file_length = (round(mid.length, 2))
        self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Length: {}s".format(file_length))\
        
        # **
        # go through midi file and convert + display the song's tempo in BPM
        # only display the first temp change (some downloaded files have a ton of tempo changes that spam screen)
        for msg in mid:
            if msg.is_meta and msg.type == 'set_tempo':
                msg_data = str(msg)
                temp1 = msg_data.find('tempo=')
                temp2 = msg_data.find('time=')
                tempo = msg_data[temp1 + 6:temp2]
                break
        self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "BPM: {}".format(round(tempo2bpm(int(tempo)))))
        
        # **
        # go through midi file for processing
        for msg in mid:
            # adjust octave range & count messages for song progress bar
            if not msg.is_meta and msg.type != 'program_change' and msg.type != 'control_change':
                # if we made it this far then the message must be note_on/off type
                # adjust octave will also check for on/off commands - if none are present the file is un-playable
                self.adjust_octave(msg, notes)
                message_count += 1 # message count is really only counting on/off messages
                
        # **
        # skip midi file if it does not have off commands
        if self.off_check == False:
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "This file cannot be played becuase it does not contain 'off' commands")
            self.emit(QtCore.SIGNAL("playerNextFile()"))
            self.current_song += 1
            return
            
        #~ if self.on_check == False:
            #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "This file cannot be played becuase it does not contain 'on' commands")
            #~ self.emit(QtCore.SIGNAL("playerNextFile()"))
            #~ self.current_song += 1
            #~ return
        
        # WHAT IS ADJUST VALUE - UNDERSTAND BETTER
        # testing note range of each MIDI file
        min_value = min([int(i) for i in notes]) # the min and max values are strings from the midi file and need to be converted to ints
        max_value = max([int(i) for i in notes])
        range_notes = max_value - min_value
        adjust_value = min_value - 1 # the number that needs to be subtracted from every note to make it playable
        print("All Notes: {}".format(notes))
        print("Min Note: {} Max Note: {}".format(min_value, max_value))
        print("Range: ", range_notes)
        
        # go through midi file and actually play notes          
        for msg in mid:
            
            # is there better way to have all same code in and out of pause check??
            if self.pause_check:
                self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*P A U S E D*")
                
                while self.pause_check: 
                    # stop/next/back are all same as when not paused except in here they also reset the pause_check 
                    
                    # turn off solenoids while song is paused
                    #~ self.clear_outputs()
                    
                    if self.stop_check:
                        self.pause_check = False
                        return
                
                    if self.next_check:
                        self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*S K I P P E D*")
                        self.current_song +=1
                        self.next_check = False
                        self.pause_check = False
                        return
                        
                    if self.back_check:
                        # file_length < 20 sec fixes not being able to go back a file when playing a really short file
                        if progress < 5 or file_length < 20: 
                            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*P R E V I O U S*")
                            self.current_song -= 1
                            self.emit(QtCore.SIGNAL("playerLastFile()"))
                        else:
                            # just return to main while loop and restart file from beginning 
                            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*R E S T A R T*")
                        self.back_check = False
                        self.pause_check = False
                        return
                        
                    time.sleep(0.2)
                    
            if self.stop_check:
                return
        
            if self.next_check:
                self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*S K I P P E D*")
                self.current_song +=1
                self.next_check = False
                return
                
            if self.back_check:
                # file_length < 20 sec fixes not being able to go back a file when playing a really short file
                if progress < 5 or file_length < 20: 
                    self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*P R E V I O U S*")
                    self.current_song -= 1
                    self.emit(QtCore.SIGNAL("playerLastFile()"))
                else:
                    # just return to main while loop and restart file from beginning 
                    self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "*R E S T A R T*")
                self.back_check = False
                return
     
            if not msg.is_meta and msg.type != 'program_change' and msg.type != 'control_change':
                
                # if we made it this far then the message must be note_on/off type
                time.sleep(msg.time) # MUST GO BERFORE PLAY_NOTE FUNCTION
                self.play_note(msg, notes, adjust_value)
                    
                # song progress
                current_message += 1
                progress_old = progress
                progress = int((current_message / message_count)*100) # save progress of the song as an int
                if progress_old != progress: # only emit the progress value when it updates
                    self.emit(QtCore.SIGNAL("updatePlayerProgress(int)"), progress)
                        
        # this runs after each file naturally reaches the end (next btn was NOT pressed)
        self.emit(QtCore.SIGNAL("playerNextFile()"))
        self.current_song += 1
    
    
    # NEED TO WRAP MY HEAD AROUND OCTAVE ADJUST - WHY IS THERE ANOTHER -24 WHILE NOTE>24 IN PLAY_NOTE???
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
        #~ if status == 'on':
            #~ self.on_check = True
            
        return
    
    def play_note(self, msg, notes, adjust_value):
        
        # enable skip (& back) btns until the song starts playing
        self.emit(QtCore.SIGNAL("playerNextEnabled(bool)"), True)
        self.emit(QtCore.SIGNAL("playerBackEnabled(bool)"), True)
        
        msg_data = str(msg)
        temp1 = msg_data.find('note_')
        temp2 = msg_data.find('channel')
        status = msg_data[temp1 + 5:temp2]  # status = on or off (redundant: just use msg.type == 'note_on')
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
        note = int(note) - adjust_value # adjust notes to playable range

        # ******** TRY BOTH WAYS !?!?!?
        #adjust for notes that are still outside the range of the piano
        while note > 24:
            #~ note = note - 8 # changed from -24 to -8
            note = note - 24

        #print to terminal for debug purposes
        #~ print("Note {} {}".format(note, status))
        #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Note {} {}".format(note, status))
        
        # google easier way? use dictionaries??
        #Output to solenoids
        if status == 'off ':
            print("Note {} {}".format(note, status))
            #~ self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Note {} {}".format(note, status)) 
            
            # CHANGE TO DICTIONARIES LIKE LIVE MODE!!!
            #~ if note == 1:
                #~ bus1.write_pin(1, 0)
            #~ elif note == 2:
                #~ bus1.write_pin(2, 0)
            #~ elif note == 3:
                #~ bus1.write_pin(3, 0)
            #~ elif note == 4:
                #~ bus1.write_pin(4, 0)
            #~ elif note == 5:
                #~ bus1.write_pin(5, 0)
            #~ elif note == 6:
                #~ bus1.write_pin(6, 0)
            #~ elif note == 7:
                #~ bus1.write_pin(7, 0)
            #~ elif note == 8:
                #~ bus1.write_pin(8, 0)
            #~ elif note == 9:
                #~ bus1.write_pin(9, 0)
            #~ elif note == 10:
                #~ bus1.write_pin(10, 0)
            #~ elif note == 11:
                #~ bus1.write_pin(11, 0)
            #~ elif note == 12:
                #~ bus1.write_pin(12, 0)
            #~ elif note == 13:
                #~ bus1.write_pin(13, 0)
            #~ elif note == 14:
                #~ bus1.write_pin(14, 0)
            #~ elif note == 15:
                #~ bus1.write_pin(15, 0)
            #~ elif note == 16:
                #~ bus1.write_pin(16, 0)
            #~ elif note == 17:
                #~ bus2.write_pin(1, 0)
            #~ elif note == 18:
                #~ bus2.write_pin(2, 0)
            #~ elif note == 19:
                #~ bus2.write_pin(3, 0)
            #~ elif note == 20:
                #~ bus2.write_pin(4, 0)
            #~ elif note == 21:
                #~ bus2.write_pin(5, 0)
            #~ elif note == 22:
                #~ bus2.write_pin(6, 0)
            #~ elif note == 23:
                #~ bus2.write_pin(7, 0)
            #~ elif note == 24:
                #~ bus2.write_pin(8, 0)
            #~ elif note == 25:
                #~ bus2.write_pin(9, 0)
                
        if status == 'on ':
            print("Note {} {}".format(note, status))
            self.emit(QtCore.SIGNAL("updatePlayerText(QString)"), "Note {} {}".format(note, status)) 
            
            #~ if note == 1:
                #~ bus1.write_pin(1, 1)
            #~ elif note == 2:
                #~ bus1.write_pin(2, 1)
            #~ elif note == 3:
                #~ bus1.write_pin(3, 1)
            #~ elif note == 4:
                #~ bus1.write_pin(4, 1)
            #~ elif note == 5:
                #~ bus1.write_pin(5, 1)
            #~ elif note == 6:
                #~ bus1.write_pin(6, 1)
            #~ elif note == 7:
                #~ bus1.write_pin(7, 1)
            #~ elif note == 8:
                #~ bus1.write_pin(8, 1)
            #~ elif note == 9:
                #~ bus1.write_pin(9, 1)
            #~ elif note == 10:
                #~ bus1.write_pin(10, 1)
            #~ elif note == 11:
                #~ bus1.write_pin(11, 1)
            #~ elif note == 12:
                #~ bus1.write_pin(12, 1)
            #~ elif note == 13:
                #~ bus1.write_pin(13, 1)
            #~ elif note == 14:
                #~ bus1.write_pin(14, 1)
            #~ elif note == 15:
                #~ bus1.write_pin(15, 1)
            #~ elif note == 16:
                #~ bus1.write_pin(16, 1)
            #~ elif note == 17:
                #~ bus2.write_pin(1, 1)
            #~ elif note == 18:
                #~ bus2.write_pin(2, 1)
            #~ elif note == 19:
                #~ bus2.write_pin(3, 1)
            #~ elif note == 20:
                #~ bus2.write_pin(4, 1)
            #~ elif note == 21:
                #~ bus2.write_pin(5, 1)
            #~ elif note == 22:
                #~ bus2.write_pin(6, 1)
            #~ elif note == 23:
                #~ bus2.write_pin(7, 1)
            #~ elif note == 24:
                #~ bus2.write_pin(8, 1)
            #~ elif note == 25:
                #~ bus2.write_pin(9, 1)
         
        return
            
    #~ def clear_outputs(self):
        #~ bus1.write_port(0, 0x00)
        #~ bus1.write_port(1, 0x00)
        #~ bus2.write_port(0, 0x00)
        #~ bus2.write_port(1, 0x00)
    
    

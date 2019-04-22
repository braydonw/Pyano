import time, logging
from PyQt4 import QtGui, QtCore, uic
from mido import MidiFile, MidiTrack, Message, MetaMessage, second2tick, bpm2tempo
from pynput import keyboard
from pynput.keyboard import Key, Controller


#---WORKER THREAD: MIDI MAKER-------------------------------------------

class MakerThread(QtCore.QThread):
    
    def __init__(self, parent = None):
        super(MakerThread, self).__init__(parent)
        # variables that are changed by the MainWindow thread
        self.maker_song_name = ""
        self.maker_song_BPM = ""
    
    def run(self):       
        
        # dictionaries that map qwerty-kb keys to midi numbers and piano notes
        key2midi = {'z': '60', 's': '61', 'x': '62', 'd': '63', 'c': '64', 'v': '65',
                    'g': '66', 'b': '67', 'h': '68', 'n': '69', 'j': '70', 'm': '71',
                    'q': '72', '2': '73', 'w': '74', '3': '75', 'e': '76', 'r': '77',
                    '5': '78', 't': '79', '6': '80', 'y': '81', '7': '82', 'u': '83'}
        key2note = {'z': 'C4 ', 's': 'C#4', 'x': 'D4 ', 'd': 'D#4', 'c': 'E4 ', 'v': 'F4 ',
                    'g': 'F#4', 'b': 'G4 ', 'h': 'G#4', 'n': 'A4 ', 'j': 'A#4', 'm': 'B4 ',
                    'q': 'C5 ', '2': 'C#5', 'w': 'D5 ', '3': 'D#5', 'e': 'E5 ', 'r': 'F5 ',
                    '5': 'F#5', 't': 'G5 ', '6': 'G#5', 'y': 'A5 ', '7': 'A#5', 'u': 'B5 '}
         
        # create a new MIDI file with an empty track
        mid = MidiFile()
        track = MidiTrack()        
        mid.tracks.append(track)

        # tempo & beat resolution; 120 BPM = 500,000 tempo
        ticks_per_beat = 240 # pulses per quarter note (240 is good default)
        tempo = bpm2tempo(int(self.maker_song_BPM)) # micro-seconds per beat
        
        # use bpm from gui to set tempo for the entire file
        track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
        
        # timing setup for recording the time between keypresses
        start_time = time.time()
        self.prev_time = 0 # self since we are modifying it in the on_press sub-method
        
        self.hold_times = []
        
        
        # MOVE ADJ TIME AND STUFF TO HERE??
        
        # method call from key listener
        def on_press(key):
            '''
            IDEA: figure out a way to only save the time of the 1st on message and the 1st corresponding
            off message - then discard all duplicate on messages in-between - or add all repeating on delays
            to the Off message?
            
            on_press needs to add all intermidate timings to a list
            on_release needs to add all those times to the Off message then clear the list
            
            will this work if holding one key and you press another? or does that mess up the hold_times[]
            
            probably need to change adj_time and prev_time... rethink logic completely
            '''
            # get the time that has passed since this thread started
            time_since_start = time.time() - start_time
                
            try:
                # see if the key pressed is in dictionary of valid keys
                midi_note = key2midi[key.char]
                kb_note = key2note[key.char]
                
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'maker', str(key.char), 'on')
                
                # if the key is valid find the time since last keypress
                adj_time = time_since_start - self.prev_time
                self.prev_time = time_since_start # ignore the time of any invalid keys
                
                # convert time since last valid keypress to ticks (PPQN)
                ticks = second2tick(adj_time, ticks_per_beat, tempo)
                #~ print(ticks)
                
                # for testing
                #~ logging.info('adj_time: {}'.format(round(adj_time, 3)))
                #~ logging.info('ticks: {}'.format(int(ticks)))
                
                # add the note on/off data to the midi file
                track.append(Message('note_on', note=int(midi_note), time=int(ticks)))                
                #~ track.append(Message('note_off', note=int(midi_note), time=0))
                
                # build and emit gui text output
                gui_output = (" " + key.char.upper() + "    " + kb_note + "   " + str((round(adj_time, 3))))
                #~ self.emit(QtCore.SIGNAL("updateMakerText(QString)"), gui_output)
                logging.info('ON  ' + gui_output)
                
                
                self.hold_times.append(ticks)
                
            except (KeyError, AttributeError) as e:
                logging.debug('invalid key {}'.format(e))
                
        # method call from key listener
        def on_release(key):

            # check for cancel/done keypress (backspace/enter)
            # remember gui btns simulate key presses
            if key == keyboard.Key.backspace or key == keyboard.Key.esc:
                # discard file
                self.emit(QtCore.SIGNAL("updateMakerGUI(QString)"), "Canceled... Discarding song...")
                self.emit(QtCore.SIGNAL("hideAllIndicators()"))
                logging.info('maker-cancel btn clicked')
                return False # returning False stops the key listener

            elif key == keyboard.Key.enter:
                # save file
                mid.save(self.maker_song_name)
                self.emit(QtCore.SIGNAL("updateMakerGUI(QString)"), "File saved successfully")
                self.emit(QtCore.SIGNAL("updateMakerName()"))
                self.emit(QtCore.SIGNAL("hideAllIndicators()"))
                logging.info('maker-done btn clicked')
                return False

            try:
                # see if the key pressed is in dictionary of valid keys
                midi_note = key2midi[key.char]
                kb_note = key2note[key.char]
                
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'maker', str(key.char), 'off')
                
                # get the time that has passed since this thread started
                time_since_start = time.time() - start_time
                
                # remove first element in hold_time list since it is already saved with the On Message
                # add the rest of the elements up and add them to the Off Message
                self.hold_times = self.hold_times[1:]

                # if the key is valid find the time since last keypress
                adj_time = time_since_start - self.prev_time
                self.prev_time = time_since_start # ignore the time of any invalid keys

                # convert time since last valid keypress to ticks (PPQN)
                ticks = second2tick(adj_time, ticks_per_beat, tempo)
                print(*self.hold_times)
                print(sum(self.hold_times))
                #~ ticks = ticks + sum(self.hold_times)
                #~ self.hold_times.clear()

                # for testing
                #~ logging.info('adj_time: {}'.format(round(adj_time, 3)))
                #~ logging.info('ticks: {}'.format(int(ticks)))

                # add the note on/off data to the midi file
                #~ track.append(Message('note_on', note=int(midi_note), time=int(ticks)))                
                track.append(Message('note_off', note=int(midi_note), time=int(ticks)))

                # build and emit gui text output
                gui_output = (" " + key.char.upper() + "    " + kb_note + "   " + str((round(adj_time, 3))))
                self.emit(QtCore.SIGNAL("updateMakerText(QString)"), gui_output)
                logging.info('OFF ' + gui_output)
                
            except (KeyError, AttributeError) as e:
                logging.debug('invalid key {}'.format(e))
        
        # starts a key listener (return False to stop)
        # this is actually starting a 3rd thread
        with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()
            

        logging.info('Exiting makerThread')

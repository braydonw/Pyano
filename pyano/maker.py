import time, logging
from PyQt4 import QtGui, QtCore, uic
from mido import MidiFile, MidiTrack, Message, second2tick, bpm2tempo
from pynput import keyboard
from pynput.keyboard import Key, Controller


#---WORKER THREAD: MIDI MAKER-------------------------------------------

class MakerThread(QtCore.QThread):
    
    def __init__(self, parent = None):
        # this is ran when on_maker_click is ran in gui thread
        
        # set MainWindow (gui thread) as parent of MakerThread
        super(self.__class__, self).__init__(parent)
        # variables that are changed by the MainWindow thread
        self.maker_song_name = ""
    
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

        ticks_per_beat = 720 # pulses per quarter note (240 is good default)              ** PLAY WITH THIS **
        tempo = bpm2tempo(120) # micro-seconds per beat
        
        # timing setup for recording the time between keypresses
        start_time = time.time()
        self.prev_time = 0 # self since we are modifying it in the on_press sub-method
        
        self.z_hold_times = []
        self.s_hold_times = []
        self.x_hold_times = []
        self.d_hold_times = []
        self.c_hold_times = []
        self.v_hold_times = []
        self.g_hold_times = []
        self.b_hold_times = []
        self.h_hold_times = []
        self.n_hold_times = []
        self.j_hold_times = []
        self.m_hold_times = []
        self.q_hold_times = []
        self.two_hold_times = []
        self.w_hold_times = []
        self.three_hold_times = []
        self.e_hold_times = []
        self.r_hold_times = []
        self.five_hold_times = []
        self.t_hold_times = []
        self.six_hold_times = []
        self.y_hold_times = []
        self.seven_hold_times = []
        self.u_hold_times = []
        
        
        # method call from key listener
        def on_press(key):
            '''
            IDEA: figure out a way to only save the time of the 1st on message and the 1st corresponding
            off message - then discard all duplicate on messages in-between - or add all repeating on delays
            to the Off message?
            
            on_press needs to add all intermidate timings to a list
            on_release needs to add all those times to the Off message then clear the list
            
            will this work if holding one key and you press another? or does that mess up the hold_times[]
            
            probably need to change adj_time (time_since_prev) and prev_time... rethink logic completely
            '''
            try:
                # see if the key pressed is in dictionary of valid keys
                midi_note = key2midi[key.char]
                kb_note = key2note[key.char]
                
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'maker', str(key.char), 'on')
                
                # get the time that has passed since this thread started
                time_since_start = time.time() - start_time
                
                # if the key is valid find the time since last keypress
                time_since_prev = time_since_start - self.prev_time
                self.prev_time = time_since_start
                
                # convert time since last valid keypress to ticks (PPQN)
                ticks = second2tick(time_since_prev, ticks_per_beat, tempo)
                
                # for testing
                #~ logging.info('time_since_prev: {}'.format(round(time_since_prev, 3)))
                #~ logging.info('ticks: {}'.format(int(ticks)))
                
                # add the note on/off data to the midi file
                track.append(Message('note_on', note=int(midi_note), time=int(ticks)))                
                
                # build and emit gui text output
                #~ gui_output = (" " + key.char.upper() + "    " + kb_note + "   " + str((round(time_since_prev, 3))))
                gui_output = (" " + key.char.upper() + "    " + kb_note + "   " + str((round(ticks))))
                #~ self.emit(QtCore.SIGNAL("updateMakerText(QString)"), gui_output)
                logging.info('ON  ' + gui_output)
                
                
                # NEEDS TO BE KEY SPECIFIC SO MULTIPLE KEY PRESSES BEFORE RELEASING 1 STILL WORKS
                
                # append to hold times until key is released
                # then remove 1st one and add the rest to the off delay
                # for that key, then clear hold_times
                if key.char == 'z': 
                    self.z_hold_times.append(ticks)
                elif key.char == 's':
                    self.s_hold_times.append(ticks)
                elif key.char == 'x':
                    self.x_hold_times.append(ticks)
                elif key.char == 'd':
                    self.d_hold_times.append(ticks)
                elif key.char == 'c':
                    self.c_hold_times.append(ticks)
                elif key.char == 'v':
                    self.v_hold_times.append(ticks)
                elif key.char == 'g':
                    self.g_hold_times.append(ticks)
                elif key.char == 'b':
                    self.b_hold_times.append(ticks)
                elif key.char == 'h':
                    self.h_hold_times.append(ticks)
                elif key.char == 'n':
                    self.n_hold_times.append(ticks)
                elif key.char == 'j':
                    self.j_hold_times.append(ticks)
                elif key.char == 'm':
                    self.m_hold_times.append(ticks)
                elif key.char == 'q': 
                    self.q_hold_times.append(ticks)
                elif key.char == '2':
                    self.two_hold_times.append(ticks)
                elif key.char == 'w':
                    self.w_hold_times.append(ticks)
                elif key.char == '3':
                    self.three_hold_times.append(ticks)
                elif key.char == 'e':
                    self.e_hold_times.append(ticks)
                elif key.char == 'r':
                    self.r_hold_times.append(ticks)
                elif key.char == '5':
                    self.five_hold_times.append(ticks)
                elif key.char == 't':
                    self.t_hold_times.append(ticks)
                elif key.char == '6':
                    self.six_hold_times.append(ticks)
                elif key.char == 'y':
                    self.y_hold_times.append(ticks)
                elif key.char == '7':
                    self.seven_hold_times.append(ticks)
                elif key.char == 'u':
                    self.u_hold_times.append(ticks)
                
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

                # if the key is valid find the time since last keypress
                time_since_prev = time_since_start - self.prev_time
                self.prev_time = time_since_start # ignore the time of any invalid keys

                ticks = second2tick(time_since_prev, ticks_per_beat, tempo)
                
                #~ print(len(self.z_hold_times))
                #~ print(self.z_hold_times)
                
                if key.char == 'z':

                    # remove first element in hold_time list since it is already saved with the On Message
                    # add the rest of the elements up and add them to the Off Message
                    self.z_hold_times = self.z_hold_times[1:]
                    
                    # check here to make sure list is not empty? NO sum empty list = 0
                    ticks = ticks + sum(self.z_hold_times)
                    
                    # reset
                    self.z_hold_times = []
                    
                elif key.char == 's':
                    ticks = ticks + sum(self.s_hold_times[1:0])
                    self.s_hold_times = []
                elif key.char == 'x':
                    ticks = ticks + sum(self.x_hold_times[1:0])
                    self.c_hold_times = []
                elif key.char == 'd':
                    ticks = ticks + sum(self.d_hold_times[1:0])
                    self.d_hold_times = []
                elif key.char == 'c':
                    ticks = ticks + sum(self.c_hold_times[1:0])
                    self.c_hold_times = []
                elif key.char == 'v':
                    ticks = ticks + sum(self.v_hold_times[1:0])
                    self.v_hold_times = []
                elif key.char == 'g':
                    ticks = ticks + sum(self.g_hold_times[1:0])
                    self.g_hold_times = []
                elif key.char == 'b':
                    ticks = ticks + sum(self.b_hold_times[1:0])
                    self.b_hold_times = []
                elif key.char == 'h':
                    ticks = ticks + sum(self.h_hold_times[1:0])
                    self.h_hold_times = []
                elif key.char == 'n':
                    ticks = ticks + sum(self.n_hold_times[1:0])
                    self.n_hold_times = []
                elif key.char == 'j':
                    ticks = ticks + sum(self.j_hold_times[1:0])
                    self.j_hold_times = []
                elif key.char == 'm':
                    ticks = ticks + sum(self.m_hold_times[1:0])
                    self.m_hold_times = []
                elif key.char == 'q':
                    ticks = ticks + sum(self.q_hold_times[1:0])
                    self.q_hold_times = []
                elif key.char == '2':
                    ticks = ticks + sum(self.two_hold_times[1:0])
                    self.two_hold_times = []
                elif key.char == 'w':
                    ticks = ticks + sum(self.w_hold_times[1:0])
                    self.w_hold_times = []
                elif key.char == '3':
                    ticks = ticks + sum(self.three_hold_times[1:0])
                    self.three_hold_times = []
                elif key.char == 'e':
                    ticks = ticks + sum(self.e_hold_times[1:0])
                    self.e_hold_times = []
                elif key.char == 'r':
                    ticks = ticks + sum(self.r_hold_times[1:0])
                    self.r_hold_times = []
                elif key.char == '5':
                    ticks = ticks + sum(self.five_hold_times[1:0])
                    self.five_hold_times = []
                elif key.char == 't':
                    ticks = ticks + sum(self.t_hold_times[1:0])
                    self.t_hold_times = []
                elif key.char == '6':
                    ticks = ticks + sum(self.six_hold_times[1:0])
                    self.six_hold_times = []
                elif key.char == 'y':
                    ticks = ticks + sum(self.y_hold_times[1:0])
                    self.y_hold_times = []
                elif key.char == '7':
                    ticks = ticks + sum(self.seven_hold_times[1:0])
                    self.seven_hold_times = []
                elif key.char == 'u':
                    ticks = ticks + sum(self.u_hold_times[1:0])
                    self.u_hold_times = []
                    
                    
                
                # for testing
                #~ logging.info('time_since_prev: {}'.format(round(time_since_prev, 3)))
                #~ logging.info('ticks: {}'.format(int(ticks)))

                # add the note on/off data to the midi file
                track.append(Message('note_off', note=int(midi_note), time=int(ticks)))

                # build and emit gui text output
                #~ gui_output = (" " + key.char.upper() + "    " + kb_note + "   " + str((round(time_since_prev, 3))))
                gui_output = (" " + key.char.upper() + "    " + kb_note + "   " + str((round(ticks))))
                self.emit(QtCore.SIGNAL("updateMakerText(QString)"), gui_output)
                logging.info('OFF ' + gui_output)
                
                
            except (KeyError, AttributeError) as e:
                logging.debug('invalid key {}'.format(e))
        
        # starts a key listener (return False to stop)
        # this is actually starting a 3rd thread
        with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()
            
            
            # CHANGE TO BE LIKE OTHER KEY LISTENERS??
            

        logging.info('Exiting makerThread')

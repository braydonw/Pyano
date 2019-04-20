import logging, time
from PyQt4 import QtCore
from pynput import keyboard
from pyano.IOPi import IOPi
from pynput import keyboard
from pynput.keyboard import Key, Controller

from mido import MidiFile, MidiTrack, Message, MetaMessage, second2tick, bpm2tempo, tempo2bpm # CLEANUP

# TODO: add a point multiplier for when the user gets on a streak
# TODO: fix when holding down incorrect (red) it spams health decrement

# ADD A TON OF COMMENTS EXPLAINING EVERYTHING IN EVERY MODULE

#---WORKER THREAD: MIDI HERO--------------------------------------------

class HeroThread(QtCore.QThread):

    def __init__(self, parent = None):
        super(HeroThread, self).__init__(parent)
        self.hero_username = ""
        self.hero_song = ""
        self.hero_score = 0
        self.hero_health = 100
        
        # difficulty settings
        self.score_increment = 5 # points to add for each successful hit
        self.health_decrement = 5 # points to subtract from each miss
        self.delay_multiplier = 1.5 # multipled with midi message delay
        
        # dictionaries that map qwerty-kb keys to solenoids & piano notes
        self.key2note = {'z': 'C4 ', 's': 'C#4', 'x': 'D4 ', 'd': 'D#4', 'c': 'E4 ', 'v': 'F4 ',
                         'g': 'F#4', 'b': 'G4 ', 'h': 'G#4', 'n': 'A4 ', 'j': 'A#4', 'm': 'B4 '}
        self.solenoid2key = {'1': 'z', '2': 's', '3': 'x', '4': 'd', '5': 'c', '6': 'v',
                             '7': 'g', '8': 'b', '9': 'h', '10': 'n', '11': 'j', '12': 'm'}
        self.key2solenoid = {'z':  1, 's':  2, 'x':  3, 'd':  4, 'c':  5, 'v':  6,
                             'g':  7, 'b':  8, 'h':  9, 'n': 10, 'j': 11, 'm': 12}
                             
        #~ # IO setup
        #~ # get busses from i2c addresses
        #~ self.bus1 = IOPi(0x20)
        #~ self.bus2 = IOPi(0x21)
        #~ # set all 4 port directions to output (0x00)
        #~ self.bus1.set_port_direction(0, 0x00)
        #~ self.bus1.set_port_direction(1, 0x00)
        #~ self.bus2.set_port_direction(0, 0x00)
        #~ self.bus2.set_port_direction(1, 0x00) # THIS WAS 0xC0 ???? 
        #~ # initialize all outputs to 0
        #~ self.clear_outputs()
        
        
    def run(self):
        
        # reset everything before each run
        self.hero_score = 0
        self.hero_health = 100
        # flags that are set to True when a key is waiting for user to press
        # if flag is true & that key is pressed then add points to score
        self.z_flag = False
        self.x_flag = False
        self.c_flag = False
        self.v_flag = False
        self.b_flag = False
        self.n_flag = False
        self.m_flag = False
        self.s_flag = False
        self.d_flag = False
        self.g_flag = False
        self.h_flag = False
        self.j_flag = False
        # flags that are set to True when user successfully hits key
        # when a user playable note turns off it checks to see if the key was hit
        # if the key was not hit then it subtracts from the user's health
        self.z_hit = False
        self.x_hit = False
        self.c_hit = False
        self.v_hit = False
        self.b_hit = False
        self.n_hit = False
        self.m_hit = False
        self.s_hit = False
        self.d_hit = False
        self.g_hit = False
        self.h_hit = False
        self.j_hit = False
        
        def on_press(key):
            try:
                solenoid = self.key2solenoid[key.char]
                
                # if key is pressed and flag is true (yellow indicator is active - add to score)
                if key.char == 'z' and self.z_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'z', "green")
                    self.hero_score += self.score_increment
                    self.z_hit = True
                    self.z_flag = False # prevents holding key to spam score increase
                # if key is pressed and flag is false (no yellow indicator - subtract health)
                elif key.char == 'z' and not self.z_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'z', "red")
                    self.hero_health -= self.health_decrement
                # repeat for the rest of the keys...
                elif key.char == 'x' and self.x_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'x', "green")
                    self.hero_score += self.score_increment
                    self.x_hit = True
                    self.z_flag = False
                    #~ self.emit(QtCore.SIGNAL("updateHeroScore(QString)"), str(self.hero_score))
                elif key.char == 'x' and not self.x_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'x', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'c' and self.c_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'c', "green")
                    self.hero_score += self.score_increment
                    self.c_hit = True
                    self.c_flag = False
                elif key.char == 'c' and not self.c_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'c', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'v' and self.v_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'v', "green")
                    self.hero_score += self.score_increment
                    self.v_hit = True
                    self.v_flag = False
                elif key.char == 'v' and not self.v_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'v', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'b' and self.b_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'b', "green")
                    self.hero_score += self.score_increment
                    self.b_hit = True
                    self.b_flag = False
                elif key.char == 'b' and not self.b_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'b', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'n' and self.n_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'n', "green")
                    self.hero_score += score_increment
                    self.n_hit = True
                    self.n_flag = False
                elif key.char == 'n' and self.n_flag == False:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'n', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'm' and self.m_flag == True:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'm', "green")
                    self.hero_score += self.score_increment
                    self.m_hit = True
                    self.m_flag = False
                elif key.char == 'm' and self.m_flag == False:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'm', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 's' and self.s_flag == True:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 's', "green")
                    self.hero_score += self.score_increment
                    self.s_hit = True
                    self.s_flag = False
                elif key.char == 's' and not self.s_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 's', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'd' and self.d_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'd', "green")
                    self.hero_score += self.score_increment
                    self.d_hit = True
                    self.d_flag = False
                elif key.char == 'd' and not self.d_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'd', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'g' and self.g_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'g', "green")
                    self.hero_score += self.score_increment
                    self.g_hit = True
                    self.g_flag = False
                elif key.char == 'g' and not self.g_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'g', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'h' and self.h_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'h', "green")
                    self.hero_score += self.score_increment
                    self.h_hit = True
                    self.h_flag = False
                elif key.char == 'h' and not self.h_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'h', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'j' and self.j_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'j', "green")
                    self.hero_score += self.score_increment
                    self.j_hit = True
                    self.j_flag = False
                elif key.char == 'j' and not self.j_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'j', "red")
                    self.hero_health -= self.health_decrement
                self.emit(QtCore.SIGNAL("updateHeroScore(QString)"), str(self.hero_score))
                self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    
                # output to solenoid
                if solenoid < 17:
                    #~ #self.bus1.write_pin(solenoid, 1)
                    pass
                else:
                    solenoid -= 16
                    #~ #self.bus2.write_pin(solenoid, 1)
                    pass
                    
            except (KeyError, AttributeError) as e:
                #~ print (e)
                pass
                    
        def on_release(key):
            
            if key == keyboard.Key.esc:
                #~ self.clear_outputs()
                self.hero_health = 0
                self.emit(QtCore.SIGNAL("resetHeroGUI()"))
                listener.stop()
                return 
            
            try:
                solenoid = self.key2solenoid[key.char]
                
                if key.char == 'z':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'z', "hide")
                if key.char == 'z':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'z', "hide")
                elif key.char == 'x':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'x', "hide")
                elif key.char == 'c':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'c', "hide")
                elif key.char == 'v':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'v', "hide")
                elif key.char == 'b':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'b', "hide")
                elif key.char == 'n':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'n', "hide")
                elif key.char == 'm':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'm', "hide")
                elif key.char == 's':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 's', "hide")
                elif key.char == 'd':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'd', "hide")
                elif key.char == 'g':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'g', "hide")
                elif key.char == 'h':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'h', "hide")
                elif key.char == 'j':
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'j', "hide")
                    
                if solenoid < 17:
                    #self.bus1.write_pin(solenoid, 0x00)
                    pass
                else:
                    solenoid -= 16
                    #self.bus2.write_pin(solenoid, 0x00)
                    
            except (KeyError, AttributeError):
                pass
           
        # start key listener thread that calls on_press and on_release for each key pressed
        listener = keyboard.Listener(on_press=on_press,on_release=on_release)
        listener.start()

        while self.hero_health > 1:
            self.play_file()
        #~ self.clear_outputs()
        listener.stop()

        # add username and score to leaderboard.csv file
        # fix hardcoded path
        with open('/home/pi/pyano-git/pyano/leaderboard.csv', 'a') as csv_file:
            line = str(self.hero_score) + ',' + self.hero_username + ',' + self.hero_song + '\n'
            csv_file.write(line)
            
        print('Final Score:', self.hero_score)
        self.emit(QtCore.SIGNAL("resetHeroGUI()"))
        #~ self.clear_outputs()
        
              
    def play_file(self):
        
        mid = MidiFile(self.hero_song)
        
        # dont play non type 1 files (ADD POPUP WINDOW)
        if mid.type != 1:
            return
        
        # get set of unique notes & check for off commands
        self.note_set = set()
        self.off_check = False
        for msg in mid:
            if not msg.is_meta and msg.type != 'program_change' and msg.type != 'control_change':
                self.add_to_note_set(msg)
        
        # don't play songs without off commands (ADD POPUP WINDOW)
        if not self.off_check:
            return
            
        # TEMP: NOTES BEFORE OCTAVE ADJUST
        #~ print(self.note_set)
            
        min_note = min([int(i) for i in self.note_set])
        max_note = max([int(i) for i in self.note_set])
        
        # set the adjust value based on the range of the song
        if max_note - min_note <= 25: 
            adjust_value = min_note - 1 # adjust the lowest note in the song to the first note on the piano
        else:
            adjust_value = 59 # adjust to play middle C plus 2 octaves on the piano 
        
        # go through midi file and actually play notes          
        for msg in mid:
                
            if self.hero_health < 1:
                #~ self.clear_outputs()
                return
                
            if not msg.is_meta and msg.type != 'program_change' and msg.type != 'control_change':
                time.sleep(msg.time * self.delay_multiplier)
                self.play_note(msg, adjust_value)
                        
    def add_to_note_set(self, msg):
        
        # extract the note from the message
        msg_data = str(msg)
        temp1 = msg_data.find('note_')
        temp2 = msg_data.find('channel')
        status = msg_data[temp1 + 5:temp2]  # status = on or off
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as midi
        
        # add note to set of notes (for checking note range of each midi file)
        self.note_set.add(note)
        
        # check if the midi file has on/off commands
        if status == 'off ':
            self.off_check = True
        return
    
    def play_note(self, msg, adjust_value):
        
        if self.hero_health < 1:
                #~ self.clear_outputs()
                return
                
        # extract note and status from message
        status = msg.type[len('note_'):]
        msg_data = str(msg)
        temp1 = msg_data.find('note=')
        temp2 = msg_data.find('velocity=')
        note = msg_data[temp1 + 5:temp2]  # note represented as MIDI #
        note = int(note) - adjust_value # adjust notes to playable range
        
        # DO WE EVEN TO THE OCTAVE ADJUST AND ADJ_VALUE WITH THIS IN HERE????
        # adjust for notes that are still outside the range of the piano
        while note > 24:
            note = note - 8
        while note < 1:
            note = note + 8
            
        # if the note is in the 1st octave, have the user play it
        if note in range (1, 12, 1):
            key = self.solenoid2key[str(note)]
            if status == 'on':
                self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), key, "yellow")
                if key == 'z':
                    self.z_flag = True
                elif key == 'x':
                    self.x_flag = True
                elif key == 'c':
                    self.c_flag = True
                elif key == 'v':
                    self.v_flag = True
                elif key == 'b':
                    self.b_flag = True
                elif key == 'n':
                    self.n_flag = True
                elif key == 'm':
                    self.m_flag = True
                elif key == 's':
                    self.s_flag = True
                elif key == 'd':
                    self.d_flag = True
                elif key == 'g':
                    self.g_flag = True
                elif key == 'h':
                    self.h_flag = True
                elif key == 'j':
                    self.j_flag = True
                
            elif status == 'off':
                self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), key, "hide")
                if key == 'z':
                    # if the user missed the key (never pressed in time), then subtract from health
                    if self.z_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.z_hit, self.z_flag = False, False
                elif key == 'x':
                    if self.x_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.x_hit, self.x_flag = False, False
                elif key == 'c':
                    if self.c_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.c_hit, self.c_flag = False, False
                elif key == 'v':
                    if self.v_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.v_hit, self.v_flag = False, False
                elif key == 'b':
                    if self.b_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.b_hit, self.b_flag = False, False
                elif key == 'n':
                    if self.n_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.n_hit, self.n_flag = False, False
                elif key == 'm':
                    if self.m_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.m_hit, self.m_flag = False, False
                elif key == 's':
                    if self.s_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.s_hit, self.s_flag = False, False
                elif key == 'd':
                    if self.d_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.d_hit, self.d_flag = False, False
                elif key == 'g':
                    if self.g_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.g_hit, self.g_flag = False, False
                elif key == 'h':
                    if self.h_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.h_hit, self.h_flag = False, False
                elif key == 'j':
                    if self.j_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(QString)"), str(self.hero_health))
                    self.j_hit, self.j_flag = False, False
        
        # otherwise play it on the physical piano
        else: 
            print("Note {} {}".format(note, status))
            if status == 'on ':
                if note < 17:
                    #~ self.bus1.write_pin(note, 1)
                    pass
                else:
                    note -= 16
                    #~ self.bus2.write_pin(note, 1)
                    pass
            elif status == 'off': 
                if note < 17:
                    #~ self.bus1.write_pin(note, 0)
                    pass
                else:
                    note -= 16
                    #~ self.bus2.write_pin(note, 0)
                    pass
                    
        return
        
    #~ def clear_outputs(self):
        #~ logging.info('CLEARING OUTPUTS')
        #~ self.bus1.write_port(0, 0x00)
        #~ self.bus1.write_port(1, 0x00)
        #~ self.bus2.write_port(0, 0x00)
        #~ self.bus2.write_port(1, 0x00)

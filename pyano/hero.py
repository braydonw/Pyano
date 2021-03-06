import logging, time, os
from PyQt4 import QtCore, QtGui
from pynput import keyboard
from mido import MidiFile, MidiTrack, Message
from pyano.IOPi import IOPi

PROJ_PATH = os.getcwd()
GPIO_ENABLED = False
PRINT_NOTES = True


#---WORKER THREAD: MIDI HERO--------------------------------------------

class HeroThread(QtCore.QThread):

    def __init__(self, parent = None):
        # this is ran when on_hero_click is ran in gui thread
        
        # set MainWindow (gui thread) as parent of HeroThread
        super(self.__class__, self).__init__(parent)
        
        # variables set when on_hero_start_click is ran in gui thread
        self.hero_username = "" # set by lineEdit_hero_username
        self.hero_song = "" # set by comboBox_hero_song
        self.difficulty = None # set by comboBox_hero_difficulty
        
        # variables updated and sent back to the gui
        self.hero_score = 0
        self.hero_health = 100
        
        # lowest & highest scores to beat from leaderboard; set when 
        self.lowest_highscore = 0 # passing makes score turn green
        self.highest_highscore = 0 # passing makes score turn gold
                
        # dicts that map qwerty-kb keys to solenoids & piano notes
        # keyboard key to piano note
        self.key2note = {'z': 'C4 ', 's': 'C#4', 'x': 'D4 ', 'd': 'D#4',
                         'c': 'E4 ', 'v': 'F4 ', 'g': 'F#4', 'b': 'G4 ',
                         'h': 'G#4', 'n': 'A4 ', 'j': 'A#4', 'm': 'B4 '}
        # solenoid pin to keyboard key
        self.solenoid2key = {'1': 'z', '2': 's', '3': 'x', '4': 'd',
                             '5': 'c', '6': 'v', '7': 'g', '8': 'b',
                             '9': 'h', '10': 'n', '11': 'j', '12': 'm'}
        # keyboard key to solenoid pin as int
        self.key2solenoid = {'z':  1, 's':  2, 'x':  3, 'd':  4,
                             'c':  5, 'v':  6, 'g':  7, 'b':  8,
                             'h':  9, 'n': 10, 'j': 11, 'm': 12}
                             
        # setup solenoid output using i2c
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
        
        
    def run(self):
        # this is ran when on_hero_start_click is ran in gui thread
        
        # disable btn_hero_stop until processing is finished
        self.emit(QtCore.SIGNAL("heroStopEnabled(bool)"), False)
        
        # small pause for files that immediatly play notes
        #~ time.sleep(2)
        
        # log username and song
        # different from csv (log shows in terminal & in log file)
        logging.info('Username: ' + self.hero_username)
        logging.info('Song: ' + self.hero_song)
        
        # reset health and score at the start of each run
        self.hero_score = 0
        self.hero_health = 100

        # set variables based on difficulty from gui
        # delay_multiplier = multiplied by midi message delay
        # score_increment = score awarded for each correct keypress
        # health_increment = health awarded for each correct keypress
        # health_decrement = amount lost for missed keys and misspresses
        if self.difficulty == 'E': # easy
            self.delay_multiplier = 1.5
            self.score_increment = 15
            self.health_increment = 4
            self.health_decrement = 1
        elif self.difficulty == 'N': # normal
            self.delay_multiplier = 1
            self.score_increment = 5
            self.health_increment= 2
            self.health_decrement = 6
        elif self.difficulty == 'H': # hard
            self.delay_multiplier = 0.75
            self.score_increment = 7
            self.health_increment = 3
            self.health_decrement = 20
        elif self.difficulty == 'L': # legendary
            self.delay_multiplier = 0.6
            self.score_increment = 20
            self.health_increment = 3
            self.health_decrement = 30
        
        # flags get set true when a key is waiting for the user keypress
        # if flag is true & that key is pressed the score increases
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
        
        # flags get set true when user successfully hits key
        # when a user playable note turns off it checks to see if the 
        # key was hit & if not then it subtracts from health
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
        
        
        # function called by keylistener on each keypress
        def on_press(key):
            
            # key2solenoid throws exception for keys we want to ignore
            try:
                # solenoid is the pin number on the IOPi
                solenoid = self.key2solenoid[key.char]
                
                # big if-elif block that mathces the key pressed and the
                # flag indicating if it should have been pressed to 
                # determine how score and health should be adjusted...
                
                # if key is pressed and flag is true (yellow indicator is active - add to score)
                if key.char == 'z' and self.z_flag:
                    # emit signal updating indicator in the gui thread to green
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'z', "green")
                    # increment score & health
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    # activate hit variable so play_note function knows not to subtract health
                    self.z_hit = True
                    # reset flag for key and prevent holding key to spam score increase
                    self.z_flag = False
                # if key is pressed and flag is false (no yellow indicator - subtract health)
                elif key.char == 'z' and not self.z_flag:
                    # emit signal updating indicator in the gui thread to red
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'z', "red")
                    # decrement health
                    self.hero_health -= self.health_decrement
                    
                # repeat for the rest of the keys...
                elif key.char == 'x' and self.x_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'x', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.x_hit = True
                    self.z_flag = False
                elif key.char == 'x' and not self.x_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'x', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'c' and self.c_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'c', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.c_hit = True
                    self.c_flag = False
                elif key.char == 'c' and not self.c_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'c', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'v' and self.v_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'v', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.v_hit = True
                    self.v_flag = False
                elif key.char == 'v' and not self.v_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'v', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'b' and self.b_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'b', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.b_hit = True
                    self.b_flag = False
                elif key.char == 'b' and not self.b_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'b', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'n' and self.n_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'n', "green")
                    self.hero_score += score_increment
                    self.hero_health += self.health_increment
                    self.n_hit = True
                    self.n_flag = False
                elif key.char == 'n' and self.n_flag == False:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'n', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'm' and self.m_flag == True:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'm', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.m_hit = True
                    self.m_flag = False
                elif key.char == 'm' and self.m_flag == False:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'm', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 's' and self.s_flag == True:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 's', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.s_hit = True
                    self.s_flag = False
                elif key.char == 's' and not self.s_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 's', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'd' and self.d_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'd', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.d_hit = True
                    self.d_flag = False
                elif key.char == 'd' and not self.d_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'd', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'g' and self.g_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'g', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.g_hit = True
                    self.g_flag = False
                elif key.char == 'g' and not self.g_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'g', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'h' and self.h_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'h', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.h_hit = True
                    self.h_flag = False
                elif key.char == 'h' and not self.h_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'h', "red")
                    self.hero_health -= self.health_decrement
                elif key.char == 'j' and self.j_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'j', "green")
                    self.hero_score += self.score_increment
                    self.hero_health += self.health_increment
                    self.j_hit = True
                    self.j_flag = False
                elif key.char == 'j' and not self.j_flag:
                    self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), 'j', "red")
                    self.hero_health -= self.health_decrement
                    
                # limit health range to 0-100
                if self.hero_health < 0:
                    self.hero_health = 0
                elif self.hero_health > 100:
                    self.hero_health = 100
                
                # update health and score in gui thread
                self.emit(QtCore.SIGNAL("updateHeroScore(int)"), self.hero_score)
                self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    
                # activate solenoid
                self.bus1.write_pin(solenoid, 1)
            
            # ignore keys that are not mapped to solenoids 1-12        
            except:
                pass
        
        
        # function called by keylistener on each keyrelease            
        def on_release(key):
            
            # esc key stops the game
            # on_hero_stop_click in gui thread simulates esc keypress
            # set health to 0 and return to play_file while health >= 1
            if key == keyboard.Key.backspace:
                self.hero_health = 0
                return 
                
            # key2solenoid throws exception for keys we want to ignore
            try:
                # solenoid is the pin number on the IOPi
                solenoid = self.key2solenoid[key.char]
                
                # hide the indicator in the gui thread on keyrelease
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
                
                # deactivate solenoid
                self.bus1.write_pin(solenoid, 0)
                    
            # ignore keys that are not mapped to solenoids 1-12         
            except:
                pass
        
           
        # create key listener thread that can call on_press & on_release
        listener = keyboard.Listener(on_press=on_press,
                                     on_release=on_release)
        
        # start keylistener
        listener.start()
        
        # play the midi file until health reaches zero
        while self.hero_health >= 1:
            # disable btn_hero_stop until processing is finished
            self.emit(QtCore.SIGNAL("heroStopEnabled(bool)"), False)
            # start processing and playing file
            self.play_file()
            
        # hide indicators & reset gui thread hero page
        # reset must go before listener stop or bad things happen!!
        self.emit(QtCore.SIGNAL("hideAllIndicators()"))
        self.emit(QtCore.SIGNAL("resetHeroGUI()"))
            
        # stop keylistener & clear all solenoids
        listener.stop()
        self.clear_outputs()
        
        # add username, score, song, & difficulty to leaderboard file
        with open(PROJ_PATH + '/pyano/leaderboard.csv', 'a') as csv_file:
            csv_file.write(str(self.hero_score) + ',' + 
                           self.hero_username + ',' + self.hero_song + 
                           ',' + self.difficulty + '\n')
        
        # log final score
        logging.info('Final Score: ' + str(self.hero_score))
        
        
    def play_file(self):
        # simplified version of the functions in player mode
        # player mode should be updated with this simpler logic flow
        
        mid = MidiFile(PROJ_PATH + '/midi-files/' + self.hero_song)

        if mid.type != 1:
            self.hero_health = 0
            return
            
        note_set = set()
        has_off_cmds = False
        is_custom = False
        
        for msg in mid:
            if msg.type == 'text' and msg.text == 'custom pyano file':
                logging.info('Custom pyano file')
                is_custom = True
                break
                    
        for msg in mid:    
            if msg.type == 'note_on' or msg.type == 'note_off':
                note_set.add(msg.note)
                
                if not has_off_cmds and msg.type == 'note_off':
                    has_off_cmds = True
                    
        if not has_off_cmds:
            logging.error("ERROR: file does not have any off commands")
            self.hero_health = 0
            return
            
        min_note = min([int(i) for i in note_set])
        max_note = max([int(i) for i in note_set])
        range_notes = max_note - min_note
        
        if not is_custom and range_notes <= 25: # why 25?
            # adjust lowest note in the song to first note on piano
            adjust_value = min_note - 1 
        else:
            # custom files use midi number 60 (C4) as first key
            # midi number - adjust value = solenoid pin (ex: 60-59=1)
            adjust_value = 59
            
        # re-enable btn_hero_stop
        self.emit(QtCore.SIGNAL("heroStopEnabled(bool)"), True)
            
        for msg in mid:
            
            # break for loop when health reaches 0
            # cleans up i2c, hides indicators, then returns to playing 
            if self.hero_health < 1:
                break
            
            if msg.type == 'note_on' or msg.type == 'note_off':
                time.sleep(msg.time * self.delay_multiplier)
                self.play_note(msg, adjust_value)

        self.clear_outputs()
        self.emit(QtCore.SIGNAL("hideAllIndicators()"))
        
    
    def play_note(self, msg, adjust_value):

        note = int(msg.note) - adjust_value
        
        #~ while note > 24:
            #~ note = note - 12
        #~ while note < 1:
            #~ note = note + 12

        if note < 1 or note > 24:
            if PRINT_NOTES: print("Ignoring note " + str(note))
            return
            
        # if the note is in the 1st octave, have the user play it
        try:
            key = self.solenoid2key[str(note)]
            
            if msg.type == 'note_on':
                self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), key, "yellow")
                
                # set flags indicating that a key needs to be hit
                # if key is hit when flag is true then points are added
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
                
            elif msg.type == 'note_off':
                self.emit(QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), key, "hide")
                
                if key == 'z':
                    # if the user missed the key (never pressed in time)
                    # then subtract from health
                    if self.z_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.z_hit, self.z_flag = False, False
                elif key == 'x':
                    if self.x_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.x_hit, self.x_flag = False, False
                elif key == 'c':
                    if self.c_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.c_hit, self.c_flag = False, False
                elif key == 'v':
                    if self.v_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.v_hit, self.v_flag = False, False
                elif key == 'b':
                    if self.b_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.b_hit, self.b_flag = False, False
                elif key == 'n':
                    if self.n_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.n_hit, self.n_flag = False, False
                elif key == 'm':
                    if self.m_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.m_hit, self.m_flag = False, False
                elif key == 's':
                    if self.s_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.s_hit, self.s_flag = False, False
                elif key == 'd':
                    if self.d_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.d_hit, self.d_flag = False, False
                elif key == 'g':
                    if self.g_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.g_hit, self.g_flag = False, False
                elif key == 'h':
                    if self.h_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.h_hit, self.h_flag = False, False
                elif key == 'j':
                    if self.j_hit == False:
                        self.hero_health -= self.health_decrement
                        self.emit(QtCore.SIGNAL("updateHeroHealth(int)"), self.hero_health)
                    self.j_hit, self.j_flag = False, False
        
        # otherwise play it on the physical piano
        except: 
            
            if PRINT_NOTES: print("Note {} {}".format(note, msg.type[5:]))
            
            if msg.type == 'note_on':
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'hero', str(note), 'on') 
                if note < 17:
                    if GPIO_ENABLED: self.bus1.write_pin(note, 1)
                else:
                    note -= 16
                    if GPIO_ENABLED: self.bus2.write_pin(note, 1)
            elif msg.type == 'note_off':
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'hero', str(note), 'off') 
                if note < 17:
                    if GPIO_ENABLED: self.bus1.write_pin(note, 0)
                else:
                    note -= 16
                    if GPIO_ENABLED: self.bus2.write_pin(note, 0)
                    
        return
    
    # function that sets all i2c pins to 0 
    def clear_outputs(self):
        if GPIO_ENABLED:
            logging.info('CLEARING OUTPUTS')
            self.bus1.write_port(0, 0x00)
            self.bus1.write_port(1, 0x00)
            self.bus2.write_port(0, 0x00)
            self.bus2.write_port(1, 0x00)

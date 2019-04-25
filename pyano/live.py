'''
ADD FULL DESCRIPTION HERE

'''

# imports
import time, logging
from PyQt4 import QtCore
from pynput import keyboard
from pyano.IOPi import IOPi

# globals
GPIO_ENABLED = False


#---WORKER THREAD: MIDI LIVE--------------------------------------------

class LiveThread(QtCore.QThread):

    def __init__(self, parent = None):
        # this is ran when on_live_click is ran in gui thread
        
        # set MainWindow (gui thread) as parent of LiveThread
        super(self.__class__, self).__init__(parent)
        
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
        
        # dicts that map qwerty-kb keys to solenoids & piano notes
        # keyboard key to piano note
        key2note = {'z': 'C4 ', 's': 'C#4', 'x': 'D4 ', 'd': 'D#4', 
                    'c': 'E4 ', 'v': 'F4 ', 'g': 'F#4', 'b': 'G4 ', 
                    'h': 'G#4', 'n': 'A4 ', 'j': 'A#4', 'm': 'B4 ', 
                    'q': 'C5 ', '2': 'C#5', 'w': 'D5 ', '3': 'D#5', 
                    'e': 'E5 ', 'r': 'F5 ', '5': 'F#5', 't': 'G5 ', 
                    '6': 'G#5', 'y': 'A5 ', '7': 'A#5', 'u': 'B5 ', 
                    'i' : 'C6 '}
        # keyboard key to solenoid pin as int
        key2solenoid = {'z':  1, 's':  2, 'x':  3, 'd':  4, 'c':  5, 
                        'v':  6, 'g':  7, 'b':  8, 'h':  9, 'n': 10, 
                        'j': 11, 'm': 12, 'q': 13, '2': 14, 'w': 15, 
                        '3': 16, 'e': 17, 'r': 18, '5': 19, 't': 20, 
                        '6': 21, 'y': 22, '7': 23, 'u': 24, 'i': 25}
        
        
        # function called by keylistener on each keypress
        def on_press(key):
            
            # key2solenoid throws exception for keys we want to ignore
            try:
                # convert key to solenoid pin number & piano note
                solenoid = key2solenoid[key.char]
                note = key2note[key.char]
                
                # build and send output string to gui thread
                #~ if solenoid < 10: 
                    #~ str_solenoid = "0" + str(solenoid)
                #~ else:
                    #~ str_solenoid = str(solenoid)
                #~ gui_output = key.char.upper() + "  |   " + note + "  |  " + str_solenoid
                #~ self.emit(QtCore.SIGNAL("updateLiveText(QString)"), gui_output)
                
                # call gui function that enables key indicator
                # arguments are (mode, key, state)
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'live', str(key.char), 'on') 
                
                # activate solenoid while key is pressed
                if GPIO_ENABLED:
                    if solenoid < 17:
                        self.bus1.write_pin(solenoid, 1)
                        print("Bus 1 - Pin " + str(solenoid))
                    else:
                        # 16 pins/bus so convert bus1 17-25 to bus2 1-9
                        solenoid -= 16
                        self.bus2.write_pin(solenoid, 1)
                        print("Bus 2 - Pin " + str(solenoid))
            
            # ignore keys that are not mapped to solenoids 1-25
            # key error for chars and attrib error for things like esc
            except (KeyError, AttributeError):
                pass
                
        
        # function called by keylistener on each keyrelease        
        def on_release(key):
            
            # backspace or esc key stops the game
            # on_live_stop_click in gui thread simulates esc keypress
            if key == keyboard.Key.backspace:
                self.clear_outputs()
                self.emit(QtCore.SIGNAL("resetLiveGUI()"))
                return False # stop keylistener
            
            # key2solenoid throws exception for keys we want to ignore
            try:
                # solenoid is the pin number on the IOPi
                solenoid = key2solenoid[key.char]
                note = key2note[key.char]
                
                # build and send output string to gui thread
                if solenoid < 10: 
                    str_solenoid = "0" + str(solenoid)
                else:
                    str_solenoid = str(solenoid)
                gui_output = key.char.upper() + "  |   " + note + "  |  " + str_solenoid
                self.emit(QtCore.SIGNAL("updateLiveText(QString)"), gui_output)
                
                # call gui function that disables key indicator
                self.emit(QtCore.SIGNAL("showIndicator(QString, QString, QString)"), 'live', str(key.char), 'off') 
                
                # deactivate solenoid when key is released
                if GPIO_ENABLED:
                    if solenoid < 17:
                        self.bus1.write_pin(solenoid, 0)
                    else:
                        # 16 pins/bus so convert bus1 17-25 to bus2 1-9
                        solenoid -= 16
                        self.bus2.write_pin(solenoid, 0)
                    
            # ignore keys that are not mapped to solenoids 1-25
            except (KeyError, AttributeError):
                pass
                
                
        # start keylistener that calls on_press and on_release for each key pressed
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join() # start keylistener
            
    
    # function that sets all i2c pins to 0
    def clear_outputs(self):
        if GPIO_ENABLED:
            logging.info('CLEARING OUTPUTS')
            self.bus1.write_port(0, 0x00)
            self.bus1.write_port(1, 0x00)
            self.bus2.write_port(0, 0x00)
            self.bus2.write_port(1, 0x00)

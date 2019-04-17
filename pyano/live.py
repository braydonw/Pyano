import time, logging
from PyQt4 import QtCore
from pynput import keyboard
from pyano.IOPi import IOPi


#---WORKER THREAD: MIDI LIVE--------------------------------------------

class LiveThread(QtCore.QThread):

    def __init__(self, parent = None):
        super(LiveThread, self).__init__(parent)
        
        # IO setup
        # get busses from i2c addresses
        self.bus1 = IOPi(0x20)
        self.bus2 = IOPi(0x21)
        # set all 4 port directions to output (0x00)
        self.bus1.set_port_direction(0, 0x00)
        self.bus1.set_port_direction(1, 0x00)
        self.bus2.set_port_direction(0, 0x00)
        self.bus2.set_port_direction(1, 0x00) # THIS WAS 0xC0 ???? 
        # initialize all outputs to 0
        self.clear_outputs()
    
    def run(self):
        
        # dictionaries that map qwerty-kb keys to solenoids & piano notes
        key2solenoid = {'z':  1, 's':  2, 'x':  3, 'd':  4, 'c':  5, 'v':  6,
                        'g':  7, 'b':  8, 'h':  9, 'n': 10, 'j': 11, 'm': 12,
                        'q': 13, '2': 14, 'w': 15, '3': 16, 'e': 17, 'r': 18,
                        '5': 19, 't': 20, '6': 21, 'y': 22, '7': 23, 'u': 24}
        key2note = {'z': 'C4 ', 's': 'C#4', 'x': 'D4 ', 'd': 'D#4', 'c': 'E4 ', 'v': 'F4 ',
                    'g': 'F#4', 'b': 'G4 ', 'h': 'G#4', 'n': 'A4 ', 'j': 'A#4', 'm': 'B4 ',
                    'q': 'C5 ', '2': 'C#5', 'w': 'D5 ', '3': 'D#5', 'e': 'E5 ', 'r': 'F5 ',
                    '5': 'F#5', 't': 'G5 ', '6': 'G#5', 'y': 'A5 ', '7': 'A#5', 'u': 'B5 '}
        
        def on_press(key):
            try:
                solenoid = key2solenoid[key.char]
                note = key2note[key.char]
                gui_output = str(key.char) + " | " + note + "| " + str(solenoid) + " pressed"
                self.emit(QtCore.SIGNAL("updateLiveText(QString)"), gui_output)
                if solenoid < 17:
                    self.bus1.write_pin(solenoid, 1)
                else:
                    solenoid -= 16
                    self.bus2.write_pin(solenoid, 1)
            except (KeyError, AttributeError):
                pass
                
                
        def on_release(key):
            try:
                solenoid = key2solenoid[key.char]
                if solenoid < 17:
                    self.bus1.write_pin(solenoid, 0)
                    pass
                else:
                    solenoid -= 16
                    self.bus2.write_pin(solenoid, 0)
            except (KeyError, AttributeError):
                pass
                
            if key == keyboard.Key.esc:
                self.clear_outputs()
                self.emit(QtCore.SIGNAL("resetLiveGUI()"))
                return False # stops keyboard.listener
                
        # start key listener that calls on_press and on_release for each key pressed
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
            
    def clear_outputs(self):
        logging.info('CLEARING OUTPUTS')
        self.bus1.write_port(0, 0x00)
        self.bus1.write_port(1, 0x00)
        self.bus2.write_port(0, 0x00)
        self.bus2.write_port(1, 0x00)

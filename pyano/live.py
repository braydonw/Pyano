# cleanup imports and only keep what is used / needed in this file
import time
from PyQt4 import QtCore
from pynput import keyboard #reads keyboard inputs
#~ from pyano.IOPi import IOPi #Library for IOPI Plus expansion board

#---WORKER THREAD: MIDI LIVE--------------------------------------------

class LiveThread(QtCore.QThread):

    def __init__(self, parent = None):
        super(LiveThread, self).__init__(parent)
        
    # TRY TO MOVE IO SETUP OUT OF WORKER THREADS AND INTO MAIN WINDOW IF POSSIBLE
    # MAY HAVE TO PASS SOME VARIABLES IN
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
    # MAKE INTO FUNCTION LIKE PLAYER HAS??
    #~ bus1.write_port(0, 0x00)
    #~ bus1.write_port(1, 0x00)
    #~ bus2.write_port(0, 0x00)
    #~ bus2.write_port(1, 0x00)
    
    def run(self):
        
        # dictionaries that map qwerty-kb keys to solenoids
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
                    #~ bus1.write_pin(solenoid, 1)
                    pass
                else:
                    solenoid -= 16
                    #~ bus2.write_pin(solenoid, 1)
                #~ live_on(key.char)
            except (KeyError, AttributeError) as e:
                pass
            return

        def on_release(key):
            try:
                solenoid = key2solenoid[key.char]
                if solenoid < 17:
                    #~ bus1.write_pin(solenoid, 0)
                    pass
                else:
                    solenoid -= 16
                    #~ bus2.write_pin(solenoid, 0)
                #~ live_off(key.char)
            except (KeyError, AttributeError) as e:
                pass
                
            if key == keyboard.Key.esc:
                self.emit(QtCore.SIGNAL("resetLiveGUI()"))
                #~ bus1.write_port(0, 0x00)
                #~ bus1.write_port(1, 0x00)
                #~ bus2.write_port(0, 0x00)
                #~ bus2.write_port(1, 0x00)
                return False

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    
    #~ bus1.write_port(0, 0x00)
    #~ bus1.write_port(1, 0x00)
    #~ bus2.write_port(0, 0x00)
    #~ bus2.write_port(1, 0x00)


if __name__ == "__main__":
    main()

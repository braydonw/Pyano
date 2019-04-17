import logging
from PyQt4 import QtCore
from pynput import keyboard
from pyano.IOPi import IOPi
from pynput import keyboard
from pynput.keyboard import Key, Controller


#---WORKER THREAD: MIDI HERO--------------------------------------------

class HeroThread(QtCore.QThread):

    def __init__(self, parent = None):
        super(HeroThread, self).__init__(parent)
        self.hero_username = ""
        self.hero_song = ""
        self.hero_score = 0
        
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
        
        #~ print(self.hero_username)
        #~ print(self.hero_song)
        
        
        
        
        
        # WHEN DONE WITH EVERYTHING ELSE
        # add username and score to leaderboard.csv file
        # fix hardcoded path
        with open('/home/pi/pyano-git/pyano/leaderboard.csv', 'a') as csv_file:
            line = str(self.hero_score) + ',' + self.hero_username + ',' + self.hero_song + '\n'
            csv_file.write(line)
        
        
        
        
    def clear_outputs(self):
        logging.info('CLEARING OUTPUTS')
        self.bus1.write_port(0, 0x00)
        self.bus1.write_port(1, 0x00)
        self.bus2.write_port(0, 0x00)
        self.bus2.write_port(1, 0x00)

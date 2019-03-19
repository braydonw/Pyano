import os
import sys
import glob
import time
import string
import logging
from PyQt4 import QtGui, QtCore, uic
from mido import MidiFile, MidiTrack, Message, MetaMessage, second2tick, bpm2tempo # MetaMessage?
from pynput import keyboard
from pynput.keyboard import Key, Controller

def main():
    
    # setup simultaneous logging to log file and terminal window
    # this for loop  is required because PyQt4 uses DEBUG logging level for uic
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # add error check for pyano-git vs pyano vs else/finally if directory name is completely wrong
    fileFormatter = logging.Formatter('%(levelname)s | %(asctime)s | T:%(thread)d | %(message)s')
    consoleFormatter = logging.Formatter('%(levelname)s | %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler('/home/pi/pyano-git/logs.log')
    fileHandler.setFormatter(fileFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(consoleFormatter)
    rootLogger.addHandler(consoleHandler)
    
    # SETUP IO PI BUSSES HERE ??
    
    # setup and launch GUI
    logging.info('launching GUI')
    app = QtGui.QApplication(sys.argv)
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec_())
    
    
#---MAIN THREAD: GUI----------------------------------------------------
    
class MainWindow(QtGui.QWidget):
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent) # super returns parent obj (QWidget obj)
        uic.loadUi('pyano/layout.ui', self) # load ui file from Qt Designer
        # add error checking (try/except) for layout and resources
        #~ import resources # pyrcc4 -o resources.py resources.qrc -py3
        from resources import resources
        
        # home page connections
        self.btn_player.clicked.connect(self.on_player_click)
        self.btn_maker.clicked.connect(self.on_maker_click)
        self.btn_live.clicked.connect(self.on_live_click)
        self.btn_guide.clicked.connect(self.on_guide_click)
        self.btn_credits.clicked.connect(self.on_credits_click)
        self.btn_exit.clicked.connect(self.on_exit_click)
        
        # player page connections
        self.btn_player_home.clicked.connect(self.on_home_click)
        self.btn_player_exit.clicked.connect(self.on_exit_click)
        self.btn_player_play.clicked.connect(self.on_player_play_click)
        self.btn_player_pause.clicked.connect(self.on_player_pause_click)
        self.btn_player_stop.clicked.connect(self.on_player_stop_click)
        self.btn_player_restart.clicked.connect(self.on_player_restart_click)
        
        # maker page connections
        self.btn_maker_home.clicked.connect(self.on_home_click)
        self.btn_maker_exit.clicked.connect(self.on_exit_click)
        self.btn_maker_start.clicked.connect(self.on_maker_start_click)
        self.btn_maker_done.clicked.connect(self.on_maker_done_click)
        self.btn_maker_cancel.clicked.connect(self.on_maker_cancel_click)
        
        # live page connections
        self.btn_live_home.clicked.connect(self.on_home_click)
        self.btn_live_exit.clicked.connect(self.on_exit_click)
        
        # guide page connections
        self.btn_guide_home.clicked.connect(self.on_home_click)
        #~ self.btn_guide_exit.clicked.connect(self.on_exit_click)
        
        # credits page connections
        self.btn_credits_home.clicked.connect(self.on_home_click)
        #~ self.btn_credits_exit.clicked.connect(self.on_exit_click)
        
        # always last things in __init__
        self.stackedWidget.setCurrentIndex(0)
        self.showFullScreen()
        
        
#---SHARED PAGE ELEMENTS------------------------------------------------

    def on_home_click(self):
        logging.info('home btn pressed')
        
        self.stackedWidget.setCurrentIndex(0)
        self.label_title.setText('P Y A N O')
        
    def on_exit_click(self):
        logging.info('exit btn pressed')
        
        choice = QtGui.QMessageBox.question(self, 'Exit',
                                            "Are you sure you want to exit?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            logging.info("EXIT PRESSED: CLEANUP IO HERE")
            logging.info('\n\n\n')
            sys.exit()
        logging.info('user selected not to exit')
        
    def closeEvent(self, event):
        logging.info('exiting from menu bar close btn')
        
        # this enables the exit button on the window bar to work as well
        # don't really need this when running fullscreen but it's handy anyway
        event.ignore()
        self.on_exit_click()
        
        
#---HOME PAGE ELEMENTS--------------------------------------------------

    def on_player_click(self):
        logging.info('player btn clicked')
        
        # setup page elements
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_player.setCurrentIndex(0)
        self.label_title.setText('P L A Y E R')
        self.btn_player_pause.setVisible(False)
        self.btn_player_stop.setVisible(False)
        self.btn_player_restart.setVisible(False)        
        
        # fill in file list with all .mid files in directory
        #~ self.midi_file_list = []
        self.comboBox_player_file.clear()
        try:
            os.chdir("/home/pi/pyano-git/midi-files")
        except FileNotFoundError:
            os.chdir("/home/pi/pyano/midi-files")
                        
        for midi_file in sorted(glob.glob("*.mid")): # alphabetical sort since glob uses random order
            #~ self.midi_file_list.append(midi_file)
            self.comboBox_player_file.addItem(midi_file)

    def on_maker_click(self):
        logging.info('maker btn clicked')
        
        # setup page elements
        self.stackedWidget.setCurrentIndex(2)
        self.label_title.setText('M A K E R')
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.label_maker_recording_indicator.hide()
        self.label_maker.setText("Press start to begin")
        self.textEdit_maker.clear()
        
        # fill in lineEdit_maker_name with first available file name
        try:
            os.chdir("/home/pi/pyano-git/midi-files")
        except FileNotFoundError:
            os.chdir("/home/pi/pyano/midi-files")
        i = 1
        while os.path.exists("custom_song_%s.mid" % i):
            i += 1
        self.lineEdit_maker_name.setText("custom_song_%s.mid" % i)
        logging.info('setting default song name to: custom_song_{}.mid'.format(i))
        
        # setup maker thread (doesn't start until btn_maker_start is pressed
        self.makerThread = MakerThread(None)
        
        # connect function calls in this thread to emits from makerThread
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerText(QString)"), self.update_maker_text)
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerGUI(QString)"), self.update_maker_gui)
        
    def on_live_click(self):
        logging.info('live btn clicked')
        
        self.stackedWidget.setCurrentIndex(3)
        self.label_title.setText('L I V E')
        
    def on_guide_click(self):
        logging.info('guide btn clicked')
        
        self.stackedWidget.setCurrentIndex(4)
        self.label_title.setText('G U I D E')
        
    def on_credits_click(self):
        logging.info('credits btn clicked')
        
        self.stackedWidget.setCurrentIndex(5)
        self.label_title.setText('C R E D I T S')
        

#---PLAYER PAGE ELEMENTS------------------------------------------------

    def on_player_play_click(self):
        logging.info('player-play btn clicked')
        self.stackedWidget_player.setCurrentIndex(1)
        self.btn_player_play.setVisible(False)
        self.btn_player_pause.setVisible(True)
        self.btn_player_stop.setVisible(True)
        self.btn_player_restart.setVisible(True)
        self.btn_player_home.setEnabled(False)
        self.btn_player_exit.setEnabled(False)
        self.btn_player_usb.setVisible(False)
        self.btn_player_eject.setVisible(False)
        
    def on_player_pause_click(self):
        logging.info('player-pause btn clicked')
        pass
        
    def on_player_stop_click(self):
        logging.info('player-stop btn clicked')
        self.stackedWidget_player.setCurrentIndex(0)
        self.btn_player_play.setVisible(True)
        self.btn_player_pause.setVisible(False)
        self.btn_player_stop.setVisible(False)
        self.btn_player_restart.setVisible(False)
        self.btn_player_home.setEnabled(True)
        self.btn_player_exit.setEnabled(True)
        self.btn_player_usb.setVisible(True)
        self.btn_player_eject.setVisible(True)
        
    def on_player_restart_click(self):
        logging.info('player-restart btn clicked')
        pass


#---MAKER PAGE ELEMENTS-------------------------------------------------
        
    def on_maker_start_click(self):
        logging.info('maker-start btn clicked')
        
        # check to see if self.makerThread.maker_song_name is valid (5 checks)
        # pull name from gui
        self.makerThread.maker_song_name = self.lineEdit_maker_name.text()
        # 1.  make sure name doesn't contain any invalid characters
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        invalid_chars = ""
        for c in self.makerThread.maker_song_name:
            if c not in valid_chars:
                invalid_chars += c
        if invalid_chars:
            QtGui.QMessageBox.warning(self, 'Error', "Invalid characters in name:\n %s" % invalid_chars, QtGui.QMessageBox.Close)
            return
        # 2.  make sure name end with .mid
        file_extension = self.makerThread.maker_song_name[-4:]
        if file_extension != ".mid":
            #~ print("Filename extension error!")
            QtGui.QMessageBox.warning(self, 'Error', "Must be .mid file", QtGui.QMessageBox.Close)
            return
        # 3.  make sure name is available in directory (current os path is to pi/pyano-git/midi-files)
        if os.path.exists(self.makerThread.maker_song_name):
            QtGui.QMessageBox.warning(self, 'Error', "Filename already exist", QtGui.QMessageBox.Close)
            return
        # 4.  make sure name is not too long 
        if len(self.makerThread.maker_song_name) > 30:
            QtGui.QMessageBox.warning(self, 'Error', "Filename too long", QtGui.QMessageBox.Close)
            return
        # 5.  make sure name is not empty
        if len(self.makerThread.maker_song_name) <= 4:
            QtGui.QMessageBox.warning(self, 'Error', "Filename empty", QtGui.QMessageBox.Close)
            return
        
        # if the name is valid change gui to recording view
        self.btn_maker_start.setVisible(False)
        self.btn_maker_done.setVisible(True)
        self.btn_maker_cancel.setVisible(True)
        self.btn_maker_home.setEnabled(False)
        self.btn_maker_exit.setEnabled(False)
        self.comboBox_maker_BPM.setEnabled(False)
        self.lineEdit_maker_name.setEnabled(False)
        self.label_maker_recording_indicator.show()
        self.textEdit_maker.clear()
        self.label_maker.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_maker.setText("  Input        Note           Timing")
        
        # update bpm variable from gui combobox for midi file creation
        self.makerThread.maker_song_BPM = str(self.comboBox_maker_BPM.currentText())
        
        logging.info('song name: {}'.format(self.makerThread.maker_song_name))
        logging.info('bpm: {}'.format(self.makerThread.maker_song_BPM))
        
        # start maker thread by calling its run() method
        self.makerThread.start()
 
    def on_maker_done_click(self):        
        # simulate keypress to stop keywatcher code in maker thread (save file)
        # simulating keypress calls update_maker_gui
        # THIS IS STILL CALLING 2x (ON PRESS AND RELEASE)
        kb = Controller()
        kb.press(Key.enter)
        kb.release(Key.enter)
        
        # change song name on gui to next available filename
        # current os path is to pi/pyano-git/midi-files
        i = 1
        while os.path.exists("custom_song_%s.mid" % i):
            i += 1
        self.lineEdit_maker_name.setText("custom_song_%s.mid" % i)
        logging.info('setting default song name to: custom_song_{}.mid'.format(i))
        
    def on_maker_cancel_click(self):        
        # simulate keypress to stop keywatcher code in maker thread (discard file)
        # simulating keypress calls update_maker_gui
        # THIS IS STILL CALLING 2x (ON PRESS AND RELEASE)
        kb = Controller()
        kb.press(Key.backspace)
        kb.release(Key.backspace)

    def update_maker_gui(self, text):
        # change gui back from recording view
        self.btn_maker_start.setVisible(True)
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.btn_maker_home.setEnabled(True)
        self.btn_maker_exit.setEnabled(True)
        self.comboBox_maker_BPM.setEnabled(True)
        self.lineEdit_maker_name.setEnabled(True)
        self.label_maker_recording_indicator.hide()
        self.label_maker.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.label_maker.setText(text)
        
    def update_maker_text(self, text):
        self.textEdit_maker.append(text)
        sb = self.textEdit_maker.verticalScrollBar()
        sb.setValue(sb.maximum()) # auto scrolling text


#---WORKER THREAD: MIDI MAKER-------------------------------------------

class MakerThread(QtCore.QThread):
    
    def __init__(self, parent = None):
        super(MakerThread, self).__init__(parent)
        self.maker_song_name = ""
        self.maker_song_BPM = ""
    
    def run(self):       
        #~ print(self.maker_song_name) # to show that it is updating from gui thread
        
        self.key2midi = {'z': '60', 's': '61', 'x': '62', 'd': '63', 'c': '64', 'v': '65',
                        'g': '66', 'b': '67', 'h': '68', 'n': '69', 'j': '70', 'm': '71',
                        'q': '72', '2': '73', 'w': '74', '3': '75', 'e': '76', 'r': '77',
                        '5': '78', 't': '79', '6': '80', 'y': '81', '7': '82', 'u': '83'}
    
        self.key2note = {'z': 'C4 ', 's': 'C#4', 'x': 'D4 ', 'd': 'D#4', 'c': 'E4 ', 'v': 'F4 ',
                        'g': 'F#4', 'b': 'G4 ', 'h': 'G#4', 'n': 'A4 ', 'j': 'A#4', 'm': 'B4 ',
                        'q': 'C5 ', '2': 'C#5', 'w': 'D5 ', '3': 'D#5', 'e': 'E5 ', 'r': 'F5 ',
                        '5': 'F#5', 't': 'G5 ', '6': 'G#5', 'y': 'A5 ', '7': 'A#5', 'u': 'B5 '}
         
        # create a new MIDI file with an empty track (no self i guess??)
        mid = MidiFile()
        track = MidiTrack()        
        mid.tracks.append(track)

        # see what these & tempo do using midi player
        #~ track.append(Message('program_change', program=1)) # piano 1
        # add time signature?
        #~ track.append(MetaMessage('key_signature', key='C', mode='major'))
        # add tempo?

        # tempo & beat resolution; 120 BPM = 500,000 tempo (micro-seconds per beat)
        self.ticks_per_beat = 240 # pulses per quarter note (240 is good default)
        self.tempo = bpm2tempo(int(self.maker_song_BPM))
        
        ##### WIP #####
        # ADD SOMETHING THAT BUILDS THE SONGS META DATA PART OF THE MIDI FILE? AND INSERTS THE NAME?
        # OR DOES MIDO ALREADY DO THIS? TRY TO GET ONLINE PLAYBACK TO DEFAULT TO 120 BPM
        # SEE WHAT MAKER SONGS LOOK LIKE IN PLAYER
        ###############
        
        # timing setup for recording the time between keypresses
        start_time = time.time()
        self.prev_time = 0 # this is where the use of self confuses me
        
        # method call built into key listener
        def on_press(key):
            # get the time that has passed since this thread started
            self.time_since_start = time.time() - start_time
            
            # check for cancel/done keypress (backspace/enter)
            # remember gui btns simulate key presses
            if key == keyboard.Key.backspace:
                # discard file
                self.emit(QtCore.SIGNAL("updateMakerGUI(QString)"), "Canceled... Discarding song...")
                logging.info('maker-cancel btn clicked')
                return False # returning False stops the key listener
                
            elif key == keyboard.Key.enter:
                # save file
                mid.save(self.maker_song_name)
                self.emit(QtCore.SIGNAL("updateMakerGUI(QString)"), "File saved successfully")
                logging.info('maker-done btn clicked')
                return False
                
            try:
                # see if the key pressed is in dictionary of valid keys
                self.midi_note = self.key2midi[key.char]
                self.kb_note = self.key2note[key.char]
                
                # if the key is valid find the time since last keypress
                self.adj_time = self.time_since_start - self.prev_time
                
                # convert time since last keypress to ticks
                self.ticks = second2tick(self.adj_time, self.ticks_per_beat, self.tempo)
                
                # add the note on/off data to the midi file
                track.append(Message('note_on', note=int(self.midi_note), time=int(self.ticks)))                
                track.append(Message('note_off', note=int(self.midi_note), time=0)) # try time=1 if 0 doesnt work on physical piano
                
                # build and emit gui text output
                gui_output = (" " + key.char.upper() + "    " + self.kb_note + "   " + str((round(self.adj_time, 3))))
                self.emit(QtCore.SIGNAL("updateMakerText(QString)"), gui_output)
                logging.info(gui_output)
                
                # for testing
                #~ print(round(self.adj_time, 3))
                #~ print(int(self.ticks))
                
                # didn't throw exception so key is valid; set for next btn press
                # this allows adj_time to ignore the time of any invalid keys
                self.prev_time = self.time_since_start
                
            except (KeyError, AttributeError) as e:
                logging.debug('invalid key {}'.format(e))
                
                
        # starts a key listener; use return False to stop
        # this is actually starting a 3rd thread
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

        logging.info('Exiting makerThread')


if __name__ == '__main__':
    main()
    

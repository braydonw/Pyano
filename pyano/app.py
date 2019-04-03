import os
import sys
import glob
import time
import shutil
import string
import logging
import random
from PyQt4 import QtGui, QtCore, uic
from mido import MidiFile, MidiTrack, Message, second2tick, bpm2tempo
from pynput import keyboard
from pynput.keyboard import Key, Controller
from pyano.player import PlayerThread
from pyano.maker import MakerThread
#~ from pyano.live import LiveThread

def main():
    # setup simultaneous logging to log file and terminal window
    # this for loop  is required because PyQt4 uses DEBUG logging level for uic
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # format output to log file and console window
    fileFormatter = logging.Formatter('%(levelname)s | %(asctime)s | T:%(thread)d | %(message)s')
    consoleFormatter = logging.Formatter('%(levelname)s | %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO) # change to DEBUG for more UI info
    fileHandler = logging.FileHandler(os.getcwd() + '/logs.log')
    fileHandler.setFormatter(fileFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(consoleFormatter)
    rootLogger.addHandler(consoleHandler)
    
    # ADD IOPI & GPIO SETUP HERE
    
    # setup and launch GUI
    logging.info('launching GUI')
    app = QtGui.QApplication(sys.argv)
    #~ app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    GUI = MainWindow() # calls MainWindow's __init__ method
    GUI.show()
    sys.exit(app.exec_())
    
    
#---MAIN THREAD: GUI----------------------------------------------------
    
class MainWindow(QtGui.QWidget):
    
    # put proj_path here and remove self?
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent) # super returns parent obj (QWidget obj)
        uic.loadUi('pyano/layout.ui', self) # load ui file from Qt Designer
        from resources import resources # pyrcc4 -o resources.py resources.qrc -py3
        
        # get path to project folder
        self.proj_path = os.getcwd() # /home/pi/pyano-git
        logging.info('PATH: {}'.format(self.proj_path))
        
        # home page setup (connect GUI btn presses to function calls)
        self.btn_player.clicked.connect(self.on_player_click)
        self.btn_maker.clicked.connect(self.on_maker_click)
        self.btn_live.clicked.connect(self.on_live_click)
        self.btn_guide.clicked.connect(self.on_guide_click)
        self.btn_credits.clicked.connect(self.on_credits_click)
        self.btn_exit.clicked.connect(self.on_exit_click)
        
        # player page setup
        self.btn_player_home.clicked.connect(self.on_home_click)
        self.btn_player_play.clicked.connect(self.on_player_play_click)
        self.btn_player_pause.clicked.connect(self.on_player_pause_click)
        self.btn_player_back.clicked.connect(self.on_player_back_click)
        self.btn_player_next.clicked.connect(self.on_player_next_click)
        self.btn_player_stop.clicked.connect(self.on_player_stop_click)
        self.btn_player_shuffle.clicked.connect(self.on_player_shuffle_click)
        self.btn_player_alpha.clicked.connect(self.on_player_alpha_click)
        self.btn_player_add_files.clicked.connect(self.on_player_add_files_click)
        # icons not working with Qt Designer Resources. solution is setting them like this:
        self.btn_player_back.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-back.png'))
        self.btn_player_play.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-play.png'))
        self.btn_player_pause.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-pause.png'))
        self.btn_player_next.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-next.png'))
        self.btn_player_stop.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-stop.png'))
        self.btn_player_shuffle.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-shuffle.png'))
        self.btn_player_alpha.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-alpha.png'))
        self.btn_player_add_files.setIcon(QtGui.QIcon(self.proj_path + '/resources/player-add.png'))
        self.btn_player_home.setIcon(QtGui.QIcon(self.proj_path + '/resources/home.png'))
        
        # maker page setup
        self.btn_maker_home.clicked.connect(self.on_home_click)
        self.btn_maker_start.clicked.connect(self.on_maker_start_click)
        self.btn_maker_done.clicked.connect(self.on_maker_done_click)
        self.btn_maker_cancel.clicked.connect(self.on_maker_cancel_click)
        self.btn_maker_home.setIcon(QtGui.QIcon(self.proj_path + '/resources/home.png'))
        
        # live page setup
        self.btn_live_home.clicked.connect(self.on_home_click)
        self.btn_live_home.setIcon(QtGui.QIcon(self.proj_path + '/resources/home.png'))
        
        # guide page setup
        self.btn_guide_home.clicked.connect(self.on_home_click)
        self.btn_guide_home.setIcon(QtGui.QIcon(self.proj_path + '/resources/home.png'))
        
        # credits page setup
        self.btn_credits_home.clicked.connect(self.on_home_click)
        self.btn_credits_home.setIcon(QtGui.QIcon(self.proj_path + '/resources/home.png'))
        
        # always last things in __init__
        # stackedWidget 0-5 are the various GUI pages (home, p, m, l, guide, credits)
        self.stackedWidget.setCurrentIndex(0) 
        self.showFullScreen()
        
        
#---SHARED PAGE ELEMENTS------------------------------------------------

    def on_home_click(self):
        logging.info('H O M E  btn pressed')
        self.stackedWidget.setCurrentIndex(0)
        self.label_title.setText('P Y A N O')
        
        
#---HOME PAGE ELEMENTS--------------------------------------------------

    def on_player_click(self):
        logging.info('P L A Y E R  btn clicked')
        
        # setup page elements
        self.label_title.setText('P L A Y E R')
        self.listWidget_player_files.setFocus()
        self.btn_player_play.setVisible(True)
        self.btn_player_pause.setVisible(False)
        self.btn_player_shuffle.setVisible(True)    
        self.btn_player_alpha.setVisible(False) 
        self.btn_player_stop.setEnabled(False) 
        self.progressBar_player.setValue(0)
        self.textEdit_player.clear()
        self.label_player.setText("Press play to begin")
        self.stackedWidget.setCurrentIndex(1) # last thing in setup so you cant see changes
        
        # setup player thread (doesn't start until btn_player_start is pressed)
        self.playerThread = PlayerThread(None)
        
        # connect function calls in this thread to emits from playerThread
        self.connect(self.playerThread, QtCore.SIGNAL("updatePlayerText(QString)"), self.update_player_text)
        self.connect(self.playerThread, QtCore.SIGNAL("playerNextFile()"), self.player_next_file)
        self.connect(self.playerThread, QtCore.SIGNAL("updatePlayerProgress(int)"), self.update_player_progress)
        self.connect(self.playerThread, QtCore.SIGNAL("playerSkipEnabled(bool)"), self.player_skip_enabled)
        #~ self.connect(self.playerThread, QtCore.SIGNAL("playerEnableSkip()"), self.enable_player_skip)
        
        
        
        # fill in a file listWidget with all .mid files in directory
        self.listWidget_player_files.clear()
        os.chdir(self.proj_path + '/midi-files') 
        for midi_file in sorted(glob.glob("*.mid")): # alphabetical sort since glob uses random order
            self.playerThread.midi_file_list.append(midi_file) # build midi_file_list for playerThread
            self.listWidget_player_files.addItem(midi_file)
        
        # highlight/select first file in list
        self.listWidget_player_files.setCurrentRow(0) 
        logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')        

    def on_maker_click(self):
        logging.info('M A K E R  btn clicked')
        
        # setup page elements
        self.label_title.setText('M A K E R')
        self.kb_piano_img.setFocus() # removes focus from lineEdit_maker_name
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.label_maker_recording_indicator.hide()
        self.label_maker.setText("Press start to begin")
        self.textEdit_maker.clear()
        self.stackedWidget.setCurrentIndex(2) # last thing in setup so you cant see changes
        
        # fill in lineEdit_maker_name with first available file name
        self.update_maker_filename()
        
        # setup maker thread (doesn't start until btn_maker_start is pressed
        self.makerThread = MakerThread(None)
        os.chdir(self.proj_path + '/midi-files') # where to play files from
        
        # connect function calls in this thread to emits from makerThread
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerText(QString)"), self.update_maker_text)
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerGUI(QString)"), self.update_maker_gui)
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerName()"), self.update_maker_filename)
        
    def on_live_click(self):
        logging.info('L I V E  btn clicked')
        
        # setup page elements
        self.label_title.setText('L I V E')
        self.stackedWidget.setCurrentIndex(3) # last thing in setup so you cant see changes
        
    def on_guide_click(self):
        logging.info('G U I D E  btn clicked')
        
        self.stackedWidget.setCurrentIndex(4)
        self.label_title.setText('G U I D E')
        
    def on_credits_click(self):
        logging.info('C R E D I T S  btn clicked')
        
        self.stackedWidget.setCurrentIndex(5)
        self.label_title.setText('C R E D I T S')
    
    def on_exit_click(self):
        logging.info('E X I T  btn pressed')
        
        # pop-up message box to confirm exit
        choice = QtGui.QMessageBox.question(self, 'Exit',
                                            "Are you sure you want to exit?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            logging.info("EXIT PRESSED: CLEANUP IO HERE \n\n\n")
            sys.exit()
        logging.info('user selected not to exit')

#---PLAYER PAGE ELEMENTS------------------------------------------------

    def on_player_play_click(self):
        logging.info('player-play btn clicked')
        
        # update GUI
        # not enabled = grayed out; not visible = hidden
        self.btn_player_play.setVisible(False)
        self.btn_player_pause.setVisible(True)
        self.btn_player_home.setEnabled(False)
        self.btn_player_add_files.setEnabled(False)
        self.btn_player_shuffle.setEnabled(False)
        self.btn_player_alpha.setEnabled(False)
        self.listWidget_player_files.setEnabled(False) # THIS SHOULD WORK BUT HIGHLIGHT DOESNT ITERATE WHEN PLAYERTHREAD MOVES TO NEXT SONG YET
        
        # if no file is highlighted then highlight the first one
        if self.listWidget_player_files.currentItem() is None:
            self.listWidget_player_files.setCurrentRow(0)

        # set the current song so playerThread can find its index in midi_file_list & knows where to start playing
        self.playerThread.current_song = self.listWidget_player_files.currentRow()
        
        # display which file is highlighted/playing
        self.label_player.setText("Playing: {}".format(self.listWidget_player_files.currentItem().text()))
        
        # play button has 2 uses: start playing when no song is playing & resume when a song is paused
        if self.btn_player_stop.isEnabled():
            logging.info("*Resume Playing*")
            self.playerThread.pause_check = False # un-pause song in playerThread
        else:
            logging.info("*Start Playing*")
            self.btn_player_stop.setEnabled(True) 
            self.textEdit_player.clear() # move this to on_player_stop_click?
            self.playerThread.stop_check = False
            self.playerThread.pause_check = False
            self.playerThread.next_check = False
            self.playerThread.back_check = False
            self.playerThread.start() # calls the run() method in playerThread
            self.progressBar_player.setValue(0)

    def on_player_pause_click(self):
        logging.info('player-pause btn clicked')
        self.btn_player_play.setVisible(True)
        self.btn_player_pause.setVisible(False)
        self.label_player.setText("Paused: {}".format(self.listWidget_player_files.currentItem().text()))
        self.playerThread.pause_check = True # pause song in playerThread
        
    def on_player_back_click(self):
        logging.info('player-back btn clicked')
        
        self.playerThread.back_check = True
        
        # when no file is highlighted, pressing back highlights the last file
        if self.listWidget_player_files.currentRow() == -1:
            self.listWidget_player_files.setCurrentRow(len(self.playerThread.midi_file_list)-1)
            logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')
        
        # update highlighted list item (don't let the user go back to before the first file)
        elif self.listWidget_player_files.currentRow() != 0:
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()-1)
            logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')
        
        #~ logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')
        
        # update Now Playing text (only if song is playing, not when stopped)
        if not self.btn_player_home.isEnabled(): # home btn not enabled = song is playing or paused
            self.label_player.setText("Playing: {}".format(self.listWidget_player_files.currentItem().text()))
            if self.btn_player_play.isVisible():
                self.label_player.setText("Paused: {}".format(self.listWidget_player_files.currentItem().text()))
        
    def on_player_next_click(self):
        logging.info('player-next btn clicked')
        
        # when a song is paused clicking next automatically starts playing next file
        
        # update GUI (only if song is already playing/paused)
        if not self.btn_player_home.isEnabled():
            print("!")
            self.btn_player_play.setVisible(False)
            self.btn_player_pause.setVisible(True)
        
        self.playerThread.next_check = True
        self.player_next_file()
        
    def player_next_file(self):
        # linked to playerThread function call
        # updates GUI elements when player automatically finishes a file and moves to the next one
        
        # update highlighted list item (don't let the user skip past the last file)
        if self.listWidget_player_files.currentRow() != len(self.playerThread.midi_file_list)-1:
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()+1)
            logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')
            #~ print("!")
        else:
            # clear highlighted file since going past index size
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()+1)
            # stop playback when last file ends or user skips past last file
            self.on_player_stop_click()
        
        # update Now Playing text (only if song is playing, not when stopped)
        if not self.btn_player_home.isEnabled(): # home btn not enabled = song is playing or paused
                self.label_player.setText("Playing: {}".format(self.listWidget_player_files.currentItem().text()))
                self.progressBar_player.setValue(0)
        
    def on_player_stop_click(self):
        logging.info('player-stop btn clicked')
        
        # stop playback in the playerThread
        self.playerThread.stop_check = True
        
        # update gui elements
        self.listWidget_player_files.setEnabled(True)
        self.btn_player_home.setEnabled(True)
        self.btn_player_add_files.setEnabled(True)
        self.btn_player_shuffle.setEnabled(True)
        self.btn_player_alpha.setEnabled(True)
        self.btn_player_stop.setEnabled(False)
        self.btn_player_play.setVisible(True)
        self.btn_player_pause.setVisible(False)
        self.label_player.setText("Press play to begin")
        self.listWidget_player_files.setFocus()
        self.progressBar_player.setValue(0)
        
        
    def on_player_shuffle_click(self):
        logging.info('player-shuffle btn clicked')
        self.btn_player_alpha.setVisible(True)
        self.btn_player_shuffle.setVisible(False)
        
        # shuffle midi_file_list
        random.shuffle(self.playerThread.midi_file_list)
        
        # update GUI with newly sorted list
        self.listWidget_player_files.clear()
        for midi_file in self.playerThread.midi_file_list:
            self.listWidget_player_files.addItem(midi_file)
        self.listWidget_player_files.setCurrentRow(0)
        
    def on_player_alpha_click(self):
        logging.info('player-alpha btn clicked')
        self.btn_player_shuffle.setVisible(True)
        self.btn_player_alpha.setVisible(False)
        
        # alphabetize midi_file_list
        self.listWidget_player_files.clear()
        
        # update GUI with newly sorted list
        for midi_file in sorted(self.playerThread.midi_file_list):
            self.listWidget_player_files.addItem(midi_file)
        self.listWidget_player_files.setCurrentRow(0)
     
    def on_player_add_files_click(self):
        logging.info('player-add-files btn clicked')
        
        new_files = []
        dest_dir = self.proj_path + '/midi-files'
        usb_list = os.listdir('/media/pi')
        usb_list.remove('SETTINGS')
        if not usb_list:
            logging.info('There are no USB drives inserted.')
            QtGui.QMessageBox.warning(self, 'Error', 'No USB Drives Inserted', QtGui.QMessageBox.Close)
        else:
            for drive in usb_list:
                source_dir = ('/media/pi/{}'.format(drive))
                for root, dirs, files in os.walk(source_dir):
                    for f in files: # f would be something like "twinkle_twinkle.mid"
                        if f not in self.playerThread.midi_file_list and f.endswith('.mid'):
                            path2file = os.path.join(root, f)
                            shutil.copy2(path2file, dest_dir) # copy2 saves metadata
                            logging.info('Added {}'.format(f))
                            self.playerThread.midi_file_list.append(f)
                            new_files.append(f)
                        
            # update list to add new files (depends on list's current sort mode)
            if self.btn_player_shuffle.isVisible(): # list is in alpha order
                self.on_player_alpha_click()
            elif self.btn_player_alpha.isVisible(): # list is shuffled
                self.on_player_shuffle_click()
            
            if new_files: # if the new file list is not empty execute this
                if len(new_files) < 10: # maximum number of new file names to show before just showing a number instead
                    QtGui.QMessageBox.warning(self, 'Success', 
                    'Files imported successfully: \n{}'.format('\n'.join(new_files)), 
                    QtGui.QMessageBox.Close)
                else: 
                    QtGui.QMessageBox.warning(self, 'Success', 
                    'Files imported successfully ({})'.format(len(new_files)), 
                    QtGui.QMessageBox.Close)
            else:
                QtGui.QMessageBox.warning(self, 'Error', 
                'All .mid files have already been imported', 
                QtGui.QMessageBox.Close)

    def update_player_text(self, text):
        self.textEdit_player.append(text)
        sb = self.textEdit_player.verticalScrollBar()
        sb.setValue(sb.maximum()) # auto scrolling text

    def update_player_progress(self, percentage):
        self.progressBar_player.setValue(percentage)
    
    def player_skip_enabled(self, b):
        if b:
            self.btn_player_next.setEnabled(True)
        else:
            self.btn_player_next.setEnabled(False)
    
#---MAKER PAGE ELEMENTS-------------------------------------------------
        
    def on_maker_start_click(self):
        logging.info('maker-start btn clicked')
        
        # check to see if maker_song_name is valid (6 checks)
        # first pull song name from gui
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
            
        # 6.  limit the amount of custom songs with this naming format to 99
        if self.makerThread.maker_song_name == 'custom_song_100.mid':
            QtGui.QMessageBox.warning(self, 'Error', "Limit of 99 custom files with this naming convention", QtGui.QMessageBox.Close)
            return
        
        # if the name is valid change gui to recording view
        self.btn_maker_start.setVisible(False)
        self.btn_maker_done.setVisible(True)
        self.btn_maker_cancel.setVisible(True)
        self.btn_maker_home.setEnabled(False)
        self.comboBox_maker_BPM.setEnabled(False)
        self.lineEdit_maker_name.setEnabled(False)
        self.label_maker_recording_indicator.show()
        self.textEdit_maker.clear()
        self.label_maker.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_maker.setText("  Input        Note           Timing")
        
        # pull bpm variable from gui combobox for midi file creation
        self.makerThread.maker_song_BPM = str(self.comboBox_maker_BPM.currentText())
        
        # log song name and bpm
        logging.info('song name: {}'.format(self.makerThread.maker_song_name))
        logging.info('bpm: {}'.format(self.makerThread.maker_song_BPM))
        
        # start maker thread by calling its run() method
        self.makerThread.start()
 
    def on_maker_done_click(self):        
        # simulate keypress to stop keywatcher code in makerThread (save file)
        # simulating keypress calls update_maker_gui & update_maker_filename
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.enter)
        kb.release(Key.enter)
        
    def on_maker_cancel_click(self):        
        # simulate keypress to stop keywatcher code in makerThread (discard file)
        # simulating keypress calls update_maker_gui
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.backspace)
        kb.release(Key.backspace)
        
    def update_maker_filename(self):
        # fill in lineEdit_maker_name with first available file name
        os.chdir(self.proj_path + '/midi-files')
        i = 1
        while os.path.exists("custom_song_0%s.mid" % i):
            i += 1
        if i == 10:
            while os.path.exists("custom_song_%s.mid" % i):
                i += 1
            self.lineEdit_maker_name.setText("custom_song_%s.mid" % i)
            logging.info('setting default song name to: custom_song_{}.mid'.format(i))
        else:
            self.lineEdit_maker_name.setText("custom_song_0%s.mid" % i)
            logging.info('setting default song name to: custom_song_0{}.mid'.format(i))
        
    def update_maker_text(self, text):
        # update and auto-scroll textEdit box
        # text is a string with key, note, and timing info
        self.textEdit_maker.append(text)
        sb = self.textEdit_maker.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    def update_maker_gui(self, text):
        # change gui back from recording view when cancel or done is pressed
        # text is a string that either says "canceled" or "file saved"
        self.btn_maker_start.setVisible(True)
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.btn_maker_home.setEnabled(True)
        self.comboBox_maker_BPM.setEnabled(True)
        self.lineEdit_maker_name.setEnabled(True)
        self.label_maker_recording_indicator.hide()
        self.label_maker.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.label_maker.setText(text)


if __name__ == '__main__':
    main()
    

import os, sys, glob, shutil, time, string, random, logging, csv
from PyQt4 import QtGui, QtCore, uic # GUI framework
from pynput import keyboard # used to simulate key-presses
from pynput.keyboard import Key, Controller
from pyano.player import PlayerThread
from pyano.maker import MakerThread
from pyano.live import LiveThread
from pyano.hero import HeroThread


PROJ_PATH = '/home/pi/pyano-git'
#~ PROJ_PATH = os.getcwd()


def main():
    # setup simultaneous logging to log file and terminal window
    # this for loop  is required because PyQt4 uses DEBUG logging level for uic
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # format output to a log file and the console window
    fileFormatter = logging.Formatter('%(levelname)s | %(asctime)s | T:%(thread)d | %(message)s')
    consoleFormatter = logging.Formatter('%(levelname)s | %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO) # change to DEBUG for more UI info
    fileHandler = logging.FileHandler(os.getcwd() + '/pyano/logs.log')
    fileHandler.setFormatter(fileFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(consoleFormatter)
    rootLogger.addHandler(consoleHandler)
    
    # setup and launch GUI
    logging.info('launching GUI')
    app = QtGui.QApplication(sys.argv)
    GUI = MainWindow() # calls MainWindow's __init__ method
    GUI.show()
    sys.exit(app.exec_())
    
    
#---MAIN THREAD: GUI----------------------------------------------------
    
class MainWindow(QtGui.QWidget):
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent) # super returns parent obj (QWidget obj)
        uic.loadUi('pyano/layout.ui', self) # load ui file from Qt Designer
        from resources import resources # pyrcc4 -o resources.py resources.qrc -py3
        
        # get path to project folder
        #~ self.proj_path = os.getcwd() # /home/pi/pyano-git
        logging.info('PATH: {}'.format(PROJ_PATH))
        
        # home page setup (connect GUI btn presses to function calls)
        self.btn_player.clicked.connect(self.on_player_click)
        self.btn_maker.clicked.connect(self.on_maker_click)
        self.btn_live.clicked.connect(self.on_live_click)
        self.btn_hero.clicked.connect(self.on_hero_click)
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
        # icons not working with Qt Designer Resources, solution is setting them like this:
        self.btn_player_back.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-back.png'))
        self.btn_player_play.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-play.png'))
        self.btn_player_pause.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-pause.png'))
        self.btn_player_next.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-next.png'))
        self.btn_player_stop.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-stop.png'))
        self.btn_player_shuffle.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-shuffle.png'))
        self.btn_player_alpha.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-alpha.png'))
        self.btn_player_add_files.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/player-add.png'))
        self.btn_player_home.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/home.png'))
        
        # maker page setup
        self.btn_maker_home.clicked.connect(self.on_home_click)
        self.btn_maker_start.clicked.connect(self.on_maker_start_click)
        self.btn_maker_done.clicked.connect(self.on_maker_done_click)
        self.btn_maker_cancel.clicked.connect(self.on_maker_cancel_click)
        self.btn_maker_home.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/home.png'))
        self.comboBox_maker_BPM.setCurrentIndex(1) # set to 120 BPM
        
        # live page setup
        self.btn_live_home.clicked.connect(self.on_home_click)
        self.btn_live_start.clicked.connect(self.on_live_start_click)
        self.btn_live_done.clicked.connect(self.on_live_done_click)
        self.btn_live_home.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/home.png'))
        
        # guide page setup
        self.btn_guide_home.clicked.connect(self.on_home_click)
        self.btn_guide_home.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/home.png'))
        
        # credits page setup
        self.btn_credits_home.clicked.connect(self.on_home_click)
        self.btn_credits_home.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/home.png'))
        
        # hero page setup
        self.btn_hero_home.clicked.connect(self.on_home_click)
        self.btn_hero_start.clicked.connect(self.on_hero_start_click)
        self.btn_hero_stop.clicked.connect(self.on_hero_stop_click)
        self.btn_hero_home.setIcon(QtGui.QIcon(PROJ_PATH + '/resources/home.png'))
        self.comboBox_hero_difficulty.setCurrentIndex(1) # set to normal mode
        
        # always last things in __init__
        # stackedWidget 0-6 are the various GUI pages (home, p, m, l, guide, credits, hero)
        self.stackedWidget.setCurrentIndex(0) 
        self.showFullScreen()
        
        
#---SHARED PAGE ELEMENTS------------------------------------------------

    def on_home_click(self):
        logging.info('H O M E  btn pressed')
        self.stackedWidget.setCurrentIndex(0)
        self.label_title.setText(' P Y A N O')
    
    def hide_all_indicators(self):
        # hide all indicator labels on all pages
        
        # player page
        self.ind_p1.setVisible(False)
        self.ind_p2.setVisible(False)
        self.ind_p3.setVisible(False)
        self.ind_p4.setVisible(False)
        self.ind_p5.setVisible(False)
        self.ind_p6.setVisible(False)
        self.ind_p7.setVisible(False)
        self.ind_p8.setVisible(False)
        self.ind_p9.setVisible(False)
        self.ind_p10.setVisible(False)
        self.ind_p11.setVisible(False)
        self.ind_p12.setVisible(False)
        self.ind_p13.setVisible(False)
        self.ind_p14.setVisible(False)
        self.ind_p15.setVisible(False)
        self.ind_p16.setVisible(False)
        self.ind_p17.setVisible(False)
        self.ind_p18.setVisible(False)
        self.ind_p19.setVisible(False)
        self.ind_p20.setVisible(False)
        self.ind_p21.setVisible(False)
        self.ind_p22.setVisible(False)
        self.ind_p23.setVisible(False)
        self.ind_p24.setVisible(False)
        
        # maker page
        self.ind_mz.setVisible(False)
        self.ind_mx.setVisible(False)
        self.ind_mc.setVisible(False)
        self.ind_mv.setVisible(False)
        self.ind_mb.setVisible(False)
        self.ind_mn.setVisible(False)
        self.ind_mm.setVisible(False)
        self.ind_ms.setVisible(False)
        self.ind_md.setVisible(False)
        self.ind_mg.setVisible(False)
        self.ind_mh.setVisible(False)
        self.ind_mj.setVisible(False)
        self.ind_mq.setVisible(False)
        self.ind_mw.setVisible(False)
        self.ind_me.setVisible(False)
        self.ind_mr.setVisible(False)
        self.ind_mt.setVisible(False)
        self.ind_my.setVisible(False)
        self.ind_mu.setVisible(False)
        self.ind_m2.setVisible(False)
        self.ind_m3.setVisible(False)
        self.ind_m5.setVisible(False)
        self.ind_m6.setVisible(False)
        self.ind_m7.setVisible(False)
        
        # live page
        self.ind_lz.setVisible(False)
        self.ind_lx.setVisible(False)
        self.ind_lc.setVisible(False)
        self.ind_lv.setVisible(False)
        self.ind_lb.setVisible(False)
        self.ind_ln.setVisible(False)
        self.ind_lm.setVisible(False)
        self.ind_ls.setVisible(False)
        self.ind_ld.setVisible(False)
        self.ind_lg.setVisible(False)
        self.ind_lh.setVisible(False)
        self.ind_lj.setVisible(False)
        self.ind_lq.setVisible(False)
        self.ind_lw.setVisible(False)
        self.ind_le.setVisible(False)
        self.ind_lr.setVisible(False)
        self.ind_lt.setVisible(False)
        self.ind_ly.setVisible(False)
        self.ind_lu.setVisible(False)
        self.ind_l2.setVisible(False)
        self.ind_l3.setVisible(False)
        self.ind_l5.setVisible(False)
        self.ind_l6.setVisible(False)
        self.ind_l7.setVisible(False)
        
        # hero page
        self.ind_hz.setVisible(False)
        self.ind_hx.setVisible(False)
        self.ind_hc.setVisible(False)
        self.ind_hc.setVisible(False)
        self.ind_hv.setVisible(False)
        self.ind_hb.setVisible(False)
        self.ind_hn.setVisible(False)
        self.ind_hm.setVisible(False)
        self.ind_hs.setVisible(False)
        self.ind_hd.setVisible(False)
        self.ind_hg.setVisible(False)
        self.ind_hh.setVisible(False)
        self.ind_hj.setVisible(False)
        
    def show_indicator(self, page, key, state):
        # used for player, maker, and live indicators
        # hero uses an advanced version that includes colors
        
        # convert key string to a pyqt label_key
        
        # player page
        if page == 'player' and key == 'z':
            key = self.ind_p1
        elif page == 'player' and key == 's':
            key = self.ind_p2
        elif page == 'player' and key == 'x':
            key = self.ind_p3
        elif page == 'player' and key == 'd':
            key = self.ind_p4
        elif page == 'player' and key == 'c':
            key = self.ind_p5
        elif page == 'player' and key == 'v':
            key = self.ind_p6
        elif page == 'player' and key == 'g':
            key = self.ind_p7
        elif page == 'player' and key == 'b':
            key = self.ind_p8
        elif page == 'player' and key == 'h':
            key = self.ind_p9
        elif page == 'player' and key == 'n':
            key = self.ind_p10
        elif page == 'player' and key == 'j':
            key = self.ind_p11
        elif page == 'player' and key == 'm':
            key = self.ind_p12
        elif page == 'player' and key == 'q':
            key = self.ind_p13
        elif page == 'player' and key == '2':
            key = self.ind_p14
        elif page == 'player' and key == 'w':
            key = self.ind_p15
        elif page == 'player' and key == '3':
            key = self.ind_p16
        elif page == 'player' and key == 'e':
            key = self.ind_p17
        elif page == 'player' and key == 'r':
            key = self.ind_p18
        elif page == 'player' and key == '5':
            key = self.ind_p19
        elif page == 'player' and key == 't':
            key = self.ind_p21
        elif page == 'player' and key == '6':
            key = self.ind_p21
        elif page == 'player' and key == 'y':
            key = self.ind_p22
        elif page == 'player' and key == '7':
            key = self.ind_p23
        elif page == 'player' and key == 'u':
            key = self.ind_p24
            
        # maker page
        if page == 'maker' and key == 'z':
            key = self.ind_mz
        elif page == 'maker' and key == 's':
            key = self.ind_ms
        elif page == 'maker' and key == 'x':
            key = self.ind_mx
        elif page == 'maker' and key == 'd':
            key = self.ind_md
        elif page == 'maker' and key == 'c':
            key = self.ind_mc
        elif page == 'maker' and key == 'v':
            key = self.ind_mv
        elif page == 'maker' and key == 'g':
            key = self.ind_mg
        elif page == 'maker' and key == 'b':
            key = self.ind_mb
        elif page == 'maker' and key == 'h':
            key = self.ind_mh
        elif page == 'maker' and key == 'n':
            key = self.ind_mn
        elif page == 'maker' and key == 'j':
            key = self.ind_mj
        elif page == 'maker' and key == 'm':
            key = self.ind_mm
        elif page == 'maker' and key == 'q':
            key = self.ind_mq
        elif page == 'maker' and key == '2':
            key = self.ind_m2
        elif page == 'maker' and key == 'w':
            key = self.ind_mw
        elif page == 'maker' and key == '3':
            key = self.ind_m3
        elif page == 'maker' and key == 'e':
            key = self.ind_me
        elif page == 'maker' and key == 'r':
            key = self.ind_mr
        elif page == 'maker' and key == '5':
            key = self.ind_m5
        elif page == 'maker' and key == 't':
            key = self.ind_mt
        elif page == 'maker' and key == '6':
            key = self.ind_m6
        elif page == 'maker' and key == 'y':
            key = self.ind_my
        elif page == 'maker' and key == '7':
            key = self.ind_m7
        elif page == 'maker' and key == 'u':
            key = self.ind_mu
            
        # live page
        if page == 'live' and key == 'z':
            key = self.ind_lz
        elif page == 'live' and key == 's':
            key = self.ind_ls
        elif page == 'live' and key == 'x':
            key = self.ind_lx
        elif page == 'live' and key == 'd':
            key = self.ind_ld
        elif page == 'live' and key == 'c':
            key = self.ind_lc
        elif page == 'live' and key == 'v':
            key = self.ind_lv
        elif page == 'live' and key == 'g':
            key = self.ind_lg
        elif page == 'live' and key == 'b':
            key = self.ind_lb
        elif page == 'live' and key == 'h':
            key = self.ind_lh
        elif page == 'live' and key == 'n':
            key = self.ind_ln
        elif page == 'live' and key == 'j':
            key = self.ind_lj
        elif page == 'live' and key == 'm':
            key = self.ind_lm
        elif page == 'live' and key == 'q':
            key = self.ind_lq
        elif page == 'live' and key == '2':
            key = self.ind_l2
        elif page == 'live' and key == 'w':
            key = self.ind_lw
        elif page == 'live' and key == '3':
            key = self.ind_l3
        elif page == 'live' and key == 'e':
            key = self.ind_le
        elif page == 'live' and key == 'r':
            key = self.ind_lr
        elif page == 'live' and key == '5':
            key = self.ind_l5
        elif page == 'live' and key == 't':
            key = self.ind_lt
        elif page == 'live' and key == '6':
            key = self.ind_l6
        elif page == 'live' and key == 'y':
            key = self.ind_ly
        elif page == 'live' and key == '7':
            key = self.ind_l7
        elif page == 'live' and key == 'u':
            key = self.ind_lu
            
        # turn indicator on based on state parameter
        if state == 'on':
            key.setVisible(True)
        else:
            key.setVisible(False)
        
        pass
        
#---HOME PAGE ELEMENTS--------------------------------------------------

    def on_player_click(self):
        logging.info('P L A Y E R  btn clicked')
        
        # setup player thread (doesn't start until btn_player_start is pressed)
        self.playerThread = PlayerThread(None)
        
        # setup page elements
        self.label_title.setText(' P L A Y E R')
        self.listWidget_player_files.setFocus()
        self.btn_player_play.setVisible(True)
        self.btn_player_pause.setVisible(False)
        self.btn_player_shuffle.setVisible(True)    
        self.btn_player_alpha.setVisible(False) 
        self.btn_player_stop.setEnabled(False) 
        self.progressBar_player.setValue(0)
        self.label_player.setText("Press play to begin")
        self.hide_all_indicators()
        self.stackedWidget.setCurrentIndex(1) # last thing in setup so you cant see changes
        
        # connect function calls in this thread to emits from playerThread
        self.connect(self.playerThread, QtCore.SIGNAL("playerNextFile()"), self.player_next_file)
        self.connect(self.playerThread, QtCore.SIGNAL("playerLastFile()"), self.player_last_file)
        self.connect(self.playerThread, QtCore.SIGNAL("updatePlayerProgress(int)"), self.update_player_progress)
        self.connect(self.playerThread, QtCore.SIGNAL("playerNextEnabled(bool)"), self.player_next_enabled)
        self.connect(self.playerThread, QtCore.SIGNAL("playerBackEnabled(bool)"), self.player_back_enabled)
        self.connect(self.playerThread, QtCore.SIGNAL("showIndicator(QString, QString, QString)"), self.show_indicator)
        self.connect(self.playerThread, QtCore.SIGNAL("hideAllIndicators()"), self.hide_all_indicators)
        
        # fill in a file listWidget with all .mid files in directory
        self.listWidget_player_files.clear()
        os.chdir(PROJ_PATH + '/midi-files') 
        for midi_file in sorted(glob.glob("*.mid")): # alphabetical sort since glob uses random order
            self.playerThread.midi_file_list.append(midi_file) # build midi_file_list for playerThread
            self.listWidget_player_files.addItem(midi_file)
        
        # highlight/select first file in list
        self.listWidget_player_files.setCurrentRow(0) 
        logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')        

    def on_maker_click(self):
        logging.info('M A K E R  btn clicked')
        
        # setup maker thread (doesn't start until btn_maker_start is pressed
        self.makerThread = MakerThread(None)
        os.chdir(PROJ_PATH + '/midi-files') # where to play files from
        
        # setup page elements
        self.label_title.setText(' M A K E R')
        self.kb_piano_img.setFocus() # removes focus from lineEdit_maker_name
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.label_maker_recording_indicator.hide()
        self.label_maker.setText("Press start to begin")
        self.textEdit_maker.clear()
        self.hide_all_indicators()
        self.stackedWidget.setCurrentIndex(2) # last thing in setup so you cant see changes
        
        # fill in lineEdit_maker_name with first available file name
        self.update_maker_filename()
        
        # connect function calls in this thread to emits from makerThread
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerText(QString)"), self.update_maker_text)
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerGUI(QString)"), self.update_maker_gui)
        self.connect(self.makerThread, QtCore.SIGNAL("updateMakerName()"), self.update_maker_filename)
        self.connect(self.makerThread, QtCore.SIGNAL("showIndicator(QString, QString, QString)"), self.show_indicator)
        self.connect(self.makerThread, QtCore.SIGNAL("hideAllIndicators()"), self.hide_all_indicators)
        
    def on_live_click(self):
        logging.info('L I V E  btn clicked')
        
        # setup maker thread (doesn't start until btn_maker_start is pressed
        self.liveThread = LiveThread(None)
        
        # setup page elements
        self.label_title.setText(' L I V E')
        self.btn_live_done.setVisible(False)
        self.label_live.setText("Press start to begin")
        self.textEdit_live.clear()
        self.hide_all_indicators()
        self.stackedWidget.setCurrentIndex(3) # last thing in setup so you cant see changes
        
        # connect function calls in this thread to emits from liveThread
        self.connect(self.liveThread, QtCore.SIGNAL("updateLiveText(QString)"), self.update_live_text)
        self.connect(self.liveThread, QtCore.SIGNAL("resetLiveGUI()"), self.reset_live_gui)
        self.connect(self.liveThread, QtCore.SIGNAL("showIndicator(QString, QString, QString)"), self.show_indicator)
        self.connect(self.liveThread, QtCore.SIGNAL("hideAllIndicators()"), self.hide_all_indicators)

    def on_guide_click(self):
        logging.info('G U I D E  btn clicked')
        
        self.stackedWidget.setCurrentIndex(4)
        self.label_title.setText(' G U I D E')
        
    def on_credits_click(self):
        logging.info('C R E D I T S  btn clicked')
        
        self.stackedWidget.setCurrentIndex(5)
        self.label_title.setText(' C R E D I T S')
    
    def on_hero_click(self):
        logging.info('H E R O  btn clicked')
        
        # setup hero thread (doesn't start until btn_maker_start is pressed
        self.heroThread = HeroThread(None)

        # setup page elements
        self.label_title.setText(' H E R O')
        self.btn_hero_stop.setVisible(False)
        self.textEdit_hero_leader1.clear()
        self.textEdit_hero_leader2.clear()
        self.textEdit_hero_leader1.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit_hero_leader2.setAlignment(QtCore.Qt.AlignCenter)
        #~ self.lineEdit_hero_username.clear()
        self.lineEdit_hero_username.setText("Braydon")
        self.lineEdit_hero_username.setFocus()
        self.hide_all_indicators()
        self.label_hero_health.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.label_hero_score.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.stackedWidget_hero.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(6)
        
        # fill in comboBox with all non-custom midi files + a random option
        self.comboBox_hero_song.clear()
        self.comboBox_hero_song.addItem('Random Song')
        os.chdir(PROJ_PATH + '/midi-files') 
        for midi_file in sorted(glob.glob("*.mid")): # alphabetical sort since glob uses random order
            # ignore custom files (only works if name starts with custom right now)
            if not midi_file.startswith('custom'):
                self.comboBox_hero_song.addItem(midi_file)
        
        # get top 7 highscores from leaderboard.csv file (& set lowest and highest highscores in hero thread)
        highscores = self.get_hero_highscores()
            
        # display highscores in 2 panels: usernames & scores
        for row in highscores:
            self.textEdit_hero_leader1.append(row[1])
            self.textEdit_hero_leader2.append(row[0])
            
        # connect function calls in this thread to emits from heroThread
        self.connect(self.heroThread, QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), self.update_hero_indicator)
        self.connect(self.heroThread, QtCore.SIGNAL("updateHeroScore(QString)"), self.update_hero_score)
        self.connect(self.heroThread, QtCore.SIGNAL("updateHeroHealth(QString)"), self.update_hero_health)
        self.connect(self.heroThread, QtCore.SIGNAL("resetHeroGUI()"), self.reset_hero_gui)
        #~ self.connect(self.heroThread, QtCore.SIGNAL("heroNewHighscore(QString)"), self.hero_new_highscore)
        
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
        
        # update GUI (only if song is already playing/paused)
        if not self.btn_player_home.isEnabled():
            self.btn_player_play.setVisible(False)
            self.btn_player_pause.setVisible(True)
            
        else: # this allows you to go back when the song is not playing
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()-1)
            if self.listWidget_player_files.currentRow() == -1:
                self.listWidget_player_files.setCurrentRow(len(self.playerThread.midi_file_list)-1)
            
        self.playerThread.back_check = True
    
    def player_last_file(self):
        # only gets called when back btn is pressed and progress is < 5%
        
        # when no file or the first file is highlighted, pressing back highlights the last file
        if self.listWidget_player_files.currentRow() == -1 or self.listWidget_player_files.currentRow() == 0:
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
    
    def player_back_enabled(self, b):
        if b:
            self.btn_player_back.setEnabled(True)
        else:
            self.btn_player_back.setEnabled(False)
                
    def on_player_next_click(self):
        logging.info('player-next btn clicked')
        
        # when a song is paused clicking next automatically starts playing next file
        
        # update GUI (only if song is already playing/paused)
        if not self.btn_player_home.isEnabled():
            self.btn_player_play.setVisible(False)
            self.btn_player_pause.setVisible(True)
        
        self.playerThread.next_check = True
        self.player_next_file()
    
    def player_next_file(self):
        # gets called when next btn is clicked AND when song naturally finishes  
        # linked to playerThread function call
        
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
    
    def player_next_enabled(self, b):
        if b:
            self.btn_player_next.setEnabled(True)
        else:
            self.btn_player_next.setEnabled(False)
                
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
        
        self.btn_player_back.setEnabled(True)
        self.btn_player_next.setEnabled(True)
        
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
        dest_dir = PROJ_PATH + '/midi-files'
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

    def update_player_progress(self, percentage):
        self.progressBar_player.setValue(percentage)
    
    
#---MAKER PAGE ELEMENTS-------------------------------------------------
        
    def on_maker_start_click(self):
        logging.info('maker-start btn clicked')
        
        # check to see if maker_song_name is valid (6 checks)
        # first pull song name from gui
        self.makerThread.maker_song_name = self.lineEdit_maker_name.text()
        
        # 1.  make sure name doesn't contain any invalid characters
        valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
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
        self.label_maker_saveas.setEnabled(False)
        self.label_maker_BPM.setEnabled(False)
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
        os.chdir(PROJ_PATH+ '/midi-files')
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
        self.label_maker_saveas.setEnabled(True)
        self.label_maker_BPM.setEnabled(True)
        self.label_maker_recording_indicator.hide()
        self.label_maker.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.label_maker.setText(text)


#---LIVE PAGE ELEMENTS--------------------------------------------------

    def on_live_start_click(self):
        logging.info('live-start btn clicked')
        
        # update GUI
        self.btn_live_start.setVisible(False)
        self.btn_live_done.setVisible(True)
        self.btn_live_home.setEnabled(False)
        self.label_live.setText("Press done to stop")
        self.textEdit_live.clear()
        
        # start live thread by calling its run() method
        self.liveThread.start()
    
    def on_live_done_click(self):
        logging.info('live-done btn clicked')
        
        # simulate keypress to stop keywatcher code in liveThread
        # simulating keypress calls reset_live_gui
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.esc)
        kb.release(Key.esc)
        
    def reset_live_gui(self):
        self.btn_live_start.setVisible(True)
        self.btn_live_done.setVisible(False)
        self.btn_live_home.setEnabled(True)
        self.label_live.setText("Press start to begin")
        
    def update_live_text(self, text):
        # update and auto-scroll textEdit box
        # text is a string with key, note, and timing info
        self.textEdit_live.append(text)
        sb = self.textEdit_live.verticalScrollBar()
        sb.setValue(sb.maximum())


#---HERO PAGE ELEMENTS--------------------------------------------------

    def on_hero_start_click(self):
        logging.info('hero-start btn clicked')
        
        # check to see if hero_username is valid
        # first pull username name from gui
        self.heroThread.hero_username = self.lineEdit_hero_username.text()
        # 1.  make sure name doesn't contain any invalid characters
        valid_chars = "-_%s%s" % (string.ascii_letters, string.digits)
        invalid_chars = ""
        for c in self.heroThread.hero_username:
            if c not in valid_chars:
                invalid_chars += c
        if invalid_chars:
            QtGui.QMessageBox.warning(self, 'Error', "Invalid characters in name:\n %s" % invalid_chars, QtGui.QMessageBox.Close)
            return
        # 2.  make sure name is not too long 
        if len(self.heroThread.hero_username) > 10:
            QtGui.QMessageBox.warning(self, 'Error', "Username is too long \n10 character max", QtGui.QMessageBox.Close)
            return
        # 3.  make sure name is not empty
        if len(self.heroThread.hero_username) <= 2:
            QtGui.QMessageBox.warning(self, 'Error', "Username is either too short or empty \nMust be at least 3 characters", QtGui.QMessageBox.Close)
            return
        
        # pull song variable from gui combobox
        selection = str(self.comboBox_hero_song.currentText())
        if selection == 'Random Song':
            # build list of midi files then select a random one
            os.chdir(PROJ_PATH + '/midi-files') 
            midi_file_list = []
            for midi_file in sorted(glob.glob("*.mid")):
                # ignore custom files (only works if name starts with custom right now)
                if not midi_file.startswith('custom'):
                    midi_file_list.append(midi_file)
            self.heroThread.hero_song = random.choice(midi_file_list)
        else:
            self.heroThread.hero_song = selection
        self.label_hero_song.setText('Playing: ' + self.heroThread.hero_song)
        
        # set difficulty level
        self.heroThread.difficulty = self.comboBox_hero_difficulty.currentText()
        
        # update GUI
        self.btn_hero_start.setVisible(False)
        self.btn_hero_stop.setVisible(True)
        self.btn_hero_home.setEnabled(False)
        self.label_hero_health.setText('Health: 100%')
        self.stackedWidget_hero.setCurrentIndex(1)
        
        # FOR AN EXAMPLE
        #~ self.label_z.setVisible(True)
        
        # start hero thread by calling its run() method
        self.heroThread.start()
        
    def on_hero_stop_click(self):
        logging.info('hero-stop btn clicked')
        
        # simulate keypress to stop keywatcher code in liveThread
        # simulating keypress calls reset_live_gui
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.esc)
        kb.release(Key.esc)
        
    def reset_hero_gui(self):
        
        # update GUI
        self.btn_hero_start.setVisible(True)
        self.btn_hero_stop.setVisible(False)
        self.btn_hero_home.setEnabled(True)
        self.stackedWidget_hero.setCurrentIndex(0)
        self.hide_all_indicators()
        self.textEdit_hero_leader1.clear()
        self.textEdit_hero_leader2.clear()
        self.textEdit_hero_leader1.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit_hero_leader2.setAlignment(QtCore.Qt.AlignCenter)
        self.update_hero_score('0')
        self.img_hero_kb.setFocus() # so continued typing doesnt modify username
        self.label_hero_health.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.label_hero_score.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        
        # get top 7 highscores from leaderboard.csv file (& set lowest and highest highscores in hero thread)
        highscores = self.get_hero_highscores()
        
        # display highscores in 2 panels: usernames & scores
        for row in highscores:
            self.textEdit_hero_leader1.append(row[1])
            self.textEdit_hero_leader2.append(row[0])
    
    def update_hero_indicator(self, key, color):
        
        # convert key string to a pyqt label_key
        if key == 'z':
            key = self.ind_hz
        elif key == 'x':
            key = self.ind_hx
        elif key == 'c':
            key = self.ind_hc
        elif key == 'v':
            key = self.ind_hv
        elif key == 'b':
            key = self.ind_hb
        elif key == 'n':
            key = self.ind_hn
        elif key == 'm':
            key = self.ind_hm
        elif key == 's':
            key = self.ind_hs
        elif key == 'd':
            key = self.ind_hd
        elif key == 'g':
            key = self.ind_hg
        elif key == 'h':
            key = self.ind_hh
        elif key == 'j':
            key = self.ind_hj 
        
        # swap color string with pyqt color data struct
        if color == 'green':
            color  = QtGui.QColor(0, 255, 0) 
        elif color == 'yellow':
            color  = QtGui.QColor(255, 255, 0) 
        elif color == 'red':
            color  = QtGui.QColor(255, 0, 0)
        else: # if color = "tran" or anything else then hide it
            key.setVisible(False)
            return
        
        # format strings for setting stylesheet
        border_values = "{r}, {g}, {b}, {a}".format(
                                            r = color.red(),
                                            g= color.green(),
                                            b = color.blue(),
                                            a = 255)
        background_values = "{r}, {g}, {b}, {a}".format(
                                            r = color.red(),
                                            g = color.green(),
                                            b = color.blue(),
                                            a = 155)
        
        # update stylesheet and make label visible
        key.setStyleSheet("QLabel { color: rgba("+border_values+"); background-color: rgba("+background_values+"); }")
        key.setVisible(True)
    
    def update_hero_score(self, score):
        self.label_hero_score.setText('Score: ' + score)
        
        if int(score) >= self.heroThread.highest_highscore: # gold
            self.label_hero_score.setStyleSheet("QLabel {color: rgb(175, 175, 0);}") # CHANGE TO BETTER GOLD
        elif int(score) >= self.heroThread.lowest_highscore: # green
            self.label_hero_score.setStyleSheet("QLabel {color: rgb(0, 170, 0);}")
        
    def update_hero_health(self, health):
        self.label_hero_health.setText('Health: ' + health + '%')
        
        if int(health) <= 25: # red
            self.label_hero_health.setStyleSheet("QLabel {color: rgb(255, 0, 0);}")
        else: # black
            self.label_hero_health.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")

    def get_hero_highscores(self):
        # get top 7 highscores from leaderboard.csv file
        with open(PROJ_PATH + '/pyano/leaderboard.csv', 'r') as lb_file:
            highscores = []
            try:
                csv_reader = csv.reader(lb_file, delimiter=',', lineterminator='\n')
                next(csv_reader) # skip first row containing field names
                sorted_lb = sorted(csv_reader, key=lambda row: int(row[0]), reverse=True)
                i = 0
                for row in sorted_lb:
                    if i == 7:
                        break
                    highscores.append(row)
                    i += 1
            except IndexError as e:
                logging.error(e)
        #~ print(highscores)
        
        # set lowest and highest highscores for hero thread (pass these to change score color)
        try:
            self.heroThread.highest_highscore = int(highscores[0][0])
            
            if len(highscores) < 7:
                self.heroThread.lowest_highscore = 0
            else:
                self.heroThread.lowest_highscore = int(highscores[-1][0])
        except:
            print("CSV File Error: empty file or extra whitespace")

        return highscores
        

if __name__ == '__main__':
    main()
    

import os, sys, glob, shutil, time, string, random, logging, csv
from PyQt4 import QtGui, QtCore, uic
from pynput import keyboard
from pynput.keyboard import Key, Controller
from pyano.player import PlayerThread
from pyano.maker import MakerThread
from pyano.live import LiveThread
from pyano.hero import HeroThread

PROJ_PATH = os.getcwd() # /home/pi/pyano-git


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
    fileHandler = logging.FileHandler(PROJ_PATH + '/logs.log')
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
        super(self.__class__, self).__init__(parent) # super returns parent obj (QWidget obj)
        uic.loadUi('pyano/layout.ui', self) # load ui file from Qt Designer
        from resources import resources # pyrcc4 -o resources.py resources.qrc -py3
        
        # reset leaderboard when program launches
        #~ self.clear_leaderboard_file()

        # log path to project folder
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

        # live page setup
        self.btn_live_home.clicked.connect(self.on_home_click)
        self.btn_live_start.clicked.connect(self.on_live_start_click)
        self.btn_live_stop.clicked.connect(self.on_live_stop_click)
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

        # always last things in __init__
        # stackedWidget 0-6 are the 7 GUI pages (home, p, m, l, guide, credits, hero)
        self.stackedWidget.setCurrentIndex(0)
        self.showFullScreen()



#---SHARED PAGE ELEMENTS------------------------------------------------


    def on_home_click(self):
        logging.info('H O M E  btn clicked')
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
        self.ind_li.setVisible(False)

        # hero page
        self.ind_h1.setVisible(False)
        self.ind_h2.setVisible(False)
        self.ind_h3.setVisible(False)
        self.ind_h4.setVisible(False)
        self.ind_h5.setVisible(False)
        self.ind_h6.setVisible(False)
        self.ind_h7.setVisible(False)
        self.ind_h8.setVisible(False)
        self.ind_h9.setVisible(False)
        self.ind_h10.setVisible(False)
        self.ind_h11.setVisible(False)
        self.ind_h12.setVisible(False)
        self.ind_h13.setVisible(False)
        self.ind_h14.setVisible(False)
        self.ind_h15.setVisible(False)
        self.ind_h16.setVisible(False)
        self.ind_h17.setVisible(False)
        self.ind_h18.setVisible(False)
        self.ind_h19.setVisible(False)
        self.ind_h20.setVisible(False)
        self.ind_h21.setVisible(False)
        self.ind_h22.setVisible(False)
        self.ind_h23.setVisible(False)
        self.ind_h24.setVisible(False)


    def show_indicator(self, mode, key, state):
        # used for player, maker, and live indicators
        # hero uses an advanced version that includes colors

        # convert key string to a pyqt label_key

        # player mode
        if mode == 'player' and key == 'z':
            key = self.ind_p1
        elif mode == 'player' and key == 's':
            key = self.ind_p2
        elif mode == 'player' and key == 'x':
            key = self.ind_p3
        elif mode == 'player' and key == 'd':
            key = self.ind_p4
        elif mode == 'player' and key == 'c':
            key = self.ind_p5
        elif mode == 'player' and key == 'v':
            key = self.ind_p6
        elif mode == 'player' and key == 'g':
            key = self.ind_p7
        elif mode == 'player' and key == 'b':
            key = self.ind_p8
        elif mode == 'player' and key == 'h':
            key = self.ind_p9
        elif mode == 'player' and key == 'n':
            key = self.ind_p10
        elif mode == 'player' and key == 'j':
            key = self.ind_p11
        elif mode == 'player' and key == 'm':
            key = self.ind_p12
        elif mode == 'player' and key == 'q':
            key = self.ind_p13
        elif mode == 'player' and key == '2':
            key = self.ind_p14
        elif mode == 'player' and key == 'w':
            key = self.ind_p15
        elif mode == 'player' and key == '3':
            key = self.ind_p16
        elif mode == 'player' and key == 'e':
            key = self.ind_p17
        elif mode == 'player' and key == 'r':
            key = self.ind_p18
        elif mode == 'player' and key == '5':
            key = self.ind_p19
        elif mode == 'player' and key == 't':
            key = self.ind_p21
        elif mode == 'player' and key == '6':
            key = self.ind_p21
        elif mode == 'player' and key == 'y':
            key = self.ind_p22
        elif mode == 'player' and key == '7':
            key = self.ind_p23
        elif mode == 'player' and key == 'u':
            key = self.ind_p24

        # maker mode
        if mode == 'maker' and key == 'z':
            key = self.ind_mz
        elif mode == 'maker' and key == 's':
            key = self.ind_ms
        elif mode == 'maker' and key == 'x':
            key = self.ind_mx
        elif mode == 'maker' and key == 'd':
            key = self.ind_md
        elif mode == 'maker' and key == 'c':
            key = self.ind_mc
        elif mode == 'maker' and key == 'v':
            key = self.ind_mv
        elif mode == 'maker' and key == 'g':
            key = self.ind_mg
        elif mode == 'maker' and key == 'b':
            key = self.ind_mb
        elif mode == 'maker' and key == 'h':
            key = self.ind_mh
        elif mode == 'maker' and key == 'n':
            key = self.ind_mn
        elif mode == 'maker' and key == 'j':
            key = self.ind_mj
        elif mode == 'maker' and key == 'm':
            key = self.ind_mm
        elif mode == 'maker' and key == 'q':
            key = self.ind_mq
        elif mode == 'maker' and key == '2':
            key = self.ind_m2
        elif mode == 'maker' and key == 'w':
            key = self.ind_mw
        elif mode == 'maker' and key == '3':
            key = self.ind_m3
        elif mode == 'maker' and key == 'e':
            key = self.ind_me
        elif mode == 'maker' and key == 'r':
            key = self.ind_mr
        elif mode == 'maker' and key == '5':
            key = self.ind_m5
        elif mode == 'maker' and key == 't':
            key = self.ind_mt
        elif mode == 'maker' and key == '6':
            key = self.ind_m6
        elif mode == 'maker' and key == 'y':
            key = self.ind_my
        elif mode == 'maker' and key == '7':
            key = self.ind_m7
        elif mode == 'maker' and key == 'u':
            key = self.ind_mu

        # live mode
        if mode == 'live' and key == 'z':
            key = self.ind_lz
        elif mode == 'live' and key == 's':
            key = self.ind_ls
        elif mode == 'live' and key == 'x':
            key = self.ind_lx
        elif mode == 'live' and key == 'd':
            key = self.ind_ld
        elif mode == 'live' and key == 'c':
            key = self.ind_lc
        elif mode == 'live' and key == 'v':
            key = self.ind_lv
        elif mode == 'live' and key == 'g':
            key = self.ind_lg
        elif mode == 'live' and key == 'b':
            key = self.ind_lb
        elif mode == 'live' and key == 'h':
            key = self.ind_lh
        elif mode == 'live' and key == 'n':
            key = self.ind_ln
        elif mode == 'live' and key == 'j':
            key = self.ind_lj
        elif mode == 'live' and key == 'm':
            key = self.ind_lm
        elif mode == 'live' and key == 'q':
            key = self.ind_lq
        elif mode == 'live' and key == '2':
            key = self.ind_l2
        elif mode == 'live' and key == 'w':
            key = self.ind_lw
        elif mode == 'live' and key == '3':
            key = self.ind_l3
        elif mode == 'live' and key == 'e':
            key = self.ind_le
        elif mode == 'live' and key == 'r':
            key = self.ind_lr
        elif mode == 'live' and key == '5':
            key = self.ind_l5
        elif mode == 'live' and key == 't':
            key = self.ind_lt
        elif mode == 'live' and key == '6':
            key = self.ind_l6
        elif mode == 'live' and key == 'y':
            key = self.ind_ly
        elif mode == 'live' and key == '7':
            key = self.ind_l7
        elif mode == 'live' and key == 'u':
            key = self.ind_lu
        elif mode == 'live' and key == 'i':
            key = self.ind_li


        # hero mode (excluding user played notes)
        if mode == 'hero' and key == '13':
            key = self.ind_h13
        elif mode == 'hero' and key == '14':
            key = self.ind_h14
        elif mode == 'hero' and key == '15':
            key = self.ind_h15
        elif mode == 'hero' and key == '16':
            key = self.ind_h16
        elif mode == 'hero' and key == '17':
            key = self.ind_h17
        elif mode == 'hero' and key == '18':
            key = self.ind_h18
        elif mode == 'hero' and key == '19':
            key = self.ind_h19
        elif mode == 'hero' and key == '20':
            key = self.ind_h21
        elif mode == 'hero' and key == '21':
            key = self.ind_h21
        elif mode == 'hero' and key == '22':
            key = self.ind_h22
        elif mode == 'hero' and key == '23':
            key = self.ind_h23
        elif mode == 'hero' and key == '24':
            key = self.ind_h24

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

        # setup gui page elements
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
        # always the last thing in setup so you cant see changes
        self.stackedWidget.setCurrentIndex(1) 
        
        # fill in listWidget with all .mid files in directory
        self.listWidget_player_files.clear()
        os.chdir(PROJ_PATH + '/midi-files')
        # sort glob to get alphabetical instead of random
        for midi_file in sorted(glob.glob("*.mid")):
            # display file on the gui
            self.listWidget_player_files.addItem(midi_file[:-4])
            # build midi_file_list for playerThread
            self.playerThread.midi_file_list.append(midi_file) 
        os.chdir(PROJ_PATH)

        # highlight/select first file in listWidget
        self.listWidget_player_files.setCurrentRow(0)
        logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')

        # connect function calls in this thread to emits from playerThread
        self.connect(self.playerThread, QtCore.SIGNAL("playerNextFile()"), self.player_next_file)
        self.connect(self.playerThread, QtCore.SIGNAL("playerLastFile()"), self.player_last_file)
        self.connect(self.playerThread, QtCore.SIGNAL("resetPlayerGUI()"), self.reset_player_gui)
        self.connect(self.playerThread, QtCore.SIGNAL("playerBtnsEnabled(bool)"), self.player_btns_enabled)
        self.connect(self.playerThread, QtCore.SIGNAL("updatePlayerProgress(int)"), self.update_player_progress)
        self.connect(self.playerThread, QtCore.SIGNAL("showIndicator(QString, QString, QString)"), self.show_indicator)
        self.connect(self.playerThread, QtCore.SIGNAL("hideAllIndicators()"), self.hide_all_indicators)


    def on_maker_click(self):
        logging.info('M A K E R  btn clicked')

        # setup makerThread (doesn't start until on_maker_start_click)
        self.makerThread = MakerThread(None)

        # setup gui page elements
        self.label_title.setText(' M A K E R')
        self.kb_piano_img.setFocus() # remove focus from lineEdit_maker_name
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.label_maker.setText("Press start to begin")
        self.textEdit_maker.clear()
        self.hide_all_indicators()
        self.stackedWidget.setCurrentIndex(2)

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

        # setup liveThread (doesnt start until on_live_start_click)
        self.liveThread = LiveThread(None)

        # setup gui page elements
        self.label_title.setText(' L I V E')
        self.btn_live_stop.setVisible(False)
        self.label_live.setText("Press start to begin")
        self.textEdit_live.clear()
        self.hide_all_indicators()
        self.stackedWidget.setCurrentIndex(3)

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

        # setup gui page elements
        self.label_title.setText(' H E R O')
        self.btn_hero_stop.setVisible(False)
        self.textEdit_hero_leader1.clear()
        self.textEdit_hero_leader2.clear()
        self.textEdit_hero_leader1.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit_hero_leader2.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_hero_username.clear()
        self.lineEdit_hero_username.setFocus()
        self.hide_all_indicators()
        self.label_hero_health.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.label_hero_score.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.comboBox_hero_difficulty.setCurrentIndex(1) # set to normal mode
        self.stackedWidget_hero.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(6)

        # fill in comboBox with non-custom midi files + a random option
        self.comboBox_hero_song.clear()
        self.comboBox_hero_song.addItem('Random Song')
        os.chdir(PROJ_PATH + '/midi-files')
        for midi_file in sorted(glob.glob("*.mid")):
            # ignore custom files (only works if name starts with custom right now)
            if not midi_file.startswith('custom'):
                self.comboBox_hero_song.addItem(midi_file)
        os.chdir(PROJ_PATH)

        # get top 7 highscores from leaderboard.csv file 
        # & set lowest and highest highscores in hero thread
        highscores = self.get_hero_highscores()

        # display highscores in 2 panels: usernames & scores
        for row in highscores:
            self.textEdit_hero_leader1.append(row[1])
            self.textEdit_hero_leader2.append(row[0])

        # connect function calls in this thread to emits from heroThread
        self.connect(self.heroThread, QtCore.SIGNAL("updateHeroIndicator(QString, QString)"), self.update_hero_indicator)
        self.connect(self.heroThread, QtCore.SIGNAL("updateHeroScore(int)"), self.update_hero_score)
        self.connect(self.heroThread, QtCore.SIGNAL("updateHeroHealth(int)"), self.update_hero_health)
        self.connect(self.heroThread, QtCore.SIGNAL("heroStopEnabled(bool)"), self.hero_stop_enabled)
        self.connect(self.heroThread, QtCore.SIGNAL("resetHeroGUI()"), self.reset_hero_gui)
        self.connect(self.heroThread, QtCore.SIGNAL("showIndicator(QString, QString, QString)"), self.show_indicator)
        self.connect(self.heroThread, QtCore.SIGNAL("hideAllIndicators()"), self.hide_all_indicators)


    def on_exit_click(self):
        logging.info('E X I T  btn clicked')

        # pop-up message box to confirm exit
        choice = QtGui.QMessageBox.question(self, 'Exit',
                                            "Are you sure you want to exit?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            logging.info("CLOSING PYANO...\n\n\n")
            sys.exit()
        logging.info('***user selected not to exit***')



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
        self.listWidget_player_files.setEnabled(False)

        # if no file is highlighted then highlight the first one
        if self.listWidget_player_files.currentItem() is None:
            self.listWidget_player_files.setCurrentRow(0)

        # set the current song so playerThread can find its index in 
        # midi_file_list & knows where to start playing
        self.playerThread.current_song = self.listWidget_player_files.currentRow()

        # display which file is highlighted/playing
        self.label_player.setText("Playing: {}".format(self.listWidget_player_files.currentItem().text()))

        # play button has 2 uses: start playing when no song is playing
        # & resume when a song is paused
        if self.btn_player_stop.isEnabled(): # cheap way if checking
            logging.info("*Resume Playing*")
            self.playerThread.pause_check = False # un-pause song in playerThread
        else:
            logging.info("*Start Playing*")
            self.btn_player_stop.setEnabled(True)
            self.playerThread.stop_check = False
            self.playerThread.pause_check = False
            self.playerThread.next_check = False
            self.playerThread.back_check = False
            self.playerThread.start() # calls run() in playerThread
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
            self.player_btns_enabled(False)

        else: # this allows you to go back when the song is not playing
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()-1)
            if self.listWidget_player_files.currentRow() == -1:
                self.listWidget_player_files.setCurrentRow(len(self.playerThread.midi_file_list)-1)
        
        # set back flag in playerThread
        self.playerThread.back_check = True


    def player_last_file(self):
        # only gets called when back btn is pressed and progress is < 5%

        # when no file or the first file is highlighted, pressing back highlights the last file
        if self.listWidget_player_files.currentRow() == -1 or self.listWidget_player_files.currentRow() == 0:
            self.listWidget_player_files.setCurrentRow(len(self.playerThread.midi_file_list)-1)
        elif self.listWidget_player_files.currentRow() != 0:
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()-1)
        logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')

        # update Now Playing text (unless song is stopped)
        # home btn not enabled = song is playing or paused
        if not self.btn_player_home.isEnabled(): 
            self.label_player.setText("Playing: {}".format(self.listWidget_player_files.currentItem().text()))
            if self.btn_player_play.isVisible():
                self.label_player.setText("Paused: {}".format(self.listWidget_player_files.currentItem().text()))


    def on_player_next_click(self):
        logging.info('player-next btn clicked')
        
        # when a song is paused clicking next starts playing next file

        # update GUI (only if song is already playing/paused)
        if not self.btn_player_home.isEnabled():
            self.btn_player_play.setVisible(False)
            self.btn_player_pause.setVisible(True)
            self.player_btns_enabled(False)
        
        # update gui highlight on file list and now playing text
        self.player_next_file()
        
        # set next flag in playerThread
        self.playerThread.next_check = True


    def player_next_file(self):
        # gets called by this thread on_player_next_click and by
        # playerThread when a song naturally finishes or cant be played

        # update highlighted list item (don't let the user skip past the last file)
        if self.listWidget_player_files.currentRow() != len(self.playerThread.midi_file_list)-1:
            self.listWidget_player_files.setCurrentRow(self.listWidget_player_files.currentRow()+1)
            logging.info(self.listWidget_player_files.currentItem().text() + ' is selected')
        else:
            # go back to first highlighted file since going past index size
            self.listWidget_player_files.setCurrentRow(0)
            # stop playback when last file ends or user skips past last file
            self.playerThread.stop_check = True

        # update Now Playing text (unless song is stopped)
        if not self.btn_player_home.isEnabled():
            if self.listWidget_player_files.currentItem() != None:
                self.label_player.setText("Playing: {}".format(self.listWidget_player_files.currentItem().text()))
        self.progressBar_player.setValue(0)


    def on_player_stop_click(self):
        logging.info('player-stop btn clicked')

        # stop playback in the playerThread
        self.playerThread.stop_check = True # calls reset_player_gui


    def reset_player_gui(self):

        # update gui elements
        self.listWidget_player_files.setEnabled(True)
        self.btn_player_home.setEnabled(True)
        self.btn_player_add_files.setEnabled(True)
        self.btn_player_shuffle.setEnabled(True)
        self.btn_player_alpha.setEnabled(True)
        self.btn_player_stop.setEnabled(False)
        self.btn_player_play.setVisible(True)
        self.btn_player_pause.setVisible(False)
        self.btn_player_back.setEnabled(True)
        self.btn_player_next.setEnabled(True)
        self.label_player.setText("Press play to begin")
        self.listWidget_player_files.setFocus()
        self.progressBar_player.setValue(0)


    def on_player_shuffle_click(self):
        logging.info('player-shuffle btn clicked')
        
        # update gui elements
        self.btn_player_alpha.setVisible(True)
        self.btn_player_shuffle.setVisible(False)

        # shuffle midi_file_list
        random.shuffle(self.playerThread.midi_file_list)

        # update gui with newly sorted list
        self.listWidget_player_files.clear()
        for midi_file in self.playerThread.midi_file_list:
            self.listWidget_player_files.addItem(midi_file[:-4])
        self.listWidget_player_files.setCurrentRow(0)


    def on_player_alpha_click(self):
        logging.info('player-alpha btn clicked')
        
        # update gui elements
        self.btn_player_shuffle.setVisible(True)
        self.btn_player_alpha.setVisible(False)

        # clear midi_file_list
        self.listWidget_player_files.clear()
        self.playerThread.midi_file_list = []

        # alphabetize & update gui with newly sorted list
        os.chdir(PROJ_PATH + '/midi-files')
        for midi_file in sorted(glob.glob("*.mid")):
            self.playerThread.midi_file_list.append(midi_file)
            self.listWidget_player_files.addItem(midi_file[:-4])
        os.chdir(PROJ_PATH)
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

            # re-sort playerThread.midi_file_list since we appended to it
            self.playerThread.midi_file_list = sorted(self.playerThread.midi_file_list)

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
        # used to update progress bar with current song progress in playerThread
        self.progressBar_player.setValue(percentage)


    def player_btns_enabled(self, b):
        # used to disable and re-enable the player buttons during song
        # processing to avoid spam clicks breaking the code
        if b:
            self.btn_player_next.setEnabled(True)
            self.btn_player_back.setEnabled(True)
            self.btn_player_stop.setEnabled(True)
            self.btn_player_pause.setEnabled(True)
        else:
            self.btn_player_next.setEnabled(False)
            self.btn_player_back.setEnabled(False)
            self.btn_player_stop.setEnabled(False)
            self.btn_player_pause.setEnabled(False)



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
        if os.path.exists(PROJ_PATH + '/midi-files/' + self.makerThread.maker_song_name):
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

        self.lineEdit_maker_name.setEnabled(False)
        self.label_maker_saveas.setEnabled(False)
        self.textEdit_maker.clear()
        self.textEdit_maker.setAlignment(QtCore.Qt.AlignCenter)
        self.label_maker.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_maker.setText("Input           Note         Solenoid")
        self.label_maker.setAlignment(QtCore.Qt.AlignCenter)

        # log song name
        logging.info('song name: {}'.format(self.makerThread.maker_song_name))

        # start maker thread by calling its run() method
        self.makerThread.start()


    def on_maker_done_click(self):
        logging.info('maker-done btn clicked')
        
        # simulate keypress to stop keywatcher code in makerThread (save file)
        # simulating keypress calls update_maker_gui & update_maker_filename
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.enter)
        kb.release(Key.enter)


    def on_maker_cancel_click(self):
        logging.info('maker-cancel btn clicked')
        
        # simulate keypress to stop keywatcher code in makerThread (discard file)
        # simulating keypress calls update_maker_gui
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.backspace)
        kb.release(Key.backspace)


    def update_maker_filename(self):
        # fill in lineEdit_maker_name with first available file name
        i = 1
        while os.path.exists(PROJ_PATH + '/midi-files/custom_song_0%s.mid' % i):
            i += 1
        if i == 10:
            while os.path.exists(PROJ_PATH + '/midi-files/custom_song_%s.mid' % i):
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


    def update_maker_gui(self, text):
        # change gui back from recording view when cancel or done is pressed
        # text is a string that either says "canceled" or "file saved"
        self.btn_maker_start.setVisible(True)
        self.btn_maker_done.setVisible(False)
        self.btn_maker_cancel.setVisible(False)
        self.btn_maker_home.setEnabled(True)
        self.lineEdit_maker_name.setEnabled(True)
        self.label_maker_saveas.setEnabled(True)
        self.label_maker.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.label_maker.setText(text)



#---LIVE PAGE ELEMENTS--------------------------------------------------


    def on_live_start_click(self):
        logging.info('live-start btn clicked')

        # update gui
        self.textEdit_live.clear()
        self.textEdit_live.setAlignment(QtCore.Qt.AlignCenter)
        self.btn_live_start.setVisible(False)
        self.btn_live_stop.setVisible(True)
        self.btn_live_home.setEnabled(False)
        self.label_live.setText("Press stop to cancel")

        # start live thread by calling its run() method
        self.liveThread.start()


    def on_live_stop_click(self):
        logging.info('live-done btn clicked')

        # simulate keypress to stop keywatcher code in liveThread
        # simulating keypress calls reset_live_gui
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.backspace)
        kb.release(Key.backspace)


    def reset_live_gui(self):
        self.btn_live_start.setVisible(True)
        self.btn_live_stop.setVisible(False)
        self.btn_live_home.setEnabled(True)
        self.label_live.setText("Press start to begin")


    def update_live_text(self, text):
        # update and auto-scroll textEdit box
        # text is a string with key, note, and solenoid pressed
        self.textEdit_live.append(text)



#---HERO PAGE ELEMENTS--------------------------------------------------


    def on_hero_start_click(self):
        logging.info('hero-start btn clicked')

        # check to see if hero_username is valid
        # first pull username name from gui
        self.heroThread.hero_username = self.lineEdit_hero_username.text()
        # 1.  make sure name doesn't contain any invalid characters
        valid_chars = "-_:)( %s%s" % (string.ascii_letters, string.digits)
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
        
        # disable stop button until song processing completes
        self.hero_stop_enabled(False)

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
            os.chdir(PROJ_PATH)
            self.heroThread.hero_song = random.choice(midi_file_list)
        else:
            self.heroThread.hero_song = selection
        self.label_hero_song.setText('Playing: ' + self.heroThread.hero_song)

        # set difficulty level in heroThread using gui selection
        self.heroThread.difficulty = self.comboBox_hero_difficulty.currentText()

        # update GUI
        self.btn_hero_start.setVisible(False)
        self.btn_hero_stop.setVisible(True)
        self.btn_hero_home.setEnabled(False)
        self.label_hero_health.setText('Health: 100%')
        self.stackedWidget_hero.setCurrentIndex(1)


        # start hero thread by calling its run() method
        self.heroThread.start()


    def on_hero_stop_click(self):
        logging.info('hero-stop btn clicked')
        
        # disable stop button to avoid spamming
        self.hero_stop_enabled(False)

        # simulate keypress to stop keywatcher code in liveThread
        # simulating keypress calls reset_live_gui
        # THIS IS STILL CALLING 2x (KNOWN THREADING ISSUE)
        kb = Controller()
        kb.press(Key.backspace)
        kb.release(Key.backspace)

    
    def hero_stop_enabled(self, b):
        # this is actually needed even though is looks pointless
        # heroThread needs a gui thread function to callback to
        # can't just change btn_hero_stop from heroThread without this
        if b:
            self.btn_hero_stop.setEnabled(True)
        else:
            self.btn_hero_stop.setEnabled(False)


    def reset_hero_gui(self):

        # update GUI
        self.btn_hero_start.setVisible(True)
        self.btn_hero_stop.setVisible(False)
        self.btn_hero_home.setEnabled(True)
        self.hide_all_indicators()
        self.textEdit_hero_leader1.clear()
        self.textEdit_hero_leader2.clear()
        self.textEdit_hero_leader1.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit_hero_leader2.setAlignment(QtCore.Qt.AlignCenter)
        self.update_hero_score(0)
        self.img_hero_kb.setFocus() # so continued typing doesnt modify username
        self.label_hero_health.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.label_hero_score.setStyleSheet("QLabel {color: rgb(40, 40, 40);}")
        self.stackedWidget_hero.setCurrentIndex(0)

        # get top 7 highscores from leaderboard.csv file (& set lowest and highest highscores in hero thread)
        highscores = self.get_hero_highscores()

        # display highscores in 2 panels: usernames & scores
        for row in highscores:
            self.textEdit_hero_leader1.append(row[1])
            self.textEdit_hero_leader2.append(row[0])


    def update_hero_indicator(self, key, color):

        # convert key string to a pyqt label_key
        if key == 'z':
            key = self.ind_h1
        elif key == 's':
            key = self.ind_h2
        elif key == 'x':
            key = self.ind_h3
        elif key == 'd':
            key = self.ind_h4
        elif key == 'c':
            key = self.ind_h5
        elif key == 'v':
            key = self.ind_h6
        elif key == 'g':
            key = self.ind_h7
        elif key == 'b':
            key = self.ind_h8
        elif key == 'h':
            key = self.ind_h9
        elif key == 'n':
            key = self.ind_h10
        elif key == 'j':
            key = self.ind_h11
        elif key == 'm':
            key = self.ind_h12

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

        # update score on gui
        self.label_hero_score.setText('Score: ' + str(score))

        # change color of score when making it onto the leaderboard
        if score >= self.heroThread.highest_highscore: # gold
            self.label_hero_score.setStyleSheet("QLabel {color: rgb(175, 175, 0);}")
        elif score >= self.heroThread.lowest_highscore: # green
            self.label_hero_score.setStyleSheet("QLabel {color: rgb(0, 170, 0);}")


    def update_hero_health(self, health):

        # update health on gui
        self.label_hero_health.setText('Health: ' + str(health) + '%')

        # change health to red when below 25%
        if health <= 25: # red
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


    def clear_leaderboard_file(self):
        with open(PROJ_PATH + '/pyano/leaderboard.csv', 'w+') as csv_file:
            csv_file.write('score,username,song,difficulty' + '\n')



if __name__ == '__main__':
    main()


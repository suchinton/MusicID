import subprocess
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit,\
     QPushButton,QToolButton, QFileDialog, QLabel, QTabWidget, \
     QPlainTextEdit,QTableWidget, QProgressBar
from PyQt5 import QtWidgets 
from PyQt5 import uic
import sys
import os
import Recorder
from threading import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import *
import webbrowser

from spotiFind import Spoti_Find

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()

        # Load App
        uic.loadUi("MusicID_MW.ui",self)

        # Define Tab to navigat
        self.Tabs = self.findChild(QTabWidget,"Tabs")
                
        # Define Widgets

        ## for main tab
        self.Listen = self.findChild(QPushButton, "ListenButton")

        self.Search_by_T = self.findChild(QLineEdit,"Search_by_T")
        self.Search_by_T_B = self.findChild(QPushButton,"Search_by_T_B")

        self.Message = self.findChild(QLabel,"Message")
        self.progressBar = self.findChild(QProgressBar,"progressBar")

        self.Path = self.findChild(QLineEdit,"Path")
        self.FilePicker = self.findChild(QToolButton,"FilePicker") ## Picks File. 
        self.DirPicker = self.findChild(QToolButton,"DirPicker") ## Picks dir. 
        self.Submit = self.findChild(QPushButton, "SubmitButton")
        
        ## for result tab

        self.Status = self.findChild(QPlainTextEdit,"Status")
        self.Artist = self.findChild(QLabel,"Artist")
        self.Track = self.findChild(QLabel,"Track")
        self.Album = self.findChild(QLabel,"Album")

        ## for Recommendation tab
        self.Recommend = self.findChild(QTableWidget,"Recommend")

        ## for Spotify tab
        self.spotBrowser = self.findChild(QWebEngineView, "spotBrowser")

        # Actions to events
        self.Listen.clicked.connect(self.T_SearchDB)

        self.FilePicker.clicked.connect(self.PickFile)
        self.DirPicker.clicked.connect(self.PickDir)
        self.Search_by_T_B.clicked.connect(self.FindTrack)
        self.Submit.clicked.connect(self.T_Index_refresh)
        self.Recommend.doubleClicked.connect(self.OpenLink)

        self.Message.hide()
        self.progressBar.hide()
        # Show App
        self.show()
    
    # Thread Fns to keep GUI responsive

    def T_SearchDB(self):
        self.t1 = Thread(target = self.SearchDB)
        self.t1.start()

    def T_Index_refresh(self):
        self.t3 = Thread(target=self.Index_refresh)
        self.t3.start()

    def PickFile(self):
        try:
            filepath = QFileDialog.getOpenFileName(self, 'Select File', "", "*.mp3;; *.m4a;; *.wav")
            self.Path.setText(str(filepath[0]))
        except:
            print("File not selected")

    def PickDir(self):
        try:
            folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
            self.Path.setText(folderpath)
        except:
            print("Dir not picked")

    def Index_refresh(self):
        if str(self.Path.text()).endswith(('.mp3','.m4a','.wav')):
            self.Message.show()
            os.system(f"cd lib && ./musicID index {str(self.Path.text())} >> db")
            self.Message.hide()
        elif str(self.Path.text()).startswith("/"):
            self.Message.show()
            self.progressBar.show()
            n = int(subprocess.getoutput(f"ls {str(self.Path.text())} | wc -l"))
            self.progressBar.setMaximum(n)
            self.progressBar.setValue(0)
            #os.system("cd lib && rm db")
            for root, dirs, files in os.walk(self.Path.text()):
                for name in files:
                    self.progressBar.setValue(self.progressBar.value()+1)
                    os.system(f"cd lib && ./musicID index {os.path.join(root,name)} >> db")
            self.Message.hide()
            self.progressBar.hide()
            os.system("cd lib && cat db | grep /")
    
    def FindTrack(self):
        self.track_result = Spoti_Find(str(self.Search_by_T.text()))
        self.updateRecomendations()
        self.Tabs.setCurrentIndex(2)

    def updateRecomendations(self):
        row = 0
        self.Recommend.setRowCount(len(self.track_result))
        for i in range(len(self.track_result)):
            self.Recommend.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Artist"])))
            self.Recommend.setItem(row, 1, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Album"])))
            self.Recommend.setItem(row, 2, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Track"])))
            self.Recommend.setItem(row, 3, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Link"])))
            row += 1

    def openSpotify(self, link):
        self.spotBrowser.setUrl(self.value)



    def SearchDB(self):  
        self.Listen.setEnabled(False)
        self.Listen.setText("Listening... ﳃ")
        Recorder.rec()
        self.Listen.setText("Searching... ")
        os.system("cd lib && ./musicID search ../output.wav db > ~/MusicID/Status.txt")
        self.Listen.setText("Listen... ")
        self.Listen.setEnabled(True)

        self.Tabs.setCurrentIndex(1)
        
        self.text_file = open("Status.txt", "r")

        self.info = self.text_file.read()
        self.Status.setPlaceholderText(self.info)
        self.Artist.setText(subprocess.getoutput("cat Status.txt | grep Artist"))
        self.Track.setText(subprocess.getoutput("cat Status.txt | grep Track"))
        self.Album.setText(subprocess.getoutput("cat Status.txt | grep Album"))
        
        self.track_result = Spoti_Find(str(self.Track.text()).replace('Track title: ',''))
        self.updateRecomendations()
        self.text_file.close()
    
    def OpenLink(self):
        for index in self.Recommend.selectionModel().selectedIndexes():
            self.value = str(self.Recommend.item(self.Recommend.currentRow(), self.Recommend.currentColumn()).text())
            if self.value.startswith("http://") or self.value.startswith("https://"):
                self.openSpotify()
                webbrowser.open(self.value)

# init the app

app = QApplication(sys.argv)
Main_pg = MainWindow()
app.exec_()
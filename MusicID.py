from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton,QToolButton, QFileDialog, QTextEdit, QLabel
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import Recorder
from threading import *
import requests

class ResultWindow(QMainWindow):
    def __init__(self):
        super(ResultWindow,self).__init__()

        # Load App
        uic.loadUi("Result.ui",self)

        # Define Widgets
        self.Display = self.findChild(QTextEdit,"Display")
        self.Art = self.findChild(QLabel,"Art")
        #self.Artist_L = self.findChild(QLabel,"Artist_L")        
        #self.Track_L = self.findChild(QLabel,"Track_L")
        #self.Album_L = self.findChild(QLabel,"Album_L")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()

        # Load App
        uic.loadUi("MusicID_MW.ui",self)
        
        # Define Widgets
        self.Directory = self.findChild(QLineEdit,"Directory")
        self.Submit = self.findChild(QPushButton, "SubmitButton")
        self.toolbutton = self.findChild(QToolButton,"FilePicker")
        self.Listen = self.findChild(QPushButton, "ListenButton")

        # Actions to events
        self.toolbutton.clicked.connect(self.PickDir)
        self.Submit.clicked.connect(self.T_Index_refresh)
        self.Listen.clicked.connect(self.T_SearchDB)

        # Show App
        self.show()
    
    ## Thread Fns to keep GUI responsive
    def T_SearchDB(self):
        self.t = Thread(target = self.SearchDB)
        self.t.start()
        self.t.join()

    def T_Index_refresh(self):
        t = Thread(target=self.Index_refresh)
        t.start()

    def PickDir(self):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.Directory.setText(folderpath)

    def Index_refresh(self):
        os.system("cd lib && rm db")
        for root, dirs, files in os.walk(self.Directory.text()):
            for name in files:
                os.system(f"cd lib && ./musicID index {os.path.join(root,name)} >> db")
        os.system("cd lib && cat db | grep /")

    def SearchDB(self):
        self.Listen.setEnabled(False)
        self.Listen.setText("Listening... ﳃ")
        Recorder.rec()
        self.Listen.setText("Searching... ")
        os.system("cd lib && ./musicID search ../output.wav db > ~/MusicID/Status.txt")

        text_file = open("Status.txt", "r")
        result = text_file.read()

        print(result)
        
        self.show_result = ResultWindow()

        self.show_result.Display.setText(result)


        #self.url_img = 'https://i.scdn.co/image/ab67616d0000b273c8a11e48c91a982d086afc69'

        #self.image = QImage()
        #self.image.loadFromData(requests.get(self.url_img).content)
        #self.show_result.Art.setPixmap(QPixmap(self.image))
         
        #self.artist = os.system("cat Status.txt | grep artist")
        #self.show_result.Artist_L.setText(self.artist)
#
        #self.track = os.system("cat Status.txt | grep Track")
        #self.show_result.Track_L.setText(self.track)
#
        #self.album = os.system("cat Status.txt | grep Album")
        #self.show_result.Album_L.setText(self.album)
#
        self.show_result.show()

        text_file.close()
        os.remove("output.wav")
        os.remove("Status.txt")
        
        self.Listen.setText("Listen... ")
        self.Listen.setEnabled(True)

# init the app

app = QApplication(sys.argv)
Main_pg = MainWindow()
app.exec_()


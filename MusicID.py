from distutils import text_file
from multiprocessing.connection import wait
from time import sleep
from tokenize import String
from unittest import result
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit,\
     QPushButton,QToolButton, QFileDialog, QTextEdit, QTabWidget, QPlainTextEdit
from PyQt5 import uic
import sys
import os
import Recorder
from threading import *

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

        self.Directory = self.findChild(QLineEdit,"Directory")
        self.toolbutton = self.findChild(QToolButton,"FilePicker") ## Picks dir. 
        self.Submit = self.findChild(QPushButton, "SubmitButton")
        
        ## for result tab

        self.Status = self.findChild(QPlainTextEdit,"Status")
        self.Artist = self.findChild(QLineEdit,"Artist")
        self.Track = self.findChild(QLineEdit,"Track")
        self.Album = self.findChild(QLineEdit,"Album")

        # Actions to events
        self.Listen.clicked.connect(self.T_SearchDB)

        self.toolbutton.clicked.connect(self.PickDir)
        self.Submit.clicked.connect(self.T_Index_refresh)

        # Show App
        self.show()
    
    # Thread Fns to keep GUI responsive
    def T_Search(self):
        #self.T_SearchDB()
        self.t0 = Thread(target = self.T_SearchDB)
        self.t0.start() 
        
    
    def Show_results(self):
        self.text_file = open("Status.txt", "r")
        self.result = self.text_file.read()
        self.Display.setText(self.result)
        self.text_file.close()

    def T_SearchDB(self):
        self.t1 = Thread(target = self.SearchDB)
        self.t1.start()

    def T_Index_refresh(self):
        self.t3 = Thread(target=self.Index_refresh)
        self.t3.start()

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
        self.Listen.setText("Listen... ")
        self.Listen.setEnabled(True)

        self.Tabs.setCurrentIndex(1)
        
        self.text_file = open("Status.txt", "r")

        self.info = self.text_file.read()
        self.Status.setPlaceholderText(self.info)

        result = self.text_file.readlines()
        M_resut = []

        for line in result:
            M_resut.append(line.strip())

        print(M_resut)

        #Ar = ''.join(result[8])
        #Tr = ''.join(result[9])
        #Al = ''.join(result[10])
        #self.Artist.setText(Ar)
        #self.Track.setText(
        #self.Album.setText(Al)
        
        #self.Display.setText(self.result)
        self.text_file.close()

# init the app

app = QApplication(sys.argv)
Main_pg = MainWindow()
app.exec_()


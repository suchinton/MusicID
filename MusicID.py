from cgitb import reset
from operator import le
from pickle import FALSE
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton,QToolButton, QFileDialog, QTextEdit
from PyQt5 import uic
import sys
import os
import Recorder

class ResultWindow(QMainWindow):
    def __init__(self):
        super(ResultWindow,self).__init__()

        # Load App
        uic.loadUi("Result.ui",self)

        # Define Widgets
        self.Display = self.findChild(QTextEdit,"Display")        


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
        self.Submit.clicked.connect(self.Index_refresh)
        self.Listen.clicked.connect(self.SearchDB)

        # Show App
        self.show()

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
        self.Listen.setText("Listening... ﳃ")
        self.Listen.setEnabled(False)
        Recorder.rec()
        self.Listen.setText("Listen... ")
        self.Listen.setEnabled(True)
        os.system("cd lib && ./musicID search ../output.wav db > ~/MusicID/Status.txt")

        text_file = open("Status.txt", "r")
        result = text_file.read()

        print(result)

        self.show_result = ResultWindow()
        self.show_result.Display.setText(result)
        self.show_result.show()

        text_file.close()
        os.remove("output.wav")
        os.remove("Status.txt")

# init the app

app = QApplication(sys.argv)
Main_pg = MainWindow()
app.exec_()


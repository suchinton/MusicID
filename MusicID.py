import subprocess
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit,\
     QPushButton,QToolButton, QFileDialog, QLabel, QTabWidget, \
     QPlainTextEdit,QTableWidget, QProgressBar, QListWidget,QDockWidget, QMessageBox
from PyQt5.QtCore import *
from PyQt5 import QtWidgets 
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QMovie
import sys
import os
import Recorder
from threading import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import notify2

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
        self.Loading = self.findChild(QLabel,"Loading")
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

        self.Album_Art = self.findChild(QLabel,"Album_Art")
        self.Status = self.findChild(QPlainTextEdit,"Status")
        self.Location = self.findChild(QLabel,"Location")
        self.Artist = self.findChild(QLabel,"Artist")
        self.Track = self.findChild(QLabel,"Track")
        self.Album = self.findChild(QLabel,"Album")

        ## for Recommendation tab
        self.Recommend = self.findChild(QTableWidget,"Recommend")

        ## for Spotify tab
        self.spotBrowser = self.findChild(QWebEngineView, "spotBrowser")
        
        ## for Song list Dock (side-bar)

        self.dockWidget = self.findChild(QDockWidget,"dockWidget")
        self.SideBarButton = self.findChild(QToolButton,"SideBarButton")
        self.SongsList = self.findChild(QListWidget,"SongsList")

        # Actions to events
        self.Listen.clicked.connect(self.SearchDB_1)
        self.FilePicker.clicked.connect(self.PickFile)
        self.DirPicker.clicked.connect(self.PickDir)
        self.Search_by_T_B.clicked.connect(self.FindTrack)
        self.Submit.clicked.connect(self.Index_refresh)
        self.Recommend.doubleClicked.connect(self.OpenLink)
        self.SideBarButton.clicked.connect(self.dockWidget.show)

        self.dockWidget.hide()
        self.Message.hide()
        self.progressBar.hide()

        try:
            self.T_UpdateList()
        except:
            FileNotFoundError

        # Show App
        self.show()
    
    # Thread Fns to keep GUI responsive

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
            try:
                self.Message.show()
                os.system(f"cd lib && ./musicID index {self.Path.text()} >> db")
                self.T_UpdateList()
                self.Message.hide()
                QMessageBox.information(self,"Done",f"Track has been added to DB")
            except:
                print("Error!! couldn't Hash given file")

        elif str(self.Path.text()).startswith("/"):
            self.Message.show()
            self.progressBar.show()
            self.set_ProgressBarMax()
            self.DI = Dir_Index(self.Path.text())
            self.DI.start()
            self.DI.update_progress.connect(self.update_progressBar)
            self.DI.finished.connect(self.Dir_Indexed)
    
    def set_ProgressBarMax(self):
        self.Size = 0
        for root, dirs, files in os.walk(str(self.Path.text())):
            for name in files:
                self.Size += 1
        print(self.Size)
        self.progressBar.setMaximum(self.Size)

    def update_progressBar(self, i):
        self.i = i
        self.progressBar.setValue(self.i)

    def Dir_Indexed(self):
        self.T_UpdateList()
        self.Message.hide()
        self.progressBar.hide()
        QMessageBox.information(self,"Done",f"All files have been added to DB")

    def SearchDB_1(self):           ## step 1 in searching db- record output.wav
        self.Listen.setEnabled(False)
        self.animation = QMovie("./res/mic.gif")
        self.Loading.setMovie(self.animation)
        self.animation.start()
        self.Listen.setText("Listening...")
        self.T_RecClass()

    def T_RecClass(self):           ## QThread recording starts
        self.t0 = RecClass()
        self.t0.start()
        self.t0.finished.connect(self.SearchDB_2)        ## after QThread process is finished we move on to SearchDB_2

    def SearchDB_2(self):                               ## step 2 in calling QThread for Searching
        self.Listen.setText("Searching...")
        self.T_SearchDB()

    def T_SearchDB(self):               ## QThread starts Searching 
        self.t1 = SearchClass()
        self.t1.start()
        self.t1.finished.connect(self.SearchDB_3)

    def SearchDB_3(self):                    ## step 3 in calling QThread for Searching
        self.Listen.setText("Listen")
        self.Listen.setEnabled(True)
        self.animation.stop()
        self.Loading.setPixmap(QPixmap("./res/mic.gif"))
        self.Tabs.setCurrentIndex(1)
        
        try:
            self.text_file = open("Status.txt", "r")
            self.info = self.text_file.read()

            if 'No match found' in self.info:
                self.Status.setPlaceholderText(self.info)
                self.Artist.setText(subprocess.getoutput("cat Status.txt | grep Artist"))
                self.Track.setText(subprocess.getoutput("cat Status.txt | grep Track"))
                self.Album.setText(subprocess.getoutput("cat Status.txt | grep Album"))
                self.img = QPixmap("./res/Default.png")
                self.Album_Art.setPixmap(self.img)
                self.Location.setText("")
                n = notify2.Notification(
                     "No Match Found...",
                     "Try re-indexing your Music Dir or Try again",
                     icon= f"{os.getcwd()}/res/Default.png"
                    )
                n.show()
                QMessageBox.warning(self,"No Match","No Match was found for the Track, please try again or add song to databse")

            else:
                self.path_to_file = str(subprocess.getoutput("cat Status.txt  | grep $HOME ")).replace('Found match: ','').replace("'","")
                self.Status.setPlaceholderText(self.info)
                self.Artist.setText(subprocess.getoutput("cat Status.txt | grep Artist"))
                self.Track.setText(subprocess.getoutput("cat Status.txt | grep Track"))
                self.Album.setText(subprocess.getoutput("cat Status.txt | grep Album"))

                if os.path.exists(self.path_to_file):
                    os.system(f"ffmpeg -i '{self.path_to_file}' Cover.png")
                    self.img = self.circleImage("Cover.png")
                    self.Album_Art.setPixmap(self.img)
                    self.Location.setText('<a href='+self.path_to_file+'>Location: '+self.path_to_file+'</a>')
                    n = notify2.Notification(
                         "Match Found!",
                         f"{self.Artist.text()} \n {self.Track.text()}",
                         icon= f"{os.getcwd()}/Cover.png"
                        )
                           
                else:
                    self.img = QPixmap("./res/Default.png")
                    self.Album_Art.setPixmap(self.img)
                    self.Location.setText("")
                    n = notify2.Notification(
                         "Match Found!",
                         f"{self.Artist.text()} \n {self.Track.text()}",
                         icon= f"{os.getcwd()}/res/Default.png"
                        )

                self.track_result = Spoti_Find(str(self.Track.text()).replace('Track title: ',''))
                self.updateRecomendations()
                n.show()

                self.text_file.close()
                os.system("rm Status.txt")
                os.system("rm output.wav")
                os.system("rm Cover.png")
                os.system("rm db")
        except:
            FileNotFoundError
    
    def FindTrack(self):
        try:    
            self.track_result = Spoti_Find(str(self.Search_by_T.text()))
            self.updateRecomendations()
            self.Tabs.setCurrentIndex(2)
        except:
            print("Error in FindTrack fn")

    def updateRecomendations(self):
        row = 0
        self.Recommend.setRowCount(len(self.track_result))
        for i in range(len(self.track_result)):
            self.Recommend.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Artist"])))
            self.Recommend.setItem(row, 1, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Album"])))
            self.Recommend.setItem(row, 2, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Track"])))
            self.Recommend.setItem(row, 3, QtWidgets.QTableWidgetItem(str(self.track_result[i]["Link"])))
            row += 1

    def OpenLink(self):
        for index in self.Recommend.selectionModel().selectedIndexes():
            self.value = str(self.Recommend.item(self.Recommend.currentRow(), self.Recommend.currentColumn()).text())
            if self.value.startswith("http://") or self.value.startswith("https://"):
                url = QUrl.fromUserInput(self.value)
                self.spotBrowser.load(url)
                self.Tabs.setCurrentIndex(3)
            
    def openSpotify(self):
        url = QUrl.fromUserInput(self.value)
        self.spotBrowser.load(url)

    def T_UpdateList(self):
        t3 = Thread(target=self.UpdateList)
        t3.start()

    def UpdateList(self):
        try:
            Database = open('./lib/db', 'r')

            home = str(subprocess.getoutput("echo $HOME"))
            L = []

            for line in Database:
                if home in line:
                    L.append(line.replace(subprocess.getoutput("echo $HOME/"),"~/"))

            self.SongsList.addItems(L)
            Database.close()
        except:
            FileNotFoundError

    def circleImage(self,Img):
        source = QPixmap(Img)
        size = min(source.width(), source.height())

        target = QPixmap(size, size)
        target.fill(Qt.transparent)

        qp = QPainter(target)
        qp.setRenderHints(qp.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        qp.setClipPath(path)

        sourceRect = QRect(0, 0, size, size)
        sourceRect.moveCenter(source.rect().center())
        qp.drawPixmap(target.rect(), source, sourceRect)
        qp.end()

        return target

class Dir_Index(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, Path, parent=None):
        QThread.__init__(self, parent)
        self.Path = Path
    def start(self):
        QThread.start(self)
    def run(self):
        try:
            i = 0
            for root, dirs, files in os.walk(str(self.Path)):
                for name in files:
                    with open('./lib/db') as myfile:
                        if str(os.path.join(root,name)) in myfile.read():
                            print("Track already added") 
                            i += 1
                            print(f"{i} process complete ... {str(os.path.join(root,name))} already in DB")
                            self.update_progress.emit(i)   
                        else:    
                            os.system(f"cd lib && ./musicID index {os.path.join(root,name)} >> db")
                            i += 1
                            print(f"{i} process complete")
                            self.update_progress.emit(i)
        except:
            print("error in Dir_index class")

class RecClass(QThread):
    def run(self):
        try:
            Recorder.rec()
        except:
            print("Error in class RecClass(QThread)")

class SearchClass(QThread):
    def run(self):
        try:
            os.system("cd lib && ./musicID search ../output.wav db > ~/MusicID/Status.txt")
        except:
                print("Error in class SearchClass(QThread)")

# init the app
if __name__ == '__main__':

    if os.path.exists("./lib/musicID"):
        print("no need to make file again")
    else:
        os.system("cd lib && make")
        os.system("bash install_dependencies.sh")

    if os.path.exists("./lib/db"):
        print("DB Loaded...")
    else:
        print("DB doesn't exist... creating file now")
        os.system("touch ./lib/db")

    if os.path.exists("Cover.png"):
        os.system("rm Cover.png")

    notify2.init('MusicID')
    
    app = QApplication(sys.argv)
    Main_pg = MainWindow()
    sys.exit(app.exec())

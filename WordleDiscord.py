import discord
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import threading
class DiscordGameBot:
    currentGameDict = {}
    mainwindow = None
    
    def __init__(self) -> None:
        #TEMP create current
        refreshThread = threading.Thread(target=self.captureScreenShot)
        refreshThread.daemon = True
        refreshThread.start()

        
        
    def setMainWindow(self, mw):
        self.mainwindow = mw
        
    def captureScreenShot(self):
        time.sleep(2)
        screen = QtWidgets.QApplication.primaryScreen()
        screenShot = screen.grabWindow(self.mainwindow.winId())
        screenShot.save("bullBird.jpg", 'jpg')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    x = DiscordGameBot()
    x.setMainWindow(mw)
    sys.exit(app.exec())
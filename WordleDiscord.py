import discord
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import threading
import responses


class DiscordGameBot:
    currentGameDict = {}
    mainwindow = None

    def __init__(self) -> None:

        TOKEN = "MTEyNzM0Mjk4MzYyNTMyNjYxMg.GfWMk1."
        token += "1jHNWvWdnw_l-AvVA9gYh8DwvlKGNKWL0N5ghQ"
        client = discord.Client()

        @client.event
        async def onReady():
            print(f'{client.user} is now running')

        client.run(TOKEN)
        # TEMP create c
        # TEMP create current
        # refreshThread = threading.Thread(target=self.captureScreenShot)
        # refreshThread.daemon = True
        # refreshThread.start()

    def setMainWindow(self, mw):
        self.mainwindow = mw

    def captureScreenShot(self):
        time.sleep(2)
        screen = QtWidgets.QApplication.primaryScreen()
        screenShot = screen.grabWindow(self.mainwindow.winId())
        screenShot.save("bullBird.jpg", 'jpg')

    async def receiveMessage(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    x = DiscordGameBot()
    x.setMainWindow(mw)
    sys.exit(app.exec())

import sys
import os
from PyQt5.QtWidgets import QApplication, QButtonGroup, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget, QPushButton, QMainWindow, QDialog, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtGui import QColor, QFont, QKeyEvent, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize
from WordleRow import WordleRow
import WordleGrid
from KeyBoard import KeyBoard
from enums import Status
import pyperclip
from GameOverWindow import GameOverWindow
from discord import Webhook
import asyncio
import aiohttp
# import enchant
import webbrowser


# d = enchant.Dict("en_US")
CACHE_PATH = "game.txt"
PROFILE_PATH = "profile.txt"


class MainWindow(QMainWindow):
    BACK_SPACE = 16777219
    ENTER_SUBMIT = 16777220
    correctColor = QColor(106, 170, 100)
    inWordColor = QColor(201, 180, 88)
    incorrectColor = QColor(120, 124, 126)
    unknownColor = QColor(211, 214, 218)
    name = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.centralWidget = QWidget()

        self.gameOverWindow = None
        self.nameEntryForm = None
        self.nameLineEdit = None

        app_icon = QIcon('Icons\MainIconGOOD.png')
        self.setWindowIcon(app_icon)
        self.centralWidget.setWindowIcon(app_icon)
        # self.setFixedSize(600,950)
        self.wordleGrid = WordleGrid.WordleGrid()

        self.setWindowTitle('WORDLE')
        # set background color
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(p)

        self.layout2 = QVBoxLayout()
        self.clipBoardButton = QPushButton("Copy Results to Clipboard")
        self.layout2.setSpacing(3)
        self.toolBar = self.createToolbar()
        self.layout2.addWidget(self.toolBar)
        self.layout2.setAlignment(
            self.toolBar, Qt.AlignmentFlag.AlignHCenter)

        self.layout2.setContentsMargins(0, 0, 0, 0)
        # This resets the current letter or column back to the beginning
        self.resetCurrCol()
        self.guesses = []
        self.layout2.addWidget(self.wordleGrid)
        self.layout2.setAlignment(
            self.wordleGrid, Qt.AlignmentFlag.AlignHCenter)
        self.keyboard = KeyBoard()
        self.clipBoardButton.setEnabled(False)
        self.clipBoardButton.clicked.connect(self.copyToClipboard)

        lines = []
        if os.path.isfile(CACHE_PATH):
            file = open(CACHE_PATH, 'r')
            lines = file.readlines()
            file.close()

        if len(lines) > 0:
            # if puzzle in cache is yesterdays
            if int(lines[0]) != self.wordleGrid.getPuzzleNumber():
                self.clearCache()
                self.appendToCache(str(self.wordleGrid.getPuzzleNumber()))
            else:
                lines.pop(0)  # remove the puzzle number from the list
                self.replayTheCache(lines)

        else:
            self.appendToCache(str(self.wordleGrid.getPuzzleNumber()))

        self.disappearingLabel = QLabel()
        self.disappearingLabel.setFont(QFont('Arial Black', 12))
        self.disappearingLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        sp = QSizePolicy()
        sp.setRetainSizeWhenHidden(True)

        self.disappearingLabel.setSizePolicy(sp)

        self.layout2.addWidget(self.disappearingLabel)
        self.layout2.setAlignment(
            self.disappearingLabel, Qt.AlignmentFlag.AlignHCenter)
        self.disappearingLabel.setVisible(False)
        self.layout2.addWidget(self.keyboard)
        self.layout2.setAlignment(
            self.keyboard, Qt.AlignmentFlag.AlignHCenter)

        self.layout2.addWidget(self.clipBoardButton)
        self.centralWidget.setLayout(self.layout2)

        self.setCentralWidget(self.centralWidget)

        if os.path.isfile(PROFILE_PATH):
            file = open(PROFILE_PATH, 'r')
            lines = file.readlines()
            if (len(lines) > 0):
                self.name = lines[0]
            file.close()
            self.show()
        else:
            self.dialog = QDialog(self)
            formGroup = QGroupBox()
            self.nameLineEdit = QLineEdit()
            okButton = QPushButton("Ok")
            okButton.clicked.connect(self.setName)
            mainLayout = QVBoxLayout()
            formLayout = QFormLayout()

            formLayout.addRow(QLabel("Name"), self.nameLineEdit)
            formGroup.setLayout(formLayout)
            mainLayout.addWidget(formGroup)
            mainLayout.addWidget(okButton)
            self.dialog.setLayout(mainLayout)
            self.dialog.show()

    def setName(self):
        self.name = self.nameLineEdit.text()
        file = open(PROFILE_PATH, 'w')
        file.write(self.name)
        file.close()
        self.dialog.close()
        self.show()

    def clearCache(self):
        file = open(CACHE_PATH, "w")
        file.close()
    '''
    Loads last games information into the WordleGrid and recalculate
    '''

    def replayTheCache(self, pastPuzzle: list):
        n = 0
        for row in pastPuzzle:
            word = row.rstrip()
            curr = self.wordleGrid.wordleRows[n]
            curr.quickSet(word)
            dict = self.wordleGrid.evalSubmission()
            self.keyboard.findButtonsToChangeColors(dict)
            self.wordleGrid.isWinner = (len(dict["correct"]) == 5)
            self.wordleGrid.nextGuess()
            n += 1
        self.wordleGrid.isDone = self.wordleGrid.isWinner or len(
            pastPuzzle) == 6
        if (self.wordleGrid.isDone):
            self.clipBoardButton.setEnabled(True)

    def copyToClipboard(self):

        pyperclip.copy(self.wordleGrid.createPuzzleResults())
        if (self.wordleGrid.isWinner):
            self.displayTempMsg(
                "Copied Results to clipboard", "lightgrey", 2000)
        else:
            self.displayTempMsg(
                "Do you really want to share these results?", "lightgrey", 2000)

    def createToolbar(self):
        output = QWidget()
        layout = QHBoxLayout()

        wordleButton = QPushButton("Wordle")

        wordleButton.setFont(QFont('Arial Black', 25))
        wordleButton.setFixedSize(QSize(200, 75))
        wordleButton.clicked.connect(self.centerText)

        refreshButton = QPushButton()
        refreshButton.setIcon(QIcon("icon\\refresh.png"))
        refreshButton.setIconSize(QSize(50, 50))
        refreshButton.setFixedSize(QSize(50, 50))
        refreshButton.clicked.connect(self.refresh)

        buttonGroup = QButtonGroup()
        buttonGroup.addButton(refreshButton)
        refreshButton.setStyleSheet("border: 0px;")
        layout.setSpacing(0)
        layout.addWidget(wordleButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(refreshButton, alignment=Qt.AlignmentFlag.AlignRight)
        wordleButton.setStyleSheet("border: 0px;"
                                   "color: white;"
                                   "alignment: center")

        output.setLayout(layout)
        return output

    def centerText(self):
        webbrowser.open("https://www.youtube.com/watch?v=xvFZjo5PgG0")

    def refresh(self):
        if self.wordleGrid.isDifferentDay():
            self.reset()

        else:
            self.displayTempMsg("Still the same day.", "pink", 3000)

    def reset(self):

        self.clearCache()
        self.resetCurrCol()
        self.wordleGrid.reset()
        self.wordleGrid.pickWordForTheDay()
        self.keyboard.reset()
        self.clipBoardButton.setEnabled(False)
        self.gameOverWindow = None

    def appendToCache(self, word):
        file = open(CACHE_PATH, "a")
        file.write(word + "\n")
        file.close()

    def displayTempMsg(self, msg: str, color: str, time: int):
        self.disappearingLabel.setStyleSheet("background-color: "+color)
        self.disappearingLabel.setText(msg)
        self.disappearingLabel.setVisible(True)
        self.disappearingLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        QTimer().singleShot(time, self.disappearingLabel.hide)

    def resetCurrCol(self):
        self.currCol = -1

    def showGameOverWindow(self):
        if self.gameOverWindow == None:
            self.gameOverWindow = GameOverWindow(self)
        self.gameOverWindow.show()

    async def sendDiscordMessage(self, msg):
        async with aiohttp.ClientSession() as session:

            webHook = Webhook.from_url(
                "https://discord.com/api/webhooks/1127398517942517791/VVTL1nHMkN4virf0BTX3QrOWb3OXLJvZyLCjmXZ6ltt_Nbcdfg-5ld1iubGhEHsoPyoB", session=session)
            await webHook.send(self.name+"'s results:\n"+msg)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if not self.wordleGrid.isDone:
            keyInt = e.key()
            currGuess = self.wordleGrid.currWordleRow
            if (isinstance(currGuess, WordleRow)):

                if ((keyInt >= 65 and keyInt <= 90) or (keyInt >= 97 and keyInt <= 122)):

                    if (self.currCol < 4):
                        self.currCol += 1
                        currGuess.setBox(self.currCol, e.text().upper())

                elif (keyInt == self.BACK_SPACE):
                    if (self.currCol > -1):

                        currGuess.setBox(self.currCol, "")

                        if (self.currCol != -2):
                            self.currCol -= 1
                elif (keyInt == self.ENTER_SUBMIT):

                    submittedWord = currGuess.getWordStr()
                    if (len(submittedWord) == 5):

                        if self.wordleGrid.isWord(submittedWord):
                            self.appendToCache(submittedWord)
                            dict = self.wordleGrid.evalSubmission()
                            self.keyboard.findButtonsToChangeColors(dict)
                            self.wordleGrid.isWinner = (
                                len(dict["correct"]) == 5)
                            self.wordleGrid.nextGuess()
                            if self.wordleGrid.isWinner or self.wordleGrid.getGuessCount() == 6:

                                loop = asyncio.new_event_loop()
                                loop.run_until_complete(self.sendDiscordMessage(
                                    self.wordleGrid.createPuzzleResults()))
                                loop.close()

                                self.showGameOverWindow()
                                self.wordleGrid.isDone = True
                                self.clipBoardButton.setEnabled(True)
                                if (self.wordleGrid.isWinner):
                                    if self.wordleGrid.getGuessCount() <= 2:
                                        self.displayTempMsg(
                                            "YOU CHEATIN' SoB", "green", 3000)
                                    elif self.wordleGrid.getGuessCount() > 2 and self.wordleGrid.getGuessCount() <= 4:
                                        self.displayTempMsg(
                                            "Well, you're slightly above average. BIG DEAL", "yellow", 6000)
                                    else:
                                        self.displayTempMsg(
                                            "You solved it. Barely.", "lightgrey", 2000)

                                else:
                                    self.displayTempMsg("Loser!", "red", 10000)
                                    webbrowser.open(
                                        "https://www.youtube.com/watch?v=eNynxWZK30A")

                            self.resetCurrCol()

                        else:
                            self.displayTempMsg(
                                "\""+submittedWord+"\" is not an English word, Idiot!!!", "pink", 2000)

                    else:
                        self.displayTempMsg(
                            "CAN YOU EVEN COUNT!", "pink", 2000)

        return super().keyPressEvent(e)


if __name__ == '__main__':
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    sys.exit(app.exec())

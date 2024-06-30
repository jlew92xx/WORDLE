import sys
import os
from PyQt5.QtWidgets import QApplication, QButtonGroup, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget, QPushButton, QMainWindow, QDialog, QLineEdit, QFormLayout, QGroupBox, QSpacerItem
from PyQt5.QtGui import QColor, QFont, QKeyEvent, QIcon, QPixmap, QMouseEvent, QPalette
from PyQt5.QtCore import Qt, QTimer, QSize
import WordleGrid
from KeyBoard import KeyBoard
import pyperclip
import time
from GameOverWindow import GameOverWindow
from discord import Webhook
import aiohttp
# import enchant


# d = enchant.Dict("en_US")
CACHE_PATH = "game.txt"
PROFILE_PATH = "profile.txt"
RIGHT_PIC_PATH = "snowman.png"
LEFT_PIC_PATH = "winter.png"

class MainWindow(QMainWindow):
    BACK_SPACE = 16777219
    ENTER_SUBMIT = 16777220
    correctColor = QColor(106, 170, 100)
    inWordColor = QColor(201, 180, 88)
    incorrectColor = QColor(120, 124, 126)
    unknownColor = QColor(211, 214, 218)
    hta = []
    name = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.centralWidget = QWidget()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.gameOverWindow = None
        self.nameEntryForm = None
        self.nameLineEdit = None

        app_icon = QIcon('MainIconGOOD.png')
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
        # refresh button


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

        self.disappearingLabel = QLabel()
        self.disappearingLabel.setFont(QFont('Arial Black', 15))
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

        # refreshThread = threading.Thread(target=self.checkNewDay)
        # refreshThread.daemon = True
        # refreshThread.start()

    def setName2(self, name):
        self.name = name

    def setIcons(self, left, right):
        rightIcon = QIcon(right)
        self.rightButton.setIcon(rightIcon)

        leftIcon = QIcon(left)
        self.leftButton.setIcon(leftIcon)
        
    
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

        for row in pastPuzzle:
            if row.rstrip() != "done":
                self.submitOneWord(row)

    def submitOneWord(self, word):
        word = word.rstrip().upper()
        curr = self.wordleGrid.getCurrentTurn()
        curr.quickSet(word)
        dict = self.wordleGrid.evalSubmission()
        self.keyboard.findButtonsToChangeColors(dict)
        self.wordleGrid.isWinner = (len(dict["correct"]) == 5)
        self.wordleGrid.nextGuess()


    def paintKeyboard(self, keyboardDict: dict):
        self.keyboard.evalKeyboard(keyboardDict)

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
        buttonWidget = QWidget()
        buttonLayout = QHBoxLayout()

        wordleButton.setFont(QFont('boulder', 32))
        wordleButton.setFixedSize(QSize(200, 75))
        wordleButton.clicked.connect(self.centerText)
        
        self.leftButton = QPushButton()
        self.leftButton.setIconSize(QSize(50, 50))
        self.leftButton.setFixedSize(QSize(50, 50))
        self.leftButton.setStyleSheet("background-color: black")
        
        self.rightButton = QPushButton()
        self.rightButton.setIconSize(QSize(50, 50))
        self.rightButton.setFixedSize(QSize(50, 50))
        self.rightButton.setStyleSheet("background-color: black")

        buttonLayout.addWidget(
            self.rightButton, alignment=Qt.AlignmentFlag.AlignRight)
        buttonLayout.addWidget(
            self.leftButton, alignment=Qt.AlignmentFlag.AlignRight)

        buttonWidget.setLayout(buttonLayout)

        self.leftButton.setStyleSheet("border: 0px;")
        layout.setSpacing(0)
        layout.addWidget(wordleButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        wordleButton.setStyleSheet("border: 0px;"
                                   "color: white;"
                                   "alignment: center")

        layout.addWidget(buttonWidget,
                         alignment=Qt.AlignmentFlag.AlignRight)

        output.setLayout(layout)
        return output

    def centerText(self):
        pass



    def paintGame(self, guesses: list):
        self.wordleGrid.paintGrid(guesses)

    def reset(self):

        self.clearCache()
        self.resetCurrCol()
        self.wordleGrid.reset()
        # self.wordleGrid.pickWordForTheDay()
        self.keyboard.reset()
        self.clipBoardButton.setEnabled(False)
        self.rightButton.setEnabled(True)
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

    def showTempMsg(self, msg, color):
        self.disappearingLabel.setStyleSheet("background-color: "+color)
        self.disappearingLabel.setText(msg)
        self.disappearingLabel.setVisible(True)

    def hideTempMsg(self):
        self.disappearingLabel.setVisible(False)

    def resetCurrCol(self):
        self.currCol = -1

    def showGameOverWindow(self):
        if self.gameOverWindow == None:
            self.gameOverWindow = GameOverWindow(self)
        self.gameOverWindow.show()

    def createFileName(self, userName):
        return "TEMP" + str(self.wordleGrid.getPuzzleNumber())+"_" + userName + ".txt"

    def getPuzzleNumber(self):
        return str(self.wordleGrid.getPuzzleNumber())


    def isDone(self):
        return self.wordleGrid.isDone

    def setHardmode(self, pHardmode):
        self.wordleGrid.setHardmode(pHardmode)

    def isWinner(self):
        return self.wordleGrid.isWinner

    def isWord(self, word):
        return self.wordleGrid.isWord(word)

    def createPuzzleResults(self):
        return self.wordleGrid.createPuzzleResults()

    def isHardmodeCompliant(self, input):
        return self.wordleGrid.isHardModeComplient(input)


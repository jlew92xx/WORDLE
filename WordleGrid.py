from PyQt5.QtCore import QSize
from WordleRow import WordleRow
from datetime import date
import hashlib
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from enums import Status

wordBank_Path = "Wordbank\Wordle-La.txt"
guessBank_Path = "Wordbank\Wordle-Ta.txt"
correctColor = QColor(106, 170, 100)
inWordColor = QColor(201, 180, 88)
incorrectColor = QColor(120, 124, 126)
unknownColor = QColor(211, 214, 218)
EPOCH_DATE = date(2023, 6, 26)


class WordleGrid(QWidget):

    wordBank = []
    guessDictionary = {}
    wordleRows = []
    currWordleRow = None
    currTurn = 0

    def __init__(self) -> None:
        super().__init__()
        self.isWinner = False
        self.isDone = False
        with open(wordBank_Path) as wb:
            self.wordBank = wb.read().splitlines()
        self.buildGuessBank()
        self.buildGrid()
        self.setFixedSize(QSize(600, 600))
        self.puzzleNumber = self.getPuzzleNumber()
        self.wordOfTheDay = ""
        self.pickWordForTheDay()

    def buildGrid(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        for x in range(6):
            wordleRow = WordleRow(unknownColor)
            wordleRow.setCorrectColor(correctColor)
            wordleRow.setInWordColor(inWordColor)
            wordleRow.setIncorrectColor(incorrectColor)
            layout.addWidget(wordleRow)
            self.wordleRows.append(wordleRow)
        self.setLayout(layout)
        self.currWordleRow = self.wordleRows[self.currTurn]

    def evalSubmission(self):
        if isinstance(self.currWordleRow, WordleRow):
            return self.currWordleRow.evalSubmission(self.getWordOfTheDay())

    def evalSubmission2(self):
        if isinstance(self.currWordleRow, WordleRow):
            return self.currWordleRow.evalSubmission2(self.getWordOfTheDay())

    def getPuzzleNumber(self):
        delta = date.today() - EPOCH_DATE
        return delta.days

    def isDifferentDay(self):
        if (self.puzzleNumber == self.getPuzzleNumber()):
            return False
        else:
            self.puzzleNumber = self.getPuzzleNumber()
            return True

    def buildTempList(self):
        with open(guessBank_Path) as gb:
            tempList = self.wordBank + gb.read().splitlines()
        return tempList

    def buildGuessBank(self):
        tempList = self.buildTempList()

        for word in tempList:
            k = word[:2]

            if k not in self.guessDictionary.keys():
                self.guessDictionary[k] = [word]
            else:
                if isinstance(self.guessDictionary[k], list):
                    self.guessDictionary[k].append(word)

    def reset(self):
        self.currTurn = 0
        self.pickWordForTheDay()

    def hashCurrDate(self):
        currDate = str(date.today()) + "SALT"
        output = int(hashlib.sha256(currDate.encode('utf-8')).hexdigest(), 16)

        return output

    def pickWordForTheDay(self):
        numFiveLetterWords = len(self.wordBank)
        self.wordOfTheDay = self.wordBank[self.hashCurrDate(
        ) % numFiveLetterWords].upper()

    def setWordOfTheDay(self, word: str):
        self.wordOfTheDay = word.upper()

    def createPuzzleResults(self) -> str:

        if (self.isWinner):
            s = str(self.getGuessCount())
        else:
            s = "⛈️"
        output = "JL's Wordle " + \
            str(self.getPuzzleNumber()) + " " + s + "/6" + "\n\n"
        for guess in self.wordleRows:
            if (isinstance(guess, WordleRow)):
                row = guess.getRowResult()
                for status in row:

                    if (status is Status.CORRECT):
                        output += "🟩"

                    elif (status is Status.INWORD):
                        output += "🟨"

                    elif (status is Status.INCORRECT):
                        output += "⬜"

                    else:
                        break
                output += "\n"

        return output.rstrip()

    def getWordOfTheDay(self):
        return self.wordOfTheDay

    # Checks if the user guess is an actual word.
    def isWord(self, word: str) -> bool:
        key = word[:2].lower()
        output = False
        if key in self.guessDictionary.keys():
            lis = self.guessDictionary[key]
            output = word.lower() in lis
        return output

    def getGuessCount(self):
        return self.currTurn

    def nextGuess(self):
        self.currTurn = self.currTurn + 1
        if self.currTurn < 6:
            self.currWordleRow = self.wordleRows[self.currTurn]

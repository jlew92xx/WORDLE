from PyQt5.QtCore import QSize
from datetime import date
import hashlib
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from enums import Status
import WordleConfigure
wordBank_Path = "Wordle-La.txt"
guessBank_Path = "Wordle-Ta.txt"
correctColor = QColor(106, 170, 100)
inWordColor = QColor(201, 180, 88)
incorrectColor = QColor(120, 124, 126)
unknownColor = QColor(211, 214, 218)



class WordleGrid(QWidget):
    wordBank = []
    guessDictionary = {}

    def __init__(self) -> None:
        super().__init__()
        self.wordleRows = []


        self.buildGrid()
        self.setFixedSize(QSize(600, 600))

        
        
    
    def buildGrid(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        for x in range(WordleConfigure.NUMOFGUESS):
            wordleRow = WordleRow(unknownColor)
            wordleRow.setCorrectColor(correctColor)
            wordleRow.setInWordColor(inWordColor)
            wordleRow.setIncorrectColor(incorrectColor)
            layout.addWidget(wordleRow)
            self.wordleRows.append(wordleRow)
        self.setLayout(layout)
        

    '''
    used for the WordleSolver class. returns dict that includes the index as well
    '''
    def reset(self):
        for guess in self.wordleRows:
            guess.reset()
    
    def paintGrid(self, guesses:list):
        L = len(guesses)
        for i in range(0, L):
            self.wordleRows[i].paintRow(guesses[i]) 
        

from PyQt5.QtGui import QColor
from enums import Status


inWordColorRed = QColor(156, 39, 6)
inWordColorOrange = QColor(245, 118, 26)

class WordleRow(QWidget):
    correctColor = None
    inWordColor = None
    incorrectColor = None
    unknownColor = None
    
    def __init__(self, unknownColor):
        super().__init__()
        
        self.layout2 = QHBoxLayout()
        self.layout2.setSpacing(0)
        self.layout2.setContentsMargins(0, 0, 0, 0)
        self.boxes = []
        self.setUnknownColor(unknownColor)
        for x in range(WordleConfigure.WORDSIZE):
            wb = WordleBox()
            wb.setIndex(x)
            wb.setBoxColor(self.unknownColor)
            self.layout2.addWidget(wb)
            self.boxes.append(wb)

        self.setLayout(self.layout2)

    def setCorrectColor(self, color: QColor):
        self.correctColor = color
    def getBoxAtIndex(self, index):
        return self.boxes[index]
    def setInWordColor(self, color: QColor):
        self.inWordColor = color
        self.inWordColorArray = [(color, Status.INWORD), (inWordColorRed, Status.INWORDRED), (inWordColorOrange, Status.INWORDORANGE)]
    
    def setIncorrectColor(self, color: QColor):
        self.incorrectColor = color

    def setUnknownColor(self, color: QColor):
        self.unknownColor = color

    def getRowResult(self):
        output = []
        for box in self.boxes:
            if (isinstance(box, WordleBox)):
                output.append(box.getStatus())
        return output

    def getWordStr(self):
        output = ""
        for box in self.boxes:
            if (isinstance(box, WordleBox)):
                output += box.toPlainText()

        return output
    def reset(self):
        for box in self.boxes:
            if (isinstance(box, WordleBox)):
                box.reset()
    
    def evalSubmission(self, actual: str):
        output = {"correct": [], "inword": [], "incorrect": [], "inwordred":[], "inwordorange": []}
        n = 0
        # check for green
        ch = ""
        actual = actual.upper()
        notCorrectBoxes = []
        correctedEquiv = ""
        for box in self.boxes:
            if (isinstance(box, WordleBox)):
                ch = box.toPlainText()
                al = actual[n]
                if al == ch:
                    box.setBoxColor(self.correctColor)
                    
                    box.setStatus(Status.CORRECT)
                    output["correct"].append((ch, box.getIndex()))
                else:
                    notCorrectBoxes.append(box)
                    correctedEquiv += al

                n += 1

        for box in notCorrectBoxes:
            if (isinstance(box, WordleBox)):
                ch = box.toPlainText()
                if ch in correctedEquiv:
                    i = (ord(ch) + box.getIndex()) % 3
                    inWordColor = self.inWordColorArray[i][0]
                    inWordStatus = self.inWordColorArray[i][1]
                    box.setBoxColor(inWordColor)
                    box.setStatus(inWordStatus)
                    output[inWordStatus.name.lower()].append((ch, box.getIndex()))
                    correctedEquiv = correctedEquiv.replace(ch, '', 1)
                else:
                    output["incorrect"].append((ch, box.getIndex()))
                    box.setBoxColor(self.incorrectColor)
                    box.setStatus(Status.INCORRECT)
        return output

    # Used when I need to quick set a row for the solver and the replay
    def quickSet(self, word: str):
        n = 0
        for c in word:
            self.setBox(n, c)
            n += 1
    def paintRow(self, guess:list):
        for i in range(0, 5):
            currBox = self.boxes[i]
            if (isinstance(currBox, WordleBox)):
                c = guess[i][0]
                st = guess[i][1]
                currColor = None
                if st == Status.CORRECT:
                    currColor = self.correctColor
                elif st == Status.INCORRECT:
                    currColor = self.incorrectColor
                else:
                    currColor = self.inWordColor
                currBox.setHtml(
                    "<p align=\"center\" valign=\"middle\"><font color=\"black\">"+c)
                currBox.setBoxColor(currColor)
                
    def setBox(self, n, c):
        box = self.boxes[n]
        if (c != ""):
            if (isinstance(box, WordleBox)):
                box.setHtml(
                    "<p align=\"center\" valign=\"middle\"><font color=\"black\">"+c)

        else:
            box.setPlainText("")

from PyQt5.QtGui import QColor, QVector3D
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from enums import Status


class WordleBox(QTextEdit):
    GREY = QColor(211, 214, 218)
    GREEN = QColor(106, 170, 100)
    YELLOW = QColor(201, 180, 88)
    DARK_GREY = QColor(120, 124, 126)
    status = Status.UNKNOWN
    index = -1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(QSize(100, 100))
        self.setBoxColor(self.GREY)
        self.setEnabled(False)
        self.setAutoFillBackground(True)
        font = QFont()
        font.setPointSize(45)
        self.setFont(font)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def setIndex(self, i):
        self.index = i

    def getIndex(self):
        return self.index

    def setStatus(self, pStatus: Status):
        self.status = pStatus

    def getStatus(self):
        return self.status

    def setBoxColor(self, color: QColor):
        p = self.palette()
        self.setHtml(
            "<p align=\"center\" valign=\"middle\"><font color=\"white\">"+self.toPlainText())
        p.setColor(self.viewport().backgroundRole(), color)
        self.viewport().setPalette(p)

    def reset(self):
        self.setBoxColor(self.GREY)
        self.setText("")
        self.setStatus(Status.UNKNOWN)

    def rotateAndChangeColor(self, color):

        self.setBoxColor(color)

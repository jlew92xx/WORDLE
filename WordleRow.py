from WordleBox import WordleBox
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QColor
from enums import Status
import random

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
        for x in range(5):
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

    def reset(self):
        for box in self.boxes:
            if (isinstance(box, WordleBox)):
                box.reset()

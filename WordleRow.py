from WordleBox import WordleBox
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QColor
from enums import Status


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

    def setInWordColor(self, color: QColor):
        self.inWordColor = color

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
        output = {"correct": [], "inword": [], "incorrect": []}
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
                    # box.rotateAndChangeColor(self.correctColor)
                    box.setStatus(Status.CORRECT)
                    output["correct"].append(ch)
                else:
                    notCorrectBoxes.append(box)
                    correctedEquiv += al

                n += 1

        for box in notCorrectBoxes:
            if (isinstance(box, WordleBox)):
                ch = box.toPlainText()
                if ch in correctedEquiv:
                    box.setBoxColor(self.inWordColor)
                    box.setStatus(Status.INWORD)
                    output["inword"].append(ch)
                    correctedEquiv = correctedEquiv.replace(ch, '', 1)
                else:
                    output["incorrect"].append(ch)
                    box.setBoxColor(self.incorrectColor)
                    box.setStatus(Status.INCORRECT)
        return output

    def evalSubmission2(self, actual: str):
        output = {"correct": [], "inword": [], "incorrect": []}
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
                    # box.setBoxColor(self.correctColor)
                    box.rotateAndChangeColor(self.correctColor)
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
                    box.setBoxColor(self.inWordColor)
                    box.setStatus(Status.INWORD)
                    output["inword"].append((ch, box.getIndex()))
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

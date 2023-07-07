from PyQt5.QtGui import QColor, QVector3D
from PyQt5.QtWidgets import QGraphicsRotation, QTextEdit
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
        font.setPointSize(30)
        self.setFont(font)

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
        p.setColor(self.viewport().backgroundRole(), color)
        self.viewport().setPalette(p)

    def reset(self):
        self.setBoxColor(self.GREY)
        self.setText("")
        self.setStatus(Status.UNKNOWN)

    def rotateAndChangeColor(self, color):

        self.setBoxColor(color)

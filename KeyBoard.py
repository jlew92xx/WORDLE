from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont
import pyautogui
from enums import Color, Status
DARK_GREY = "(120,124,126)"
GREEN = "(106, 170, 100)"
YELLOW = "(201,180,88)"
LIGHTGREY = "(211,214,218)"
RED = "(156, 39, 6)"
ORANGE = "(245, 118, 26)"
FIRST_ROW = "qwertyuiop".upper()
SECOND_ROW = "asdfghjkl".upper()
THIRD_ROW = "zxcvbnm".upper()
HEIGHT = 60
width = 50
SPACING = 2


class KeyboardButton(QPushButton):
    
    def __init__(self, text, key):
        super().__init__(text)
        
        self.setFixedSize(QSize(width, HEIGHT))
        self.color = None
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setStyleSheet("background-color: " + Color.LIGHTGREY.value+";"
                           "color: black;"
                           "border-radius: 2px;"
                           "border-color: black;"
                           "padding: 2px;"
                           "text-align: center")
        self.setBoxColor(Color.LIGHTGREY)
        # self.setFont(QFont('Arial Black', 8))
        self.key = key
        self.clicked.connect(self.pressKey)

    def pressKey(self):
        pyautogui.press(self.key)

    def setBoxColor(self, color: Color):
        self.color = color
        self.setStyleSheet("border-radius: 5px;"
                           "background-color :rgb" + color.value+";"
                           "border-width: 2px;"
                           "border-color: black;"
                           "padding: 0px;"
                           "text-align: center"
                           )

    def getBoxColor(self):
        return self.color

    def setNonLetterSize(self):
        self.setFixedSize(QSize(75, HEIGHT))

    def getKey(self):
        return self.key


class KeyBoard(QWidget):

    def __init__(self):
        super().__init__()
        self.dictKeys = {}
        self.keyboardLayout = QVBoxLayout()
        self.keyboardLayout.setSpacing(0)
        self.letterKeys = []
        self.setFixedSize(QSize(600, 225))
        self.buildKeyBoard()

        self.setLayout(self.keyboardLayout)

    def reset(self):
        for key in self.letterKeys:
            key.setBoxColor(Color.LIGHTGREY)

    def buildKeyBoard(self):
        enterBut = KeyboardButton("enter", "enter")
        enterBut.setNonLetterSize()
        backBut = KeyboardButton("<-", "backspace")
        backBut.setNonLetterSize()
        firstRowWidget = QWidget()
        firstRowLayout = QHBoxLayout()
        firstRowLayout.setSpacing(SPACING)
        secondRowWidget = QWidget()
        secondRowLayout = QHBoxLayout()
        secondRowLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        secondRowLayout.setSpacing(SPACING*3)
        thirdRowWidget = QWidget()
        thirdRowLayout = QHBoxLayout()
        thirdRowLayout.setSpacing(0)

        for c in FIRST_ROW:
            button = KeyboardButton(c, c)
            self.dictKeys[c] = button
            firstRowLayout.addWidget(button)
            self.letterKeys.append(button)
        firstRowWidget.setLayout(firstRowLayout)
        self.keyboardLayout.addWidget(firstRowWidget)
        for c in SECOND_ROW:
            button = KeyboardButton(c, c)
            self.dictKeys[c] = button
            secondRowLayout.addWidget(button)
            self.letterKeys.append(button)

        secondRowWidget.setLayout(secondRowLayout)
        self.keyboardLayout.addWidget(secondRowWidget)

        thirdRowLayout.addWidget(enterBut)

        for c in THIRD_ROW:
            button = KeyboardButton(c, c)
            thirdRowLayout.addWidget(button)
            self.letterKeys.append(button)
            self.dictKeys[c] = button

        thirdRowLayout.addWidget(backBut)

        thirdRowWidget.setLayout(thirdRowLayout)
        self.keyboardLayout.addWidget(thirdRowWidget)

    def findButtonsToChangeColors(self, dict):
        # inword = dict["inword"]
        # correct = dict["correct"]
        # incorrect = dict["incorrect"]
        # for button in self.letterKeys:
        #     if (button.getBoxColor() is not Color.GREEN and button.getBoxColor() is not Color.DARK_GREY):
        #         #This is the button k value
        #         k = button.getKey()
                
        #         if
        
        for c in dict["inword"]:
            for button in self.letterKeys:
                if (isinstance(button, KeyboardButton)):
                    if (button.getBoxColor() is not Color.GREEN):
                        if (c[0] == button.getKey()):
                            button.setBoxColor(Color.YELLOW)
       
        for c in dict["inwordred"]:
            for button in self.letterKeys:
                if (isinstance(button, KeyboardButton)):
                    if (button.getBoxColor() is not Color.GREEN):
                        if (c[0] == button.getKey()):
                            button.setBoxColor(Color.RED)
                            
        for c in dict["inwordorange"]:
            for button in self.letterKeys:
                if (isinstance(button, KeyboardButton)):
                    if (button.getBoxColor() is not Color.GREEN):
                        if (c[0] == button.getKey()):
                            button.setBoxColor(Color.ORANGE)    
        for c in dict["correct"]:
            for button in self.letterKeys:
                if (isinstance(button, KeyboardButton)):
                    if (c[0] == button.getKey()):
                        button.setBoxColor(Color.GREEN)

        for c in dict["incorrect"]:
            for button in self.letterKeys:
                if (isinstance(button, KeyboardButton)):
                    if (button.getBoxColor() is Color.LIGHTGREY):
                        if (c[0] == button.getKey()):
                            button.setBoxColor(Color.DARK_GREY)
                            
    def evalKeyboard(self, keyboardDict:dict):
        
        for c in keyboardDict.keys():
            button = self.dictKeys[c]
            status = keyboardDict[c]
            if (isinstance(button, KeyboardButton)):
                if (status == Status.CORRECT):
                    button.setBoxColor(Color.GREEN)
                elif(status == Status.INWORD):
                    button.setBoxColor(Color.YELLOW)
                elif(status == Status.INCORRECT):
                    button.setBoxColor(Color.DARK_GREY)

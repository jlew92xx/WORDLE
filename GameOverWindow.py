from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QWhatsThis
from WordleSolver import WordleSolver
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QWhatsThisClickedEvent


class GameOverWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.mainWindow = parent
        self.setWindowTitle("Compare your results with WordleBot's.")
        app_icon = QIcon('Icons\wordleBot.png')
        self.setWindowIcon(app_icon)
        layout = QVBoxLayout()
        solver = WordleSolver()
        solver.solve()
        botGrid = solver.grid

        layout.addWidget(botGrid, 0, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            self.mainWindow.centerText()
            return True

        return False

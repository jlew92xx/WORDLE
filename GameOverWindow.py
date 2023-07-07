from PyQt5.QtWidgets import QVBoxLayout, QWidget
from WordleSolver import WordleSolver
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class GameOverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compare your results with WordleBot's.")
        app_icon = QIcon('Icons\wordleBot.png')
        self.setWindowIcon(app_icon)
        layout = QVBoxLayout()
        solver = WordleSolver()
        solver.solve()

        botGrid = solver.grid

        layout.addWidget(botGrid, 0, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

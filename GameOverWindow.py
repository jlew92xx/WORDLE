from PyQt5.QtWidgets import QVBoxLayout, QWidget
from WordleSolver import WordleSolver
from PyQt5.QtCore import Qt


class GameOverWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        solver = WordleSolver()
        solver.solve()

        botGrid = solver.grid

        layout.addWidget(botGrid, 0, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

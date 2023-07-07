from enum import Enum

class Color(Enum):
    DARK_GREY = "(120,124,126)"
    GREEN = "(106, 170, 100)"
    YELLOW = "(201,180,88)"
    LIGHTGREY = "(211,214,218)"

class Status(Enum):
    UNKNOWN = 1
    CORRECT = 2
    INWORD = 3
    INCORRECT = 4

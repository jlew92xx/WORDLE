from pathlib import Path
from PyQt5.QtGui import QColor
"""
This is my configure file. 
"""
MAIN = "main"
def isMain():
    branch = ""
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f: content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            branch = line.partition("refs/heads/")[2]
    return (branch == MAIN)
WORDSIZE = 6
NUMOFGUESS = 6
ISMAIN = isMain()
STOREPUZZLENUMBERFILE = ""
MAINDATABASE = 'playerStats.db'
TESTDATABASE = 'testDatabase.db'
SALT = ""
pictureDir = ""
DATABASE = ""

GREY = QColor(211, 214, 218)
GREEN = QColor(106, 170, 100)
YELLOW = QColor(201, 180, 88)
DARK_GREY = QColor(120, 124, 126)
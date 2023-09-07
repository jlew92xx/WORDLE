
from MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys, os
from PyQt5.QtGui import QKeyEvent
import WordleRow
import WordleGrid, WordleBox
import asyncio
import webbrowser
from PyQt5.QtCore import Qt

CACHE_PATH = "game.txt"
PROFILE_PATH = "profile.txt"

class WordleMain(MainWindow):
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.show()
        lines = []
        if os.path.isfile(CACHE_PATH):
            file = open(CACHE_PATH, 'r')
            lines = file.readlines()
            file.close()

        if len(lines) > 0:
            # if puzzle in cache is yesterdays
            if int(lines[0]) != self.wordleGrid.getPuzzleNumber():
                self.clearCache()
                self.appendToCache(str(self.wordleGrid.getPuzzleNumber()))
            else:
                lines.pop(0)  # remove the puzzle number from the list
                self.replayTheCache(lines)

        else:
            self.appendToCache(str(self.wordleGrid.getPuzzleNumber()))
    
    def keyPressEvent(self, e: QKeyEvent) -> None:
        if not self.wordleGrid.isDone:
            keyInt = e.key()
            currGuess = self.wordleGrid.currWordleRow

            if ((keyInt >= 65 and keyInt <= 90) or (keyInt >= 97 and keyInt <= 122)):

                if (self.currCol < 4):
                    self.currCol += 1
                    currGuess.setBox(self.currCol, e.text().upper())

            elif (keyInt == self.BACK_SPACE):
                if (self.currCol > -1):

                    currGuess.setBox(self.currCol, "")

                    if (self.currCol != -2):
                        self.currCol -= 1
            elif (keyInt == self.ENTER_SUBMIT):

                submittedWord = currGuess.getWordStr()
                if (len(submittedWord) == 5):
                    if self.wordleGrid.isWord(submittedWord):
                        self.appendToCache(submittedWord)
                        dict = self.wordleGrid.evalSubmission()
                        self.keyboard.findButtonsToChangeColors(dict)
                        self.wordleGrid.isWinner = (
                            len(dict["correct"]) == 5)
                        self.wordleGrid.nextGuess()
                        if self.wordleGrid.isWinner or self.wordleGrid.getGuessCount() == 6:

                            # loop = asyncio.new_event_loop()
                            # loop.run_until_complete(self.sendDiscordMessage(
                            #     self.wordleGrid.createPuzzleResults()))
                            # loop.close()

                            self.showGameOverWindow()
                            self.wordleGrid.isDone = True
                            self.clipBoardButton.setEnabled(True)
                            self.finishButton.setEnabled(True)
                            if (self.wordleGrid.isWinner):
                                if self.wordleGrid.getGuessCount() <= 2:
                                    self.displayTempMsg(
                                        "YOU CHEATIN' SoB", "green", 3000)
                                elif self.wordleGrid.getGuessCount() > 2 and self.wordleGrid.getGuessCount() <= 4:
                                    self.displayTempMsg(
                                        "Well, you're slightly above average. BIG DEAL", "yellow", 6000)
                                else:
                                    self.displayTempMsg(
                                        "You solved it. Barely.", "lightgrey", 2000)

                            else:
                                self.displayTempMsg("Loser!", "red", 10000)
                                webbrowser.open(
                                    "https://www.youtube.com/watch?v=eNynxWZK30A")

                        self.resetCurrCol()

                    else:
                        self.displayTempMsg(
                            "\""+submittedWord+"\" is not an English word, Idiot!!!", "pink", 2000)

                else:
                    self.displayTempMsg(
                        "CAN YOU EVEN COUNT!", "pink", 2000)

            return super().keyPressEvent(e)
    
if __name__ == '__main__':
    #os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    #app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = WordleMain()
    sys.exit(app.exec())
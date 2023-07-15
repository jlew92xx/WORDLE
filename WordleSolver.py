from WordleGrid import WordleGrid
from PyQt5.QtWidgets import QApplication
import re
import sys
from wordfreq import word_frequency


class WordleSolver:

    listOfRegex = []
    listOfWords = []

    def __init__(self) -> None:
        self.grid = WordleGrid()
        for n in range(0, 5):
            self.listOfRegex.append('.')
        self.listOfWords = self.grid.buildTempList()

    def buildRegexString(self):
        output = ''

        for rg in self.listOfRegex:
            if (isinstance(rg, str)):
                if (rg.startswith("^")):
                    output = output + "[" + rg + "]"

                else:
                    output += rg

        return output

    def regrexList(self, copyListOfWords, inWord: list) -> list:
        rg = self.buildRegexString().lower()
        r = re.compile(rg)

        regex = ""
        for c in inWord:
            ch = c[0].lower()
            regex += "(?=(?:[^"+ch+"]*["+ch+"]){"+str(c[1])+",})"

        r2 = re.compile(regex)
        outputList = [s for s in copyListOfWords if r2.match(s) and r.match(s)]

        return outputList

    def setCorrectChar(self, tp: tuple):
        self.listOfRegex[tp[1]] = tp[0]

    def setInWordChars(self, tp: tuple):
        if (self.listOfRegex[tp[1]] == '.'):
            self.listOfRegex[tp[1]] = '^'+tp[0]
        elif self.listOfRegex[tp[1]].startswith('^'):
            self.listOfRegex[tp[1]] += tp[0]

        count = 0
        index = -1
        c = tp[0]
        for n in range(0, 5):
            spot = self.listOfRegex[n]
            if spot.startswith('^'):
                if not c in spot:
                    index = n
                    count += 1

        if count == 1:
            self.listOfRegex[index] = c

    def setIncorrectChars(self, tp):
        for x in range(0, 5):
            if self.listOfRegex[x] == '.':
                self.listOfRegex[x] = '^'+tp[0]
            elif self.listOfRegex[x].startswith('^'):
                self.listOfRegex[x] += tp[0]

    def wordFreakAnalysis(self, listOfWordsCopy) -> str:
        output = "aaaaa"
        if len(listOfWordsCopy) != 0:
            output = listOfWordsCopy[0]
            for word in listOfWordsCopy[1:]:
                if (word_frequency(output, 'en') < word_frequency(word, 'en')):

                    output = word

        return output

    def reset(self):
        self.listOfRegex = []
        for n in range(0, 5):
            self.listOfRegex.append('.')
        self.grid.reset()

    '''
    Return list of tuples first is the letter and 2nd is the count
    '''

    def countByLetter(self, listIn: list) -> list:
        output = []
        for tup in listIn:
            c = tup[0]
            # check if it's in the list.
            i = 0
            needsToBeAppended = True
            for cc in output:
                if cc[0] == c:
                    output[i] = (c, cc[1] + 1)
                    needsToBeAppended = False
                    break
                i += 1
            if needsToBeAppended:
                output.append((c, 1))

        return output

    def solve(self, firstGuess: str):

        currGuess = firstGuess.upper()

        listOfWordsCopy = self.listOfWords.copy()
        while (not (self.grid.isDone or self.grid.isWinner)):

            print(currGuess)
            self.grid.currWordleRow.quickSet(currGuess)
            dict = self.grid.evalSubmission2()
            correctList = dict["correct"]
            inWordList = dict["inword"]
            incorrectList = dict["incorrect"]

            self.grid.isWinner = (len(correctList) == 5)
            self.grid.nextGuess()
            if (self.grid.isWinner):
                break
            for tp in correctList:
                self.setCorrectChar(tp)
            # I need to add any duplicates when one's yellow and one is incorrect
            listAdd = []
            for inc in incorrectList:
                for inw in inWordList:
                    if inc[0] == inw[0]:
                        try:
                            listAdd.append(incorrectList.pop(
                                incorrectList.index(inc)))
                        except:
                            pass

            tempInWord = inWordList + listAdd

            for tp in incorrectList:
                self.setIncorrectChars(tp)

            for tp in tempInWord:
                self.setInWordChars(tp)

            listCount = self.countByLetter(inWordList + correctList)
            listOfWordsCopy = self.regrexList(listOfWordsCopy, listCount)

            self.grid.isDone = (self.grid.getGuessCount() == 6)
            currGuess = self.wordFreakAnalysis(listOfWordsCopy).upper()

        # print(self.grid.createPuzzleResults())

    def bestFirstGuess(self):
        wordbank = self.grid.getWordBank()
        guessbank = self.listOfWords
        output = "clomp"
        outputCountWrong = 23

        for guess in guessbank[(2314 + 10195):]:
            count = 0
            for word in wordbank:
                self.grid.setWordOfTheDay(word)
                self.solve(guess)
                if not self.grid.isWinner:
                    count += 1
                self.reset()
                if count > outputCountWrong:
                    break
            if count < outputCountWrong:
                outputCountWrong = count
                output = guess
                print(output + " " + str(outputCountWrong))

        print("The word, " + output + " is your best first guess with " +
              outputCountWrong + " failures")

        return output


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ws = WordleSolver()
    # ws.bestFirstGuess()
    ws.grid.setWordOfTheDay("BRUTE")
    ws.solve("ariel")
    print(ws.grid.createPuzzleResults())

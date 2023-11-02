import asyncio
from WordleGrid import WordleGrid
from PyQt5.QtWidgets import QApplication
import re
from datetime import datetime, timedelta
import sys
from wordfreq import zipf_frequency
import time
from discord import Webhook
import asyncio
import aiohttp
from collections import Counter
from itertools import chain
import csv

HOUR = 7
secondsInDay = 86400


class WordleSolver:

    listOfRegex = []
    listOfWords = []
    secondsOfSleep = 0

    def __init__(self, grid) -> None:
        self.getTimeSleep()
        # self.secondsOfSleep = 5
        
        for n in range(0, 5):
            self.listOfRegex.append('.')
            self.grid = grid
        self.listOfWords = self.grid.buildTempList()
        letterCount = Counter(chain.from_iterable(self.listOfWords))
        self.letterFreq = {
            character: value / sum(letterCount.values())
            for character, value in letterCount.items()
        }
        print(self.letterFreq)

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

    def calcWordLetterDiversityScore(self, word):
        score = 0.0
        attempt = self.grid.getGuessCount()
        for char in word:
            score += self.letterFreq[char]

        score /= (5 - len(set(word)) + 1)
        freq = zipf_frequency(word, "en")/100
        score = score / (attempt)
        freq *= (attempt)
        score += freq
        return score

    def wordFreakAnalysis(self, listOfWordsCopy) -> str:
        output = "aaaaa"
        if len(listOfWordsCopy) != 0:
            output = listOfWordsCopy[0]
            outputScore = self.calcWordLetterDiversityScore(output)
            for word in listOfWordsCopy[1:]:
                wordScore = self.calcWordLetterDiversityScore(word)
                if (outputScore < wordScore):

                    output = word
                    outputScore = wordScore

        return output

    def reset(self, ):
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

    def solve(self):

        currGuess = self.chooseFirstGuess().upper()

        listOfWordsCopy = self.listOfWords.copy()
        while (not (self.grid.isDone or self.grid.isWinner)):

            print(currGuess)
            self.grid.currWordleRow.quickSet(currGuess)
            dict = self.grid.evalSubmission()
            correctList = dict["correct"]
            inWordList = dict["inword"] + dict["inwordred"] + dict["inwordorange"]
            incorrectList = dict["incorrect"]

            self.grid.isWinner = (len(correctList) == 5)
            self.grid.nextGuess()
            self.grid.isDone = (self.grid.getGuessCount() == 6)
            if (self.grid.isWinner or self.grid.isDone):
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

            currGuess = self.wordFreakAnalysis(listOfWordsCopy).upper()

        print(self.grid.createPuzzleResults())

    def bestFirstGuess(self):
        guessbank = self.listOfWords
        scores = []
        for guess in guessbank:
            rowDict = {}
            rowDict['word'] = guess
            rowDict['score'] = self.calcWordLetterDiversityScore(guess)
            scores.append(rowDict)
        field_names = ['word', 'score']
        with open('scores.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(scores)

    def chooseFirstGuess(self):
        with open("firstGuest.txt") as fg:
            tempList = fg.read().splitlines()
        hashInt = self.grid.hashCurrDate()
        n = len(tempList)
        output = tempList[hashInt % n]
        return output

    def getTimeSleep(self):
        currTime = datetime.now()
        if (currTime.hour < HOUR):
            time = datetime(currTime.year, currTime.month,
                            currTime.day, HOUR, 0, 0, 0)
            self.secondsOfSleep = (time - currTime).total_seconds()
            print(self.secondsOfSleep)
        elif (currTime.hour == HOUR and currTime.minute == 0):
            self.secondsOfSleep = 0

        else:
            tommorowAt7 = currTime + timedelta(1)
            tommorowAt7 = tommorowAt7.replace(
                hour=HOUR, minute=0, second=0, microsecond=0)
            self.secondsOfSleep = (tommorowAt7 - currTime).total_seconds()
            print(self.secondsOfSleep)

    async def sendDiscordMessage(self, msg):
        async with aiohttp.ClientSession() as session:
            webHook = Webhook.from_url(
                "https://discord.com/api/webhooks/1127398517942517791/VVTL1nHMkN4virf0BTX3QrOWb3OXLJvZyLCjmXZ6ltt_Nbcdfg-5ld1iubGhEHsoPyoB", session=session)
            await webHook.send("WordBot's results 🤖:\n"+msg)

    def getBotResults(self):
        return self.grid.createPuzzleResults();
    
    def postScoreLoop(self):
        while (True):
            time.sleep(self.secondsOfSleep)
            self.grid.pickWordForTheDay()
            self.solve()
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.sendDiscordMessage(
                self.grid.createPuzzleResults()))
            loop.close()
            self.reset()
            self.secondsOfSleep = secondsInDay-.02


if __name__ == '__main__':
    app = QApplication(sys.argv)
    grid = WordleGrid()
    ws = WordleSolver(grid)

    ws.solve()

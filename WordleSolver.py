from WordleGrid import WordleGrid
from PyQt5.QtWidgets import QApplication
import re, sys
from wordfreq import word_frequency
class WordleSolver:
    app = QApplication(sys.argv)
    grid = WordleGrid()
    listOfRegex = []
    listOfWords = []
    rejects = []
    def __init__(self) -> None:
        
        for n in range(0, 5):
            self.listOfRegex.append('.')
        self.listOfWords = self.grid.buildTempList()

    def buildRegexString(self):
        output = ''

        for rg in self.listOfRegex:
            if(isinstance(rg, str)):
                if(rg.startswith("^")):
                    output = output +"[" + rg + "]"
                
                else:
                    output += rg

        return output



    def regrexList(self, copyListOfWords, inWord:list) -> list:
        rg = self.buildRegexString().lower()
        r = re.compile(rg)
        outputList = [s for s in copyListOfWords if r.match(s)]
        regex = ""
        for c in inWord:
            ch = c[0].lower()
            regex += "(?=(?:[^"+ch+"]*["+ch+"]){"+str(c[1])+",})"
        
        r2 = re.compile(regex)
        outputList = [s for s in outputList if r2.match(s)]

        return outputList




    def setCorrectChar(self, tp:tuple):
        self.listOfRegex[tp[1]] = tp [0]

    def setInWordChars(self, tp:tuple):
        if(self.listOfRegex[tp[1]] == '.'):
            self.listOfRegex[tp[1]] = '^'+tp [0]
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
    '''
    Return list of tuples first is the letter and 2nd is the count
    '''
    def countByLetter(self, listIn:list)->list:
        output = []
        for tup in listIn:
            c = tup[0]
            #check if it's in the list.
            i = 0
            needsToBeAppended =True
            for cc in output:
                if cc[0] == c:
                    output[i] =(c, cc[1] + 1)
                    needsToBeAppended = False
                    break
                i += 1
            if needsToBeAppended:
                output.append((c, 1))

        return output


    def solve(self):
        ws.grid.setWordOfTheDay("eerie")
        currGuess = "SALET"
        
        listOfWordsCopy = self.listOfWords.copy()
        while(not (self.grid.isDone or  self.grid.isWinner)):
            
            print(currGuess)
            self.grid.currWordleRow.quickSet(currGuess)
            dict = self.grid.evalSubmission2()
            
            self.grid.isWinner = (len(dict["correct"]) == 5)
            self.grid.nextGuess()
            if(self.grid.isWinner):
                break
            for tp in dict["correct"]:
                self.setCorrectChar(tp)
            #I need to add any duplicates when one's yellow and one is incorrect    
            listAdd = []
            for inc in dict["incorrect"]:
                for inw in dict["inword"]:
                    if inc[0] == inw [0]:
                        listAdd.append(dict["incorrect"].pop(dict["incorrect"].index(inc)))

            tempInWord = dict["inword"] + listAdd

            for tp in dict["incorrect"]:
                self.setIncorrectChars(tp)

            for tp in tempInWord:
                self.setInWordChars(tp)

            listCount = self.countByLetter(dict["inword"] + dict["correct"])
            listOfWordsCopy = self.regrexList(listOfWordsCopy, listCount)
            
            self.grid.isDone = (self.grid.getGuessCount() == 6)
            currGuess = self.wordFreakAnalysis(listOfWordsCopy).upper()
            
            

        print(self.grid.createPuzzleResults())

if __name__ == '__main__':
    
    ws = WordleSolver()
    ws.solve()

from enums import Status
import WordleConfigure
class WordleGame():



    def __init__(self, name, wod, isFirstGame) -> None:
        self.guesses = []
        self.keyboard = {}
        self.isDone = False
        self.isWinner = False
        self.isFirstGame = isFirstGame
        self.name = name
        self.wod = wod
        self.guessNumber = 0
        
    def replay(self, words:list):
        for word in words:
            word = word.strip()
            if word == "":
                return
            self.eval(word)
            
    def eval(self, input):
        #at this point we know that the word is a correct-lettered actual word.
        self.guessNumber += 1
        output = []
        for i in range(0,len(input)):
            output.append(0)
        
        i = 0
        correctCount = 0 
        tempWod = list(self.wod)
        for iL in input:

            if(iL == self.wod[i]):
                output[i] = (iL, Status.CORRECT)
                self.keyboard[iL] = Status.CORRECT
                tempWod[i] = "@"
                correctCount += 1
            i += 1
        
        if(correctCount == WordleConfigure.WORDSIZE):
            self.isDone = True
            self.isWinner = True
            self.guesses.append(output) 
            return
        
        i = 0
        
        for o in output:
            if o == 0:
                c = input[i]
                if c in tempWod:
                    output[i] = (input[i], Status.INWORD)
                    tempWod[tempWod.index(c)] = "@"
                    #we do not want to override a green keyboard key
                    if (not c in self.keyboard.keys()):
                        self.keyboard[c] = Status.INWORD
                        
                else:
                    output[i] = (c, Status.INCORRECT)
                    #we do not want to override a green or yellow keyboard key
                    if (not c in self.keyboard.keys()):
                        self.keyboard[c] = Status.INCORRECT
            i += 1
        if(self.guessNumber == WordleConfigure.NUMOFGUESS):
            self.isDone = True
        self.guesses.append(output)    
    
    def createPuzzleResults(self, puzzleNumber) -> str:
        if (self.isWinner):
            s = str(self.guessNumber)
        else:
            s = "⛈️"
        output = "JL's Wordle " + str(puzzleNumber) + " " + s + "/" + str(WordleConfigure.NUMOFGUESS) + 2 * "\n"
        for guess in self.guesses:
                
            for X in guess:
                status = X[1]
                if (status is Status.CORRECT):
                    output += "🟩"

                elif (status is Status.INWORD):
                    output += "🟨"

                elif (status is Status.INCORRECT):
                    output += "⬜"

                else:
                    break
            output += "\n"

        return output.rstrip()      
    
    
if __name__ == '__main__':
     game = WordleGame("jayloo92", "EERIE")

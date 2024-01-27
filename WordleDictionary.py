import hashlib

WoDCANDIDATESPATH = "Wordle-La.txt"
GUESSCANDIDATESPATH = "Wordle-Ta.txt"
class WordleDictionary():
    
    
    def __init__(self, salt) -> None:
        self.wodCandidates = []
        self.wordBankDict = {}
        self.salt = salt
        self.buildWodCandidates()
        self.buildWordBankDict()
        
    
    def pickWordForTheDay(self, date:str):
        numFiveLetterWords = len(self.wodCandidates)
        s = date + self.salt
        number = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16)
        return self.wodCandidates[number % numFiveLetterWords].upper()
        
    def isWord(self, word:str) -> bool:
        key = word[:2].lower()
        output = False
        if key in self.wordBankDict.keys():
            lis = self.wordBankDict[key]
            output = word.lower() in lis
        return output
    
    
    def buildWodCandidates(self):
        with open(WoDCANDIDATESPATH) as wb:
                self.wodCandidates = wb.read().splitlines()
                
    def buildWordBankDict(self):
        tempList = self.buildTempList()
        
        for word in tempList:
            k = word[:2]

            if k not in self.wordBankDict.keys():
                self.wordBankDict[k] = [word]
            else:
                if isinstance(self.wordBankDict[k], list):
                    self.wordBankDict[k].append(word)
                    
                        
    def buildTempList(self):
        with open(GUESSCANDIDATESPATH) as gb:
            tempList = self.wodCandidates + gb.read().splitlines()
        return tempList   
    
    


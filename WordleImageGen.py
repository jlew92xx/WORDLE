from PIL import Image, ImageDraw, ImageFont
from WordleGame import WordleGame
import WordleConfigure
from enums import Status
SQUARE_SIDE_SIZE = 50 * 2
GAP = 5 *2
TOP_LEFTX = 12 * 2
TOP_LEFTY = 40 * 2
keyWidth = 49
keyHeight = 70

size = (300*2, 1030)
correctColor = (106, 170, 100)
inWordColor = (201, 180, 88)
incorrectColor = (120, 124, 126)
unknownColor =   (211, 214, 218)

FIRST_ROW = "qwertyuiop".upper()
SECOND_ROW = "asdfghjkl".upper()
THIRD_ROW = "zxcvbnm".upper()

class WordleImage():
    outputImage = None
    draw = None
    
    def drawWordleGame(self, filename:str, game:WordleGame, isResend:bool):
        wordleResults = game.guesses
        self.outputImage = Image.new('RGB', size, "black")
        self.draw = ImageDraw.Draw(self.outputImage)
        
        
        currLx = TOP_LEFTX
        currLy = TOP_LEFTY
        
        self.draw.text(
                (currLx + 1.75*(SQUARE_SIDE_SIZE), currLy - 60), 
                "WORDLE", 
                fill='white',
                font= ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 50, encoding="unic"),
                align='center',
                stroke_width = 1,
                stroke_fill='white'
            )

        for row in wordleResults:
            for square in row:
                color = None
                c = square[0] #the charater of the square
                status = square[1]
                if status == Status.CORRECT:
                    color = (106, 170, 100)
                elif status == Status.INWORD:
                    color = (201, 180, 88)
                elif status == Status.INCORRECT:
                    color = (120, 124, 126)
                
                xy = [(currLx, currLy), (currLx + SQUARE_SIDE_SIZE, currLy + SQUARE_SIDE_SIZE)]    
                self.drawWordleSquare(xy, color, c)
                currLx += (SQUARE_SIDE_SIZE + GAP)
                
            currLx = TOP_LEFTX
            
            currLy += (SQUARE_SIDE_SIZE + GAP)
            
        
        #now do the the blank squares
        numBlankRows = WordleConfigure.NUMOFGUESS - game.guessNumber
        for row in range(numBlankRows):
            for square in range(WordleConfigure.WORDSIZE):
                xy = [(currLx, currLy), (currLx + SQUARE_SIDE_SIZE, currLy + SQUARE_SIDE_SIZE)] 
                self. drawWordleSquare(xy, unknownColor, "")
                currLx += (SQUARE_SIDE_SIZE + GAP)
                
            currLx = TOP_LEFTX
           
            currLy += (SQUARE_SIDE_SIZE + GAP)
            
        currLy += (10)
        if(not game.isDone and isResend):
            self.draw.text(
                (currLx + 1.25*(SQUARE_SIDE_SIZE), currLy), 
                "Not in Word List", 
                fill='yellow',
                font= ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 30, encoding="unic"),
                align='center',
                stroke_width = 1,
                stroke_fill='yellow'
            )
        elif(not game.isWinner and game.isDone):
            
            self.draw.text(
                (currLx + 2.25*(SQUARE_SIDE_SIZE), currLy), 
                game.wod, 
                fill='white',
                font= ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 30, encoding="unic"),
                align='center',
                stroke_width = 1,
                stroke_fill='red'
            )
        
        currLy += (40)
        #first row
        gameKeyBoard = game.keyboard
        
        keyGap = 5
        for c in FIRST_ROW:
            color = unknownColor
            if(c in gameKeyBoard.keys()):
               if(gameKeyBoard[c]  == Status.CORRECT):
                   color = correctColor
               elif(gameKeyBoard[c]  == Status.INWORD):
                   color = inWordColor
               elif(gameKeyBoard[c]  == Status.INCORRECT):
                   color = incorrectColor
                   
            xy = [(currLx, currLy),(currLx + keyWidth, currLy + keyHeight)]
            self.drawKeySquare(xy, color, c)
            currLx += (keyWidth + keyGap)
            
            
        currLx = TOP_LEFTX + .5*keyWidth
        currLy += keyHeight + keyGap
            
        for c in SECOND_ROW:
            color = unknownColor
            if(c in gameKeyBoard.keys()):
               if(gameKeyBoard[c]  == Status.CORRECT):
                   color = correctColor
               elif(gameKeyBoard[c]  == Status.INWORD):
                   color = inWordColor
               elif(gameKeyBoard[c]  == Status.INCORRECT):
                   color = incorrectColor
                   
            xy = [(currLx, currLy),(currLx + keyWidth, currLy + keyHeight)]
            self.drawKeySquare(xy, color, c)
            currLx += (keyWidth + keyGap)
        
        currLx = TOP_LEFTX + 1.5*keyWidth
        currLy += keyHeight +keyGap
        
        for c in THIRD_ROW:
            color = unknownColor
            if(c in gameKeyBoard.keys()):
               if(gameKeyBoard[c]  == Status.CORRECT):
                   color = correctColor
               elif(gameKeyBoard[c]  == Status.INWORD):
                   color = inWordColor
               elif(gameKeyBoard[c]  == Status.INCORRECT):
                   color = incorrectColor
                   
            xy = [(currLx, currLy),(currLx + keyWidth, currLy + keyHeight)]
            self.drawKeySquare(xy, color, c)
            currLx += (keyWidth + keyGap)       
        self.outputImage.save(filename)

    
    



    
    
    
    def drawWordleSquare(self, xy, color, c):
        self.draw.rectangle(
            xy, 
            fill=color, 
            outline='black',
        )
        
        self.draw.text(
            (xy[0][0] + 20, xy[0][1]), 
            c, 
            fill='white',
            font= ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 50 *2, encoding="unic"),
            align='center',
            stroke_width = 1,
            stroke_fill= 'white'
        )
    
    def drawKeySquare(self, xy, color, c):
        self.draw.rounded_rectangle(xy, fill=color, outline="black", width=3, radius=7)
        fontColor = "white"
        if(color == unknownColor):
            fontColor = "black"
        
        self.draw.text(
            (xy[0][0] + 8.5, xy[0][1] + 8.8), 
            c, 
            fill= fontColor,
            font= ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 25 *2, encoding="unic"),
            align='center',
            stroke_width = 1,
            stroke_fill= fontColor
        )

# Save the customized image
if __name__ == '__main__':
    wordGen  = WordleImage()
    game = WordleGame("bill", "jaunt", False)
    
    game.eval("ARIEL")
    game.eval("FARTS")
    game.eval("TASTY")
    wordGen.drawWordleGame("jlewis.jpg", game, True)
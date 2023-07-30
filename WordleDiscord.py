import discord
from discord.ext.commands import Bot
import sys, os, glob
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import ChatBot
import Ults
from datetime import datetime, timedelta
from pathlib import Path
import threading

HOUR = 0
FILEPREFIX = "TEMP"
TOKEN = "MTEyNzM0Mjk4MzYyNTMyNjYxMg.GfWMk1."
TOKEN += "1jHNWvWdnw_l-AvVA9gYh8DwvlKGNKWL0N5ghQ"
class DiscordGameBot:
    lastPictureMsg = {}
    mainwindow = None
    unlocked = True
    
    def __init__(self, app) -> None:
        self.client = discord.Client(intents= discord.Intents.default())
        self.mainwindow = MainWindow()
        self.Today = None
        # self.secondsToTomorrow = Ults.getTimeSleep(HOUR)
        # resetThread = threading.Thread(target=self.resetRoutine)
        # resetThread.daemon = True
        # resetThread.start()
        
        self.app = app
        
        self.startDiscord()
        

    def resetRoutine(self):


        for filename in glob.glob("./" + FILEPREFIX + "*"):
            os.remove(filename) 
        lastPictureMsg = {}
        self.mainwindow.wordleGrid.pickWordForTheDay()
        #self.secondsToTomorrow = 86400 # how many seconds there are in a day.
            
    
    def startDiscord(self):

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is now running')
            self.Today = datetime.today().date()
            
        @self.client.event
        async def on_message(message ):

                
            channelType = message.channel.type.name
            if channelType == 'text':
                return
            if message.author.bot:
                if message.attachments:
                    userNameFile = Path(message.attachments[0].filename).with_suffix('').name
                    try:
                        lastPicMsg = await message.channel.fetch_message(self.lastPictureMsg[userNameFile])
                        await lastPicMsg.delete()
                    except:
                        pass
                    self.lastPictureMsg[userNameFile] = message.id
                return
            
            msgDate =message.created_at - timedelta(hours=5)
            if(msgDate.date() != self.Today):
                self.Today = msgDate.date()
                self.resetRoutine()
                
            username = str(message.author)
            userMessage = str(message.content).lower()
            channel = str(message.channel)
            
            
            print(f"{username} said '{userMessage}' {(channel)}")
            filename = self.mainwindow.createFileName(username)
            if(not os.path.isfile(filename)):
                if userMessage == "play":
                    
                    with open(filename, 'w') as f:
                        pass
                    
                    await message.author.send("I'm ready when you are! Start feeding me 5 letter words.")
                else:
                    await message.author.send("You're currently not playing a game. Just send \"play\" to begin")
            else:
                
                
                file = open(filename, 'r')
                lines = file.readlines()
                file.close()
                
                
                isDone = False
                if(not len(lines) == 0):
                    if(lines[-1].rstrip() == "done"):
                        isDone = True
                if (not isDone):
                    if(len(userMessage) == 5):
                        submittedWord = userMessage.upper().rstrip()
                        if(self.mainwindow.isWord(submittedWord)):
                            file = open(filename, 'a')
                            file.write(submittedWord.rstrip() + '\n')
                            file.close
                            self.mainwindow.reset()
                            self.app.processEvents()
                            while (True):
                                if(self.unlocked):
                                    self.unlocked = False
                                    self.mainwindow.replayTheCache(lines)
                                    self.mainwindow.submitOneWord(submittedWord)
                                    self.app.processEvents()
                                    time.sleep(.1)
                                    self.unlocked = True
                                    await self.captureScreenShotAndSend(message, username)

                                    break
                                else:
                                    time.sleep(.13)
   
                            if(self.mainwindow.isDone()):
                                wod = self.mainwindow.wordleGrid.wordOfTheDay
                                
                                file = open(filename, 'a')
                                file.write("done" + '\n')
                                file.close
                                try:
                                    self.mainwindow.setName2(username)
                                    msg = self.mainwindow.createPuzzleResults()
                                    if(username != "jayloo92#7867"):
                                        await self.mainwindow.sendDiscordMessage(msg)
                                except:
                                    pass
                                

                                eogMsg = ""
                                lines.append(submittedWord)
                                guessesCommas = ", ".join(lines) 
                                if(self.mainwindow.isWinner()):
                                    guessCount = self.mainwindow.wordleGrid.getGuessCount()
                                    prompt = ""
                                    if guessCount <= 3:
                                        prompt = username +" won today's Wordle game with " + str(guessCount) +" guesses. Congratulate them in the style of GLaDOS. The word of the day was "+ wod
                                         
                                    elif(guessCount > 3 and guessCount < 5):
                                        prompt = username +" just did an average in today's Wordle with" + str(guessCount) +" guesses. Congratulate them in the style of GLaDOS. The word of the day was "+ wod
                                        
                                    else:
                                        prompt = username +" barely won today's Wordle with " + str(guessCount) + "'Congratulate' them in the style of GLaDOS. The word of the day is "+ wod
                                    
                                else:
                                    prompt = "Mercilessly mock "+username +" for losing today's wordle when the word of the day is " + wod +". Do it in the style of GLaDOS"
                                
                                eogMsg = ChatBot.giveResponse(prompt+ ". Your name is WordBot.")
                                await message.author.send(eogMsg)
                                print(eogMsg +"Msg")
                            



                            
                        else:
                            msgWrong = ChatBot.giveResponse("The user is playing Wordle and just submitted the 'word'," + submittedWord + "that's not a word. You, WordBot, need to tell them this in the style of Glados in one sentence.")
                            await message.author.send(msgWrong)
                    
                    else:
                        await message.author.send("Learn how to count!")
                
            

                     
                else:
                    await message.author.send("You're done! Leave me alone!")
            
                self.mainwindow.reset()
                self.app.processEvents()                  
                


        self.client.run(TOKEN)
    
    async def postScores(self):
        channel = Bot.get_channel(1127398485369557092)

    def appendToCache(self, word, fileName):
        file = open(fileName, "a")
        file.write(word + "\n")
        file.close()
    
    def setMainWindow(self, mw):
        self.mainwindow = mw
        
    async def captureScreenShotAndSend(self, message, userName):

        screen = QtWidgets.QApplication.primaryScreen()
        screenShot = screen.grabWindow(self.mainwindow.winId())
        fileName = userName +".jpg"
        screenShot.save(fileName, 'jpg')
        
        try:
            await message.author.send("",file = discord.File(fileName))
            
        except  Exception as e:
            time.sleep(.1)
            

    async def receiveMessage(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app
    x = DiscordGameBot(app)
    


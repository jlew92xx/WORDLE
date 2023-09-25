import discord
from discord.ext.commands import Bot
import sys, os, glob
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import ChatBot
import math
from datetime import datetime, timedelta
from pathlib import Path
from WordleSQL import WordleSQL
from WordleSolver import WordleSolver

import threading

HOUR = 0
FILEPREFIX = "TEMP"
TOKEN = """MTEyNzM0Mjk4MzYyNTMyNjYxMg.GPrx0o.5lg86UIW0QkItot_kgIPP-pwZ5l59FunVutbBU"""

guildId = 1127338015249944596
todaysWordlers = 'todays-wordlers'
class DiscordGameBot:
    lastPictureMsg = {}
    mainwindow = None
    unlocked = True
    playStat = WordleSQL()
    
    
    def __init__(self, app) -> None:
        intents = discord.Intents.default()
        intents.members = True
        self.client = discord.Client(intents= intents)
        app = QApplication(sys.argv)
        self.mainwindow = MainWindow()
        self.solver = WordleSolver(self.mainwindow.wordleGrid)
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
        self.lastPictureMsg = {}
        

        self.mainwindow.wordleGrid.pickWordForTheDay()
        #self.secondsToTomorrow = 86400 # how many seconds there are in a day.
            
    
    def startDiscord(self):

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is now running')
            self.Today = datetime.today().date()


        @self.client.event
        async def on_member_join(member: discord.Member):
            name = member.name
            prompt = f"""Write a welcome message for {member.name} to my wordle discord server named Weer Wolerr. 
            Tell them they can play your wordle by sending you the message \"play\". Tell they can also change your personality by sending you a message
            with an exclamation point followed by person \"=\" and their desired personality.\
            For example, if they want you to respond to their wordle score as a kawaii girl, they would send you \"!person = kawaii girl\" They can also post 
            their New York Times Wordle in the nyt-wordle channel but you think that's an inferior wordle. Tell them to behave and be nice to the other wordlers.
            """
           
            msg = ChatBot.giveResponse(prompt+ ".")
            print(msg)
            await member.send(msg)
            
        
        @self.client.event
        async def on_message(message):

                
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
            
            msgDate = message.created_at - timedelta(hours=5)

            if(msgDate.date() != self.Today):
                self.Today = msgDate.date()
                self.playStat.dailyReset()
                self.resetRoutine()
                
                
                self.solver.reset()
                self.solver.grid = self.mainwindow.wordleGrid  
                self.solver.solve()
                
                await self.solver.sendDiscordMessage(self.solver.getBotResults())
                
                
                
                
            username = str(message.author)
            userMessage = str(message.content)
            channel = str(message.channel)
            print(f"{username} said '{userMessage}' {(channel)}")
            self.playStat.insertPlayer(username)
            if(userMessage.startswith('!')):
                userMessage = userMessage.replace("!", "")
                command = userMessage.split("=")
                if(len(command) == 2):
                    commandWord = command[0].lower().strip()
                    paramWord = command[1].strip()
                    
                    if commandWord == "person":
                        self.playStat.setPrompt(username, paramWord)
                        await message.author.send("Your personality has been set.")
                    elif commandWord == "hardmode":
                        paramWord = paramWord.lower()
                        if paramWord == "on":

                            self.playStat.setHardMode(1, username)
                            await message.author.send("Hardmode is on")
                        elif paramWord == "off":
                            
                            await message.author.send("Hardmode is off")
                            self.playStat.setHardMode(0, username)
                        else:
                            await message.author.send("Invalid option: say \"on\" or \"off\"")
                            
                    else:
                        await message.author.send("Invalid Command.")
                else:
                    await message.author.send("Invalid Command.")
                    
                    
                return
            userMessage = userMessage.lower()
            
            filename = self.mainwindow.createFileName(username)
            if(not os.path.isfile(filename)):
                if userMessage == "play":
                    self.playStat.insertPlayer(username)
                    with open(filename, 'w') as f:
                        pass
                    introPrompt = "In a short single sentence, tell " + username + " that you are for them to send you five letter words for their Wordle game in the style of " + self.playStat.getPrompt(username)
                    introMsg = ChatBot.giveResponse(introPrompt+ ".")
                    print(introMsg)
                    await message.author.send(introMsg)
                else:
                    await message.author.send("You're currently not playing a game. Just send \"play\" to begin")
            else:
                
                
                file = open(filename, 'r')
                lines = file.readlines()
                file.close()
                wod = self.mainwindow.wordleGrid.wordOfTheDay
                
                isDone = False
                if(not len(lines) == 0):
                    if(lines[-1].rstrip() == "done" or len(lines) > 6):
                        isDone = True
                if (not isDone):
                    if(len(userMessage) == 5):
                        submittedWord = userMessage.upper().rstrip()
                        if(self.mainwindow.isWord(submittedWord)):

                            self.mainwindow.reset()
                            isHardmodeOn = self.playStat.getHardmode(username)
                            self.mainwindow.setHardmode(isHardmodeOn)
                            self.app.processEvents()
                            while (True):
                                print( username + " "+str(datetime.now().second)+ "\n")
                                if(self.unlocked):
                                    self.unlocked = False
                                    self.mainwindow.replayTheCache(lines)
                                    if not isHardmodeOn or self.mainwindow.isHardmodeCompliant(submittedWord):
                                        file = open(filename, 'a')
                                        file.write(submittedWord.rstrip() + '\n')
                                        file.close()
                                        self.mainwindow.submitOneWord(submittedWord)

                                        self.app.processEvents()
                                        
                                        self.unlocked = True
                                        filenamePic = username + ".jpg"
                                        self.captureScreenShot(filenamePic)
                                        try:
                                            await message.author.send("",file = discord.File(filenamePic))
                                            print(username +" Message sent at " + str(datetime.now()))
                                            break
                                        except  Exception as e:
                                            time.sleep(.1)
                                            print("failed to send.")
                                    else:
                                        msgWrong = "You're in HARDMODE!"
                                        self.unlocked = True
                                        await message.author.send(msgWrong)
                                        await message.author.send("",file = discord.File(username + ".jpg"))
                                        return
                                else:
                                    print("This section code is locked")
                                    time.sleep(.13)
   
                            if(self.mainwindow.isDone()):
                                
                                
                                file = open(filename, 'a')
                                file.write("done" + '\n')
                                file.close
                                try:
                                    self.mainwindow.setName2(username)
                                    msg = self.mainwindow.createPuzzleResults()
                                    if(username != "jayloo92test"):
                                        await self.mainwindow.sendDiscordMessage(msg)
                                    else:
                                        print(msg)
                                except:
                                    pass
                                

                                eogMsg = ""
                                lines.append(submittedWord)
                                guessesCommas = ", ".join(lines)
                                self.playStat.updateAfterGame(username, self.mainwindow.isWinner(), self.mainwindow.wordleGrid.getGuessCount())
                                person = self.playStat.getPrompt(username)
                                if(self.mainwindow.isWinner()):
                                    guessCount = self.mainwindow.wordleGrid.getGuessCount()
                                    prompt = ""
                                    
                                    if guessCount <= 3:
                                        prompt = username +" won today's Wordle game with " + str(guessCount) +" guesses. In less than 2000 characters, Congratulate them in the style of " + person + ". The word of the day was "+ wod + ". Their guess were " + guessesCommas
                                         
                                    elif(guessCount > 3 and guessCount < 5):
                                        prompt = username +" just did an average in today's Wordle with" + str(guessCount) +" guesses. In less than 2000 characters, Congratulate them in the style of " + person + ". The word of the day was "+ wod +". Their guess were " + guessesCommas
                                        
                                    else:
                                        prompt = username +" barely won today's Wordle with " + str(guessCount) + "In less than 2000 characters,'Congratulate' them in the style of " + person + ". The word of the day is "+ wod +". Their guess were " + guessesCommas
                                    
                                else:
                                    prompt = "In less than 2000 characters, Mercilessly mock "+username +" for losing today's wordle when the word of the day is " + wod +". Do it in the style of" + person + ""
                                
                                eogMsg = ChatBot.giveResponse(prompt+ ".")
                                print(eogMsg)
                                lenMsg = len(eogMsg)
                                if(lenMsg < 2000):
                                    await message.author.send(eogMsg)
                                else:
                                    total = 0
                                    limit = 2000
                                    sending = ""
                                    listMsg = eogMsg.split('\n')
                                    total = 0
                                    for line in listMsg:
                                        if total + len(line) > limit:
                                          await message.author.send(sending[:-1])
                                          total = len(line)
                                          sending = line + "\n"
                                        else:
                                            total += len(line)
                                            sending += line + "\n"
                                            
                                    await message.author.send(sending[:-1]) 
                                    
                                    
                                
                                    
                                    
                                    
                            



                            
                        else:
                            
                            msgWrong = "Not in the word database!"
                                
                            await message.author.send(msgWrong)
                            await message.author.send("",file = discord.File(username + ".jpg"))
                    
                    else:
                        await message.author.send("Learn how to count!")
                        await message.author.send("",file = discord.File(username + ".jpg"))
            

                     
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
        
    def captureScreenShot(self, fileName):

        screen = QtWidgets.QApplication.primaryScreen()
        screenShot = screen.grabWindow(self.mainwindow.winId())
        screenShot.save(fileName, 'jpg')
        

            

    async def receiveMessage(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app
    x = DiscordGameBot(app)
    


import discord
from discord.ext import tasks
from discord.ext.commands import Bot
import sys, os, glob
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import ChatBot
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from WordleSQL import WordleSQL
from WordleSolver import WordleSolver
from WordleGame import WordleGame
#import schedule
TESTACCOUNT = "jayloo92test"
HOUR = 0
FILEPREFIX = "TEMP"
tokenFile = open("DiscordKey.txt", 'r')
token = tokenFile.readlines()
print(token)
tokenFile.close()
TOKEN = token[0]


def seconds_until_time(hours, minutes):
    now = datetime.now()
    det = 0
    target = ((now + timedelta(days = det)).replace(hour = hours, minute=minutes, second=0))
    diff =(target - now).total_seconds()
    if diff < 0:
        diff += 3600
    return diff



guildId = 1127338015249944596
todaysWordlers = 'todays-wordlers'
class DiscordGameBot:
    lastPictureMsg = {}
    currGames = {}
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
        self.todaysPuzzleNumber = self.mainwindow.wordleGrid.getPuzzleNumber()
        self.puzzleFinishers = {}
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
        

        
        #self.secondsToTomorrow = 86400 # how many seconds there are in a day.
            
    @tasks.loop(seconds=1)
    async def dailyResetTask():
        print("start sleeping....")
        await asyncio.sleep(seconds_until_time(7, 11))
        print("it works")
        
    def startDiscord(self):

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is now running')

            print(str(datetime.today()))
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
           
            msg = ChatBot.giveResponse(prompt+ ".", "Welcome to Weer Woler! Sorry My AI failed! But here's the prompt it was suppose use:\n " + prompt)
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
            
            msgDate = message.created_at - timedelta(hours=6)
            
            if(self.todaysPuzzleNumber != self.mainwindow.wordleGrid.getPuzzleNumber()):
                self.mainwindow.wordleGrid.pickWordForTheDay()
                self.currGames = {}
                self.todaysPuzzleNumber =  self.mainwindow.wordleGrid.getPuzzleNumber()
                self.playStat.dailyReset()
                self.resetRoutine()
                print("reset routines ran at message date: " +str(msgDate))
                
                
                
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
            
            fileNotCreated = not os.path.isfile(filename)
            notInCurrGames = not username in self.currGames.keys()
            wod = self.mainwindow.wordleGrid.wordOfTheDay
            if(fileNotCreated):
                if userMessage == "play":
                    self.playStat.insertPlayer(username)
                    wod = self.mainwindow.wordleGrid.pickWordForTheDay()
                    newGame = WordleGame(username, wod, True)
                    self.currGames[username] = newGame
                    with open(filename, 'w') as f:
                        pass

                    await message.author.send("Five-letter words please...")
                else:
                    await message.author.send("You're currently not playing a game. Just send \"play\" to begin")
            else:
                
                
                file = open(filename, 'r')
                lines = file.readlines()
                file.close()
                
                if(notInCurrGames):
                    #create a replay and add it to the dictionary
                    #TODO I need a way to determine if this is FirstPlayed game
                    self.currGames[username] = WordleGame(username, wod, True)
                    self.currGames[username].replay(lines)

                if (not self.currGames[username].isDone):
                    if(len(userMessage) == 5):
                        submittedWord = userMessage.upper().rstrip()
                        if(self.mainwindow.isWord(submittedWord)):
                        
                            print( username + " "+str(datetime.now().second)+ "\n")
                           

                            file = open(filename, 'a')
                            file.write(submittedWord.rstrip() + '\n')
                            file.close()
                            
                            self.currGames[username].eval(submittedWord)
                            self.mainwindow.paintGame(self.currGames[username].guesses)
                            self.mainwindow.evalKeyboard(self.currGames[username].keyboard)

                            filenamePic = username + ".jpg"
                            didLose = self.currGames[username].isDone and not self.currGames[username].isWinner
                            if didLose:
                                    self.mainwindow.showTempMsg(wod, "red")
                            self.app.processEvents()
                            self.captureScreenShot(filenamePic)
                            if didLose:
                                self.mainwindow.hideTempMsg()
                            self.mainwindow.reset()
                            self.app.processEvents()
                            try:
                                
                                await message.author.send("",file = discord.File(filenamePic))
                                print(username +" Message sent at " + str(datetime.now()))
                                
                            except  Exception as e:
                                time.sleep(.1)
                                print("failed to send.")
                                            



                            if(self.currGames[username].isDone):

                                    try:
                                        self.mainwindow.setName2(username)
                                        self.puzzleFinishers[username] = message.author
                                        msg = self.currGames[username].createPuzzleResults(self.mainwindow.getPuzzleNumber())
                                        if(username != "jayloo92test"):
                                            await self.mainwindow.sendDiscordMessage(msg)
                                        else:
                                            print(msg)
                                    except:
                                        pass
                            

                                    eogMsg = ""
                                    lines.append(submittedWord)
                                    
                                    guessesCommas = ", ".join(lines).replace('\n', "")
                                    self.playStat.updateAfterGame(username, self.currGames[username].isWinner, self.currGames[username].guessNumber)
                                    person = self.playStat.getPrompt(username)
                                    prompt = "In the style of " + person + ", respond to " + username + "'s Wordle game. "
                                    if(self.currGames[username].isWinner):
                                        guessCount = self.currGames[username].guessNumber
                                        
                                        
                                        if guessCount <= 3:
                                            prompt += username +" did an exceptionally good job on today's Wordle game with " + str(guessCount)
                                                
                                        elif(guessCount > 3 and guessCount < 5):
                                            prompt += username +" just did average in today's Wordle with" + str(guessCount)
                                            
                                        else:
                                            prompt += username +" barely won today's Wordle. One more wrong guess and they would of lost it because they had " + str(guessCount)
                                        prompt += " guesses."
                                    else:
                                        prompt = "Mercilessly mock " + username + " for losing today's wordle."
                                    
                                    prompt += "The word of the day was "+ wod +". Their guess were " + guessesCommas   
                                    currYear = self.Today.year
                                    try:
                                        if self.Today == datetime(currYear, 10, 31 ).date():
                                            prompt += " Also wish them a happy Halloween"
                                        elif self.Today == datetime(currYear, 12, 25).date():
                                            prompt += " Also wish them a Merry Christmas"
                                        elif self.Today == datetime(currYear, 1, 1).date():
                                            prompt += " Also wish them a Happy New Year"
                                        elif self.Today == datetime(currYear, 2, 14).date():
                                            prompt += " Also wish them a Happy Valentine Day"
                                    except:
                                        pass
                                    prompt += " And work in an advertisment for Elizabeth Payne's Girl Scout cookies. Keep the response under a 1000 characters" 
                                    if(username != "jayloo92test"):
                                        eogMsg = ChatBot.giveResponse(prompt+ ".", "games over")
                                    else:
                                        eogMsg = prompt
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
                                                print(sending)
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
                            if(self.currGames[username].guessNumber > 0):
                                await message.author.send("",file = discord.File(username + ".jpg"))
                    
                    else:
                        await message.author.send("You're currently playing a game. Please try sending a 5-letter word")
                        if(self.currGames[username].guessNumber > 0):
                            await message.author.send("",file = discord.File(username + ".jpg"))
            
                     
                else:
                    await message.author.send("You're done! Leave me alone!")
            
                
                                  
                


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
        time.sleep(.1)
        screenShot.save(fileName, 'jpg')
        


    async def receiveMessage(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    x = DiscordGameBot(app)
    


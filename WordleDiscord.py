import discord
from discord.ext import tasks
from discord.ext.commands import Bot
import sys
import os
import glob
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import ChatBot
import asyncio
from datetime import datetime, timedelta, date
from pathlib import Path
from WordleSQL import WordleSQL
from WordleSolver import WordleSolver
from WordleGame import WordleGame
from WordleDictionary import WordleDictionary
import holidays
from dateutil.easter import *
from lunardate import LunarDate
import WordleReactor as WR
# import schedule
TESTACCOUNT = "jayloo92test"
EPOCH_DATE = date(2023, 6, 26)
FILEPREFIX = "TEMP"
MAIN = "main"
MAINDATABASE = 'playerStats.db'
TESTDATABASE = 'testDatabase.db'

MONTHICONS =[("./ICONS/snowman.png","./ICONS/winter.png"), #Jan
        ("./ICONS/cupid.png","./ICONS/love.png"), #Feb
        ("./ICONS/march_clover.png","./ICONS/march_rainbow.png"), #Mar
        ("./ICONS/april_sun-shower.png","./ICONS/flowers.png"), #Apr
        ("./ICONS/beach-ball.png","./ICONS/tulips.png"), #May
        ("./ICONS/sun.png","./ICONS/beach.png"), #Jun
        ("./ICONS/america.png","./ICONS/statue-of-liberty.png"), #Jul
        ("./ICONS/hot.png","./ICONS/icecream-cone.png"), #Aug
        ("./ICONS/rugby-ball.png","./ICONS/september.png"), #Sep
        ("./ICONS/pumpkin.png","./ICONS/dry-leaves.png"), #Oct
        ("./ICONS/cornucopia.png","./ICONS/turkey.png"), #Nov
        ("./ICONS/christmasTree.png","./ICONS/holly.png")] #Dec
HOLIDAYICONS = {
    "1/1":("./ICONS/firework.png","./ICONS/champaign.png"),
    "10/31":("./ICONS/jacko.png", "./ICONS/ghost.png"),
    "11/11":("./ICONS/veteran.png-", "./ICONS/soldier.png"),
    "12/31":("./ICONS/firework.png","./ICONS/champaign.png"),
    "CNY": ("./ICONS/chineseDragon.png","./ICONS/chinese-new-year.png"),
    "EASTER": ("./ICONS/easter-egg.png", "./ICONS/rabbit.png")
}

def isChineseNewYear(d:date)->bool:
    return d == LunarDate(d.year, 1,1).toSolarDate()

def isChineseNewYearFestival(d:date)->bool:
    cny = LunarDate(d.year, 1,1).toSolarDate()
    delta = (d - cny).days
    
    output = delta >= -1 and delta <= 2
    return output
    

def isEaster(i:date)->bool:
    d = easter(i.year)
    
    return d == i
    

def convertMonthDayStr(date:date):
    output = str(date.month) + "/" + str(date.day)
    return output



def isMain():
    branch = ""
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f: content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            branch = line.partition("refs/heads/")[2]
    return (branch == MAIN)



def getPuzzleNumber():
        delta = date.today() - EPOCH_DATE
        return delta.days
'''
    Gets the puzzle storedin a file.
    The reason it is store in a file is if the program 
    shutdowns one day and reopens another it knows to run the reset process on the database.
    Will fail if file is not in the repo.
'''
def getStoredPuzzleNumber()->int:
    file = open(STOREPUZZLENUMBERFILE, 'r')
    output = file.readlines()[0]
    return (int(output))

def setStoredPuzzleNumber(newNumber):
    file = open(STOREPUZZLENUMBERFILE, 'w')
    file.write(str(newNumber))


ISMAIN = isMain()
STOREPUZZLENUMBERFILE  = ""
SALT = ""
pictureDir = ""
if ISMAIN:
    tokenFile = open("DiscordKey.txt", 'r')
    STOREPUZZLENUMBERFILE = "MainNumber.txt"
    SALT = "salt1"
    pictureDir = "./MainPictures/"
    
    
else:
    tokenFile = open("TestKey.txt" , "r")
    STOREPUZZLENUMBERFILE = "TestNumber.txt"
    SALT = "Jonathan"
    pictureDir = "./TestPictures/" 
    
token = tokenFile.readlines()
JLWORDLECHANNELID = 1127398485369557092
TESTCHANNELID = 1133965604974506025
tokenFile.close()
TOKEN = token[0]

    



guildId = 1127338015249944596
todaysWordlers = 'todays-wordlers'


class DiscordGameBot:
    lastPictureMsg = {}
    currGames = {}
    mainwindow = None
    unlocked = True
    

    def __init__(self, app) -> None:
        intents = discord.Intents.all()
        intents.members = True
        self.client = discord.Client(intents=intents)

        app = QApplication(sys.argv)

        self.mainwindow = MainWindow()
        self.WordleScoreChannel = None
        if ISMAIN:
            self.channelId = JLWORDLECHANNELID
            self.playStat = WordleSQL(MAINDATABASE)
            
        else:
            self.channelId = TESTCHANNELID
            self.playStat = WordleSQL(TESTDATABASE)
        self.Today = datetime.today().date()
       
        self.setIcons()
        
        self.wordleDict = WordleDictionary(SALT)
        self.wod = self.wordleDict.pickWordForTheDay(str(self.Today))
        self.todaysPuzzleNumber = getStoredPuzzleNumber()
        puzzNo = getPuzzleNumber()
        if self.todaysPuzzleNumber != puzzNo:
            self.playStat.differentDayReboot()
            setStoredPuzzleNumber(puzzNo)
            self.todaysPuzzleNumber = puzzNo
            
        self.puzzleFinishers = {}
        # self.secondsToTomorrow = Ults.getTimeSleep(HOUR)
        # resetThread = threading.Thread(target=self.resetRoutine)
        # resetThread.daemon = True
        # resetThread.start()

        self.app = app
        app.processEvents()
        self.startDiscord()



        # self.secondsToTomorrow = 86400 # how many seconds there are in a day.

    def setIcons(self):
        keyDay = convertMonthDayStr(self.Today)
        tup = None
        if(keyDay in HOLIDAYICONS.keys()):
            tup = HOLIDAYICONS[keyDay]
            
        elif(isChineseNewYearFestival(self.Today)):
            tup = HOLIDAYICONS["CNY"]
        elif(isEaster(self.Today)):
            tup = HOLIDAYICONS["EASTER"]
        else:
            tup = MONTHICONS[self.Today.month - 1]
            
        self.mainwindow.setIcons(tup[0], tup[1])   

    def startDiscord(self):

        @self.client.event
        async def on_ready():
            print(f'{self.client.user} is now running')
            self.WordleScoreChannel = self.client.get_channel(self.channelId)
            
            self.Today = datetime.today().date()

        @self.client.event
        async def on_member_join(member: discord.Member):
            if ISMAIN:
                name = member.name
                prompt = f"""Write a welcome message for {member.name} to my wordle discord server named Weer Wolerr. 
                Tell them they can play your wordle by sending you the message \"play\". Tell they can also change your personality by sending you a message
                with an exclamation point followed by person \"=\" and their desired personality.\
                For example, if they want you to respond to their wordle score as a kawaii girl, they would send you \"!person = kawaii girl\" They can also post 
                their New York Times Wordle in the nyt-wordle channel but you think that's an inferior wordle. Tell them to behave and be nice to the other wordlers.
                """

                msg = ChatBot.giveResponse(
                    prompt + ".", "Welcome to Weer Woler! Sorry My AI failed! But here's the prompt it was suppose use:\n " + prompt)
                print(msg)
                await member.send(msg)
            else:
                msg = "Welcome to TestWordbot or whatever. It is an honor to be part of the elite few that have been given the honor.... OH whatever just try to break my code. You can reset your game by sending me !reset . Thank you for your service"

        @self.client.event
        async def on_message(message):

            channelType = message.channel.type.name
            if channelType == 'text':
                m = str(message.content).split("\n")
                reactions = WR.getReactions(m)
                if reactions != None:
                    for reaction in reactions:
                        await message.add_reaction(reaction)
                return
            if message.author.bot:
                if message.attachments:
                    #TODO fix this 
                    userNameFile = Path(
                        message.attachments[0].filename).with_suffix('').name
                    try:
                        lastPicMsg = await message.channel.fetch_message(self.lastPictureMsg[userNameFile])
                        await lastPicMsg.delete()
                    except:
                        pass
                    self.lastPictureMsg[userNameFile] = message.id
                return

            msgDate = message.created_at - timedelta(hours=6)

            newPuzzNum = getPuzzleNumber()
            if (self.todaysPuzzleNumber != newPuzzNum):
                
                self.currGames = {}
                self.Today = datetime.today().date()
                self.setIcons()
                self.wod = self.wordleDict.pickWordForTheDay(str(self.Today))
                self.todaysPuzzleNumber = newPuzzNum
                setStoredPuzzleNumber(newPuzzNum)
                self.playStat.dailyReset()
                print("reset routines ran at message date: " + str(msgDate))

            username = str(message.author)
            userMessage = str(message.content)
            channel = str(message.channel)
            print(f"{username} said '{userMessage}' {(channel)}")
            self.playStat.insertPlayer(username)
            notInCurrGames = not username in self.currGames.keys()
            if (userMessage.startswith('!')):
                userMessage = userMessage.replace("!", "")
                command = userMessage.split("=")
                commandWord = command[0].lower().strip()
                if (len(command) == 2):
                    
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
                elif(len(command) == 1):
                    if not ISMAIN and commandWord == "reset":
                        self.playStat.resetGame()
                        if not notInCurrGames:
                            self.currGames.pop(username)
                    
                else:
                    await message.author.send("Invalid Command.")

                return
            userMessage = userMessage.lower()

        

            notPlaying = not self.playStat.getIsPlaying(username)
            hasPlayedFirst = self.playStat.getDoneWithFirst(username)
           
            if (notPlaying):
                
                if(hasPlayedFirst):
                    await message.author.send("You're done. Leave me alone")
                    return
                if userMessage == "play":
                    self.playStat.insertPlayer(username)
                    
                    newGame = WordleGame(username, self.wod, True)
                    self.currGames[username] = newGame
                    self.playStat.beginFirstGame(username)

                    await message.author.send("Five-letter words please...")
                else:
                    await message.author.send("You're currently not playing a game. Just send \"play\" to begin")
            else:

                lines = self.playStat.getGuessesList(username)

                if (notInCurrGames):
                    # create a replay and add it to the dictionary
                    self.currGames[username] = WordleGame(username, self.wod, True)
                    self.currGames[username].replay(lines)
                game = self.currGames[username]
                if (not game.isDone):
                    if (len(userMessage) == 5):
                        submittedWord = userMessage.upper().rstrip()
                        if (self.wordleDict.isWord(submittedWord)):


                            self.playStat.appendGuess(submittedWord, username)

                            game.eval(submittedWord)
                            self.mainwindow.paintGame(
                                game.guesses)
                            self.mainwindow.evalKeyboard(
                                game.keyboard)

                            filenamePic = pictureDir + username + ".jpg"
                            didLose = game.isDone and not game.isWinner
                            if didLose:
                                self.mainwindow.showTempMsg(self.wod, "red")
                            self.app.processEvents()
                            self.captureScreenShot( filenamePic)
                            if didLose:
                                self.mainwindow.hideTempMsg()
                            self.mainwindow.reset()
                            self.app.processEvents()
                            try:

                                await message.author.send("", file=discord.File(filenamePic))
                                print(username + " Message sent at " +
                                      str(datetime.now()))

                            except Exception as e:
                                time.sleep(.1)
                                print("failed to send.")

                            if (game.isDone):

                                eogMsg = ""
                                guessesCommas = ""
                                if game.guessNumber > 2:
                                    lines.append(" and " + submittedWord)

                                    guessesCommas = ", ".join(
                                        lines).replace('\n', "")
                                elif game.guessNumber == 2:
                                    guessesCommas = lines[0] + " and " + submittedWord
                                    
                                else:
                                    guessesCommas = submittedWord
                                
                                person = self.playStat.getPrompt(username)
                                prompt = "In the style of " + person + \
                                    ", respond to " + username + "'s Wordle game. "
                                if (game.isWinner):
                                    guessCount = game.guessNumber

                                    if guessCount <= 3:
                                        prompt += username + \
                                            " did an exceptionally good job winning today's Wordle game with " + \
                                            str(guessCount)

                                    elif (guessCount > 3 and guessCount <= 5):
                                        prompt += username + \
                                            " just did an average job winning today's Wordle with " + \
                                            str(guessCount)

                                    else:
                                        prompt += username + \
                                            " barely won today's Wordle. One more wrong guess and they would of lost it because they had " + \
                                            str(guessCount)
                                    prompt += " guesses."
                                    prompt += " Their win streak has increased to " + str(self.playStat.getStreak(username) + 1)
                                else:
                                    prompt = "Mercilessly mock " + username + " for losing today's wordle. "
                                    prompt += " They lost their win streak of " + str(self.playStat.getStreak(username))

                                prompt += "The word of the day was " + self.wod + \
                                    ". Their guess(es) were " + guessesCommas
                                currYear = self.Today.year

                                try:
                                    if self.Today == datetime(currYear, 10, 31).date():
                                        prompt += " Also wish them a happy Halloween"
                                    elif self.Today == datetime(currYear, 12, 25).date():
                                        prompt += " Also wish them a Merry Christmas"
                                    elif self.Today == datetime(currYear, 1, 1).date():
                                        prompt += " Also wish them a Happy New Year. The new year is " + str(currYear)
                                    elif self.Today == datetime(currYear, 2, 14).date():
                                        prompt += " Also wish them a Happy Valentine Day"
                                    elif self.Today == datetime(currYear, 4, 1).date():
                                        prompt += " Also try to RickRoll them with a disguised link for April fools day"
                                    elif isChineseNewYear(self.Today):
                                        prompt += " Also wish them a happy Chinese New year " + str(currYear)
                                except:
                                    pass
                                prompt += ". Keep the response under a 1000 characters"
                                eogScore = game.createPuzzleResults(self.todaysPuzzleNumber)
                                await self.postScores(username + "'s results:\n" + eogScore)
                                self.playStat.updateAfterGame(
                                        username, game.isWinner, game.guessNumber)
                                if (ISMAIN):
                                    eogMsg = ChatBot.giveResponse(
                                        prompt + ".", "games over")

                                else:
                                    eogMsg = prompt
                                print(eogMsg)
                                lenMsg = len(eogMsg)
                                if (lenMsg < 2000):
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
                            if (self.currGames[username].guessNumber > 0):
                                await message.author.send("", file=discord.File(pictureDir + username + ".jpg"))

                    else:
                        await message.author.send("You're currently playing a game. Please try sending a 5-letter word")
                        if (self.currGames[username].guessNumber > 0):
                            await message.author.send("", file=discord.File(pictureDir + username + ".jpg"))
                            

        self.client.run(TOKEN)

    async def postScores(self, msg):
        if self.WordleScoreChannel == None:
            self.WordleScoreChannel = self.client.get_channel(self.channelId)
        await self.WordleScoreChannel.send(msg)

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
    

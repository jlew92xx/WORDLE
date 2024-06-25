import discord
import discord.utils as discordTools
from discord.ext import tasks
from discord.ext.commands import Bot
import sys
import re
import os
import glob
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import WordleConfigure
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
MAINGUILDID = 1127338015249944596
TESTGUILDID = 1132882138941886525
REMINDINGHOUR = 19
REMINDINGMINUTE = 20
GROUPWORDLE = "group-wordle"
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
    #if the delta between today's date and the chinese year new year is 1 day before or 2 days after then we show the
    output = delta >= -1 and delta <= 2
    return output

def isThanksgiving(d:date)->bool:
    ##if it's not in November
    if date.month != 11:
        return False
    #if it's not a thursday
    if date.weekday != 3:
        return False  
    day = date.day
    if(day > 21 and day < 29):
        return True
    
    return False

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

    


NUM_PUBLIC_CHANNEL = 5
 
todaysWordlers = 'todays-wordlers'


class DiscordGameBot:
    lastPictureMsg = {}
    currGames = {}
    publicGames = {}    
    mainwindow = None
    unlocked = True
    guildId = 0

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
            self.guildId = MAINGUILDID
            
        else:
            self.channelId = TESTCHANNELID
            self.playStat = WordleSQL(TESTDATABASE)
            self.guildId = TESTGUILDID
        self.Today = datetime.today().date()
       
        self.setIcons()
        self.userObjects ={}
        self.wordleDict = WordleDictionary(SALT)
        self.wod = self.wordleDict.pickWordForTheDay(str(self.Today))
        self.todaysPuzzleNumber = getStoredPuzzleNumber()
        puzzNo = getPuzzleNumber()
        self.countAi = 0
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
            for user in self.client.users:
                self.userObjects[user.name] = user
            self.Today = datetime.today().date()
            await self.createChannels() #creates the public channels.
            msg1.start()
        
        # Message 1
        @tasks.loop(hours=24)
        async def msg1():
            #message_channel = self.client.get_channel(705524214270132367)
            #await message_channel.send("test 1")
            userdata = self.playStat.getPlayersToBeReminded()
            for user in userdata:
                username = user[0]
                streak = user[1]
                msg = f"""Greetings {username},
                This is a reminder from your favorite WordBot to play my Wordle for today."""
                if streak == 0:
                    msg += """ There is no better day than today to start your win streak (if you can win this simple game). """
                else:
                    msg += f"""If you want to continue your streak of {streak}, I strongly suggest you play me before it is too late, but I'm not your boss (but maybe someday;))."""
                
                msg += """\nYou can shut me up by sending me \"!mute\" if you're rude and send me \"!unmute\" if you were rude and came to your senses. Thank you for being a member of Weer Wolerr! It means the world to me!
                
                VWOWDER WORRRMLEER!
                
                WordBot"""
                
                if user == "colorlessjack":
                   
                   msg = msg + '\n' + "P.S. In case you weren't aware, threatening someone's bloodline is a serious matter. Maybe think twice before making such reckless and harmful statements in the future."
                try:
                    await self.userObjects[username].send(msg)
                    print("Reminder sent to " + username + " at " +  datetime.now().__str__())
                except:
                    print("Failure to send Reminder to " + username + " at " +  datetime.now().__str__())   
                
            
        @msg1.before_loop
        async def before_msg1():
            for _ in range(60*60*24):  # loop the whole day
                if datetime.now().hour  == REMINDINGHOUR and datetime.now().minute == REMINDINGMINUTE:  # 24 hour format
                    print('It is time')
                    return
                await asyncio.sleep(1)
                
                
        @self.client.event
        async def on_member_join(member: discord.Member):
            name = member.name
            self.userObjects[name] = member
            if ISMAIN:
                
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
            tag = message.mentions
            isGroupWordle = False
            
            if channelType == 'text':
                isGroupWordle = (GROUPWORDLE in message.channel.name)
                m = str(message.content).split("\n")
                reactions = WR.getReactions(m)
                if reactions != None:
                    for reaction in reactions:
                        try:
                            await message.add_reaction(reaction)
                        except:
                            print(reaction)
                if not isGroupWordle:
                    return
            if message.author.bot:
                if message.attachments:
                    #TODO fix this 
                    userNameFile = Path(
                        message.attachments[0].filename).with_suffix('').name
                    try:
                        if userNameFile in self.lastPictureMsg.keys():
                            lastPicMsg = self.lastPictureMsg[userNameFile]
                            await lastPicMsg.delete()
                    except:
                        pass
                    if(message.embeds == []):
                        self.lastPictureMsg[userNameFile] = message
                    else:
                        if userNameFile in self.lastPictureMsg.keys():
                            del self.lastPictureMsg[userNameFile]
                return

            msgDate = message.created_at - timedelta(hours=6)

            newPuzzNum = getPuzzleNumber()
            if (self.todaysPuzzleNumber != newPuzzNum):
                self.countAi = 0
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
            channelName = str(message.channel)
            print(f"{username} said '{userMessage}' {(channelName)}")
            self.playStat.insertPlayer(username)
            notInCurrGames = not username in self.currGames.keys()
            if (userMessage.startswith('!')):
                userMessage = userMessage.replace("!", "")
                command = userMessage.split("=")
                commandWord = command[0].lower().strip()
                
                if commandWord == "chall":
                    #TODO add a checker if another  game is being play
                    isInDict = channelName in self.publicGames.keys()
                    if (isInDict and self.publicGames[channelName] != None):
                        await message.channel.send("A game is already being played")
                        return
                    paramWord = command[1].strip()
                    params = paramWord.strip().split(" ")
                
                    if len(message.mentions) != 1:
                        await message.channel.send("You have to mention one and only person in the first param of the challenge the command.")
                        return
                    memb = message.mentions[0]
                    
                    
                    wordToBGuessed = params[-1]
                    # if (not re.search("\|\|*\|\|", wordToBGuessed)):
                    #     await message.channel.send("You must surround your guess with \"||.\"")
                    #     await message.delete()
                    #     return
                    wordToBGuessed = wordToBGuessed.replace('|', "")
                    if self.wordleDict.isWord(wordToBGuessed):
                            await memb.send(f"{username} has challenge you in a game of Wordle in which they chose a word for you.\nPlay in the group-wordle channel! You follow the link to the proper channel <#{message.channel.id}>")
                            await message.channel.send(f"{username} has challenged {memb.name} in a game of wordle.\nYou can challenge someone after this game by sending !chall = @<username> ||<word>||\n Just make sure there is a space between the username and the word")
                            self.publicGames[channelName] = WordleGame(memb.name, wordToBGuessed, False)
                    
                    await message.delete()
                    
                elif (len(command) == 2):
                    
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
                    if (not ISMAIN or isGroupWordle) and commandWord == "reset":
                        if not ISMAIN:
                            self.playStat.resetGame()
                        elif isGroupWordle:
                            rolename = "The Wordle Authorities"
                            role = discordTools.get(self.client.guild.roles, name = rolename)
                            roles = message.author.roles
                            if not role in roles:
                                await message.channel.send(f"{username}, you have authority here")
                            try:
                                game = self.wordleDict[channelName]
                                await message.channel.send(f"{username} has cancelled {game.name}'s game. Sorry {game.name} sucks.")
                                self.wordleDict[channelName] = None
                            except:
                                await message.channel.send(f"{username} has cancelled {game.name}'s game. Sorry {game.name} sucks.")
                                
                        if not notInCurrGames:
                            self.currGames.pop(username)
                    elif commandWord == "mute":
                        self.playStat.setMute(username, 1)
                        await message.author.send("OK OK I'll shutup :/")
                    elif commandWord == "unmute":
                        await message.author.send("I'll remind you at 7:20pm CST to play some delicious Wordle.")
                        self.playStat.setMute( username, 0)
                    else:
                        await message.channel.send("Invalid Command.")
                
                else:
                    await message.channel.send("Invalid Command.")

                return
            userMessage = userMessage.lower()

            notPlaying = False
            hasPlayedFirst = False
            if not isGroupWordle:
                notPlaying = not self.playStat.getIsPlaying(username)
                hasPlayedFirst = self.playStat.getDoneWithFirst(username)
            else:
                isInDict = channelName in self.publicGames.keys()
                if(isInDict):
                    isValueNone = self.publicGames[channelName]
                notPlaying = not (channelName in self.publicGames.keys() and self.publicGames[channelName] != None)
                notInCurrGames = False
                
            if (notPlaying):
                
                if(hasPlayedFirst):
                    await message.author.send("You're done. Leave me alone")
                    return
                if userMessage == "play":
                    
                    if isGroupWordle:
                        todayStr = str(datetime.now())
                        newGame = WordleGame(username, self.wordleDict.pickWordForTheDay(todayStr), True)
                        self.publicGames[channelName] = newGame
                        
                    else:
                        newGame = WordleGame(username, self.wod, True)
                        self.currGames[username] = newGame
                        self.playStat.beginFirstGame(username)

                    await message.channel.send("Five-letter words please...")
                elif not isGroupWordle:
                    response = ""
                    if self.countAi < 5:
                        response = ChatBot.giveResponse(username + " just sent you a message \"+" + userMessage + "\" on discord. respond to them in a very snarky way. Your name is WordBot and you just want people just play your Wordle by sending you the word \"play\" to begin." ,"You're currently not playing a game. Just send \"play\" to begin")
                        print(response)
                        self.countAi += 1
                    else:
                        response = "You're currently not playing a game. Just send \"play\" to begin"
                    await message.channel.send(response)
                else:
                    print("it thinks its not playing.")
            else:

                lines = self.playStat.getGuessesList(username)

                if (notInCurrGames and not isGroupWordle):
                    # create a replay and add it to the dictionary
                    self.currGames[username] = WordleGame(username, self.wod, True)
                    self.currGames[username].replay(lines)
                game = None
                if not isGroupWordle:
                    game = self.currGames[username]
                else:
                    game = self.publicGames[channelName]
                    #TODO make it where the person being challenge can only play
                    #if it's not an open game and the person who should not be playing tries to play.
                    if not game.isOpen and game.name != username:
                        if(self.wordleDict.isWord(userMessage.upper().rstrip()) or userMessage == "play"):
                            await message.channel.send(f"{game.name} is currently playing a challenge game in this channel. You use another open group-wordle channel if you please.")
                        return
                if (not game.isDone):
                    if (len(userMessage) == WordleConfigure.WORDSIZE):
                        submittedWord = userMessage.upper().rstrip()
                        if (self.wordleDict.isWord(submittedWord)):
                            filenamePic = pictureDir
                            if not isGroupWordle:
                                self.playStat.appendGuess(submittedWord, username)
                                filenamePic += username
                            else:
                                filenamePic += channelName
                            filenamePic += ".jpg"
                            game.eval(submittedWord)
                            self.mainwindow.paintGame(
                                game.guesses)
                            self.mainwindow.evalKeyboard(
                                game.keyboard)

                            
                            didLose = game.isDone and not game.isWinner
                            if didLose:
                                self.mainwindow.showTempMsg(game.wod, "red")
                            self.app.processEvents()
                            self.captureScreenShot( filenamePic)
                            if didLose:
                                self.mainwindow.hideTempMsg()
                            self.mainwindow.reset()
                            self.app.processEvents()
                            try:

                                await message.channel.send("", file=discord.File(filenamePic))
                                print(username + " Message sent at " +
                                      str(datetime.now()))

                            except Exception as e:
                                time.sleep(.1)
                                print("failed to send.")

                            if (game.isDone):
                                if isGroupWordle:
                                    tittle =f"{username} has completed the game."
                                    desc = "Put some bull bird here later."
                                    ava = message.author.display_avatar
                                    color =  discord.Colour.green()
                                    em = discord.Embed(title = tittle, description = desc, colour = color)
                                    em.set_author(name = f"{username}")
                                    em.set_thumbnail(url = f"{ava}")
                                    em.set_image(url = f'attachment://{filenamePic}')
                                    await message.channel.send(embed = em, file=discord.File(filenamePic))
                                    self.publicGames[channelName] = None

                                    return
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

                                prompt += ". The word of the day was " + self.wod + \
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
                                    elif self.Today == datetime(currYear, 7, 4):
                                        prompt += " Also wish them a Happy fourth of July"
                                    elif isChineseNewYear(self.Today):
                                        prompt += " Also wish them a happy Chinese New year " + str(currYear)
                                    elif isThanksgiving(self.Today):
                                        prompt += " Also wish them a happy Thanksgiving"
                                    elif isEaster(self.Today):
                                         prompt += " Also wish them a happy easter"
                                except:
                                    pass
                                prompt += ". Keep the response under a 1000 characters"
                                #TODO place the following before the first game checker when I create unlimited play.
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
                        ## I need all of this to be in a first game checker.
                        else:

                            msgWrong = "Not in the word database!"
                            await message.channel.send(msgWrong)
                            
                            if (game.guessNumber > 0):
                                pictureResendPath = pictureDir
                                if isGroupWordle:
                                    pictureResendPath += channelName
                                else:
                                    pictureResendPath += username
                                pictureResendPath += ".jpg"
                                await message.channel.send("", file=discord.File(pictureResendPath))

                    else:
                        if not isGroupWordle:
                            await message.channel.send("You're currently playing a game. Please try sending a 5-letter word")
                            if (game.guessNumber > 0):
                                await message.channel.send("", file=discord.File(pictureDir + username + ".jpg"))
                            

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

    async def createChannels(self):
        guild = self.client.get_guild(self.guildId)
        i = 0
        channelName = ""
        mycategory = discordTools.get(guild.categories,name="group-wordle")
        if mycategory == None:
           mycategory = await guild.create_category("group-wordle")
           
        while i < NUM_PUBLIC_CHANNEL:
            channelName = "group-wordle-" + str(i)
            channel = discordTools.get(guild.text_channels, name=channelName)
            if channel == None:
                channel = await guild.create_text_channel(channelName, category=mycategory)
            
            i += 1

    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    x = DiscordGameBot(app)
    

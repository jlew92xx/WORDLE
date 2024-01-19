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
from datetime import datetime, timedelta
from pathlib import Path
from WordleSQL import WordleSQL
from WordleSolver import WordleSolver
from WordleGame import WordleGame
# import schedule
TESTACCOUNT = "jayloo92test"
HOUR = 0
FILEPREFIX = "TEMP"
tokenFile = open("DiscordKey.txt", 'r')
token = tokenFile.readlines()

tokenFile.close()
TOKEN = token[0]
"""
To calculate the date of Chinese New Year for a given year in the Gregorian calendar, we need to use the following algorithm:

1. Determine the variable a by dividing the given year by 19 and taking the remainder.
2. Determine the variable b by dividing the given year by 100 and taking the remainder.
3. Determine the variable c by dividing the given year by 4 and taking the remainder.
4. Determine the variable d by dividing the given year by 7 and taking the remainder.
5. Calculate the variable e by adding up the values of a, 11b+4, 8c+13, and 12d+3, and then taking the remainder when divided by 30.
6. If e equals 25 and a is greater than 11, or if e equals 24, then increment e by 1.
7. Determine the variable g by subtracting e from the given year.
8. Determine the variable h by calculating 30.6 multiplied by e plus 0.5 and then rounding down to the nearest whole number.
9. If h is less than 19, the Chinese New Year falls in January of the given year; otherwise, it falls in February.
10. Determine the day of the Chinese New Year by subtracting h from the total number of days in the month of the Chinese New Year, which is either 31 for January or 28 or 29 for February depending on whether it is a leap year or not.

Now, we can define the function to determine if the give date is the chinese new year:
"""
def isChineseNewYear(year, p_month, p_day):
    if p_month > 2 :
        return False
    if p_month == 1 and p_day < 21:
        return False
    if p_month == 2 and p_day > 20:
        return False
    


def seconds_until_time(hours, minutes):
    now = datetime.now()
    det = 0
    target = ((now + timedelta(days=det)).replace(hour=hours,
              minute=minutes, second=0))
    diff = (target - now).total_seconds()
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
        self.client = discord.Client(intents=intents)

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
        app.processEvents()
        self.startDiscord()

    def resetRoutine(self):

        for filename in glob.glob("./" + FILEPREFIX + "*"):
            os.remove(filename)
        self.lastPictureMsg = {}

        # self.secondsToTomorrow = 86400 # how many seconds there are in a day.

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

            msg = ChatBot.giveResponse(
                prompt + ".", "Welcome to Weer Woler! Sorry My AI failed! But here's the prompt it was suppose use:\n " + prompt)
            print(msg)
            await member.send(msg)

        @self.client.event
        async def on_message(message):

            channelType = message.channel.type.name
            if channelType == 'text':
                return
            if message.author.bot:
                if message.attachments:
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

            if (self.todaysPuzzleNumber != self.mainwindow.wordleGrid.getPuzzleNumber()):
                self.mainwindow.wordleGrid.pickWordForTheDay()
                self.currGames = {}
                self.Today = datetime.today().date()
                self.todaysPuzzleNumber = self.mainwindow.wordleGrid.getPuzzleNumber()
                self.playStat.dailyReset()
                self.resetRoutine()
                print("reset routines ran at message date: " + str(msgDate))

            username = str(message.author)
            userMessage = str(message.content)
            channel = str(message.channel)
            print(f"{username} said '{userMessage}' {(channel)}")
            self.playStat.insertPlayer(username)
            if (userMessage.startswith('!')):
                userMessage = userMessage.replace("!", "")
                command = userMessage.split("=")
                if (len(command) == 2):
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
            if (fileNotCreated):
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

                if (notInCurrGames):
                    # create a replay and add it to the dictionary
                    # TODO I need a way to determine if this is FirstPlayed game
                    self.currGames[username] = WordleGame(username, wod, True)
                    self.currGames[username].replay(lines)

                if (not self.currGames[username].isDone):
                    if (len(userMessage) == 5):
                        submittedWord = userMessage.upper().rstrip()
                        if (self.mainwindow.isWord(submittedWord)):


                            file = open(filename, 'a')
                            file.write(submittedWord.rstrip() + '\n')
                            file.close()

                            self.currGames[username].eval(submittedWord)
                            self.mainwindow.paintGame(
                                self.currGames[username].guesses)
                            self.mainwindow.evalKeyboard(
                                self.currGames[username].keyboard)

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

                                await message.author.send("", file=discord.File(filenamePic))
                                print(username + " Message sent at " +
                                      str(datetime.now()))

                            except Exception as e:
                                time.sleep(.1)
                                print("failed to send.")

                            if (self.currGames[username].isDone):

                                try:
                                    self.mainwindow.setName2(username)
                                    self.puzzleFinishers[username] = message.author
                                    msg = self.currGames[username].createPuzzleResults(
                                        self.mainwindow.getPuzzleNumber())
       
                                except:
                                    pass

                                eogMsg = ""
                                lines.append(submittedWord)

                                guessesCommas = ", ".join(
                                    lines).replace('\n', "")
                                self.playStat.updateAfterGame(
                                    username, self.currGames[username].isWinner, self.currGames[username].guessNumber)
                                person = self.playStat.getPrompt(username)
                                prompt = "In the style of " + person + \
                                    ", respond to " + username + "'s Wordle game. "
                                if (self.currGames[username].isWinner):
                                    guessCount = self.currGames[username].guessNumber

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
                                else:
                                    prompt = "Mercilessly mock " + username + " for losing today's wordle."

                                prompt += "The word of the day was " + wod + \
                                    ". Their guess were " + guessesCommas
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
                                        prompt += " Also try to RickRoll them with a disguised link for April fools"
                                except:
                                    pass
                                prompt += ". Keep the response under a 1000 characters"
                                if (username != "jayloo92test"):
                                    await self.mainwindow.sendDiscordMessage(msg)
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
                                await message.author.send("", file=discord.File(username + ".jpg"))

                    else:
                        await message.author.send("You're currently playing a game. Please try sending a 5-letter word")
                        if (self.currGames[username].guessNumber > 0):
                            await message.author.send("", file=discord.File(username + ".jpg"))

                else:
                    await message.author.send("You're done! Leave me alone!")

        self.client.run(TOKEN)

    async def postScores(self):
        channel = Bot.get_channel(1127398485369557092)
        await channel.send("TESTING")

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
    x.postScores()

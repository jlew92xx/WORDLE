import discord
from discord.ext.commands import Bot
import sys, os
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import time
import threading


class DiscordGameBot:
    currentGames = []
    mainwindow = None
    
    def __init__(self, app) -> None:

        self.mainwindow = MainWindow()
        
        
        self.app = app
        
        self.startDiscord()
        

        

        
        
    def startDiscord(self):

        TOKEN = "MTEyNzM0Mjk4MzYyNTMyNjYxMg.GfWMk1."
        TOKEN += "1jHNWvWdnw_l-AvVA9gYh8DwvlKGNKWL0N5ghQ"
        client = discord.Client(intents= discord.Intents.default())

        @client.event
        async def on_ready():
            print(f'{client.user} is now running')
            
        @client.event
        async def on_message(message):
            channelType = message.channel.type.name
            print(channelType)
            if message.author.bot or channelType == 'text':
                return
            
            username = str(message.author)
            userMessage = str(message.content).lower()
            channel = str(message.channel)
            
            print(f"{username} said '{userMessage}' {(channel)}")
            filename = self.mainwindow.createFileName(username)
            if(not os.path.isfile(filename)):
                if userMessage == "play":
                    self.currentGames.append(username)
                    filename = self.mainwindow.createFileName(username)
                    with open(filename, 'w') as f:
                        pass
                    
                    await message.author.send("I'm ready when you are! Start feeding me 5 letter words.")
                else:
                    await message.author.send("You're currently not playing a game. Just send \"play\" to begin")
            else:
                
                
                file = open(filename, 'r')
                lines = file.readlines()
                file.close()
                
                self.mainwindow.reset()
                self.mainwindow.replayTheCache(lines)
                
                if (not self.mainwindow.isDone()):
                    if(len(userMessage) == 5):
                        submittedWord = userMessage.upper().rstrip()
                        if(self.mainwindow.isWord(userMessage)):
                            lines.append(submittedWord)
                            
                            self.mainwindow.reset()
                            self.mainwindow.replayTheCache(lines)
                            self.app.processEvents()
                            time.sleep(.25)
                            await self.captureScreenShotAndSend(message, username)
                            if(self.mainwindow.isDone()):
                                try:
                                    self.mainwindow.setName2(username)
                                    msg = self.mainwindow.createPuzzleResults()
                                    await self.mainwindow.sendDiscordMessage(msg)
                                except:
                                    print("WHATS GOING ON HERE")
                                if(self.mainwindow.isWinner()):
                                    await message.author.send("YOU WON!!")
                                else:
                                    await message.author.send("You're a loser.")
                                    

             
                            file = open(filename, 'w')
                            for line in lines:
                                file.write(line.rstrip() + '\n')
                            file.close
                            
                        else:
                            await message.author.send("English words please.")
                    
                    else:
                        await message.author.send("Learn how to count!")
                        
                else:
                    await message.author.send("You're done! Leave me alone!")                     
                

            

        client.run(TOKEN)
    
    async def postScores(self):
        channel = Bot.get_channel(1127398485369557092)

    def appendToCache(self, word, fileName):
        file = open(fileName, "a")
        file.write(word + "\n")
        file.close()
    
    def setMainWindow(self, mw):
        self.mainwindow = mw
        
    async def captureScreenShotAndSend(self, message, userName):
        # self.mainwindow.setOntop()
        # self.mainwindow.show()
        # self.app.processEvents()
        # time.sleep(.3)
        screen = QtWidgets.QApplication.primaryScreen()
        screenShot = screen.grabWindow(self.mainwindow.winId())
        fileName = userName +".jpg"
        screenShot.save(fileName, 'jpg')
        
        try:
            await message.author.send("",file = discord.File(fileName))
            
        except  Exception as e:
            time.sleep(.1)
            screen = QtWidgets.QApplication.primaryScreen()
            screenShot = screen.grabWindow(self.mainwindow.winId())
            screenShot.save(fileName, 'jpg')
            await message.author.send("",file = discord.File(fileName))
            

    async def receiveMessage(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app
    x = DiscordGameBot(app)
    


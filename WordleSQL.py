import sqlite3
import ChatBot

columnNames = ["Name", "NumberOfGuesses",
               "NumGamesPlayed", "Streak", "wonToday"]


class WordleSQL():

    def __init__(self, databaseStr):

        self.conn = sqlite3.connect(databaseStr)
        self.curs = self.conn.cursor()
        self.curs.execute("""CREATE TABLE IF NOT EXISTS playerStats (
            name text,
            NumberOfGuesses integer,
            NumGamesWon integer,
            NumGamesPlayed integer,
            Streak integer,
            wonToday text,
            prompt text,
            hardmode integer,
            currGame text,
            doneWithFirst integer,
            isPlaying integer,
            UNIQUE(name)
            
            
            );""")
        self.conn.commit()

    def printRow(self):
        pass

    def printContents(self):
        pass

    def insertPlayer(self, name):
        self.curs.execute(
            "SELECT name FROM playerStats WHERE name = ?", (name,))
        data = self.curs.fetchall()
        if len(data) == 0:
            characterName = ChatBot.giveResponse(
                "A nonsensical hero name", "A jerk Named Jonathan Lewis")
            params = (name, 0, 0, 0, 0, "False", characterName, 0, "", 0, 0)
            self.curs.execute(
                "INSERT OR IGNORE INTO playerStats VALUES(?,?,?,?,?,?,?,?,?,?,?)", params)
            self.conn.commit()

    def printTableToConsole(self):
        self.curs.execute("SELECT * FROM playerStats")
        print(self.curs.fetchall())
        
    def beginFirstGame(self, username):
         self.curs.execute("""UPDATE
                                playerStats 
                                SET
                                    isPlaying = 1,
                                    doneWithFirst = 0
                                WHERE 
                                    name = ?""", (username, ))
         self.conn.commit()
         
    def BeginOtherGame(self, username):
        self.curs.execute("""UPDATE
                                playerStats 
                                SET
                                    isPlaying = 1,
                                    currGame = ""
                                WHERE 
                                    name = ?""", (username, ))
        self.conn.commit() 

    def updateAfterGame(self, name, isWinner: bool, guesses: int):
        if (isWinner):
            self.curs.execute("""UPDATE
                                    playerStats 
                                    SET
                                        Streak = Streak + 1,
                                        wonToday = ?,
                                        NumGamesPlayed = NumGamesPlayed + 1,
                                        NumGamesWon = NumGamesWon + 1,
                                        NumberOfGuesses = ? + NumberOfGuesses,
                                        doneWithFirst = 1,
                                        isPlaying = 0
                                    WHERE 
                                        name = ?""", ("True", guesses, name, ))

        else:
            self.curs.execute("""UPDATE
                                    playerStats
                                    SET
                                        Streak = 0,
                                        NumGamesPlayed = NumGamesPlayed + 1,
                                        NumberOfGuesses = ? + NumberOfGuesses,
                                        doneWithFirst = 1,
                                        isPlaying = 0
                                    WHERE
                                        name = ?""", (guesses + 1, name,))

        self.conn.commit()
    
    def appendGuess(self, word, username):
        guesses = self.getGuessesString(username) 
        guesses += word + ","
        self.curs.execute("""UPDATE
                                    playerStats 
                                    SET
                                        currGame = ?
                                    WHERE 
                                        name = ?""", (guesses, username, ))
        self.conn.commit()
        
    def dailyReset(self):
        self.curs.execute("""
                          UPDATE playerStats
                            SET Streak = 0
                            WHERE
                                wonToday = "False"
                          """)
        self.curs.execute("""
                          UPDATE playerStats
                            SET
                                wonToday = "False",
                                currGame = "",
                                doneWithFirst = 0,
                                isPlaying = 0
                            
                          """)
        self.conn.commit()
        
    def resetGame(self):
        self.curs.execute("""
                          UPDATE playerStats
                            SET
                                wonToday = "False",
                                currGame = "",
                                doneWithFirst = 0,
                                isPlaying = 0
                            
                          """)
        self.conn.commit()
        
    def differentDayReboot(self):
        self.curs.execute("""
                          UPDATE playerStats
                            SET
                                wonToday = "False",
                                currGame = "",
                                doneWithFirst = 0,
                                isPlaying  = 0
                          """)
        self.conn.commit()
        
    def getPrompt(self, userName):
        self.curs.execute("""select
                                prompt
                            FROM
                                playerStats
                            WHERE
                                name = ?""", (userName,))
        output = self.curs.fetchone()
        return output[0]

    def setPrompt(self, userName, inPrompt):
        self.curs.execute("""UPDATE
                                    playerStats
                                    SET
                                        prompt = ?
                                    WHERE
                                        name = ?""", (inPrompt, userName,))
        self.conn.commit()

    def addColumnWithDefaultValue(self, columnName, type, default):
        self.curs.execute("ALTER TABLE playerStats ADD COLUMN " + columnName + type)
        self.curs.execute("""
                          UPDATE playerStats
                            SET ? = ?
                          """, (columnName, default))
        self.conn.commit()

    def removeCol(self, columnName):
        self.curs.execute("ALTER TABLE playerStats DROP " + columnName)
        self.conn.commit()
        
    def setHardMode(self, on: int, username: str):

        self.curs.execute("""UPDATE
                                    playerStats
                                    SET
                                        hardmode = ?
                                    WHERE
                                        name = ?""", (on, username,))
        self.conn.commit()

    def getHardmode(self, userName) -> bool:
        self.curs.execute("""select
                                hardmode
                            FROM
                                playerStats
                            WHERE
                                name = ?""", (userName,))
        output = self.curs.fetchone()[0]
        return  output == 1
       
        
    def getIsPlaying(self, userName) -> bool:
        self.curs.execute("""select
                                isPlaying
                            FROM
                                playerStats
                            WHERE
                                name = ?""", (userName,))
        output = self.curs.fetchone()[0]
        if output == 1:
            return True
        else:
            return False
    #doneWithFirst
    def getDoneWithFirst(self, userName) -> bool:
        self.curs.execute("""select
                                doneWithFirst
                            FROM
                                playerStats
                            WHERE
                                name = ?""", (userName,))
        output = self.curs.fetchone()[0]
        return output == 1
            
    
    def getGuessesString(self, userName) -> str:
        self.curs.execute("""select
                                currGame
                            FROM
                                playerStats
                            WHERE
                                name = ?""", (userName,))
        output = self.curs.fetchone()[0]
        return output
    def getGuessesList(self, userName)->list:
        guessStr = self.getGuessesString(userName)
        guessStr = guessStr[:-1]
        return guessStr.split(",")

if __name__ == '__main__':
    wsql = WordleSQL("playStats.db")
    
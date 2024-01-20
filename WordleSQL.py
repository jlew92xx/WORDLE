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
                "A nonsensical hero name", "Batman")
            params = (name, 0, 0, 0, 0, "False", characterName, 0)
            self.curs.execute(
                "INSERT OR IGNORE INTO playerStats VALUES(?,?,?,?,?,?,?,?)", params)
            self.conn.commit()

    def printTableToConsole(self):
        self.curs.execute("SELECT * FROM playerStats")
        print(self.curs.fetchall())

    def updateAfterGame(self, name, isWinner: bool, guesses: int):
        if (isWinner):
            self.curs.execute("""UPDATE
                                    playerStats 
                                    SET
                                    Streak = Streak + 1,
                                    wonToday = ?,
                                    NumGamesPlayed = NumGamesPlayed + 1,
                                    NumGamesWon = NumGamesWon + 1,
                                    NumberOfGuesses = ? + NumberOfGuesses
                                    WHERE 
                                        name = ?""", ("True", guesses, name, ))

        else:
            self.curs.execute("""UPDATE
                                    playerStats
                                    SET
                                        Streak = 0,
                                        NumGamesPlayed = NumGamesPlayed + 1,
                                        NumberOfGuesses = ? + NumberOfGuesses
                                    WHERE
                                        name = ?""", (guesses + 1, name,))

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
                            SET wonToday = "False"
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

    def addColumnWithDefaultValue(self, columnName, default):
        # self.curs.execute("""ALTER TABLE playerStats
        #                             ADD hardmode integer;
        #                   """)
        self.curs.execute("""UPDATE
                                    playerStats
                                    SET
                                        hardmode = ?""", (default,))
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
        if output == 1:
            return True
        else:
            return False


if __name__ == '__main__':
    wsql = WordleSQL()
    wsql.setPrompt("ellily", "kawaii girl")

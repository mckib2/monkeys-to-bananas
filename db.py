"""Database abstraction layer."""

from typing import Dict, Union, List
import sqlite3
import pathlib
import logging
logger = logging.getLogger('m2b-database')

DB_FILE = 'm2b.db'


def initialize():
    logger.info('Starting DB initialization')
    if pathlib.Path(DB_FILE).exists():
        logger.info(f'Deleting {DB_FILE}')
        pathlib.Path(DB_FILE).unlink()
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()

        # Create tables
        cur.execute("CREATE TABLE users (userName text PRIMARY KEY, startTime text, gameCode text, gameRole text, isAccepted INTEGER)")
        cur.execute("CREATE TABLE games (gameCode text PRIMARY KEY, gameCreated text, gameStarted INTEGER, redDeck text, greenDeck text)")

        # Insert a test user into the users table
        cur.execute("INSERT INTO users (userName, startTime, gameCode, gameRole, isAccepted) VALUES ('abc', '12:00:00 November 7, 2021', 'testGame', 'player', 0)")

        # Insert a test game into the games table
        cur.execute("INSERT INTO games (gameCode, gameCreated, gameStarted) VALUES ('testGame', '12:00:00 November 7, 2021', 1)")


def addGame(aGameObject: Dict[str, Union[str, int]]):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO games (gameCode, gameCreated, gameStarted) VALUES (?, ?, ?)"
        cur = con.cursor()
        # cur.execute("INSERT INTO games (gameCode, gameCreated, gameStarted) VALUES ('?', '?', '?')", (aGameObject["gameCode"], aGameObject["gameOwner"], aGameObject["gameCreated"], aGameObject["gameStarted"]))
        cur.execute(ins, (aGameObject["gameCode"], aGameObject["gameCreated"], aGameObject["gameStarted"]))


def addUser(aUserObject: Dict[str, Union[str, int]]):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO users (username, startTime, gameCode, gameRole) VALUES (?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(ins, (aUserObject["userName"], aUserObject["startTime"], aUserObject["gameCode"], aUserObject["gameRole"]))


def addUserToGame(aUserName: str, aGameRole: str, aGameCode: str, anAcceptanceValue: int):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = ?, gameRole = ?, isAccepted = ? WHERE userName = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, aGameRole, anAcceptanceValue, aUserName))


def existsGameCode(aGameCode: str) -> bool:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numGameCodes FROM games WHERE gameCode = ?", (aGameCode,))
        tempRow = cur.fetchall()
        if int(tempRow[0][0]) > 0:
            return True
        else:
            return False


def existsUserName(aUserName: str) -> bool:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(userName) AS numUserNames FROM users WHERE userName = ?", (aUserName,))
        tempRow = cur.fetchall()
        if int(tempRow[0][0]) > 0:
            return True
        else:
            return False


def getAcceptedPlayers(aGameCode: str) -> List:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE gameCode = ? AND isAccepted != 0", (aGameCode,))
        return cur.fetchall()


def getGameCode(aUserName: str) -> str:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameCode FROM users WHERE userName = ?", (aUserName,))
        tempRow = cur.fetchall()
        return tempRow[0][0]


def getGame(aGameCode: str) -> List:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM games WHERE gameCode = ?", (aGameCode,))
        return cur.fetchall()


def getGames() -> List:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM games")
        return cur.fetchall()


def getGameStartedStatus(aGameCode: str) -> bool:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameStarted FROM games WHERE gameCode = ?", (aGameCode,))
        tempRow = cur.fetchall()
        return tempRow[0][0]


def getNumActiveGames() -> int:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numActiveGames FROM games")
        tempRow = cur.fetchall()
        return tempRow[0][0]


def getNumPlayersInGame(aGameCode: str) -> int:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numPlayers FROM users WHERE gameCode = ?", (aGameCode,))
        tempRow = cur.fetchall()
        return tempRow[0][0]


def getPlayers(aGameCode: str) -> List:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE gameCode = ? ORDER BY userName ASC", (aGameCode,))
        return cur.fetchall()


def getUsers() -> List:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        return cur.fetchall()


def getUserGame(aUserName: str) -> str:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameCode FROM users WHERE userName = ?", (aUserName,))
        tempRow = cur.fetchall()
        return tempRow[0][0]


def removeUser(aUserName: str):
    con = sqlite3.connect(DB_FILE)
    with con:
        rem = "DELETE FROM users WHERE userName = ?"
        cur = con.cursor()
        cur.execute(rem, (aUserName,))


def removeUserFromGame(aUserName: str, aGameCode: str):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = ?, isAccepted = 0 WHERE userName = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, aUserName))


def setGameDeck(aGameCode: str, aColor: str, aString: str):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = f"UPDATE games SET {aColor}Deck = ? WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aString, aGameCode))

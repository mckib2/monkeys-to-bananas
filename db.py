'''Database abstraction layer.'''

import json
import random
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
        cur.execute("CREATE TABLE users (userName text PRIMARY KEY, startTime text, gameCode text, gameRole text, isAccepted INTEGER, userRedHand text, playedRedCard INTEGER)")
        cur.execute("CREATE TABLE games (gameCode text PRIMARY KEY, gameCreated text, gameStarted INTEGER, redDeck text, greenDeck text, currentJudge INTEGER, currentGreenCard INTEGER)")

        # Insert a test user into the users table
        cur.execute("INSERT INTO users (userName, startTime, gameCode, gameRole, isAccepted) VALUES ('abc', '12:00:00 November 7, 2021', 'testGame', 'player', 0)")

        # Insert a test game into the games table
        cur.execute("INSERT INTO games (gameCode, gameCreated, gameStarted) VALUES ('testGame', '12:00:00 November 7, 2021', 1)")





def addGame(aGameObject):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO games (gameCode, gameCreated, gameStarted, currentJudge) VALUES ('{}', '{}', '{}', 0)".format(aGameObject["gameCode"], aGameObject["gameCreated"], aGameObject["gameStarted"])
        cur = con.cursor()
        cur.execute(ins)

def addUser(aUserObject):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO users (username, startTime, gameCode, gameRole) VALUES ('{}', '{}', '{}', '{}')".format(aUserObject["userName"], aUserObject["startTime"], aUserObject["gameCode"], aUserObject["gameRole"])
        cur = con.cursor()
        cur.execute(ins)

def addUserToGame(aUserName, aGameRole, aGameCode, anAcceptanceValue):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = '{}', gameRole = '{}', isAccepted = {}, userRedHand = '[]' WHERE userName = '{}'".format(aGameCode, aGameRole, anAcceptanceValue, aUserName)
        cur = con.cursor()
        cur.execute(upd)

def dealGreenCard(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()

        cur.execute("SELECT greenDeck FROM games WHERE gameCode = '{}'".format(aGameCode))
        greenDeckText = cur.fetchall()[0][0]
        greenDeck = json.loads(greenDeckText)

        newCard = greenDeck.pop(0)

        cur.execute("UPDATE games SET currentGreenCard = {}, greenDeck = '{}' WHERE gameCode = '{}'".format(newCard, json.dumps(greenDeck), aGameCode))

def dealRedCard(aUserName, aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()

        cur.execute("SELECT redDeck FROM games WHERE gameCode = '{}'".format(aGameCode))
        redDeckText = cur.fetchall()[0][0]
        print("In dealRedCard(); redDeckText = {}".format(redDeckText))
        redDeck = json.loads(redDeckText)

        cur.execute("SELECT userRedHand FROM users WHERE userName = '{}'".format(aUserName))
        playerHandText = cur.fetchall()[0][0]
        playerHand = json.loads(playerHandText)

        # newCard = redDeck.pop(random.randrange(0, len(redDeck)))
        newCard = redDeck.pop(0)
        playerHand.append(newCard)

        cur.execute("UPDATE users SET userRedHand = '{}' WHERE userName = '{}'".format(json.dumps(playerHand), aUserName))
        cur.execute("UPDATE games SET redDeck = '{}' WHERE gameCode = '{}'".format(json.dumps(redDeck), aGameCode))

def existsGameCode(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numGameCodes FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        if int(tempRow[0][0]) > 0:
            return True
        else:
            return False

def existsUserName(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(userName) AS numUserNames FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        if int(tempRow[0][0]) > 0:
            return True
        else:
            return False

def getAcceptedPlayers(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE gameCode = '{}' AND isAccepted != 0".format(aGameCode))
        return cur.fetchall()

def getCurrentGreenCard(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT currentGreenCard FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getCurrentJudge(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT currentJudge FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getGameCode(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameCode FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getGame(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM games WHERE gameCode = '{}'".format(aGameCode))
        return cur.fetchall()

def getGameRole(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameRole FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getGames():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM games")
        return cur.fetchall()

def getGameStartedStatus(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameStarted FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getNumActiveGames():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numActiveGames FROM games")
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getNumPlayersInGame(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numPlayers FROM users WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getPlayerRedHand(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT userRedHand FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getPlayers(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE gameCode = '{}' ORDER BY userName ASC".format(aGameCode))
        return cur.fetchall()

def getUsers():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        return cur.fetchall()

def getUserGame(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameCode FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def removeUser(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        rem = "DELETE FROM users WHERE userName = '{}'".format(aUserName)
        cur = con.cursor()
        cur.execute(rem)

def removeUserFromGame(aUserName, aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = '{}', isAccepted = 0 WHERE userName = '{}'".format(aGameCode, aUserName)
        cur = con.cursor()
        cur.execute(upd)

def setCurrentJudge(aGameCode, aCurrentJudge):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET currentJudge = {} WHERE gameCode = '{}'".format(aCurrentJudge, aGameCode)
        cur = con.cursor()
        cur.execute(upd)

def setGameDeck(aGameCode, aColor, aString):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET {}Deck = '{}' WHERE gameCode = '{}'".format(aColor, aString, aGameCode)
        cur = con.cursor()
        cur.execute(upd)

def setGameStartedStatus(aGameCode, aStatus):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET gameStarted = {} WHERE gameCode = '{}'".format(aStatus, aGameCode)
        cur = con.cursor()
        cur.execute(upd)

def setPlayerRedCardPlayed(aUserName, aRedCardIndex):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET redCardPlayed = {} WHERE userName = '{}'".format(aRedCardIndex, aUserName)
        cur = con.cursor()
        cur.execute(upd)

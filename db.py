'''Database abstraction layer.'''

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
        cur.execute("CREATE TABLE users (userName text PRIMARY KEY, startTime text, gameCode text, gameRole text)")
        cur.execute("CREATE TABLE games (gameCode text PRIMARY KEY, gameOwner text, gameCreated text, gameStarted INTEGER)")
        cur.execute("CREATE TABLE gamePlayers (id INTEGER PRIMARY KEY, gameCode text, playerName text, playerIsAccepted INTEGER, playerRole text, playerIsReady INTEGER, playerRedCards text, playerGreenCards text)")
        cur.execute("CREATE TABLE dealedDecks (id INTEGER PRIMARY KEY, gameCode text, deckType text, cardIndex INTEGER, cardReference INTEGER)")
        cur.execute("CREATE TABLE redCards (id INTEGER PRIMARY KEY, mainText text, supportText text)")
        cur.execute("CREATE TABLE greenCards (id INTEGER PRIMARY KEY, mainText text, supportText text)")

        # Populate red card table with card definitions
        cur.execute("INSERT INTO redCards (mainText, supportText) VALUES ('peanut butter', 'creamy substance used on PB&J sandwiches')")
        cur.execute("INSERT INTO redCards (mainText, supportText) VALUES ('cottage cheese', 'last step of the dairy cycle following whole milk')")

        # Populate green card table with card definitions
        cur.execute("INSERT INTO greenCards (mainText, supportText) VALUES ('delicious', 'tastes good')")
        cur.execute("INSERT INTO greenCards (mainText, supportText) VALUES ('slimy', 'like a viscous liquid')")

        # Insert a test user into the users table
        cur.execute("INSERT INTO users (userName, startTime, gameCode, gameRole) VALUES ('abc', '12:00:00 November 7, 2021', 'testGame', 'player')")

def addGame(aGameObject):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO games (gameCode, gameOwner, gameCreated, gameStarted) VALUES ('{}', '{}', '{}', '{}')".format(aGameObject["gameCode"], aGameObject["gameOwner"], aGameObject["gameCreated"], aGameObject["gameStarted"])
        cur = con.cursor()
        cur.execute(ins)

def addUser(aUserObject):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO users (username, startTime, gameCode, gameRole) VALUES ('{}', '{}', '{}', '{}')".format(aUserObject["userName"], aUserObject["startTime"], aUserObject["gameCode"], aUserObject["gameRole"])
        cur = con.cursor()
        cur.execute(ins)

def addUserToGame(aUserName, aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = {} WHERE userName = {}".format(aGameCode, aUserName)
        cur = con.cursor()
        cur.execute(upd)

def removeUser(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        rem = "DELETE FROM users WHERE userName = '{}'".format(aUserName)
        cur = con.cursor()
        cur.execute(rem)

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

def getGames():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM games")
        return cur.fetchall()

def getNumActiveGames():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numActiveGames FROM games")
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getRedCards():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM redCards")
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
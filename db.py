"""Database abstraction layer."""

from typing import Any, Dict, Union, List
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
        cur.execute("CREATE TABLE users (userName text PRIMARY KEY, startTime text, gameCode text, gameRole text, isAccepted INTEGER, userRedHand text, redCardPlayed INTEGER, winningGreenCards text)")
        '''
            {
                "userName": text,           # "brian" | "mindy"
                "startTime": text,          # "Date and time string"
                "gameCode": text,           # "myCoolGameCode"
                "gameRole": text,           # "player" | "owner"
                "isAccepted": INTEGER,      # 0 = false, 1 = true
                "userRedHand": text,        # [ ##, ##, ##, ##, ## ]
                "redCardPlayed": INTEGER,   # number which is an index in carddecks.redCards where the card is defined
                "winningGreenCards": text   # [ ##, ##, ## ]
            }
        '''
        cur.execute("CREATE TABLE games (gameCode text PRIMARY KEY, gameCreator text, gameCreated text, gameStarted INTEGER, redDeck text, greenDeck text, currentJudge INTEGER, currentGreenCard INTEGER, redCardWinner INTEGER, discardedRedCards text, judgeAdvanced INTEGER, finishedPlayers text)")
        '''
            {
                "gameCode": text,           # "myCoolGameCode"
                "gameCreator": text,        # "userName"
                "gameCreated": text,        # "Date and time string"
                "gameStarted": INTEGER,     # 0 = false, 1 = true
                "redDeck": text,            # [ ##, ##, ##, ..., ## ] where numbers are indexes in carddecks.redCards where the cards are defined
                "greenDeck": text,          # [ ##, ##, ##, ..., ## ] where numbers are indexes in carddecks.greenCards where the cards are defined
                "currentJudge": INTEGER,    # number which is an index of the response to "SELECT userName FROM users WHERE gameCode = 'myCoolGameCode'"
                "currentGreenCard": INTEGER,# number which is an index in carddecks.greenCards where the card is defined
                "redCardWinner": INTEGER,   # number which is an index in carddecks.redCards where the card is defined
                "discardedRedCards": text   # [ ##, ##, ##, ..., ## ] where numbers are indexes in carddecks.redCards where the cards are defined
                "judgeAdvanced": INTEGER    # 0 = false, 1 = true
                "finishedPlayers": text     # [ "playerName", "playerName", ..., "playerName" ]
            }
        '''
        # Insert a test user into the users table
        cur.execute("INSERT INTO users (userName, startTime, gameCode, gameRole, isAccepted) VALUES ('abc', '12:00:00 November 7, 2021', 'testGame', 'player', 0)")

        # Insert a test game into the games table
        cur.execute("INSERT INTO games (gameCode, gameCreated, gameStarted) VALUES ('testGame', '12:00:00 November 7, 2021', 1)")





def addFinishedPlayer(aGameCode, aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        sel = "SELECT finishedPlayers FROM games WHERE gameCode = ?"
        cur.execute(sel, aGameCode)
        tempRow = cur.fetchall()
        finishedPlayers = json.loads(tempRow[0][0])

        if aUserName not in finishedPlayers:
            finishedPlayers.append(aUserName)
            upd = "UPDATE games SET finishedPlayers = ? WHERE gameCode = ?"
            cur.execute(upd, (json.dumps(finishedPlayers), aGameCode))

def addGame(aGameObject: Dict[str, Any]):
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = '''INSERT INTO games 
                (
                    gameCode, gameCreator, gameCreated, gameStarted,
                    redDeck, greenDeck, currentJudge, currentGreenCard,
                    redCardWinner, discardedRedCards
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cur = con.cursor()
        cur.execute(ins, 
            (
                aGameObject["gameCode"], 
                aGameObject["gameCreator"], 
                aGameObject["gameCreated"], 
                aGameObject["gameStarted"], 
                aGameObject["redDeck"], 
                aGameObject["greenDeck"], 
                aGameObject["currentJudge"], 
                aGameObject["currentGreenCard"], 
                aGameObject["redCardWinner"], 
                aGameObject["discardedRedCards"]
            )
        )

def addUser(aUserObject: Dict) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        ins = "INSERT INTO users (username, startTime, gameCode, gameRole, isAccepted, userRedHand, redCardPlayed, winningGreenCards) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(ins, (aUserObject["userName"], aUserObject["startTime"], aUserObject["gameCode"], aUserObject["gameRole"], aUserObject["isAccepted"], aUserObject["userRedHand"], aUserObject["redCardPlayed"], aUserObject["winningGreenCards"]))

def addUserToGame(aUserName: str, aGameRole: str, aGameCode: str, anAcceptanceValue: str):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = ?, gameRole = ?, isAccepted = ? WHERE userName = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, aGameRole, anAcceptanceValue, aUserName))

def clearFinishedPlayers(aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET finishedPlayers = '[]' WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, ))

def clearJudgeAssignment(aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameRole = 'player' WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, ))

def clearRedCardsPlayed(aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET redCardPlayed = -1 WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, ))

def dealGreenCard(aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()

        cur.execute("SELECT greenDeck FROM games WHERE gameCode = ?", (aGameCode, ))
        greenDeckText = cur.fetchone()[0]
        greenDeck = json.loads(greenDeckText)

        newCard = greenDeck.pop(0)

        cur.execute("UPDATE games SET currentGreenCard = ?, greenDeck = ? WHERE gameCode = ?", (newCard, json.dumps(greenDeck), aGameCode))

def dealRedCard(aUserName: str, aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()

        cur.execute("SELECT redDeck FROM games WHERE gameCode = ?", (aGameCode, ))
        redDeckText = cur.fetchone()[0]
        redDeck = json.loads(redDeckText)

        cur.execute("SELECT userRedHand FROM users WHERE userName = ?", (aUserName, ))
        playerHandText = cur.fetchone()[0]
        playerHand = json.loads(playerHandText)

        newCard = redDeck.pop(0)
        playerHand.append(newCard)

        cur.execute("UPDATE users SET userRedHand = ? WHERE userName = ?", (json.dumps(playerHand), aUserName))
        cur.execute("UPDATE games SET redDeck = ? WHERE gameCode = ?", (json.dumps(redDeck), aGameCode))

def existsGameCode(aGameCode: str) -> bool:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(gameCode) AS numGameCodes FROM games WHERE gameCode = ?", (aGameCode, ))
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

def getAcceptedPlayers(aGameCode: str) -> List[str]:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT userName FROM users WHERE gameCode = ? AND isAccepted != 0", (aGameCode, ))
        returnList = [r[0] for r in cur.fetchall()]
        return returnList

def getAllGreenCardsWon(aGameCode: str) -> List [int]:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT winningGreenCards FROM users WHERE gameCode = ?", (aGameCode, ))
        returnList = []
        for subList in cur.fetchall():
            returnList += json.loads(subList[0])

        return returnList



def getCardPlayer(aGameCode, aRedCardIndex):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT userName FROM users WHERE gameCode = '{}' AND redCardPlayed = {}".format(aGameCode, aRedCardIndex))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getCurrentGreenCard(aGameCode: str) -> int:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT currentGreenCard FROM games WHERE gameCode = ?", (aGameCode, ))
        return cur.fetchone()[0]

def getCurrentJudge(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT currentJudge FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getDiscardedRedCards(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT discardedRedCards FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getFinishedPlayers(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT finishedPlayers FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getGameCode(aUserName: str) -> str:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameCode FROM users WHERE userName = ?", (aUserName, ))
        return cur.fetchone()[0]

def getGame(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM games WHERE gameCode = '{}'".format(aGameCode))
        return cur.fetchall()

def getGameCreator(aGameCode: str) -> str:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameCreator FROM games WHERE gameCode = ?", (aGameCode, ))
        return cur.fetchone()[0]

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

def getGameStartedStatus(aGameCode: str) -> int:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT gameStarted FROM games WHERE gameCode = ?", (aGameCode, ))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getJudgeAdvancedStatus(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT judgeAdvanced FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getJudgeName(aGameCode: str) -> str:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT userName FROM users WHERE gameCode = ? AND gameRole = 'judge'", (aGameCode, ))
        return cur.fetchall()[0]

def getNumActiveGames():
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
        cur.execute("SELECT COUNT(gameCode) AS numPlayers FROM users WHERE gameCode = ?", (aGameCode, ))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getPlayedRedCards(aGameCode: str) -> List[int]:
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT redCardPlayed FROM users WHERE gameCode = ? AND redCardPlayed > 0", (aGameCode, ))
        return cur.fetchall()

def getPlayerRedCardPlayed(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT redCardPlayed FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getPlayerRedHand(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT userRedHand FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getPlayers(aGameCode: str) -> List[Dict[str, Any]]:
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE gameCode = ? ORDER BY userName ASC", (aGameCode, ))

        returnList = []
        for row in cur.fetchall():
            returnList.append(dict(zip(row.keys(), row)))
            # barf

        return returnList

def getRedCardWinner(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT redCardWinner FROM games WHERE gameCode = '{}'".format(aGameCode))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getUsers():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users")
        return cur.fetchall()

def getUserWinningGreenCards(aUserName):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT winningGreenCards FROM users WHERE userName = '{}'".format(aUserName))
        tempRow = cur.fetchall()
        return tempRow[0][0]

def getWinnings(aGameCode):
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT userName, winningGreenCards FROM users WHERE gameCode = '{}'".format(aGameCode))
        return cur.fetchall()

def removeRedCardFromHand(aUserName, aRedCardIndex):
    redHand = json.loads(getPlayerRedHand(aUserName))
    redHand.pop(redHand.index(aRedCardIndex))

    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET userRedHand = '{}' WHERE userName = '{}'".format(json.dumps(redHand), aUserName)
        cur = con.cursor()
        cur.execute(upd)

def removeUser(aUserName: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        rem = "DELETE FROM users WHERE userName = ?"
        cur = con.cursor()
        cur.execute(rem, (aUserName, ))

def removeUserFromGame(aUserName: str, aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = ?, isAccepted = 0 WHERE userName = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, aUserName))

def setCurrentJudge(aGameCode: str, aPlayerIndex: int, aUserName: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET currentJudge = ? WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aPlayerIndex, aGameCode))
        upd = "UPDATE users SET gameRole = 'judge' WHERE userName = ?"
        cur.execute(upd, (aUserName, ))

def setDiscardedRedCards(aGameCode, aStringifiedList):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET discardedRedCards = '{}' WHERE gameCode = '{}'".format(aStringifiedList, aGameCode)
        cur = con.cursor()
        cur.execute(upd)

def setGameDeck(aGameCode: str, aColor: str, aStringifiedList: str):
    con = sqlite3.connect(DB_FILE)
    with con:
        deckName = "redDeck" if aColor == "red" else "greenDeck"
        upd = f"UPDATE games SET {deckName} = ? WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aStringifiedList, aGameCode))

def setGameStartedStatus(aGameCode: str, aStatus: int) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET gameStarted = ? WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aStatus, aGameCode))

def setJudgeAdvanced(aGameCode: str, aStatus: int) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET judgeAdvanced = ? WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aStatus, aGameCode))

def setPlayerRedCardPlayed(aUserName, aRedCardIndex):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET redCardPlayed = {} WHERE userName = '{}'".format(aRedCardIndex, aUserName)
        cur = con.cursor()
        cur.execute(upd)

def setRedCardWinner(aGameCode: str, aRedCardIndex: int) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE games SET redCardWinner = ? WHERE gameCode = ?"
        cur = con.cursor()
        cur.execute(upd, (aRedCardIndex, aGameCode))

def setUserGameCode(aUserName: str, aGameCode: str) -> None:
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameCode = ? WHERE userName = ?"
        cur = con.cursor()
        cur.execute(upd, (aGameCode, aUserName))

def setUserGameRole(aUserName, aGameRole):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET gameRole = '{}' WHERE userName = '{}'".format(aGameRole, aUserName)
        cur = con.cursor()
        cur.execute(upd)

def setUserWinningGreenCards(aUserName, aStringifiedList):
    con = sqlite3.connect(DB_FILE)
    with con:
        upd = "UPDATE users SET winningGreenCards = '{}' WHERE userName = '{}'".format(aStringifiedList, aUserName)
        cur = con.cursor()
        cur.execute(upd)

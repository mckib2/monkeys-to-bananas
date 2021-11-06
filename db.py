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
        cur.execute("CREATE TABLE users (userName text PRIMARY KEY, startTime text, gameId text, gameRole text)")
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


def get_games():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("select * from games")
        return cur.fetchall()

def getNumActiveGames():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(id) AS numActiveGames FROM games")
        tempRow = cur.fetchall()
        return tempRow[0][0]

def get_redCards():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("select * from redCards")
        return cur.fetchall()



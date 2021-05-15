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
        cur.execute("CREATE TABLE games (id INTEGER PRIMARY KEY, keyword text, ownerid INTEGER)")
        cur.execute("CREATE TABLE players (id INTEGER PRIMARY KEY, username text, gameid INTEGER, approved INTEGER")
        cur.execute("INSERT INTO games (keyword) VALUES ('myCoolKeyword')")


def get_games():
    con = sqlite3.connect(DB_FILE)
    with con:
        cur = con.cursor()
        cur.execute("select * from games")
        return cur.fetchall()

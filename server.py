'''Server application.'''

import sqlite3
import logging
import pathlib

from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)
DB_FILE = 'm2b.db'


@app.route('/')
def hello_world():
    return str(DB.get_games())


class DB:
    @classmethod
    def _init_db(self):
        logger.info('Starting DB initialization')
        if pathlib.Path(DB_FILE).exists():
            logger.info(f'Deleting {DB_FILE}')
            pathlib.Path(DB_FILE).unlink()
        con = sqlite3.connect(DB_FILE)
        with con:
            cur = con.cursor()

            # Create tables
            cur.execute("CREATE TABLE games (id INTEGER PRIMARY KEY, keyword text)")
            cur.execute("INSERT INTO games (keyword) VALUES ('myCoolKeyword')")

    @classmethod
    def get_games(self):
        con = sqlite3.connect(DB_FILE)
        with con:
            cur = con.cursor()
            cur.execute("select * from games")
            return cur.fetchall()

# on start
DB._init_db()

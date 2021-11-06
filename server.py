'''Server application.'''

import logging
from flask import Flask, render_template
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)

# on start
maxActiveGames = 10
maxNumPlayers = 10
db.initialize()


@app.route('/')
'''
def splash_page():
    infoForSplashPage = {
        "games":db.get_games(),
        "maxActiveGames":maxActiveGames
    }
    # return render_template('splash.html', games=db.get_games())
    return render_template('splash.html', info=infoForSplashPage)
'''
def index():
    infoForIndexPage = {
        "redCards": db.get_redCards(),
        "maxActiveGames": maxActiveGames
    }
    return render_template()

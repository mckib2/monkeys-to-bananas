'''Server application.'''

import logging
from flask import Flask, render_template
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)


@app.route('/')
def splash_page():
    return render_template('splash.html', games=db.get_games())


# on start
maxActiveGames = 10
maxNumPlayers = 10
db.initialize()

print ("Current number of active games: " + db.getNumActiveGames())

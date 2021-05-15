'''Server application.'''

import logging
from flask import Flask, render_template
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)


@app.route('/')
def splash_page():
    infoForSplashPage = {
        "bootstrapInfo":bootstrapInfo,
        "games":db.get_games(),
        "maxActiveGames":maxActiveGames
    }
    # return render_template('splash.html', games=db.get_games())
    return render_template('splash.html', info=infoForSplashPage)

# on start
maxActiveGames = 10
maxNumPlayers = 10
bootstrapInfo = {
    "head":[
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/css/bootstrap.min.css' rel='stylesheet' integrity='sha384-+0n0xVW2eSR5OomGNYDnhzAbDsOXxcvSN1TPprVMTNDbiYZCxYbOOl7+AMvyTG2x' crossorigin='anonymous'>"
    ],
    "body":[
        "<script src='https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js' integrity='sha384-gtEjrD/SeCtmISkJkNUaaKMoLD0//ElJ19smozuHV6z3Iehds+3Ulb9Bn9Plx0x4' crossorigin='anonymous'></script>"
    ]
}
db.initialize()

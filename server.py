'''Server application.'''

import logging
from flask import Flask, render_template, request, redirect
import db
import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)

# on start
maxActiveGames = 10
maxNumPlayers = 8
minUserNameCharacters = 3
minGameCodeCharacters = 3
legalInputCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

db.initialize()

@app.route('/', methods=[ 'post', 'get' ])
def index():
    infoForIndexPage = {
        "numActiveGames": db.getNumActiveGames(),
        "maxActiveGames": maxActiveGames,
        "minUserNameCharacters": minUserNameCharacters,
        "legalInputCharacters": legalInputCharacters
    }

    if request.method == 'POST':
        userName = request.form.get('userName')
        if len(userName) < minUserNameCharacters:
            infoForIndexPage['errorMessage'] = 'User name must have at least {} characters'.format(minUserNameCharacters)
        else:
            isLegal = True
            i = 0
            while i < len(userName) and isLegal == True:
                if legalInputCharacters.find(userName[i]) == -1:
                    isLegal = False
                else:
                    i = i + 1

            if isLegal == False:
                infoForIndexPage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsUserName(userName) == True:
                    infoForIndexPage['errorMessage'] = 'That user name already exists'
                else:
                    now = datetime.datetime.now()
                    newUser = {
                        'userName': userName,
                        'startTime': str(now),
                        'gameCode': '',
                        'gameRole': ''
                    }
                    db.addUser(newUser)
                    return redirect(f'gameDecide/{userName}')
    
    if 'errorMessage' in infoForIndexPage:
        infoForIndexPage['previousUserNameEntry'] = request.form.get('userName')

    return render_template('index.html', info=infoForIndexPage)

@app.route('/gameDecide/<aUserName>')
def gameDecide(aUserName):
    userList = db.getUsers()
    returnString = "gameDecide was fed: {}<br>".format(aUserName)
    returnString += "User list:<br><hr>"
    returnString += json.dumps(userList)

    infoForGameDecide = {
        'aUserName': aUserName
    }

    return render_template('gameDecide.html', info=infoForGameDecide)

@app.route('/signOut/<aUserName>')
def signOut(aUserName):
    db.removeUser(aUserName)
    return redirect(f'/')

@app.route('/createGame/<aUserName>')
def createGame(aUserName):
    userGame = db.getUserGame(aUserName)
    if len(userGame) != 0:
        # user is already part of a game
        # need to figure out where to send them at this point
    else:
        infoForCreateGamePage = {
            "aUserName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        }

        return render_template('createGame.html', info=infoForCreateGamePage)

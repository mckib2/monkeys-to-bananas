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
                        'gameRole': '',
                        'isAccepted': 0
                    }
                    db.addUser(newUser)
                    return redirect(f'gameDecide/{userName}')
    
    if 'errorMessage' in infoForIndexPage:
        infoForIndexPage['previousUserNameEntry'] = request.form.get('userName')

    return render_template('index.html', info=infoForIndexPage)

@app.route('/showDB')
def showDB():
    infoForShowDBPage = {
        "tableNames": [ "users", "games" ],
        "users": db.getUsers(),
        "games": db.getGames()
    }
    return render_template('showDB.html', info=infoForShowDBPage)

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

@app.route('/createGame/<aUserName>', methods=[ 'post', 'get' ])
def createGame(aUserName):
    userGame = db.getUserGame(aUserName)
    if len(userGame) == 0:
        infoForCreateGamePage = {
            "aUserName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        }

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < minGameCodeCharacters:
            infoForCreateGamePage['errorMessage'] = 'Game code must have at least {} characters'.format(minGameCodeCharacters)
        else:
            isLegal = True
            i = 0
            while i < len(gameCode) and isLegal == True:
                if legalInputCharacters.find(gameCode[i]) == -1:
                    isLegal = False
                else:
                    i = i + 1

            if isLegal == False:
                infoForCreateGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode) == True:
                    infoForCreateGamePage['errorMessage'] = 'That game code already exists'
                else:
                    now = datetime.datetime.now()
                    newGame = {
                        'gameCode': gameCode,
                        'gameCreated': str(now),
                        'gameStarted': 0
                    }
                    db.addGame(newGame)
                    db.addUserToGame(aUserName, 'owner', gameCode, 1)
                    return redirect(f'/gameOwnerWait/{aUserName}')
        
    
    if 'errorMessage' in infoForCreateGamePage:
        infoForCreateGamePage['previousGameCodeEntry'] = gameCode
    
    return render_template('createGame.html', info=infoForCreateGamePage)

@app.route('/gameOwnerWait/<gameOwner>')
def gameOwnerWait(gameOwner):
    userGame = db.getUserGame(gameOwner)
    players = db.getPlayers(userGame)

    infoForGameOwnerWaitPage = {
        'ownerName': gameOwner,
        'gameCode': db.getGameCode(gameOwner),
        'players': players,
        'numPlayers': len(players)
    }

    return render_template('gameOwnerWait.html', info=infoForGameOwnerWaitPage)
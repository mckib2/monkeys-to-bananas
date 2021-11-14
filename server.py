'''Server application.'''

import logging
from flask import Flask, render_template, request, redirect
import db
import carddecks
import datetime
import json
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)

# on start
maxActiveGames = 10
minNumPlayers = 3
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
        "tableNames": [ "users", "games", "redCards", "greenCards" ],
        "users": db.getUsers(),
        "games": db.getGames(),
        "redCards": carddecks.redCards,
        "greenCards": carddecks.greenCards
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

@app.route('/gameOwnerWait/<gameOwner>', methods=[ 'post', 'get' ])
def gameOwnerWait(gameOwner):
    userGame = db.getUserGame(gameOwner)

    if request.method == 'POST':
        if request.form.get('actionToTake') == 'admit':
            db.addUserToGame(request.form.get('admittee'), 'player', userGame, 1)
        else:
            db.removeUserFromGame(request.form.get('removee'), userGame)

    players = db.getPlayers(userGame)
    acceptedPlayers = db.getAcceptedPlayers(userGame)
    numPlayersNotAccepted = len(players) - len(acceptedPlayers)

    infoForGameOwnerWaitPage = {
        'ownerName': gameOwner,
        'gameCode': db.getGameCode(gameOwner),
        'players': players,
        'numAcceptedPlayers': len(acceptedPlayers),
        'numPlayersNotAccepted': numPlayersNotAccepted,
        'minNumPlayers': minNumPlayers,
        'maxNumPlayers': maxNumPlayers
    }

    return render_template('gameOwnerWait.html', info=infoForGameOwnerWaitPage)

@app.route('/gamePlayerWait/<aUserName>', methods=[ 'post', 'get' ])
def gamePlayerWait(aUserName):
    userGame = db.getUserGame(aUserName)

    if request.method == 'POST':
        if request.form.get('actionToTake') == 'leave':
            db.removeUserGame(aUserName, userGame)
            return redirect('/gameDecide/{aUserName}')

    players = db.getPlayers(userGame)
    infoForGamePlayerWaitPage = {
        'playerName': aUserName,
        'gameCode': userGame,
        'players': players,
        'numPlayers': len(players)
    }

    return render_template('gamePlayerWait.html', info=infoForGamePlayerWaitPage)

@app.route('/joinGame/<aUserName>', methods=[ 'post', 'get' ])
def joinGame(aUserName):
    userGame = db.getUserGame(aUserName)
    if len(userGame) == 0:
        infoForJoinGamePage = {
            "aUserName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        }

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < minGameCodeCharacters:
            infoForJoinGamePage['errorMessage'] = 'Game code must have at least {} characters'.format(minGameCodeCharacters)
        else:
            isLegal = True
            i = 0
            while i < len(gameCode) and isLegal == True:
                if legalInputCharacters.find(gameCode[i]) == -1:
                    isLegal = False
                else:
                    i = i + 1

            if isLegal == False:
                infoForJoinGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode) == True:
                    if db.getGameStartedStatus(gameCode):
                        infoForJoinGamePage['errorMessage'] = 'That game is already in progress'
                    elif db.getNumPlayersInGame(gameCode) > maxNumPlayers:
                        infoForJoinGamePage['errorMessage'] = 'Too many players in that game'
                    else:
                        now = datetime.datetime.now()
                        db.addUserToGame(aUserName, 'player', gameCode, 0)
                        return redirect(f'/gamePlayerWait/{aUserName}')
                else:
                    infoForJoinGamePage['errorMessage'] = 'That game does not exist'

    if 'errorMessage' in infoForJoinGamePage:
        infoForJoinGamePage['previousGameCodeEntry'] = gameCode
    
    return render_template('joinGame.html', info=infoForJoinGamePage)

@app.route('/initGame/<aUserName>')
def initGame(aUserName):
    gameCode = db.getUserGame(aUserName)
    if not db.getGameStartedStatus(gameCode):
        # make a shuffled red deck
        indexes = []
        for number in range(len(carddecks.redCards)):
            indexes.append(number)
        
        gameRedDeck = []
        for index in range(len(indexes)):
            newIndex = indexes.pop(random.randrange(0, len(indexes)))
            gameRedDeck.append(newIndex)

        db.setGameDeck(gameCode, "red", json.dumps(gameRedDeck))

        # make a shuffled green deck
        indexes = []
        for number in range(len(carddecks.greenCards)):
            indexes.append(number)

        gameGreenDeck = []
        for index in range(len(indexes)):
            newIndex = indexes.pop(random.randrange(0, len(indexes)))
            gameGreenDeck.append(newIndex)

        db.setGameDeck(gameCode, "green", json.dumps(gameGreenDeck))

        # give all accepted players 5 random red cards
        # assign 'judge' to first player
        # give 'judge' a random green card
        # start turn

        return 0
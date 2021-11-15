"""Server application."""

import logging
from flask import Flask, render_template, request, redirect
import db
import carddecks
import datetime
import json
import random
import string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)

# on start
maxActiveGames = 10
minNumPlayers = 3
maxNumPlayers = 8
minUserNameCharacters = 3
minGameCodeCharacters = 3
legalInputCharacters = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)

db.initialize()


@app.route('/', methods=['post', 'get'])
def index():
    infoForIndexPage = {
        "numActiveGames": db.getNumActiveGames(),
        "maxActiveGames": maxActiveGames,
        "minUserNameCharacters": minUserNameCharacters,
        "legalInputCharacters": legalInputCharacters,
    }

    if request.method == 'POST':
        userName = request.form.get('userName')
        if len(userName) < minUserNameCharacters:
            infoForIndexPage['errorMessage'] = f"User name must have at least {minUserNameCharacters} characters"
        else:
            if not userName.isalnum():
                infoForIndexPage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsUserName(userName):
                    infoForIndexPage['errorMessage'] = 'That user name already exists'
                else:
                    now = datetime.datetime.now()
                    newUser = {
                        'userName': userName,
                        'startTime': str(now),
                        'gameCode': '',
                        'gameRole': '',
                        'isAccepted': 0,
                    }
                    db.addUser(newUser)
                    return redirect(f'gameDecide/{userName}')
    
    if 'errorMessage' in infoForIndexPage:
        infoForIndexPage['previousUserNameEntry'] = request.form.get('userName')

    return render_template('index.html', info=infoForIndexPage)


@app.route('/showDB')
def showDB():
    infoForShowDBPage = {
        "tableNames": ["users", "games", "redCards", "greenCards"],
        "users": db.getUsers(),
        "games": db.getGames(),
        "redCards": carddecks.redCards,
        "greenCards": carddecks.greenCards,
    }
    return render_template('showDB.html', info=infoForShowDBPage)


@app.route('/gameDecide/<aUserName>')
def gameDecide(aUserName: str):
    userList = db.getUsers()
    returnString = f"gameDecide was fed: {aUserName}<br>"
    returnString += "User list:<br><hr>"
    returnString += json.dumps(userList)

    infoForGameDecide = {
        'aUserName': aUserName
    }

    return render_template('gameDecide.html', info=infoForGameDecide)


@app.route('/signOut/<aUserName>')
def signOut(aUserName: str):
    db.removeUser(aUserName)
    return redirect('/')


@app.route('/createGame/<aUserName>', methods=['post', 'get'])
def createGame(aUserName: str):
    userGame = db.getUserGame(aUserName)
    if not userGame:
        infoForCreateGamePage = {
            "aUserName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        }
    else:
        infoForCreateGamePage = {}

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < minGameCodeCharacters:
            infoForCreateGamePage['errorMessage'] = f"Game code must have at least {minGameCodeCharacters} characters"
        else:
            if not gameCode.isalnum():
                infoForCreateGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode):
                    infoForCreateGamePage['errorMessage'] = 'That game code already exists'
                else:
                    now = datetime.datetime.now()
                    newGame = {
                        'gameCode': gameCode,
                        'gameCreated': str(now),
                        'gameStarted': 0,
                    }
                    db.addGame(newGame)
                    db.addUserToGame(aUserName, 'owner', gameCode, 1)
                    return redirect(f'/gameOwnerWait/{aUserName}')

    if 'errorMessage' in infoForCreateGamePage:
        infoForCreateGamePage['previousGameCodeEntry'] = gameCode  # TODO: what if GET?
    
    return render_template('createGame.html', info=infoForCreateGamePage)


@app.route('/gameOwnerWait/<gameOwner>', methods=['post', 'get'])
def gameOwnerWait(gameOwner: str):
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


@app.route('/gamePlayerWait/<aUserName>', methods=['post', 'get'])
def gamePlayerWait(aUserName: str):
    userGame = db.getUserGame(aUserName)

    if request.method == 'POST':
        if request.form.get('actionToTake') == 'leave':
            db.removeUserFromGame(aUserName, userGame)
            return redirect(f"/gameDecide/{aUserName}")

    players = db.getPlayers(userGame)
    infoForGamePlayerWaitPage = {
        'playerName': aUserName,
        'gameCode': userGame,
        'players': players,
        'numPlayers': len(players)
    }

    return render_template('gamePlayerWait.html', info=infoForGamePlayerWaitPage)


@app.route('/joinGame/<aUserName>', methods=['post', 'get'])
def joinGame(aUserName: str):
    userGame = db.getUserGame(aUserName)
    if not userGame:
        infoForJoinGamePage = {
            "aUserName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        }
    else:
        infoForJoinGamePage = {}

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < minGameCodeCharacters:
            infoForJoinGamePage['errorMessage'] = f"Game code must have at least {minGameCodeCharacters} characters"
        else:
            if not gameCode.isalnum():
                infoForJoinGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode):
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
        infoForJoinGamePage['previousGameCodeEntry'] = gameCode  # TODO: what if GET?
    
    return render_template('joinGame.html', info=infoForJoinGamePage)


@app.route('/initGame/<aUserName>')
def initGame(aUserName: str):
    gameCode = db.getUserGame(aUserName)
    if not db.getGameStartedStatus(gameCode):
        # make a shuffled red deck
        indexes = [x for x in range(len(carddecks.redCards))]
        gameRedDeck = random.sample(indexes, k=len(indexes))
        db.setGameDeck(gameCode, "red", json.dumps(gameRedDeck))
        gameGreenDeck = random.sample(indexes, k=len(indexes))
        db.setGameDeck(gameCode, "green", json.dumps(gameGreenDeck))

        # give all accepted players 5 random red cards
        # assign 'judge' to first player
        # give 'judge' a random green card
        # start turn

        return 0

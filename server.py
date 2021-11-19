'''Server application.'''

import logging
from flask import Flask, render_template, request, redirect
import db
import datetime
import json
import random

import carddecks


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')
app = Flask(__name__)

# on start
standardRefreshRate = 5000 # milliseconds
notAdmittedString = "zNOTADMITTEDz"
maxActiveGames = 10
minNumPlayers = 3
maxNumPlayers = 8
minUserNameCharacters = 3
minGameCodeCharacters = 3
legalInputCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
maxNumRedCardsInHand = 5

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
        if request.form.get('shortcut'):
            makeGame()
            return redirect(f'gameOwnerWait/brianTest')

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
    # returnString = "gameDecide was fed: {}<br>".format(aUserName)
    # returnString += "User list:<br><hr>"
    # returnString += json.dumps(userList)

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
        'maxNumPlayers': maxNumPlayers,
        'standardRefreshRate': standardRefreshRate
    }

    return render_template('gameOwnerWait.html', info=infoForGameOwnerWaitPage)

@app.route('/gamePlayerWait/<aUserName>', methods=[ 'post', 'get' ])
def gamePlayerWait(aUserName):
    gameCode = db.getUserGame(aUserName)
    print("In gamePlayerWait() for userName: {}; gameCode: {}".format(aUserName, gameCode))

    if str(gameCode) == str(notAdmittedString):
        return redirect('/joinGame/{aUserName}')

    if request.method == 'POST':
        if request.form.get('actionToTake') == 'leave':
            db.removeUserGame(aUserName, gameCode)
            return redirect('/gameDecide/{aUserName}')

    players = db.getPlayers(gameCode)
    infoForGamePlayerWaitPage = {
        'playerName': aUserName,
        'gameCode': gameCode,
        'players': players,
        'numPlayers': len(players),
        'standardRefreshRate': standardRefreshRate
    }

    if db.getGameStartedStatus(gameCode):
        return redirect(f'/startTurn/{aUserName}')
    else:
        return render_template('gamePlayerWait.html', info=infoForGamePlayerWaitPage)

@app.route('/joinGame/<aUserName>', methods=[ 'post', 'get' ])
def joinGame(aUserName):
    userGame = db.getUserGame(aUserName)
    print("In joinGame()...userGame = {}".format(userGame))
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
        # "De-game" players that weren't admitted to this game
        players = db.getPlayers(gameCode)
        acceptedPlayers = db.getAcceptedPlayers(gameCode)
        for player in players:
            if player not in acceptedPlayers:
                db.setUserGameCode(player[0], notAdmittedString)

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

        db.setGameStartedStatus(gameCode, 1)

        # Deal all players' red cards
        players = db.getPlayers(gameCode)
        for i in range(0, maxNumRedCardsInHand):
            for player in players:
                db.dealRedCard(player[0], gameCode)

        # start turn
        return redirect(f'/startTurn/{aUserName}')

@app.route('/startTurn/<aUserName>')
def startTurn(aUserName):
    gameCode = db.getUserGame(aUserName)

    # if you are the game owner (because these things only need to happen once each turn):
    if db.getGameRole(aUserName) == 'owner':
        # check to see if we need to re-shuffle the discard decks and add them to the feed decks

        # clear out the redCardWinner for the game
        db.setRedCardWinner(gameCode, -1)

        # assign 'judge' to next player
        advanceJudge(gameCode)

        # give 'judge' a random green card
        db.dealGreenCard(gameCode)

    judgeName = getJudgeName(gameCode)
    print("Judge's name = {}".format(judgeName))

    # if you are the judge, then go to the judgeWaitForSubmissions page
    if judgeName == aUserName:
        print("server.py found the judge: {}".format(aUserName))
        return redirect(f'/judgeWaitForSubmissions/{aUserName}')
    else:
        # if you are a player, then go to the playerMakesSubmission page
        # return redirect(f'/judgeWaitForSubmissions/{aUserName}')
        return redirect(f'/playerMakesSubmission/{aUserName}')

@app.route('/judgeWaitForSubmissions/<aUserName>')
def judgeWaitForSubmissions(aUserName):
    gameCode = db.getUserGame(aUserName)

    greenCardIndex = db.getCurrentGreenCard(gameCode)
    print("greenCardIndex = {}".format(greenCardIndex))

    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[greenCardIndex],
        "cardIndex": greenCardIndex
    }

    playedRedCards = db.getPlayedRedCards(gameCode)
    numPlayers = db.getNumPlayersInGame(gameCode)

    infoForJudgeWaitForSubmissionsPage = {
        "aUserName": aUserName,
        "greenCardInfo": json.dumps(greenCard),
        "numRedCardsPlayed": len(playedRedCards)
    }

    if len(playedRedCards) >= (numPlayers - 1):
        return redirect(f'/judgePicksWinner/{aUserName}')
    else:
        return render_template('judgeWaitForSubmissions.html', info=infoForJudgeWaitForSubmissionsPage)

@app.route('/playerMakesSubmission/<aUserName>')
def playerMakesSubmission(aUserName):
    gameCode = db.getUserGame(aUserName)

    greenCardIndex = db.getCurrentGreenCard(gameCode)
    print("greenCardIndex = {}".format(greenCardIndex))

    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[greenCardIndex],
        "cardIndex": greenCardIndex
    }

    playerRedHand = []
    playerRedHandIndices = json.loads(db.getPlayerRedHand(aUserName))
    for i in playerRedHandIndices:
        newRedCard = {
            "cardColor": "red",
            "cardText": carddecks.redCards[i],
            "cardIndex": i,
            "cardButtonText": "Play this card"
        }
        playerRedHand.append(newRedCard)

    infoForPlayerMakesSubmissionPage = {
        "aUserName": aUserName,
        "greenCardInfo": json.dumps(greenCard),
        "redHandInfo": json.dumps(playerRedHand)
    }

    return render_template('playerMakesSubmission.html', info=infoForPlayerMakesSubmissionPage)

@app.route('/playerPlaysRedCard/<aUserName>', methods=[ "post" ])
def playerPlaysRedCard(aUserName):
    gameCode = db.getUserGame(aUserName)
    redCardIndex = request.form.get('redCardIndex')
    db.setPlayerRedCardPlayed(aUserName, redCardIndex)
    db.removeRedCardFromHand(aUserName, int(redCardIndex))
    fillHand(aUserName, gameCode)

    return redirect(f'/playerWaitForJudgment/{aUserName}')

@app.route('/playerWaitForJudgment/<aUserName>')
def playerWaitForJudgment(aUserName):
    gameCode = db.getUserGame(aUserName)
    winningRedCard = db.getRedCardWinner(gameCode)
    if winningRedCard != -1:
        return redirect(f'/showWinner/{aUserName}')
    else:
        infoForPlayerWaitForJudgmentPage = {
            "userName": aUserName,
            "gameCode": gameCode,
            "standardRefreshRate": standardRefreshRate
        }
        return render_template('playerWaitForJudgment.html', info=infoForPlayerWaitForJudgmentPage)

@app.route('/judgePicksWinner/<aUserName>')
def judgePicksWinner(aUserName):
    gameCode = db.getUserGame(aUserName)

    greenCardIndex = db.getCurrentGreenCard(gameCode)
    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[greenCardIndex],
        "cardIndex": greenCardIndex
    }

    redCards = []
    redCardIndexes = db.getPlayedRedCards(gameCode)
    print("Red card indexes = {}".format(json.dumps(redCardIndexes)))
    for redCardIndex in redCardIndexes:
        newRedCardObj = {
            "cardColor": "red",
            "cardText": carddecks.redCards[redCardIndex[0]],
            "cardIndex": redCardIndex[0]
        }
        redCards.append(newRedCardObj)

    infoForJudgePicksWinnerPage = {
        "userName": aUserName,
        "gameCode": gameCode,
        "greenCardInfo": json.dumps(greenCard),
        "redCardInfo": redCards
    }
    return render_template('judgePicksWinner.html', info=infoForJudgePicksWinnerPage)

@app.route('/setWinner/<aUserName>', methods=[ "post" ])
def setWinner(aUserName):
    gameCode = db.getUserGame(aUserName)
    winningRedCardIndex = request.form.get('redCardIndex')
    db.setRedCardWinner(gameCode, winningRedCardIndex)

    return redirect(f'/showWinner/{aUserName}')

@app.route('/showWinner/<aUserName>')
def showWinner(aUserName):
    gameCode = db.getUserGame(aUserName)
    winningRedCardIndex = request.form.get('redCardIndex')
    judgeName = db.getCurrentJudge(gameCode)

    greenCardIndex = db.getCurrentGreenCard(gameCode)
    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[greenCardIndex],
        "cardIndex": greenCardIndex
    }

    redCards = []
    redCardIndexes = db.getPlayedRedCards(gameCode)
    for redCardIndex in redCardIndexes:
        newRedCardObj = {
            "cardColor": "red",
            "cardText": carddecks.redCards[redCardIndex[0]],
            "cardIndex": redCardIndex[0],
            "cardPlayer": db.getCardPlayer(gameCode, redCardIndex[0])
        }
        redCards.append(newRedCardObj)

    infoForShowWinnerPage = {
        "userName": aUserName,
        'judgeName': judgeName,
        "gameCode": gameCode,
        "winningIndex": winningRedCardIndex,
        "greenCardInfo": json.dumps(greenCard),
        "redCardInfo": json.dumps(redCards),
        "standardRefreshRate": standardRefreshRate
    }

    return render_template('showWinner.html', info=infoForShowWinnerPage)



# ****************************************************************************************************
# Some supporting functions
# ****************************************************************************************************
def advanceJudge(aGameCode):
    players = db.getPlayers(aGameCode)
    currentJudge = db.getCurrentJudge(aGameCode)
    currentJudge += 1
    if currentJudge > len(players):
        currentJudge = 0
    db.setCurrentJudge(aGameCode, currentJudge)

def fillHand(aUserName, aGameCode):
    currentRedHandText = db.getPlayerRedHand(aUserName)
    # print("Player: {}; currentRedHandText: {}".format(aUserName, currentRedHandText))

    if currentRedHandText == "" or currentRedHandText == "None":
        currentHand = []
    else:
        currentHand = json.loads(currentRedHandText)

    # print("currentHand = {}".format(currentHand))
    if len(currentHand) < maxNumRedCardsInHand:
        print("   len(currentHand) = {}".format(len(currentHand)))
        for c in range(len(currentHand), maxNumRedCardsInHand):
            db.dealRedCard(aUserName, aGameCode)

def getJudgeName(aGameCode):
    players = db.getPlayers(aGameCode)
    currentJudgeIndex = db.getCurrentJudge(aGameCode)
    judgeUserName = players[currentJudgeIndex][0]
    return judgeUserName

def makeGame():
    newGameObject = {
        'gameCode': 'mckibben',
        'gameCreated': datetime.datetime.now(),
        'gameStarted': 0
    }
    db.addGame(newGameObject)

    players = [
        {
            'userName': 'brianTest',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'owner',
            'isAccepted': 1
        },
        {
            'userName': 'mindy',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 0
        },
        {
            'userName': 'sarah',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 0
        },
        {
            'userName': 'heather',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 0
        }
    ]
    for player in players:
        db.addUser(player)
        db.addUserToGame(player['userName'], player['gameRole'], player['gameCode'], player['isAccepted'])
    

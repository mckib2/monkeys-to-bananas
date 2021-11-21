"""Server application."""

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
legalInputCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
maxNumRedCardsInHand = 5

db.initialize()

@app.route('/', methods=[ 'post', 'get' ])
def index():
    logger.info(f"Starting index()...request method = {request.method}")

    infoForIndexPage = {
        "numActiveGames": db.getNumActiveGames(),
        "maxActiveGames": maxActiveGames,
        "minUserNameCharacters": minUserNameCharacters,
        "legalInputCharacters": legalInputCharacters
    }

    if request.method == 'POST':
        if request.form.get('shortcut'):
            makeGame()
            return redirect(f'gameCreatorWait/brianTest')

        userName = request.form.get('userName')
        if len(userName) < minUserNameCharacters:
            infoForIndexPage['errorMessage'] = f'User name must have at least {minUserNameCharacters} characters'
        else:
            isLegal = True
            i = 0
            while i < len(userName) and isLegal == True:
                if legalInputCharacters.find(userName[i]) == -1:
                    isLegal = False
                else:
                    i += 1

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
                        'isAccepted': 0,
                        'userRedHand': '[]',
                        'redCardPlayed': -1,
                        'winningGreenCards': '[]'
                    }
                    db.addUser(newUser)
                    return redirect(f'gameDecide/{userName}')
    
    if 'errorMessage' in infoForIndexPage:
        infoForIndexPage['previousUserNameEntry'] = request.form.get('userName')

    return render_template('index.html', info=infoForIndexPage)

@app.route('/showDB')
def showDB():
    logger.info(f"Starting showDB()")
    infoForShowDBPage = {
        "tableNames": [ "users", "games", "redCards", "greenCards" ],
        "headers": {
            "users": [
                "userName",
                "startTime",
                "gameCode",
                "gameRole",
                "isAccepted",
                "userRedHand",
                "redCardPlayed",
                "winningGreenCards"
            ],
            "games": [
                "gameCode",
                "gameCreator",
                "gameCreated",
                "gameStarted",
                "redDeck",
                "greenDeck",
                "currentJudge",
                "currentGreenCard",
                "redCardWinner",
                "discardedRedCards",
                "judgeAdvanced",
                "finishedPlayers"
            ]
        },
        "users": db.getUsers(),
        "games": db.getGames(),
        "redCards": carddecks.redCards,
        "greenCards": carddecks.greenCards
    }
    return render_template('showDB.html', info=infoForShowDBPage)

@app.route('/gameDecide/<aUserName>')
def gameDecide(aUserName: str):
    logger.info(f"Starting gameDecide()...aUserName = {aUserName}")

    infoForGameDecide = {
        'aUserName': aUserName
    }

    return render_template('gameDecide.html', info=infoForGameDecide)

@app.route('/signOut/<aUserName>')
def signOut(aUserName: str):
    logger.info(f"Starting signOut()...aUserName = {aUserName}")

    db.removeUser(aUserName)
    return redirect(f'/')

@app.route('/createGame/<aUserName>', methods=[ 'post', 'get' ])
def createGame(aUserName: str):
    logger.info(f"Starting createGame()...aUserName = {aUserName}; request method = {request.method}")

    userGame = db.getGameCode(aUserName)

    infoForCreateGamePage ={}
    if not userGame:
        infoForCreateGamePage.update ({
            "aUserName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        })

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < minGameCodeCharacters:
            infoForCreateGamePage['errorMessage'] = f'Game code must have at least {minGameCodeCharacters} characters'
        else:
            # Check if string contains only alphanumeric characters
            isLegal = True
            i = 0
            while i < len(gameCode) and isLegal == True:
                if legalInputCharacters.find(gameCode[i]) == -1:
                    isLegal = False
                else:
                    i += 1

            if isLegal == False:
                infoForCreateGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode) == True:
                    infoForCreateGamePage['errorMessage'] = 'That game code already exists'
                else:
                    newGame = {
                        'gameCode': gameCode,
                        'gameCreator': aUserName,
                        'gameCreated': datetime.datetime.now(),
                        'gameStarted': 0,
                        'redDeck': '[]',
                        'greenDeck': '[]',
                        'currentJudge': -1,
                        'currentGreenCard': -1,
                        'redCardWinner': -1,
                        'discardedRedCards': '[]'
                    }
                    db.addGame(newGame)
                    db.addUserToGame(aUserName, 'player', gameCode, 1)
                    return redirect(f'/gameCreatorWait/{aUserName}')
    
    if 'errorMessage' in infoForCreateGamePage:
        infoForCreateGamePage['previousGameCodeEntry'] = gameCode
    
    return render_template('createGame.html', info=infoForCreateGamePage)

@app.route('/gameCreatorWait/<gameCreator>', methods=[ 'post', 'get' ])
def gameCreatorWait(gameCreator: str):
    logger.info(f"Starting gameCreatorWait()...gameCreator = {gameCreator}")

    gameCode = db.getGameCode(gameCreator)

    if request.method == 'POST':
        if request.form.get('actionToTake') == 'admit':
            db.addUserToGame(request.form.get('admittee'), 'player', gameCode, 1)
        else:
            db.removeUserFromGame(request.form.get('removee'), gameCode)

    players = db.getPlayers(gameCode)
    acceptedPlayers = db.getAcceptedPlayers(gameCode)
    numPlayersNotAccepted = len(players) - len(acceptedPlayers)

    infoForGameCreatorWaitPage = {
        'gameCreator': gameCreator,
        'gameCode': gameCode,
        'players': players,
        'numAcceptedPlayers': len(acceptedPlayers),
        'numPlayersNotAccepted': numPlayersNotAccepted,
        'minNumPlayers': minNumPlayers,
        'maxNumPlayers': maxNumPlayers,
        'standardRefreshRate': standardRefreshRate
    }

    return render_template('gameCreatorWait.html', info=infoForGameCreatorWaitPage)

@app.route('/gamePlayerWait/<aUserName>', methods=[ 'post', 'get' ])
def gamePlayerWait(aUserName: str):
    logger.info(f"Starting gamePlayerWait()...aUserName = {aUserName}; request method = {request.method}")

    gameCode = db.getGameCode(aUserName)
    
    if gameCode == notAdmittedString:
        return redirect(f'/joinGame/{aUserName}')

    if request.method == 'POST':
        if request.form.get('actionToTake') == 'leave':
            db.removeUserFromGame(aUserName, gameCode)
            return redirect('/gameDecide/{aUserName}')

    if db.getGameStartedStatus(gameCode) == 1:
        return redirect(f'/startTurn/{aUserName}')
    else:
        players = db.getPlayers(gameCode)
        infoForGamePlayerWaitPage = {
            'userName': aUserName,
            'gameCode': gameCode,
            'players': players,
            'numPlayers': len(players),
            'standardRefreshRate': standardRefreshRate
        }
        return render_template('gamePlayerWait.html', info=infoForGamePlayerWaitPage)

@app.route('/joinGame/<aUserName>', methods=[ 'post', 'get' ])
def joinGame(aUserName: str):
    logger.info(f"Starting joinGame()...aUserName = {aUserName}; request method = {request.method}")

    gameCode = db.getGameCode(aUserName)

    infoForJoinGamePage = {}
    if not gameCode:
        infoForJoinGamePage.update({
            "userName": aUserName,
            "minGameCodeCharacters": minGameCodeCharacters,
            "legalInputCharacters": legalInputCharacters
        })

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < minGameCodeCharacters:
            infoForJoinGamePage['errorMessage'] = f'Game code must have at least {minGameCodeCharacters} characters'
        else:
            isLegal = True
            i = 0
            while i < len(gameCode) and isLegal == True:
                if legalInputCharacters.find(gameCode[i]) == -1:
                    isLegal = False
                else:
                    i += 1

            if isLegal == False:
                infoForJoinGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode) == True:
                    if db.getGameStartedStatus(gameCode):
                        infoForJoinGamePage['errorMessage'] = 'That game is already in progress'
                    elif db.getNumPlayersInGame(gameCode) > maxNumPlayers:
                        infoForJoinGamePage['errorMessage'] = 'Too many players in that game'
                    else:
                        db.addUserToGame(aUserName, 'player', gameCode, anAcceptanceValue=0)
                        return redirect(f'/gamePlayerWait/{aUserName}')
                else:
                    infoForJoinGamePage.update({'errorMessage': 'That game does not exist'})

    if 'errorMessage' in infoForJoinGamePage:
        infoForJoinGamePage.update({'previousGameCodeEntry': gameCode})
    
    return render_template('joinGame.html', info=infoForJoinGamePage)

@app.route('/initGame/<aUserName>')
def initGame(aUserName: str):
    logger.info(f"Starting initGame()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)
    if db.getGameStartedStatus(gameCode) == 0:
        # "De-game" players that weren't admitted to this game
        players = db.getPlayers(gameCode)
        logger.info(f"players = {players}")

        acceptedPlayers = db.getAcceptedPlayers(gameCode)
        logger.info(f"acceptedPlayers = {acceptedPlayers}")

        for player in players:
            if player['userName'] not in acceptedPlayers:
                logger.info(f"player was not in acceptedPlayers")
                db.setUserGameCode(player['userName'], notAdmittedString)
        del players

        #set first judge
        players = db.getPlayers(gameCode)
        gameCreator = db.getGameCreator(gameCode)
        i = 0
        isAssigned = False
        while i < len(players) and not isAssigned:
            if players[i]['userName'] != gameCreator:
                isAssigned = True
            else:
                i += 1
        playerIndex = i
        judgeName = players[playerIndex]['userName']
        logger.info(f"playerIndex = {playerIndex}; len(players) = {len(players)}")
        db.setCurrentJudge(gameCode, playerIndex, judgeName)
        db.setJudgeAdvanced(gameCode, 1)

        # make a shuffled red deck
        indexes = [x for x in range(len(carddecks.redCards))]
        gameRedDeck = random.sample(indexes, k=len(indexes))
        db.setGameDeck(gameCode, "red", json.dumps(gameRedDeck))

        # make a shuffled green deck
        indexes = [x for x in range(len(carddecks.greenCards))]
        gameGreenDeck = random.sample(indexes, k=len(indexes))
        db.setGameDeck(gameCode, "green", json.dumps(gameGreenDeck))

        # give 'judge' a random green card
        db.dealGreenCard(gameCode)

        # Declare the game started
        db.setGameStartedStatus(gameCode, 1)

        # Deal all players' red cards
        for i in range(0, maxNumRedCardsInHand):
            for player in players:
                db.dealRedCard(player['userName'], gameCode)

        # start turn
        return redirect(f'/startTurn/{aUserName}')

@app.route('/startTurn/<aUserName>')
def startTurn(aUserName: str):
    logger.info(f"Starting startTurn()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)
    judgeName = db.getJudgeName(gameCode)

    players = json.dumps(db.getPlayers(gameCode), indent=3)
    logger.info(f"players = {players}")

    # check to see if we need to re-shuffle the discard decks and add them to the feed decks
    # Do this later

    # clear out the finishedPlayer field
    db.clearFinishedPlayers(gameCode)

    # clear out the redCardWinner for the game
    db.setRedCardWinner(gameCode, -1)

    # clear out any playedRedCards from a previous turn
    db.clearRedCardsPlayed(gameCode)

    if aUserName == judgeName:
        # if you are the judge, then go to the judgeWaitForSubmissions page
        return redirect(f'/judgeWaitForSubmissions/{aUserName}')
    else:
        # if you are a player, then go to the playerMakesSubmission page
        return redirect(f'/playerMakesSubmission/{aUserName}')

@app.route('/judgeWaitForSubmissions/<aUserName>')
def judgeWaitForSubmissions(aUserName: str):
    logger.info(f"Starting judgeWaitForSubmissions()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)

    greenCardIndex = db.getCurrentGreenCard(gameCode)
    logger.info(f"greenCardIndex = {greenCardIndex}")

    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[greenCardIndex],
        "cardIndex": greenCardIndex
    }

    playedRedCards = db.getPlayedRedCards(gameCode)
    players = db.getPlayers(gameCode)
    numPlayers = len(players)

    infoForJudgeWaitForSubmissionsPage = {
        "aUserName": aUserName,
        "greenCardInfo": json.dumps(greenCard),
        "numRedCardsPlayed": len(playedRedCards),
        "standardRefreshRate": standardRefreshRate
    }

    if len(playedRedCards) >= (numPlayers - 1):
        return redirect(f'/judgePicksWinner/{aUserName}')
    else:
        return render_template('judgeWaitForSubmissions.html', info=infoForJudgeWaitForSubmissionsPage)

@app.route('/playerMakesSubmission/<aUserName>')
def playerMakesSubmission(aUserName: str):
    logger.info(f"Starting playerMakesSubmission()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)

    greenCardIndex = db.getCurrentGreenCard(gameCode)
    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[greenCardIndex],
        "cardIndex": greenCardIndex
    }

    playerRedHand = []
    playerRedHandIndices = db.getPlayerRedHand(aUserName)
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
def playerPlaysRedCard(aUserName: str):
    logger.info(f"Starting playerPlaysRedCard()...aUserName = {aUserName}; request.method = {request.method}")

    gameCode = db.getGameCode(aUserName)
    redCardIndex = request.form.get('redCardIndex')
    db.setPlayerRedCardPlayed(aUserName, redCardIndex)
    db.removeRedCardFromHand(aUserName, int(redCardIndex))
    fillHand(aUserName, gameCode)

    return redirect(f'/playerWaitForJudgment/{aUserName}')

@app.route('/playerWaitForJudgment/<aUserName>')
def playerWaitForJudgment(aUserName: str):
    logger.info(f"Starting playerWaitForJudgment()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)
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
    gameCode = db.getGameCode(aUserName)

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
def setWinner(aUserName: str):
    logger.info(f"Starting setWinner()...aUserName = {aUserName}; request.method = {request.method}")

    gameCode = db.getGameCode(aUserName)
    winningRedCardIndex = int(request.form.get('redCardIndex'))
    db.setRedCardWinner(gameCode, winningRedCardIndex)

    return redirect(f'/showWinner/{aUserName}')

@app.route('/showWinner/<aUserName>')
def showWinner(aUserName: str):
    logger.info(f"Starting showWinner()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)
    judgeName = db.getJudgeName(gameCode)
    if aUserName == judgeName:
        db.setGameStartedStatus(gameCode, 0)
        db.setJudgeAdvanced(gameCode, 0)
        db.clearFinishedPlayers(gameCode)

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

    winnings = []
    winningTuples = db.getWinnings(gameCode)
    for win in winningTuples:
        newWinObject = {
            "userName": win[0],
            "winningGreenCards": win[1]
        }
        winnings.append(newWinObject)

    infoForShowWinnerPage = {
        "userName": aUserName,
        "gameRole": db.getGameRole(aUserName),
        "judgeName": judgeName,
        "gameCode": gameCode,
        "winningIndex": db.getRedCardWinner(gameCode),
        "greenCardInfo": json.dumps(greenCard),
        "redCardInfo": json.dumps(redCards),
        "winnings": json.dumps(winnings),
        "standardRefreshRate": standardRefreshRate
    }

    return render_template('showWinner.html', info=infoForShowWinnerPage)

@app.route('/finishTurn/<aUserName>')
def finishTurn(aUserName):
    gameCode = db.getGameCode(aUserName)

    # All players need to do this
    # Put winner's greenCards into their record
    finishedPlayers = db.getFinishedPlayers(gameCode)
    if aUserName not in finishedPlayers:
        usersPlayedRedCard = db.getPlayerRedCardPlayed(aUserName)
        if usersPlayedRedCard == db.getRedCardWinner(gameCode):
            usersCurrentWinnings = json.loads(db.getUserWinningGreenCards(aUserName))
            usersCurrentWinnings.append(db.getCurrentGreenCard(gameCode))
            db.setUserWinningGreenCards(aUserName, json.dumps(usersCurrentWinnings))
        db.addFinishedPlayer(gameCode, aUserName)

    # These things need to happen only when the first player runs finishTurn()
    if db.getJudgeAdvancedStatus(gameCode) == 0:
        # Pick the next judge
        advanceJudge(gameCode)
        db.setJudgeAdvanced(gameCode, 1)

        # Put played redCards into the redDiscard list
        currentDiscardedRedCards = db.getDiscardedRedCards(gameCode)
        redCardsPlayed = db.getPlayedRedCards(gameCode)
        for redCard in redCardsPlayed:
            currentDiscardedRedCards.append(redCard[0])
        db.setDiscardedRedCards(gameCode, json.dumps(currentDiscardedRedCards))

    finishedPlayers = db.getFinishedPlayers(gameCode)
    players = db.getPlayers(gameCode)

    if len(finishedPlayers) >= len(players):
        judgeName = db.getJudgeName(gameCode)
        if aUserName == judgeName:
            return redirect(f'/startTurn/{aUserName}')
        else:
            return redirect(f'/gamePlayerWait/{aUserName}')
    else:
        infoForFinishTurn = {
            "userName": aUserName,
            "finishedPlayers": finishedPlayers,
            "numFinishedPlayers": len(finishedPlayers),
            "gameCode": gameCode,
            "standardRefreshRate": standardRefreshRate
        }
        return render_template('finishTurn.html', info=infoForFinishTurn)




# ****************************************************************************************************
# Some supporting functions
# ****************************************************************************************************
def advanceJudge(aGameCode):
    players = db.getPlayers(aGameCode)
    currentJudgeIndex = db.getCurrentJudge(aGameCode)
    currentJudgeIndex += 1
    currentJudgeIndex %= len(players)
    db.clearJudgeAssignment(aGameCode)
    db.setCurrentJudge(aGameCode, currentJudgeIndex, players[currentJudgeIndex]['userName'])

def fillHand(aUserName: str, aGameCode: str) -> None:
    logger.info(f"Starting fillHand()...aUserName = {aUserName}; aGameCode = {aGameCode}")

    currentRedHand = db.getPlayerRedHand(aUserName)
    for c in range(len(currentRedHand), maxNumRedCardsInHand):
        db.dealRedCard(aUserName, aGameCode)

def makeGame():
    newGameObject = {
        'gameCode': 'mckibben',
        'gameCreator': 'brianTest',
        'gameCreated': datetime.datetime.now(),
        'gameStarted': 0,
        'redDeck': '[]',
        'greenDeck': '[]',
        'currentJudge': -1,
        'currentGreenCard': -1,
        'redCardWinner': -1,
        'discardedRedCards': '[]'
    }
    db.addGame(newGameObject)

    players = [
        {
            'userName': 'brianTest',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 1,
            'userRedHand': '[]',
            'redCardPlayed': -1,
            'winningGreenCards': '[]'
        },
        {
            'userName': 'mindy',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 0,
            'userRedHand': '[]',
            'redCardPlayed': -1,
            'winningGreenCards': '[]'
        },
        {
            'userName': 'sarah',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 0,
            'userRedHand': '[]',
            'redCardPlayed': -1,
            'winningGreenCards': '[]'
        },
        {
            'userName': 'heather',
            'startTime': datetime.datetime.now(),
            'gameCode': 'mckibben',
            'gameRole': 'player',
            'isAccepted': 0,
            'userRedHand': '[]',
            'redCardPlayed': -1,
            'winningGreenCards': '[]'
        }
    ]
    for player in players:
        db.addUser(player)
        db.addUserToGame(player['userName'], player['gameRole'], player['gameCode'], player['isAccepted'])
    

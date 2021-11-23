"""Server application."""

import logging
from flask import Flask, render_template, request, redirect
import db
import datetime
import json
import random
import yaml
from collections import namedtuple

import carddecks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('m2b')

logger.info("Loading m2bconfig.json...")


# configuration = Configuration(runMode = "dev")

runMode = "prod"

with open('m2bconfig.yaml', 'r') as f:
    logging.info("m2bconfig.yaml opened...")

    configuration = yaml.safe_load(f.read())
    logging.info(f"m2bconfig = {yaml.safe_dump(configuration, indent=2)}")

    """
    Configuration = namedtuple("Configuration", list(configuration.keys()))
    configuration = Configuration(**configuration)
    logging.info(f"configuration (tuple) = {configuration}")
    """

    runMode = configuration['runMode']

app = Flask(__name__)

# on start

db.initialize()

@app.route('/', methods=[ 'post', 'get' ])
def index():
    logger.info(f"Starting index()...request method = {request.method}")

    infoForIndexPage = {
        "numActiveGames": db.getNumActiveGames(),
        "maxActiveGames": configuration['maxActiveGames'],
        "minUserNameCharacters": configuration['minUserNameCharacters'],
        "legalInputCharacters": configuration['legalInputCharacters'],
        "runMode": runMode
    }

    if request.method == 'POST':
        if request.form.get('shortcut'):
            makeGame()
            return redirect(f'gameCreatorWait/brianTest')

        userName = request.form.get('userName')
        if len(userName) < configuration["minUserNameCharacters"]:
            infoForIndexPage['errorMessage'] = f'User name must have at least {configuration["minUserNameCharacters"]} characters'
        else:
            isLegal = True
            i = 0
            while i < len(userName) and isLegal == True:
                if configuration["legalInputCharacters"].find(userName[i]) == -1:
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
                "previousJudgeName",
                "currentGreenCard",
                "previousGreenCard",
                "redCardWinner",
                "discardedRedCards",
                "judgeAdvanced",
                "finishedPlayers"
            ]
        },
        "users": db.getUsers(),
        "games": db.getGames(),
        "configuration": configuration,
        "redCards": carddecks.redCards,
        "greenCards": carddecks.greenCards,
    }
    return render_template('showDB.html', info=infoForShowDBPage, type=type)

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
            "minGameCodeCharacters": configuration['minGameCodeCharacters'],
            "legalInputCharacters": configuration['legalInputCharacters'],
            "runMode": configuration["runMode"]
        })

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < configuration['minGameCodeCharacters']:
            infoForCreateGamePage['errorMessage'] = f'Game code must have at least {configuration["legalInputCharacters"]} characters'
        else:
            # Check if string contains only alphanumeric characters
            isLegal = True
            i = 0
            while i < len(gameCode) and isLegal == True:
                if configuration["legalInputCharacters"].find(gameCode[i]) == -1:
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
                        'previousGreenCard': -1,
                        'redCardWinner': -1,
                        'discardedRedCards': '[]',
                        'previousJudgeName': ''
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
        'minNumPlayers': configuration["minNumPlayers"],
        'maxNumPlayers': configuration["maxNumPlayers"],
        'standardRefreshRate': configuration["standardRefreshRate"],
        'configuration': configuration
    }

    return render_template('gameCreatorWait.html', info=infoForGameCreatorWaitPage)

@app.route('/gamePlayerWait/<aUserName>', methods=[ 'post', 'get' ])
def gamePlayerWait(aUserName: str):
    logger.info(f"Starting gamePlayerWait()...aUserName = {aUserName}; request method = {request.method}")

    # If the gameCode doesn't exist, then the game has ended
    try:
        gameCode = db.getGameCode(aUserName)
    except TypeError:
        return redirect('/')

    # If the judge has been reassigned due to another player leaving the game, do this
    
    if db.getPreviousJudgeName(gameCode):
        judgeName = db.getJudgeName(gameCode)
        if aUserName == judgeName:
            return redirect(f'/startTurn/{aUserName}')

    if gameCode == configuration["notAdmittedString"]:
        return redirect(f'/joinGame/{aUserName}')

    if db.getGameStartedStatus(gameCode) == 1:
        return redirect(f'/startTurn/{aUserName}')
    else:
        players = db.getPlayers(gameCode)
        infoForGamePlayerWaitPage = {
            'userName': aUserName,
            'gameCode': gameCode,
            'players': players,
            'numPlayers': len(players),
            'standardRefreshRate': configuration["standardRefreshRate"]
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
            "minGameCodeCharacters": configuration['minGameCodeCharacters'],
            "legalInputCharacters": configuration['legalInputCharacters']
        })

    if request.method == 'POST':
        gameCode = request.form.get('gameCode')
        if len(gameCode) < configuration['minGameCodeCharacters']:
            infoForJoinGamePage['errorMessage'] = f'Game code must have at least {configuration["legalInputCharacters"]} characters'
        else:
            isLegal = True
            i = 0
            while i < len(gameCode) and isLegal == True:
                if configuration["legalInputCharacters"].find(gameCode[i]) == -1:
                    isLegal = False
                else:
                    i += 1

            if isLegal == False:
                infoForJoinGamePage['errorMessage'] = 'Can only contain letters and numbers'
            else:
                if db.existsGameCode(gameCode) == True:
                    if db.getGameStartedStatus(gameCode):
                        infoForJoinGamePage['errorMessage'] = 'That game is already in progress'
                    elif db.getNumPlayersInGame(gameCode) >  configuration["maxNumPlayers"]:
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
                db.setUserGameCode(player['userName'], configuration["notAdmittedString"])
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
        for i in range(0, configuration["maxNumRedCardsInHand"]):
            for player in players:
                db.dealRedCard(player['userName'], gameCode)

        # start turn
        return redirect(f'/startTurn/{aUserName}')

@app.route('/startTurn/<aUserName>')
def startTurn(aUserName: str):
    logger.info(f"Starting startTurn()...aUserName = {aUserName}")

    # If the gameCode doesn't exist, then the game has ended
    try:
        gameCode = db.getGameCode(aUserName)
    except TypeError:
        return redirect('/')

    judgeName = db.getJudgeName(gameCode)

    players = json.dumps(db.getPlayers(gameCode), indent=3)
    logger.info(f"players = {players}")

    # check to see if we need to re-shuffle the discard decks and add them to the feed decks
    # Do this later

    # clear out the redCardWinner for the game
    db.setRedCardWinner(gameCode, -1)

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
        "standardRefreshRate": configuration["standardRefreshRate"]
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
            "standardRefreshRate": configuration["standardRefreshRate"]
        }
        return render_template('playerWaitForJudgment.html', info=infoForPlayerWaitForJudgmentPage)

@app.route('/judgePicksWinner/<aUserName>')
def judgePicksWinner(aUserName):
    gameCode = db.getGameCode(aUserName)

    # Running this here to avoid conflicts which might occur later in the turn
    db.clearFinishedPlayers(gameCode)

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
            "cardText": carddecks.redCards[redCardIndex],
            "cardIndex": redCardIndex
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

    currentGreenCard = db.getCurrentGreenCard(gameCode)
    db.setPreviousGreenCard(gameCode, currentGreenCard)
    db.dealGreenCard(gameCode)

    advanceJudge(gameCode)

    winningRedCardIndex = int(request.form.get('redCardIndex'))
    db.discardPlayedRedCards(gameCode)

    db.setRedCardWinner(gameCode, winningRedCardIndex)

    return redirect(f'/showWinner/{aUserName}')

@app.route('/showWinner/<aUserName>')
def showWinner(aUserName: str):
    logger.info(f"Starting showWinner()...aUserName = {aUserName}")

    gameCode = db.getGameCode(aUserName)

    previousGreenCardIndex = db.getPreviousGreenCard(gameCode)

    greenCard = {
        "cardColor": "green",
        "cardText": carddecks.greenCards[previousGreenCardIndex],
        "cardIndex": previousGreenCardIndex
    }

    redCards = []
    redCardIndexes = db.getPlayedRedCards(gameCode)
    for redCardIndex in redCardIndexes:
        newRedCardObj = {
            "cardColor": "red",
            "cardText": carddecks.redCards[redCardIndex],
            "cardIndex": redCardIndex,
            "cardPlayer": db.getCardPlayer(gameCode, redCardIndex)
        }
        redCards.append(newRedCardObj)

    winnings = db.getWinnings(gameCode)

    infoForShowWinnerPage = {
        "userName": aUserName,
        "gameRole": db.getGameRole(aUserName),
        "gameCode": gameCode,
        "winningIndex": db.getRedCardWinner(gameCode),
        "greenCardInfo": json.dumps(greenCard),
        "redCardInfo": json.dumps(redCards),
        "winnings": json.dumps(winnings),
        "standardRefreshRate": configuration["standardRefreshRate"]
    }

    return render_template('showWinner.html', info=infoForShowWinnerPage)

@app.route('/finishTurn/<aUserName>')
def finishTurn(aUserName: str):
    logger.info(f"Starting finishTurn()...aUserName = {aUserName}")

    try:
        gameCode = db.getGameCode(aUserName)
    except TypeError:
        return redirect('/')

    # All players need to do this
    # Put winner's greenCards into their record
    finishedPlayers = db.getFinishedPlayers(gameCode)
    if aUserName not in finishedPlayers:
        usersPlayedRedCard = db.getPlayerRedCardPlayed(aUserName)
        if usersPlayedRedCard == db.getRedCardWinner(gameCode):
            usersCurrentWinnings = db.getUserWinningGreenCards(aUserName)
            usersCurrentWinnings.append(db.getPreviousGreenCard(gameCode))
            db.setUserWinningGreenCards(aUserName, json.dumps(usersCurrentWinnings))

        db.addFinishedPlayer(gameCode, aUserName)
        db.clearRedCardPlayed(aUserName)

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
            "standardRefreshRate": configuration["standardRefreshRate"]
        }
        return render_template('finishTurn.html', info=infoForFinishTurn)

@app.route('/leaveGame/<aUserName>')
def leaveGame(aUserName: str):
    # In case the game has already ended and been removed from the 'games' table
    try:
        gameCode = db.getGameCode(aUserName)
    except TypeError:
        return redirect('/')

    originalPlayers = db.getPlayers(gameCode)
    originalPlayerIndex = [player['userName'] for player in originalPlayers].index(aUserName)
    originalCurrentJudge = db.getJudgeName(gameCode)
    originalCurrentJudgeIndex = [player['userName'] for player in originalPlayers].index(originalCurrentJudge)

    newJudgeIndex = originalCurrentJudgeIndex
    if aUserName != originalCurrentJudge:
        if originalCurrentJudgeIndex > originalPlayerIndex:
            newJudgeIndex = originalCurrentJudgeIndex - 1
    else: # aUserName == originalCurrentJudge:
        if originalPlayerIndex == len(originalPlayers) - 1:
            newJudgeIndex = 0

    db.discardPlayerHand(aUserName)
    db.removeUser(aUserName)

    players = db.getPlayers(gameCode)
    if newJudgeIndex != originalCurrentJudgeIndex:
        db.setCurrentJudge(gameCode, newJudgeIndex, players[newJudgeIndex]['userName'])

    if len(players) < configuration["minNumPlayers"]:
        endGame(gameCode)

    return redirect('/')
            

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

def endGame(aGameCode: str) -> None:
    players = db.getPlayers(aGameCode)
    for player in players:
        db.removeUser(player['userName'])
    
    db.removeGame(aGameCode)


def fillHand(aUserName: str, aGameCode: str) -> None:
    logger.info(f"Starting fillHand()...aUserName = {aUserName}; aGameCode = {aGameCode}")

    currentRedHand = db.getPlayerRedHand(aUserName)
    for c in range(len(currentRedHand), configuration["maxNumRedCardsInHand"]):
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
        'previousJudgeName': '',
        'currentGreenCard': -1,
        'previousGreenCard': -1,
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
    

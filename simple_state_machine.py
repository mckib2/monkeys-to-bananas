'''Simple state machine implementation.'''

import logging

from .db import (
    get_game_state,
    set_game_state,
    inc_judge_counter,
    get_players,
    set_green_card_rcv_cnt,
    get_green_card_rcv_cnt,
    set_red_card_refill_ack_cnt,
    get_red_card_refill_ack_cnt,
    set_red_card_rcv_cnt,
    get_red_card_rcv_cnt,
    set_red_card_ack_cnt,
    get_red_card_ack_cnt,
    clear_red_card_selection,
    red_card_selected,
)

logging.basicConfig()
logger = logging.getLogger('game-loop')
logger.setLevel(logging.INFO)


def _State1(game_uid):
    logger.info('Entering State1')

    logger.info('Incrementing jugde counter')
    inc_judge_counter(game_uid)

    logger.info('Sending green card to players')
    set_green_card_rcv_cnt(game_uid, 0)

    logger.info('Sending red cards to players')
    set_red_card_refill_ack_cnt(game_uid, 0)

    set_game_state(game_uid, 'State2')
    logger.info('Exiting State1')


def _State2(game_uid):
    logger.info('Entering State2')
    players = get_players(game_uid)

    if get_green_card_rcv_cnt(game_uid) == len(players) and get_red_card_refill_ack_cnt(game_uid) == (len(players)-1):
        logger.info('All players received green/red cards!')
        set_green_card_rcv_cnt(game_uid, 0)
        set_red_card_refill_ack_cnt(game_uid, 0)

        logger.info('Prepping to wait for all players send red cards')
        set_red_card_rcv_cnt(game_uid, 0)

        set_game_state(game_uid, 'State3')
    else:
        logger.info('All players have not acknowledged receipt of green card')

    logger.info('Exiting State2')


def _State3(game_uid):
    logger.info('Entering State3')
    players = get_players(game_uid)

    if get_red_card_rcv_cnt(game_uid) == (len(players)-1):
        logger.info('All red cards received by the server!')
        set_red_card_rcv_cnt(game_uid, 0)

        logger('Prepping to wait for all players to acknowledge receipt of all red cards')
        set_red_card_ack_cnt(game_uid, 0)

        set_game_state(game_uid, 'State4')
    else:
        logger.info('Not all red cards received by server')

    logger.info('Exiting State3')


def _State4(game_uid):
    logger.info('Entering State4')
    players = get_players(game_uid)

    if get_red_card_ack_cnt(game_uid) == len(players):
        logger.info('All red cards received by players')
        set_red_card_ack_cnt(game_uid, 0)

        logger.info('Prepping receipt of judge red card selection')
        clear_red_card_selection(game_uid)

        set_game_state(game_uid, 'State5')
    else:
        logger.info('Not all red cards received by players')

    logger.info('Exiting State4')


def _State5(game_uid):
    logger.info('Entering State5')

    if red_card_selected(game_uid):
        logger.info('Red card was selected!')
        clear_red_card_selection(game_uid)

        # award green card
        win = award_green_card(game_uid)

        # win condition or start new turn
        if win:
            logger.info('A player won the game -- done!')
            set_game_state(game_uid, 'Done')
        else:
            logger.info('No win, start a new turn')
            set_game_state(game_uid, 'State1')

    else:
        logger.info('No red card selected')

    logger.info('Exiting State5')


def _Done(game_uid):
    logger.info('Entering Done')
    logger.info('Nothing to do here')
    logger.info('Exiting Done')


def StepGame(game_uid):

    # get current game state
    st = get_game_state(game_uid)
    {
        'State1': _State1,
        'State2': _State2,
        'State3': _State3,
        'State4': _State4,
        'State5': _State5,
        'Done': _Done,
    }[st](game_uid)

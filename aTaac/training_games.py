from datetime import datetime
import pickle

import alphabeta_minimax
import chaos_agent
import game_play as gp
import random
import numpy as np
from tensorflow.python.keras.utils.np_utils import to_categorical
from math import inf


# Simulate a game
from script_launcher import ScriptLauncher


def simulateGame(p1=None, p2=None, rnd=0, algo="minimax", len_board=5):
    history = []
    board = gp.initBoard(len_board)
    playerToMove = 1
    move = None

    while gp.getWinner(board) == -1:
        if algo == "random":
            # Chose a move (random or use a player model if provided)
            if playerToMove == 1 and p1 != None:
                move = gp.bestMove(board, p1, playerToMove, rnd)
            elif playerToMove == 2 and p2 != None:
                move = gp.bestMove(board, p2, playerToMove, rnd)
            else:
                moves = gp.getMoves(board)
                move = moves[random.randint(0, len(moves) - 1)]
            # Make the move
            board[move[0]][move[1]] = playerToMove
            # Add the move to the history
            history.append((playerToMove, move))
        elif algo == "minimax":
            m = alphabeta_minimax.ab_minimax(board, 5 if len(board) == 3 else 6, playerToMove, True, playerToMove,
                                             [-1, -1, -inf], [-1, -1, inf])
            move = (m[0], m[1])
            # Make the move
            board[move[0]][move[1]] = playerToMove
            # Add the move to the history
            history.append((playerToMove, move))
        elif algo == "minimax_chaos":
            if chaos_agent.is_time_for_chaos(playerToMove, attacker_skill_level=3, defender_skill_level=3):
                pass
            else:
                m = alphabeta_minimax.ab_minimax(board, 9 if len(board) == 3 else 6, playerToMove, True, playerToMove,
                                                 [-1, -1, -inf], [-1, -1, inf])
                move = (m[0], m[1])
                # Make the move
                board[move[0]][move[1]] = playerToMove
                # Add the move to the history
                history.append((playerToMove, move))

        # Switch the active player
        playerToMove = 1 if playerToMove == 2 else 2

    return history


# Get a set of board states labelled by who eventually won that game
def gamesToWinLossData(games, len_board):
    X = []
    y = []
    for game in games:
        winner = gp.getWinner(gp.movesToBoard(game, len_board))
        for move in range(len(game)):
            X.append(gp.movesToBoard(game[:(move + 1)], len_board))
            y.append(winner)

    X = np.array(X).reshape((-1, 25))
    y = to_categorical(y)

    # Return an appropriate train/test split
    trainNum = int(len(X) * 0.8)
    return X[:trainNum], X[trainNum:], y[:trainNum], y[trainNum:]


def sim_games(num_games):
    games = []
    for i in range(num_games):
        games.append(simulateGame(algo="minimax_chaos", len_board=3))
        if i % 50 == 0:
            print(f"simulated games: {i} at {datetime.now()}")
    return games


def create_files(num_files, num_games, start):
    for j in range(start, start+num_files):
        print(f"\ncreating file num {j}\n")
        games = sim_games(num_games)
        with open(f"io/training_3x3/3x3_skill_3_{j}.pickle", "wb") as f:
            pickle.dump(games, f)
        gp.gameStats(games, len_board=3, player=1)


create_files(num_files=20, num_games=100, start=1)

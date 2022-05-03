import copy
import os
import random
import time
import os

import numpy as np
from dotenv import load_dotenv
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import Sequential
from keras.utils.np_utils import to_categorical
from math import inf

import helpers
import alphabeta_minimax
from game_eval import eval_move
from docker_move import run_command_to_target, run_command_to_self
import chaos_agent
from docker_move import cyber_move, start_game_docker
import logging


load_dotenv()
attack = os.getenv('ATTACK')
defense = os.getenv('DEFENSE')
is_docker = os.getenv("DOCKER")

"""
This function initializes the empty board into a nxn list of lists of zeroes.
0 indicates an empty space, 1 indicates an X (player 1), 2 indicates an O (player 2)

Inputs: None
Outputs: board - initialized board (list of lists)

"""


def initBoard(len_board):
    if len_board == 3:
        board_3x3 = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        return board_3x3
    elif len_board == 5:
        board_5x5 = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        return board_5x5


"""
This function prints the board (list of lists) into an ASCII representation of a nxn tic tac toe board to the console.

Inputs: board - current board state (list of lists)
Outputs: ASCII tic tac toe board to console
"""


def printBoard(board):
    boardstr = ""
    for i in range(len(board)):
        for j in range(len(board[i])):
            mark = ' '
            if board[i][j] == 1:
                mark = 'X'
            elif board[i][j] == 2:
                mark = 'O'
            if (j == len(board[i]) - 1):
                boardstr += mark
            else:
                boardstr += f"{str(mark)}|"
        if (i < len(board) - 1):
            if len(board) == 3:
                boardstr+=("\n-----\n")
            else:
                boardstr +=("\n----------\n")
    return boardstr


"""
This function searches the board for valid moves remaining on the board. Indices are in [row][column] format.

Inputs: board - current board state (list of lists)
Outputs: moves - list of valid moves remaining on board. moves are tuples of indices i [row] and j [column]
"""


def getMoves(board):
    moves = []
    # search rows
    for i in range(len(board)):
        # search columns
        for j in range(len(board[i])):
            # 0 represents empty space on board, append to available moves list
            if board[i][j] == 0:
                moves.append((i, j))
    return moves


"""
This function checks a passed numpy array for homogeneity.

Inputs: arr - 1d numpy array of a row/column/diagonal 
Output: 1 - player 1 has won in a r/c/d
        2 - player 2 has won in a r/c/d
        False - no winners yet
"""


def check_win(arr, len_board):
    if len_board == 3:
        if arr[0] == arr[1] == arr[2] == 1:
            return 1
        elif arr[0] == arr[1] == arr[2] == 2:
            return 2
        else:
            return False
    elif len_board == 5:
        if len(arr) == 4:
            if arr[0] == arr[1] == arr[2] == arr[3] == 1:
                return 1
            elif arr[0] == arr[1] == arr[2] == arr[3] == 2:
                return 2
            else:
                return False
        else:
            if arr[0] == arr[1] == arr[2] == arr[3] == 1:
                return 1
            elif arr[1] == arr[2] == arr[3] == arr[4] == 1:
                return 1
            elif arr[0] == arr[1] == arr[2] == arr[3] == 2:
                return 2
            elif arr[1] == arr[2] == arr[3] == arr[4] == 2:
                return 2
            else:
                return False


"""
This function checks the board state to find a winner and works with the check_win function in sync.

Inputs: board - current board state (list of lists)
Outputs: 
"""


def getWinner(board):
    # represent the board as an array for easier manipulation
    board_array = np.array(board)
    wins = []

    # iterate through columns to check for vertical wins
    for j in range(len(board)):
        # slice each column, check for win
        winner = check_win(board_array[:, j], len_board=len(board))
        wins.append(winner)

    # iterate through rows to check for horizontal wins
    for i in range(len(board)):
        # slice each row, check for win
        winner = check_win(board_array[i, :], len_board=len(board))
        wins.append(winner)

    # get diagonals of board
    # note: this approach identifies ALL diagonals in the board (not only those of length 3), handled later
    diags = [board_array[::-1, :].diagonal(i)
             for i in range(-board_array.shape[0] + 1, board_array.shape[1])]
    diags.extend(board_array.diagonal(i) for i in range(
        board_array.shape[1] - 1, -board_array.shape[0], -1))

    # only the main diagonal and anti diagonal can be used for a win, so check for win only in those
    for each in diags:
        if len(board) == 3 and len(each) == 3:
            wins.append(check_win(each, len_board=len(board)))

        if len(board) == 5 and len(each) >= 4:
            wins.append(check_win(each, len_board=len(board)))

    # remove all booleans, leaving only integer values (1 or 2) to indicate a winner
    wins2 = [win for win in wins if win]

    # if there is no integer in wins2 (no winner yet) and if there are no more valid moves, it's a tie (return 0)
    if not wins2:
        if len(getMoves(board)) == 0:
            return 0

    # if there is an integer in wins2, there is a winner. return the winner, else, there are still moves to be made (return -1)
    if wins2:
        return wins2[0]
    else:
        return -1


# Get best next move for the given player at the given board position
def bestMove(board, model, player, rnd):
    scores = []
    moves = getMoves(board)

    # Make predictions for each possible move
    for i in range(len(moves)):
        future = np.array(board)
        future[moves[i][0]][moves[i][1]] = player
        prediction = model.predict(future.reshape((-1, len(board) ** 2)))[0]
        if player == 1:
            winPrediction = prediction[1]
            lossPrediction = prediction[2]
        else:
            winPrediction = prediction[2]
            lossPrediction = prediction[1]
        drawPrediction = prediction[0]
        if winPrediction - lossPrediction > 0:
            scores.append(winPrediction - lossPrediction)
        else:
            scores.append(drawPrediction - lossPrediction)

    # Choose the best move with a random factor
    bestMoves = np.flip(np.argsort(scores))
    for i in range(len(bestMoves)):
        if random.random() * rnd < 0.5:
            return moves[bestMoves[i]]

    # Choose a move completely at random
    return moves[random.randint(0, len(moves) - 1)]


# Reconstruct the board from the move list
def movesToBoard(moves, len_board):
    board = initBoard(len_board)
    for move in moves:
        player = move[0]
        coords = move[1]
        board[coords[0]][coords[1]] = player
    return board


"""
This function aggregates W/L/D statistics for a set of simulated games.

Input: games - list of simulated game results
       player - stats for this player are printed
Output: print to console of W/L/D statistics

"""


def gameStats(games, len_board, player=1):
    # initialize dictionary
    stats = {"win": 0, "loss": 0, "draw": 0}

    # iterate through each game
    for game in games:
        # get the result of the game
        result = getWinner(movesToBoard(game, len_board))

        # increment counters for W/L/D
        if result == -1:
            continue
        elif result == player:
            stats["win"] += 1
        elif result == 0:
            stats["draw"] += 1
        else:
            stats["loss"] += 1

    # calculate percentages and print to console
    winPct = stats["win"] / len(games) * 100
    lossPct = stats["loss"] / len(games) * 100
    drawPct = stats["draw"] / len(games) * 100

    print("Results for player %d:" % (player))
    print("Wins: %d (%.1f%%)" % (stats["win"], winPct))
    print("Loss: %d (%.1f%%)" % (stats["loss"], lossPct))
    print("Draw: %d (%.1f%%)" % (stats["draw"], drawPct))


"""
This function creates initializes a neural network to train.

Inputs: none
Outputs: keras neural network model
"""


def getModel(len_board):
    numCells = len_board ** 2  # total number of cells in a nxn board
    outcomes = 3  # total possible outcomes (W/L/D)

    # model from daniel sauble
    # information on dropout in neural networks - https://medium.com/@amarbudhiraja/https-medium-com-amarbudhiraja-learning-less-to-learn-better-dropout-in-deep-machine-learning-74334da4bfc5
    if len_board == 3:
        model = Sequential()
        model.add(Dense(200, activation='relu', input_shape=(numCells,)))
        model.add(Dropout(0.2))
        model.add(Dense(125, activation='relu'))
        model.add(Dense(75, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(outcomes, activation='softmax'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='rmsprop', metrics=['acc'])
        return model
    if len_board == 5:
        model = Sequential()
        model.add(Dense(250, activation='relu', input_shape=(numCells,)))
        model.add(Dropout(0.50))
        model.add(Dense(125, activation='relu'))
        model.add(Dense(75, activation='relu'))
        model.add(Dropout(0.25))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(outcomes, activation='softmax'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='rmsprop', metrics=['acc'])
        return model


# Get a set of board states labelled by who eventually won that game
def gamesToWinLossData(games, len_board):
    X = []
    y = []
    for game in games:
        winner = getWinner(movesToBoard(game))
        for move in range(len(game)):
            X.append(movesToBoard(game[:(move + 1)]))
            y.append(winner)

    X = np.array(X).reshape((-1, len_board ** 2))
    y = to_categorical(y)

    # Return an appropriate train/test split
    trainNum = int(len(X) * 0.8)
    return (X[:trainNum], X[trainNum:], y[:trainNum], y[trainNum:])


def get_human_player_move(player, len_board):
    print(f"human player {player}, make your move...")
    i = int(input("input i: "))
    j = int(input("input j: "))
    if not (0 <= i < len_board and 0 <= j < len_board):
        print(f"error: enter i and j values between 0 and {len_board}")
        return get_human_player_move(player, len_board)
    else:
        return i, j


def get_player_move(model, rnd, board, len_board, player, verbose, generate_data, human, exploit_tracker,
                    launcher, docker, attack, defense, attacker_skill, defender_skill, player1_algo, player2_algo,
                    game_id, chaos_count, gameplay_outcsv):

    previous_state = copy.deepcopy(board)
    if human:
        move = get_human_player_move(player, len_board)
        print(f"Human player {player}'s move: {move}")
        logging.info(f"Human player {player}'s move: {move}")
    else:
        algo_to_use = player1_algo if player == 1 else player2_algo
        if algo_to_use == "dnn":
            move = bestMove(board=board, model=model, player=player, rnd=rnd)
        elif algo_to_use == "minimax":
            depth = 8 if len_board == 3 else 6
            m = alphabeta_minimax.ab_minimax(board=board, depth=depth, player=player, is_maximizing_player=True,
                                             initial_player=player, alpha=[-1, -1, -inf], beta=[-1, -1, inf])
            move = (m[0], m[1])
        print(f"AI player {player}'s move [{move}] with {algo_to_use}. "
              f"{'Attacker'if player == 1 else 'Defender'} skill level set to {attacker_skill if player == 1 else defender_skill}.")
        logging.info(f"AI player {player}'s move [{move}] with {algo_to_use}. "
              f"{'Attacker'if player == 1 else 'Defender'} skill level set to {attacker_skill if player == 1 else defender_skill}.")

    if chaos_agent.is_time_for_chaos(player=player, attacker_skill_level=attacker_skill,
                                     defender_skill_level= defender_skill):
        chaos_board = chaos_agent.implement_chaos(player, copy.deepcopy(board), move, attacker_skill, defender_skill)
        print(f"⚠ Chaos Agent initiated for player {player}. Board changed to {chaos_board} ⚠")
        logging.info(f"⚠ Chaos Agent initiated for player {player}. Board changed to {chaos_board} ⚠")
        chaos_count[player-1] += 1
        current_state = copy.deepcopy(chaos_board)
        move_outcome = []
    else:
        board[move[0]][move[1]] = int(player)
        current_state = copy.deepcopy(board)

        move_outcome = eval_move(prev_state=previous_state, current_state=current_state, exploit_tracker=exploit_tracker,
                                 launcher=launcher, defender_skill_level=defender_skill, attack_container=attack, defense_container=defense, docker=docker, debug=verbose)

        print(f"cyber move made: {move_outcome}")
        logging.info(f"cyber move made: {move_outcome}")

    if generate_data:
        helpers.write_csv(filename=gameplay_outcsv, row=[previous_state, current_state, player, move_outcome, game_id])

    # print board to console if verbose = true
    if verbose:
        print(printBoard(board))
        logging.info(f"\n{printBoard(board)}\n")
        print(f"\nplayer {player} move complete...\n")

    winner = getWinner(board)
    return winner, board, chaos_count

"""
This function simulates a game between two AIs.

Inputs: model - keras model (neural network) for both AIs (common model)
        rnd1, rnd2 = a float number to add some randomness to


 the AIs moves
        verbose = boolean to print board and AI moves to the console (default = True)
Outputs: winner - integer to indicate the winner (1 or 2) or a tie (0)
         board - a 2d numpy array of the final board state upon a win or a tie
"""


def ai_vs_ai(model, rnd1, rnd2, len_board, verbose, delay, generate_data, exploit_tracker, launcher, docker,
             attacker_skill, defender_skill, player1_algo, player2_algo, game_id, gameplay_outcsv):
    # initialize docker containers for attack and defense
    attack, defense = start_game_docker(docker)
    # initialize counter for chaos agent occurence
    chaos_count = [0, 0]
    # initialize board, winner variable, and numpy array of board
    board = initBoard(len_board)
    winner = getWinner(board)
    # while there are still more moves to make and no winner has been determined:
    while winner == -1:
        winner, board, chaos_count = get_player_move(model, rnd1, board=board, len_board=len_board, player=1,
                                                     verbose=verbose, generate_data=generate_data, human=False,
                                                     exploit_tracker=exploit_tracker, launcher=launcher, docker=docker,
                                                     attack=attack, defense=defense, attacker_skill=attacker_skill,
                                                     defender_skill=defender_skill, player1_algo=player1_algo,
                                                     player2_algo=player2_algo, game_id=game_id,
                                                     chaos_count=chaos_count, gameplay_outcsv=gameplay_outcsv)
        if delay: time.sleep(3)
        # if no winner or tie, player 2's turn
        if winner == -1:
            winner, board, chaos_count = get_player_move(model, rnd2, board=board, len_board=len_board, player=2,
                                                         verbose=verbose, generate_data=generate_data, human=False,
                                                         exploit_tracker=exploit_tracker, launcher=launcher,
                                                         docker=docker, attack=attack, defense=defense,
                                                         attacker_skill=attacker_skill,defender_skill=defender_skill,
                                                         player1_algo=player1_algo, player2_algo=player2_algo,
                                                         game_id=game_id, chaos_count=chaos_count,
                                                         gameplay_outcsv=gameplay_outcsv)

            if delay: time.sleep(3)
        else:
            # if there is a winner or player 1 has tied the game, return data
            return winner, np.array(board), chaos_count
    return winner, np.array(board), chaos_count


def ai_vs_human(model, rnd1, rnd2, len_board, verbose, delay, generate_data, human_plays, exploit_tracker, launcher,
                docker, attacker_skill, defender_skill, player1_algo, player2_algo, game_id, gameplay_outcsv):
    # initialize docker containers for attack and defense
    attack, defense = start_game_docker(docker)
    # initialize counter for chaos agent occurence
    chaos_count = [0, 0]
    # initialize board, winner variable, and numpy array of board
    board = initBoard(len_board)
    winner = getWinner(board)

    # while there are still more moves to make and no winner has been determined:
    while winner == -1:
        winner, board, chaos_count = get_player_move(model, rnd1, board=board, len_board=len_board, player=1,
                                                     verbose=verbose, generate_data=generate_data,
                                                     human=True if human_plays == 1 else False,
                                                     exploit_tracker=exploit_tracker, launcher=launcher, docker=docker,
                                                     attack=attack, defense=defense, attacker_skill=attacker_skill,
                                                     defender_skill=defender_skill, player1_algo=player1_algo,
                                                     player2_algo=player2_algo, game_id=game_id,
                                                     chaos_count=chaos_count,gameplay_outcsv=gameplay_outcsv)

        if delay: time.sleep(3)
        # if no winner or tie, player 2's turn
        if winner == -1:
            winner, board, chaos_count = get_player_move(model, rnd2, board=board, len_board=len_board, player=2,
                                            verbose=verbose, generate_data=generate_data,
                                            human=True if human_plays == 2 else False, exploit_tracker=exploit_tracker,
                                            launcher=launcher, docker=docker, attack=attack, defense=defense,
                                            attacker_skill=attacker_skill, defender_skill=defender_skill,
                                            player1_algo=player1_algo, player2_algo=player2_algo, game_id=game_id,
                                                         chaos_count=chaos_count, gameplay_outcsv=gameplay_outcsv)

            if delay: time.sleep(3)
        else:
            # if there is a winner or player 1 has tied the game, return data
            return winner, np.array(board), chaos_count
    # return data
    return winner, np.array(board), chaos_count


def ai_vs_ai_statistics(games):
    # stats for player 1 only
    stats = {"win": 0, "loss": 0, "draw": 0}
    for game in games:
        if game == 1:
            stats["win"] += 1
        elif game == 2:
            stats["loss"] += 1
        elif game == 0:
            stats["draw"] += 1
        else:
            print(game)

    winPct = stats["win"] / len(games) * 100
    lossPct = stats["loss"] / len(games) * 100
    drawPct = stats["draw"] / len(games) * 100

    print("Results for player 1:")
    print("Total Games: ", len(games))
    print("Wins: %d (%.1f%%)" % (stats["win"], winPct))
    print("Loss: %d (%.1f%%)" % (stats["loss"], lossPct))
    print("Draw: %d (%.1f%%)" % (stats["draw"], drawPct))


def current_milli_time():
    return round(time.time() * 1000)


def printWinner(winner):
    if winner > 0:
        print("Player {0} Wins!".format(winner))
        logging.info("Player {0} Wins!".format(winner))
    else:
        print("Tie!")
        logging.info("Tie!")

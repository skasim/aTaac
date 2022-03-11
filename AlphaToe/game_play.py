import copy
import random
import time

import numpy as np
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import Sequential
from keras.utils.np_utils import to_categorical

from game_eval import eval_move
import helpers

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
    for i in range(len(board)):
        for j in range(len(board[i])):
            mark = ' '
            if board[i][j] == 1:
                mark = 'X'
            elif board[i][j] == 2:
                mark = 'O'
            if (j == len(board[i]) - 1):
                print(mark)
            else:
                print(str(mark) + "|", end='')
        if (i < len(board) - 1):
            if len(board) == 3:
                print("-----")
            else:
                print("----------")


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
    diags = [board_array[::-1, :].diagonal(i) for i in range(-board_array.shape[0] + 1, board_array.shape[1])]
    diags.extend(board_array.diagonal(i) for i in range(board_array.shape[1] - 1, -board_array.shape[0], -1))

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
def bestMove(board, model, player, rnd=0):
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


# Simulate a game
def simulateGame(p1=None, p2=None, rnd=0):
    history = []
    board = initBoard()
    playerToMove = 1

    while getWinner(board) == -1:

        # Chose a move (random or use a player model if provided)
        move = None
        if playerToMove == 1 and p1 != None:
            move = bestMove(board, p1, playerToMove, rnd)
        elif playerToMove == 2 and p2 != None:
            move = bestMove(board, p2, playerToMove, rnd)
        else:
            moves = getMoves(board)
            move = moves[random.randint(0, len(moves) - 1)]

        # Make the move
        board[move[0]][move[1]] = playerToMove

        # Add the move to the history
        history.append((playerToMove, move))

        # Switch the active player
        playerToMove = 1 if playerToMove == 2 else 2

    return history


# Reconstruct the board from the move list
def movesToBoard(moves):
    board = initBoard()
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


def gameStats(games, player=1):
    # initialize dictionary
    stats = {"win": 0, "loss": 0, "draw": 0}

    # iterate through each game
    for game in games:
        # get the result of the game
        result = getWinner(movesToBoard(game))

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
        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'])
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
        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'])
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


"""
This function simulates a game between two AIs.

Inputs: model - keras model (neural network) for both AIs (common model)
        rnd1, rnd2 = a float number to add some randomness to the AIs moves
        verbose = boolean to print board and AI moves to the console (default = True)
Outputs: winner - integer to indicate the winner (1 or 2) or a tie (0)
         board - a 2d numpy array of the final board state upon a win or a tie
"""


def ai_vs_ai(model, len_board, rnd1=0, rnd2=0, verbose=True, delay=True, generate_data=False):
    # initialize board, winner variable, and numpy array of board
    board = initBoard(len_board)
    winner = getWinner(board)

    # while there are still more moves to make and no winner has been determined:
    while winner == -1:
        # player 1 makes a move
        previous_state = copy.deepcopy(board)
        move = bestMove(board=board, model=model, player=1, rnd=rnd1)
        board[move[0]][move[1]] = 1
        current_state = copy.deepcopy(board)

        move_outcome = eval_move(prev_state=previous_state, current_state=current_state)

        if generate_data:
            load_dotenv()
            if len(board) == 3:
                fnanme = os.getenv("RANDOM_FOREST_3x3")
            if len(board) == 5:
                fnanme = os.getenv("RANDOM_FOREST_5x5")
            helpers.write_csv(filename=fname,row=[previous_state, current_state, "1", move_outcome])

        # print board to console if verbose = true
        if verbose:
            printBoard(board)
            print("\nplayer 1 move complete...\n")

        # check for winner
        winner = getWinner(board)

        if delay: time.sleep(3)
        # if no winner or tie, player 2's turn
        if winner == -1:
            # player 2 makes a move
            previous_state = copy.deepcopy(board)
            move = bestMove(board=board, model=model, player=2, rnd=rnd2)
            board[move[0]][move[1]] = 2
            current_state = copy.deepcopy(board)

            move_outcome = eval_move(prev_state=previous_state, current_state=current_state)
            if generate_data:
                helpers.write_csv(filename=f"rf_{len_board}x{len_board}.csv", row=[previous_state, current_state,
                                                                               "2", move_outcome])

            # print board to console if verbose = true
            if verbose:
                printBoard(board)
                print("\nplayer 2 move complete...\n")

            # check for winner
            winner = getWinner(board)
            if delay: time.sleep(3)
        else:
            # if there is a winner or player 1 has tied the game, return data
            return winner, np.array(board)
            break

    # return data
    return winner, np.array(board)


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
    else:
        print("Tie!")
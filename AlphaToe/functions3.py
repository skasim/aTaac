import random
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.backend import reshape
from keras.utils.np_utils import to_categorical
import time

# Get an empty board
#
# 0 indicates an empty space, 1 indicates an 'X' (player 1), and 2 indicates an 'O' (player 2)
#
# Initially the board is empty, so we return a 3x3 array of zeroes.
def initBoard():
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    return board

# Print the current state of the board
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
            print("-----")

# Get a list of valid moves (indices into the board)
def getMoves(board):
    moves = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 0:
                moves.append((i, j))
    return moves

def check_win(arr):
    if arr[0] == arr[1] == arr[2] == 1:
        return 1
    elif arr[0] == arr[1] == arr[2] == 2:
        return 2
    else:
        return False


def getWinner(board):
    board_array = np.array(board)
    wins = []

    for j in range(3):
        winner = check_win(board_array[:, j])
        wins.append(winner)

    for i in range(3):
        winner = check_win(board_array[i, :])
        wins.append(winner)

    diags = [board_array[::-1, :].diagonal(i) for i in range(-board_array.shape[0] + 1, board_array.shape[1])]
    diags.extend(board_array.diagonal(i) for i in range(board_array.shape[1] - 1, -board_array.shape[0], -1))

    for each in diags:
        if len(each) == 3:
            wins.append(check_win(each))

    wins2 = [win for win in wins if win]

    if not wins2:
        if len(getMoves(board)) == 0:
            return 0

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
        prediction = model.predict(future.reshape((-1, 9)))[0]
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


# Aggregate win/loss/draw stats for a player
def gameStats(games, player=1):
    stats = {"win": 0, "loss": 0, "draw": 0}
    for game in games:
        result = getWinner(movesToBoard(game))
        if result == -1:
            continue
        elif result == player:
            stats["win"] += 1
        elif result == 0:
            stats["draw"] += 1
        else:
            stats["loss"] += 1

    winPct = stats["win"] / len(games) * 100
    lossPct = stats["loss"] / len(games) * 100
    drawPct = stats["draw"] / len(games) * 100

    print("Results for player %d:" % (player))
    print("Wins: %d (%.1f%%)" % (stats["win"], winPct))
    print("Loss: %d (%.1f%%)" % (stats["loss"], lossPct))
    print("Draw: %d (%.1f%%)" % (stats["draw"], drawPct))

def getModel():
    numCells = 9 # How many cells in a 3x3 tic-tac-toe board?
    outcomes = 3 # How many outcomes are there in a game? (draw, X-wins, O-wins)
    model = Sequential()
    model.add(Dense(200, activation='relu', input_shape=(numCells, )))
    model.add(Dropout(0.2))
    model.add(Dense(125, activation='relu'))
    model.add(Dense(75, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(25, activation='relu'))
    model.add(Dense(outcomes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'])
    return model


# Get a set of board states labelled by who eventually won that game
def gamesToWinLossData(games):
    X = []
    y = []
    for game in games:
        winner = getWinner(movesToBoard(game))
        for move in range(len(game)):
            X.append(movesToBoard(game[:(move + 1)]))
            y.append(winner)

    X = np.array(X).reshape((-1, 9))
    y = to_categorical(y)

    # Return an appropriate train/test split
    trainNum = int(len(X) * 0.8)
    return (X[:trainNum], X[trainNum:], y[:trainNum], y[trainNum:])

# nawal: this is still a bit buggy in some cases - iron it out
def ai_vs_ai(model, rnd1=0, rnd2=0, verbose=True):
    board = initBoard()
    winner = getWinner(board)

    while winner == -1:
        # board, model, player, rnd=0
        move = bestMove(board=board, model=model, player=1, rnd=rnd1)
        board[move[0]][move[1]] = 1
        if verbose:
            printBoard(board)
            print("\n*********\n")
        winner = getWinner(board)
        if winner == -1:
            move = bestMove(board=board, model=model, player=2, rnd=rnd2)
            board[move[0]][move[1]] = 2
            if verbose:
                printBoard(board)
                print("\n*********\n")
            winner = getWinner(board)
        else:
            return winner, np.array(board)
            break

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

    print("Results for player 1:" )
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
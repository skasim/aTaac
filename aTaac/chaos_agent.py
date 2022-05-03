import random
import logging


def is_time_for_chaos(player, attacker_skill_level, defender_skill_level):
    chaos_thresholds = {
        5: .99,
        4: .90,
        3: .70,
        2: .30,
        1: .20,
        0: .05
    }
    rand = random.random()
    skill_level = attacker_skill_level if player == 1 else defender_skill_level
    chaos_probability = chaos_thresholds[skill_level]
    if rand >= chaos_probability:
        print(f"random value [{rand}] >= chaos probability [{chaos_probability}]")
        logging.info(f"random value [{rand}] >= chaos probability [{chaos_probability}]")
        return True
    return False


def implement_chaos(player, board, move, attacker_skill_level, defender_skill_level):
    """
    If there is a wide gap between the player skills then the weaker player is pwned and the
    player's move is replaced with the opposing player's move.
    If there is not a wide skills game then the player's move is replaced with 0 (i.e., move is
    deleted.
    """
    if attacker_skill_level > defender_skill_level and attacker_skill_level - defender_skill_level >= 3:
        return pwn(pwned_player=player, board=board, move=move)
    elif defender_skill_level > attacker_skill_level and defender_skill_level - attacker_skill_level >= 3:
        return pwn(pwned_player=player, board=board, move=move)
    else:
        board[move[0]][move[1]] = 0
        return board


def pwn(pwned_player, board, move):
    switch_players = {
        2: 1,
        1: 2
    }
    board[move[0]][move[1]] = switch_players[pwned_player]
    return board

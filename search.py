"""
This file contains the functions performing search (more specifically minimax-negamax-ab pruning)
"""
import math
import sys
import time
from board import Board
from evaluation import score


def update_progress(progress):
    """Progress bar"""
    barlength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barlength*progress))
    text = "\rPercent: [{0}] {1} % {2}".format("="*block + "-"*(barlength-block), format(progress*100, '.2f'), status)
    sys.stdout.write(text)
    sys.stdout.flush()



def negamax(state, player, depth):
    """
    Negamax search (recursive)

    Implementation of negamax is due to max(a,b)=-min(-a,-b)
    """
    if depth == 0:
        scr = score(state, player)
        if player == 'w':
            return (scr, ())
        return (-scr, ())
    max_score = -math.inf
    max_move = ()
    all_moves = state.legal_moves(player)
    for piece in all_moves:
        for move in all_moves[piece]:
            try:
                newstate = state.make_move(piece, move[0][0], move[0][1], move[1])
            except:
                print('except')
            if player == 'w':
                player = 'b'
            elif player == 'b':
                player = 'w'
            negascore = negamax(newstate, player, depth-1)
            if -negascore[0] > max_score:
                max_score = -negascore[0]
                max_move = piece, move
    return max_score, max_move


def ab_negamax(state, player, alpha, beta, depth):
    """
    Negamax search (recursive)

    Implementation of negamax is due to max(a,b)=-min(-a,-b)
    """
    if depth == 0:
        scr = round(score(state, player), 4)
        return (scr, ())
    max_score = -math.inf
    max_move = ()
    all_moves = state.legal_moves(player)
    next_player = player
    for progress, piece in enumerate(all_moves):
        for move in all_moves[piece]:
            newstate = state.make_move(piece, move[0][0], move[0][1], move[1])
            if player == 'w':
                next_player = 'b'
            elif player == 'b':
                next_player = 'w'
            negascore = ab_negamax(newstate, next_player, -beta, -alpha, depth-1)
            # Fail soft beta cutoff
            if -negascore[0] >= beta:
                max_move = piece, move
                return -negascore[0], max_move
            # Update max-score and alpha
            if -negascore[0] > max_score:
                max_score = -negascore[0]
                max_move = piece, move
                if -negascore[0] > alpha:
                    alpha = -negascore[0]
        try:
            if depth == levels:
                update_progress(progress+1/len(all_moves))
        except:
            pass
    return max_score, max_move



if __name__ == "__main__":
    board = Board()
    gamestate = board.iboard()
    colour = 'w'
    levels = 1
    srch = 'alpha-beta'
    #srch = 'nega'

    print('Depth search:', levels)
    print('Search used:', srch)

    if srch == 'nega':
        negastart = time.clock()
        nega = negamax(gamestate, colour, levels)
        negaend = time.clock()
        print('Negamax Elapsed time:', round(negaend-negastart, 2), 's')
        print('\nnegamax:', nega[0], nega[1])
    if srch == 'alpha-beta':
        abstart = time.clock()
        ab = ab_negamax(gamestate, colour, -math.inf, math.inf, levels)
        abend = time.clock()
        print('Alpha-beta nega Elapsed time:', round(abend-abstart, 2), 's')
        print('score:', round(ab[0], 4), '| Move:', ab[1])

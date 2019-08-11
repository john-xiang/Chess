"""
This file contains the functions for evaluating a state

The main scoring function takes as input the current state
returns the score as a linear combination of terms:
material score: the score for material
mobility score: the score for how mobile a position is
"""
from collections import defaultdict
from board import Board


def material_score(state):
    """
    Function that calculates material score
    pieces are worth the following points
    pawn, knight, bishop, queen, rook, king:
    1   , 3     , 4     , 13   , 8   , 1000
    """
    pawn = 100
    knight = 400
    bishop = 500
    rook = 850
    queen = 1300
    king = 100000

    pieces = defaultdict(int)
    for square in state.squares:
        curr_piece = state.squares[square].piece
        if curr_piece is not None and curr_piece.colour == 'w':
            wpiece = ('w'+curr_piece.piece, curr_piece)
            pieces[wpiece[0]] += 1
            if curr_piece.piece == 'B' and pieces[wpiece[0]] == 2:
                pieces[wpiece[0]] += 50
        elif curr_piece is not None and curr_piece.colour == 'b':
            bpiece = ('b'+curr_piece.piece, curr_piece)
            pieces[bpiece[0]] += 1
            if curr_piece.piece == 'B' and pieces[bpiece[0]] == 2:
                pieces[bpiece[0]] += 50

    mat_score = ((king*(pieces['wK']-pieces['bK']))\
                 +queen*(pieces['wQ']-pieces['bQ']))\
                 +(rook*(pieces['wR']-pieces['bR']))\
                 +(knight*(pieces['wN']-pieces['bN']))\
                 +(bishop*(pieces['wB']-pieces['bB']))\
                 +(pawn*(pieces['wP']-pieces['bP']))
    return mat_score


def mobility_score(state):
    """Function calculates mobility score"""
    wmoves = state.legal_moves('w')
    bmoves = state.legal_moves('b')
    movable_wpieces = len(wmoves)
    movable_bpieces = len(bmoves)
    if movable_bpieces == 0 or movable_wpieces == 0:
        return 0
    num_wmoves = 0
    num_bmoves = 0

    for pieces in wmoves:
        num_wmoves += len(pieces)
    for pieces in bmoves:
        num_bmoves += len(pieces)
    # This scoring is inspired from freedom/papa's evaluation function
    # ratio between #moveable white pieces to # moveable black pieces x ...
    # ... x ratio of white legal moves and black legal moves
    scr = round((movable_wpieces/movable_bpieces)*(num_wmoves/num_bmoves)*100, 5)
    return scr


def score(state):
    """
    Scoring function
    """
    mscore = material_score(state)
    mobscore = mobility_score(state)

    scr = mscore + mobscore #+...

    return scr


def score_all(state, player):
    """Scores all moves for the current position"""
    moves = state.legal_moves(player)
    scores = defaultdict()
    for piece in moves:
        pce = state.squares[piece].piece
        for move in moves[piece]:
            newstate = state.make_move(piece, move[0][0], move[0][1])
            scores[pce.piece, move] = score(newstate)
    return scores


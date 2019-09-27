"""
This file contains the functions for evaluating a state

The main scoring function takes as input the current state
returns the score as a linear combination of terms:
material score: the score for material
mobility score: the score for how mobile a position is
"""
from collections import defaultdict


def material_score(state, player):
    """
    Function that calculates material score
    pieces are worth the following points
    pawn, knight, bishop, queen, rook, king:
    1   , 3     , 4     , 13   , 8   , 100000
    """
    pawn = 100
    knight = 400
    bishop = 500
    rook = 850
    queen = 1300
    king = 100000
    pos_score = 0

    pieces = defaultdict(int)
    for square in state.squares:
        curr_piece = state.squares[square].piece
        if curr_piece is not None and curr_piece.colour == 'w':
            wpiece = ('w'+curr_piece.piece, curr_piece)
            pieces[wpiece[0]] += 1
            if curr_piece.piece == 'B' and pieces[wpiece[0]] == 2:
                pieces[wpiece[0]] += 50
            # Calculate position score
            if player == 'w':
                pos_score += curr_piece.pstable[curr_piece.file][curr_piece.rank]
        elif curr_piece is not None and curr_piece.colour == 'b':
            bpiece = ('b'+curr_piece.piece, curr_piece)
            pieces[bpiece[0]] += 1
            if curr_piece.piece == 'B' and pieces[bpiece[0]] == 2:
                pieces[bpiece[0]] += 50
            # Calculate position score
            if player == 'b':
                pos_score += curr_piece.pstable[curr_piece.file][curr_piece.rank]

    mat_score = ((king*(pieces['wK']-pieces['bK']))\
                 +queen*(pieces['wQ']-pieces['bQ']))\
                 +(rook*(pieces['wR']-pieces['bR']))\
                 +(knight*(pieces['wN']-pieces['bN']))\
                 +(bishop*(pieces['wB']-pieces['bB']))\
                 +(pawn*(pieces['wP']-pieces['bP']))

    return mat_score + pos_score


def mobility_score(state, player):
    """
    Function calculates mobility score
    CURRENTLY TOO SLOW
    """
    moves = state.legal_moves(player)
    moveable_pieces = len(moves)
    num_moves = 0

    for pieces in moves:
        num_moves += len(pieces)

    scr = round((0.8*num_moves + 0.2*moveable_pieces), 5)
    return scr


def score(state, player):
    """
    Scoring function
    """
    matscore = material_score(state, player)
    #mobscore = mobility_score(state, player)
    mobscore = 0

    scr = (0.8*matscore) + (0.2*mobscore) #+...
    if player == 'w':
        return scr
    return -scr


def score_all(state, player):
    """Scores all moves for the current position"""
    moves = state.legal_moves(player)
    scores = defaultdict()
    for piece in moves:
        pce = state.squares[piece].piece
        for move in moves[piece]:
            newstate = state.make_move(piece, move[0][0], move[0][1], move[1])
            scores[pce.piece, move] = score(newstate, player)
    return scores

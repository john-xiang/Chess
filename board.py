"""
This file contains the board class.

This class is responsible for setting/rendering the board, and conducting moves
"""

from collections import defaultdict
import copy
import pygame
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Square:
    """square class contains properties: colour, xy position, coordinates, piece on sq"""
    def __init__(self, colour=None, sqrcolour=None, position=None, coord=None, piece=None):
        self.colour = colour
        # RGB colour
        self.sqrcolour = sqrcolour
        self.position = position
        self.coord = coord
        # this is a Piece class
        self.piece = piece


    def get_piece(self):
        """Returns the piece on current square"""
        return self.piece


    def get_pos(self):
        """Returns the x,y position of current square"""
        return self.position


# Class that represents the state of the board
class State:
    """
    State class defines the current state: contains all squares on the board and other variables
    """
    def __init__(self):
        """
        Init method instantiates state object
        Attributes:
        squares: all squares of the board (each is a square object)
        last_move: the square where last move was made
        enpassant: tells the board whether enpassant capture is available
        wking: location of white king
        bking: location of black king
        wpieces: all white pieces
        bpieces: all black pieces
        """
        self.squares = defaultdict()
        self.last_move = ()
        self.enpassant = False
        self.status = ''
        self.wking = None
        self.bking = None


    def attack(self, piece):
        """Returns all squares the current piece is attacking"""
        moves = piece.valid_moves(self)
        atking = []
        for move in moves:
            atkfile = move[0]
            atkrank = move[1]
            atksq = self.squares[atkfile, atkrank]
            try:
                status = move[2]
                if status == 'E' and self.enpassant:
                    if piece.colour == 'w':
                        enpass = (atkfile, atkrank+1)
                    elif piece.colour == 'b':
                        enpass = (atkfile, atkrank-1)
                    atking.append((enpass))
                elif status == 'X':
                    if atksq.piece is not None and atksq.piece.colour != piece.colour:
                        atking.append((atkfile, atkrank))
            except IndexError:
                if atksq.piece is not None and atksq.piece.colour != piece.colour:
                    atking.append((atkfile, atkrank))
        return atking


    def attack_by(self, player, square):
        """This function outputs all pieces attacking the input square"""
        atkby = []
        for sqr in self.squares:
            current_piece = self.squares[sqr].piece
            if current_piece is not None and player != current_piece.colour:
                if current_piece.piece != 'P':
                    atks = current_piece.valid_moves(self)
                else:
                    if player == 'w':
                        atks = ((current_piece.file+1, current_piece.rank+1), (current_piece.file-1, current_piece.rank+1))
                    elif player == 'b':
                        atks = ((current_piece.file+1, current_piece.rank-1), (current_piece.file-1, current_piece.rank-1))
                for move in atks:
                    if square.position == (move[0], move[1]):
                        atkby.append(current_piece.piece)
        return atkby


    def check(self, player):
        """Returns true if player in check, otherwise return false"""
        if player == 'w':
            king = self.squares[self.wking.file, self.wking.rank].piece
        elif player == 'b':
            king = self.squares[self.bking.file, self.bking.rank].piece
        if king is not None:
            ksq = self.squares[king.file, king.rank]
        else:
            print('no king square')
            return False
        atks = self.attack_by(player, ksq)
        if not atks:
            return False
        return True


    def checking(self, piece):
        """If the piece is attacking the enemy's king, then a check is declared"""
        atking = self.attack(piece)
        for atks in atking:
            pce = self.squares[atks].piece
            # King is in check
            if pce.piece == 'K' and pce.colour != piece.colour:
                if pce.colour == 'w':
                    self.wking.checked = True
                    self.squares[self.wking.file, self.wking.rank].checked = True
                elif pce.colour == 'b':
                    self.bking.checked = True
                    self.squares[self.bking.file, self.bking.rank].checked = True
                return True
        return False


    def checkmate(self, player):
        """
        Function that returns true if player is mated
        If there are no legal moves then checkmate
        """
        if not self.legal_moves(player):
            return True
        return False


    def checkmate2(self, player, state):
        """
        Function that determins checkmate
        checks all squares with pieces on them
        """
        all_moves = []
        for square in state.squares:
            current_pce = state.squares[square].piece
            if current_pce is not None and current_pce.colour == player:
                moves = current_pce.valid_moves(state)
                for move in moves:
                    try:
                        newstate = self.move(current_pce, move[0], move[1], state)
                    except AttributeError:
                        newstate = 0
                    if newstate != 0:
                        all_moves.append((current_pce, move))
        # This means all_moves is empty
        if not all_moves:
            return True
        return False


    def legal_moves(self, player):
        """Function finds all legal moves for player"""
        all_moves = defaultdict(list)
        for square in self.squares:
            sqr = self.squares[square]
            if sqr.piece is not None and sqr.piece.colour == player:
                for move in sqr.piece.valid_moves(self):
                    try:
                        status = move[2]
                    except IndexError:
                        status = 0
                    # if move is castle, check the empty squares
                    if status == 'C':
                        # Castle Queen side
                        if move[0] == 2:
                            empty_sqr = self.squares[move[0]+1, move[1]]
                            atks = self.attack_by(sqr.piece.colour, empty_sqr)
                            # Only allow castle if the squares between are not attacked
                            if atks:
                                continue
                        # Castle King side
                        elif move[0] == 6:
                            empty_sqr = self.squares[move[0]-1, move[1]]
                            atks = self.attack_by(sqr.piece.colour, empty_sqr)
                            # Only allow castle if the squares between are not attacked
                            if atks:
                                continue
                    if self.try_move(sqr.piece, move[0], move[1]):
                        all_moves[sqr.position].append((move[0], move[1]))
        return all_moves


    def try_move(self, piece, file, rank):
        """
        Helper function for finding legal moves

        This function will try the move and if it leaves own king in check then not allowed
        """
        try_state = copy.deepcopy(self)
        try_piece = try_state.squares[piece.file, piece.rank].piece
        # remove piece on new square
        del try_state.squares[file, rank].piece
        try_piece.move_to(file, rank)
        try_state.squares[file, rank].piece = try_piece
        # remove piece on old square
        del try_state.squares[piece.file, piece.rank].piece
        try_state.squares[piece.file, piece.rank].piece = None

        if try_piece.piece == 'K':
            if try_piece.colour == 'w':
                try_state.wking = try_piece
            elif try_piece.colour == 'b':
                try_state.bking = try_piece
        if try_state.check(piece.colour):
            return False
        return True


class Board:
    """
    Board class initiates and renders board
    """
    def __init__(self, display, cellsize):
        """
        init method that instantiates board object
        Attributes:
        display: the game display
        cellsize: size of each square
        state: state object
        turn_num: keeps track of the turn number
        enpass_capture: variable for rendering enpassant
        castle: variable for rendering castle move
        """
        self.display = display
        self.cellsize = cellsize
        self.state = State()
        self.turn_num = 0
        self.enpass_capture = False
        self.castle = False


    def set_board(self):
        """
        class sets up the board and renders it to the game display
        """
        board_size = 8
        buffer = 25
        white = (238, 219, 179)
        black = (181, 135, 99)
        lines = [0, 1, 6, 7]
        placed = 0
        order = ['rookb', 'pawnb', 'pawnw', 'rookw',
                 'knightb', 'pawnb', 'pawnw', 'knightw',
                 'bishopb', 'pawnb', 'pawnw', 'bishopw',
                 'queenb', 'pawnb', 'pawnw', 'queenw',
                 'kingb', 'pawnb', 'pawnw', 'kingw',
                 'bishopb', 'pawnb', 'pawnw', 'bishopw',
                 'knightb', 'pawnb', 'pawnw', 'knightw',
                 'rookb', 'pawnb', 'pawnw', 'rookw']
        squares = defaultdict()
        switch = False
        # Draws the board and initializes starting positions of pieces
        for file in range(board_size):
            switch = not switch
            for rank in range(board_size):
                xfile = self.cellsize*file+buffer
                yrank = self.cellsize*rank+buffer
                if switch:
                    # draw square
                    pygame.draw.rect(self.display, white, [xfile, yrank, self.cellsize, self.cellsize])
                    # set property for the current square
                    squares[file, rank] = Square('w', white, (file, rank), (xfile, yrank))
                    switch = False
                elif not switch:
                    # draw square on display
                    pygame.draw.rect(self.display, black, [xfile, yrank, self.cellsize, self.cellsize])
                    # set property for current square
                    squares[file, rank] = Square('b', black, (file, rank), (xfile, yrank))
                    switch = True
                if rank in lines:
                    current_piece = order[placed]
                    # Initialize pieces
                    if 'rookb' in current_piece:
                        piece = Rook(file, rank, 'b')
                    elif 'rookw' in current_piece:
                        piece = Rook(file, rank, 'w')
                    elif 'pawnb' in current_piece:
                        piece = Pawn(file, rank, 'b')
                    elif 'pawnw' in current_piece:
                        piece = Pawn(file, rank, 'w')
                    elif 'knightb' in current_piece:
                        piece = Knight(file, rank, 'b')
                    elif 'knightw' in current_piece:
                        piece = Knight(file, rank, 'w')
                    elif 'bishopb' in current_piece:
                        piece = Bishop(file, rank, 'b')
                    elif 'bishopw' in current_piece:
                        piece = Bishop(file, rank, 'w')
                    elif 'queenb' in current_piece:
                        piece = Queen(file, rank, 'b')
                    elif 'queenw' in current_piece:
                        piece = Queen(file, rank, 'w')
                    elif 'kingb' in current_piece:
                        piece = King(file, rank, 'b')
                        self.state.bking = piece
                    elif 'kingw' in current_piece:
                        piece = King(file, rank, 'w')
                        self.state.wking = piece
                    image = pygame.image.load(piece.img)
                    # Draw piece onto the board
                    self.display.blit(image, squares[file, rank].coord)
                    # Set piece for the current square
                    squares[file, rank].piece = piece
                    placed += 1
        pygame.display.update()
        self.state.squares = squares
        self.enpass_capture = False
        self.castle = False


    def move(self, piece, newfile, newrank, state):
        """
        Function that performs the move
        """
        file = piece.file
        rank = piece.rank
        newstate = copy.deepcopy(state)
        npiece = newstate.squares[file, rank].piece
        moves = npiece.valid_moves(newstate)

        for move in moves:
            xfile = move[0]
            yrank = move[1]
            if (newfile, newrank) == (xfile, yrank):
                # Promotion
                if npiece.piece == 'P' and (newrank == 0 or newrank == 7):
                    newstate.squares[newfile, newrank].piece = Queen(newfile, newrank, npiece.colour)
                    del newstate.squares[file, rank].piece
                    newstate.squares[file, rank].piece = None
                    newstate.status = '='
                    return newstate
                # Check for special moves
                try:
                    status = move[2]
                except IndexError:
                    status = 0

                # Castle move
                if status == 'C':
                    # Variable for rendering castle move
                    self.castle = True
                    # Move the king
                    npiece.move_to(newfile, newrank)
                    newstate.squares[newfile, newrank].piece = npiece
                    del newstate.squares[file, rank].piece
                    newstate.squares[file, rank].piece = None

                    if npiece.colour == 'w':
                        newstate.wking = npiece
                    elif npiece.colour == 'b':
                        newstate.bking = npiece

                    # Castle Queen side
                    if newfile == 2:
                        # Set the rook to the right side of King
                        newstate.squares[newfile+1, newrank].piece = newstate.squares[newfile-2, newrank].piece
                        newstate.squares[newfile+1, newrank].piece.move_to(newfile+1, newrank)
                        newstate.squares[newfile+1, newrank].piece.first_move = False
                        # remove the old rook
                        del newstate.squares[newfile-2, newrank].piece
                        newstate.squares[newfile-2, newrank].piece = None
                        newstate.status = '0-0-0'
                    # Castle King side
                    elif newfile == 6:
                        # Set the rook to the left side of King
                        newstate.squares[newfile-1, newrank].piece = newstate.squares[newfile+1, newrank].piece
                        newstate.squares[newfile-1, newrank].piece.move_to(newfile-1, newrank)
                        newstate.squares[newfile-1, newrank].piece.first_move = False
                        # remove the old rook
                        del newstate.squares[newfile+1, newrank].piece
                        newstate.squares[newfile+1, newrank].piece = None
                        newstate.status = '0-0'
                    npiece.first_move = False
                    return newstate
                # Double move
                elif status == 'D':
                    npiece.double = True
                    npiece.first_move = False
                    npiece.move_to(newfile, newrank)
                    # set piece on new square
                    newstate.squares[newfile, newrank].piece = npiece
                    # delete the piece on old square
                    del newstate.squares[file, rank].piece
                    newstate.squares[file, rank].piece = None
                    # Change variables
                    newstate.enpassant = True
                    newstate.status = ''
                    return newstate
                # en passant
                elif status == 'E' and newstate.enpassant:
                    npiece.move_to(newfile, newrank)
                    # Delete/set the piece on new position
                    del newstate.squares[newfile, newrank].piece
                    newstate.squares[newfile, newrank].piece = npiece
                    # Delete/set the piece on old position
                    del newstate.squares[file, rank].piece
                    newstate.squares[file, rank].piece = None

                    # if piece is white, pawns go up, if black then goes down
                    if npiece.colour == 'w':
                        del newstate.squares[newfile, newrank+1].piece
                        newstate.squares[newfile, newrank+1].piece = None
                    elif npiece.colour == 'b':
                        del newstate.squares[newfile, newrank-1].piece
                        newstate.squares[newfile, newrank-1].piece = None
                    # Tell the board that the next move cannot be an en passant move
                    newstate.enpassant = False
                    # Set variable for rendering enpassant
                    self.enpass_capture = True
                    newstate.status = 'x'
                    return newstate
                elif piece.piece == 'K':
                    npiece.first_move = False
                    npiece.checked = False
                    npiece.move_to(newfile, newrank)
                    # set new piece
                    del newstate.squares[newfile, newrank].piece
                    newstate.squares[newfile, newrank].piece = npiece
                    # delete old piece
                    del newstate.squares[file, rank].piece
                    newstate.squares[file, rank].piece = None

                    # Set the current position of the king
                    if npiece.colour == 'w':
                        newstate.wking = npiece
                    elif npiece.colour == 'b':
                        newstate.bking = npiece

                    self.castle = False
                    newstate.status = ''
                    newstate.enpassant = False
                    return newstate
                npiece.move_to(newfile, newrank)
                try:
                    npiece.first_move = False
                except AttributeError:
                    pass
                del newstate.squares[newfile, newrank].piece
                newstate.squares[newfile, newrank].piece = npiece
                del newstate.squares[file, rank].piece
                newstate.squares[file, rank].piece = None
                newstate.enpassant = False
                if status == 'X':
                    newstate.status = 'x'
                else:
                    newstate.status = ''
                return newstate
        return 0

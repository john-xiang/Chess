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

    def set_piece(self, piece):
        """sets the piece"""
        self.piece = piece

    def get_piece(self):
        """returns the current piece on square"""
        return self.piece

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
        enpass_capture: variable for rendering enpassant
        wking: location of white king
        bking: location of black king
        wpieces: all white pieces
        bpieces: all black pieces
        castle: variable for rendering castle move
        """
        self.squares = defaultdict()
        self.last_move = Square()
        self.enpassant = False
        self.enpass_capture = False
        self.castle = False
        self.wking = None
        self.bking = None

    def attack_by(self, player, square):
        """This function outputs all squares/pieces attacking the input square"""
        atkby = []
        #sel_piece = square.piece
        for sqr in self.squares:
            current_piece = self.squares[sqr].piece
            if current_piece is not None and player != current_piece.colour:
                if current_piece.piece != 'P':
                    atks = current_piece.valid_moves(self)
                    if square.position in atks:
                        atkby.append(current_piece.piece)
                else:
                    if player == 'w':
                        atks = ((current_piece.file+1, current_piece.rank+1), (current_piece.file-1, current_piece.rank+1))
                    elif player == 'b':
                        atks = ((current_piece.file+1, current_piece.rank-1), (current_piece.file-1, current_piece.rank-1))
                    if square.position in atks:
                        atkby.append(current_piece.piece)
        return atkby

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
        """
        self.display = display
        self.cellsize = cellsize
        self.state = State()
        self.turn_num = 0


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
        self.state.last_move = Square()
        self.state.enpassant = False
        self.state.enpass_capture = False
        self.state.castle = False


    def check(self, player, state):
        """Returns true if player in check, otherwise return false"""
        if player == 'w':
            king = state.squares[state.wking.file, state.wking.rank].piece
        elif player == 'b':
            king = state.squares[state.bking.file, state.bking.rank].piece
        if king is not None:
            ksq = state.squares[king.file, king.rank]
        atks = state.attack_by(player, ksq)
        if not atks:
            return False
        return True


    def checking(self, piece, state):
        """If the piece is attacking the enemy's king, then a check is declared"""
        atking = self.attack(piece, state)
        for atks in atking:
            pce = state.squares[atks].piece
            # King is in check
            if pce.piece == 'K' and pce.colour != piece.colour:
                if pce.colour == 'w':
                    state.wking.check = True
                    state.squares[state.wking.file, state.wking.rank].check = True
                elif pce.colour == 'b':
                    state.bking.check = True
                    state.squares[state.bking.file, state.bking.rank].check = True
                return True
        return False

    def checkmate(self, player, state):
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
                        new_state = self.move(current_pce, move[0], move[1], state)
                    except AttributeError:
                        new_state = 0
                    if new_state != 0:
                        all_moves.append((current_pce, move))
        # This means all_moves is empty
        if not all_moves:
            return True
        return False

    def checkmate_1(self, player, state):
        """
        Function that determines if checkmate is present
        Requires wpieces, bpieces (missing deleting from list)
        """
        all_moves = []
        if player == 'w':
            for piece in state.wpieces:
                moves = piece.valid_moves(state)
                for move in moves:
                    try:
                        new_state = self.move(piece, move[0], move[1], state)
                    except AttributeError:
                        new_state = 0
                    if new_state != 0:
                        all_moves.append((piece, move))
        elif player == 'b':
            for piece in state.bpieces:
                moves = piece.valid_moves(state)
                for move in moves:
                    try:
                        new_state = self.move(piece, move[0], move[1], state)
                    except AttributeError:
                        new_state = 0
                    if new_state != 0:
                        all_moves.append((piece, move))
        if not all_moves:
            return True
        return False


    def attack(self, piece, state):
        """Returns all squares the current piece is attacking"""
        moves = piece.valid_moves(state)
        atking = []
        for move in moves:
            atkfile = move[0]
            atkrank = move[1]
            atksq = state.squares[atkfile, atkrank]
            try:
                status = move[2]
                if status == 'E' and state.enpassant:
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


    def move(self, piece, new_file, new_rank, state):
        """
        Main Function of Board
        If move is valid, retuns the new state. Otherwise return 0
        """
        file = piece.file
        rank = piece.rank
        new_state = copy.deepcopy(state)
        sel_piece = new_state.squares[file, rank].piece
        moves = sel_piece.valid_moves(new_state)

        for move in moves:
            xfile = move[0]
            yrank = move[1]
            if (new_file, new_rank) == (xfile, yrank):
                # Promotion
                if sel_piece.piece == 'P' and (new_rank == 0 or new_rank == 7):
                    new_state.squares[new_file, new_rank].piece = Queen(new_file, new_rank, sel_piece.colour)
                    del new_state.squares[file, rank].piece
                    new_state.squares[file, rank].piece = None

                    # Check for check
                    if self.check(sel_piece.colour, new_state):
                        return 0

                    return new_state

                # Check for special moves
                try:
                    status = move[2]
                    # Castle move
                    if status == 'C':
                        # Variable for rendering castle move
                        new_state.castle = True
                        # Move the king
                        sel_piece.move_to(new_file, new_rank)
                        new_state.squares[new_file, new_rank].piece = sel_piece
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None

                        if sel_piece.colour == 'w':
                            new_state.wking = sel_piece
                        elif sel_piece.colour == 'b':
                            new_state.bking = sel_piece

                        # Check for check
                        if self.check(sel_piece.colour, new_state):
                            return 0

                        # Castle Queen side
                        if new_file == 2:
                            empty_sqr = new_state.squares[new_file+1, new_rank]
                            atks = new_state.attack_by(sel_piece.colour, empty_sqr)
                            # Only allow castle if the squares between are not attacked
                            if not atks:
                                # Set the rook to the right side of King
                                new_state.squares[new_file+1, new_rank].piece = new_state.squares[new_file-2, new_rank].piece
                                new_state.squares[new_file+1, new_rank].piece.move_to(new_file+1, new_rank)
                                new_state.squares[new_file+1, new_rank].piece.first_move = False
                                # remove the old rook
                                del new_state.squares[new_file-2, new_rank].piece
                                new_state.squares[new_file-2, new_rank].piece = None
                            else:
                                return 0
                        # Castle King side
                        elif new_file == 6:
                            empty_sqr = new_state.squares[new_file-1, new_rank]
                            atks = new_state.attack_by(sel_piece.colour, empty_sqr)
                            if not atks:
                                # Set the rook to the left side of King
                                new_state.squares[new_file-1, new_rank].piece = new_state.squares[new_file+1, new_rank].piece
                                new_state.squares[new_file-1, new_rank].piece.move_to(new_file-1, new_rank)
                                new_state.squares[new_file-1, new_rank].piece.first_move = False
                                # remove the old rook
                                del new_state.squares[new_file+1, new_rank].piece
                                new_state.squares[new_file+1, new_rank].piece = None
                            else:
                                return 0
                        sel_piece.first_move = False
                        return new_state
                    # Double move
                    if status == 'D':
                        sel_piece.double = True
                        sel_piece.first_move = False
                        sel_piece.move_to(new_file, new_rank)
                        # set piece on new square
                        new_state.squares[new_file, new_rank].piece = sel_piece
                        # delete the piece on old square
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None

                        # CHeck for check
                        if self.check(sel_piece.colour, new_state):
                            return 0

                        # Change variables
                        new_state.enpassant = True
                        return new_state
                    # en passant
                    if status == 'E' and new_state.enpassant:
                        sel_piece.move_to(new_file, new_rank)
                        # Delete/set the piece on new position
                        del new_state.squares[new_file, new_rank].piece
                        new_state.squares[new_file, new_rank].piece = sel_piece
                        # Delete/set the piece on old position
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None

                        # if piece is white, pawns go up, if black then goes down
                        if sel_piece.colour == 'w':
                            del new_state.squares[new_file, new_rank+1].piece
                            new_state.squares[new_file, new_rank+1].piece = None
                        elif sel_piece.colour == 'b':
                            del new_state.squares[new_file, new_rank-1].piece
                            new_state.squares[new_file, new_rank-1].piece = None

                        # check for checks
                        if self.check(sel_piece.colour, new_state):
                            return 0

                        # Tell the board that the next move cannot be an en passant move
                        new_state.enpassant = False
                        # Set variable for rendering enpassant
                        new_state.enpass_capture = True
                        return new_state
                except IndexError:
                    if piece.piece == 'K':
                        sel_piece.first_move = False
                        sel_piece.check = False
                        sel_piece.move_to(new_file, new_rank)
                        # set new piece
                        del new_state.squares[new_file, new_rank].piece
                        new_state.squares[new_file, new_rank].piece = sel_piece
                        # delete old piece
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None

                        # Set the current position of the king
                        if sel_piece.colour == 'w':
                            new_state.wking = sel_piece
                        elif sel_piece.colour == 'b':
                            new_state.bking = sel_piece

                        # Check for check
                        if self.check(sel_piece.colour, new_state):
                            return 0

                        new_state.castle = False
                        return new_state
                    elif piece.piece == 'P':
                        #piece.double = False
                        pass
                sel_piece.move_to(new_file, new_rank)
                try:
                    sel_piece.first_move = False
                except AttributeError:
                    pass
                del new_state.squares[new_file, new_rank].piece
                new_state.squares[new_file, new_rank].piece = sel_piece
                del new_state.squares[file, rank].piece
                new_state.squares[file, rank].piece = None

                # Check for check
                if self.check(sel_piece.colour, new_state):
                    return 0
                return new_state
        print('Not a valid move')
        return 0

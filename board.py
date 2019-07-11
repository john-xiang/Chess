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
    def __init__(self, colour=None, position=None, coord=None, piece=None):
        self.colour = colour
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
        self.wking = None
        self.bking = None
        self.wpieces = []
        self.bpieces = []
        self.castle = False

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
                    squares[file, rank] = Square('w', (file, rank), (xfile, yrank))
                    switch = False
                elif not switch:
                    # draw square on display
                    pygame.draw.rect(self.display, black, [xfile, yrank, self.cellsize, self.cellsize])
                    # set property for current square
                    squares[file, rank] = Square('b', (file, rank), (xfile, yrank))
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
                    # add piece to all white pieces
                    if piece.colour == 'w':
                        self.state.wpieces.append(piece)
                    elif piece.colour == 'b':
                        self.state.bpieces.append(piece)
                    # add piece to all black pieces
                    placed += 1
        pygame.display.update()
        self.state.squares = squares
        self.state.last_move = Square()
        self.state.enpassant = False
        self.state.enpass_capture = False
        self.state.castle = False


    def check(self, colour, state):
        """Returns true if player in check, otherwise return false"""
        if colour == 'w':
            king = state.squares[state.wking.file, state.wking.rank].piece
        elif colour == 'b':
            king = state.squares[state.bking.file, state.bking.rank].piece
        if king is not None:
            kfile = king.file
            krank = king.rank
            ksq = state.squares[kfile, krank]
        try:
            atks = self.attack_by(ksq, state)
        except:
            atks = []
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
            except:
                if atksq.piece is not None and atksq.piece.colour != piece.colour:
                    atking.append((atkfile, atkrank))
        return atking


    def attack_by(self, square, state):
        """This function outputs all squares/pieces attacking the input square"""
        atkby = []
        sel_piece = square.piece
        for sqr in state.squares:
            current_piece = state.squares[sqr].piece
            if current_piece is not None:
                atks = current_piece.valid_moves(state)
                if square.position in atks:
                    #atkby.append(squares)
                    if sel_piece is not None and sel_piece.colour != current_piece.colour:
                        atkby.append(current_piece.piece)
                    else:
                        atkby.append(current_piece.piece)
        return atkby


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
                    if self.check(sel_piece.colour, new_state):
                        print('Move is not allowed! King is in check Promotion')
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
                        del new_state.squares[file, rank].piece
                        sel_piece.move_to(new_file, new_rank)
                        new_state.squares[new_file, new_rank].piece = sel_piece
                        new_state.squares[file, rank].piece = None

                        if sel_piece.colour == 'w':
                            new_state.wking = sel_piece
                        elif sel_piece.colour == 'b':
                            new_state.bking = sel_piece

                        if self.check(sel_piece.colour, new_state):
                            print('Move is not allowed! King is in check C')
                            return 0

                        # Castle Queen side
                        if new_file == 2:
                            # Set the rook to the right side of King
                            new_state.squares[new_file+1, new_rank].piece = new_state.squares[new_file-2, new_rank].piece
                            new_state.squares[new_file+1, new_rank].piece.move_to(new_file+1, new_rank)
                            new_state.squares[new_file+1, new_rank].piece.first_move = False
                            # remove the old rook
                            del new_state.squares[new_file-2, new_rank].piece
                            new_state.squares[new_file-2, new_rank].piece = None
                        # Castle King side
                        elif new_file == 6:
                            # Set the rook to the left side of King
                            new_state.squares[new_file-1, new_rank].piece = new_state.squares[new_file+1, new_rank].piece
                            new_state.squares[new_file-1, new_rank].piece.move_to(new_file-1, new_rank)
                            new_state.squares[new_file-1, new_rank].piece.first_move = False
                            # remove the old rook
                            del new_state.squares[new_file+1, new_rank].piece
                            new_state.squares[new_file+1, new_rank].piece = None

                        piece.first_move = False
                        return new_state
                    # Double move
                    if status == 'D':
                        sel_piece.double = True
                        sel_piece.first_move = False
                        sel_piece.move_to(new_file, new_rank)
                        # Delete and old position and set new one
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None
                        new_state.squares[new_file, new_rank].piece = sel_piece
                        # CHeck for check
                        if self.check(sel_piece.colour, new_state):
                            print('Move is not allowed! King is in check D')
                            return 0
                        # Change variables
                        new_state.enpassant = True
                        piece.double = True
                        piece.first_move = False
                        piece.move_to(new_file, new_rank)
                        return new_state
                    # en passant
                    if status == 'E' and new_state.enpassant:
                        sel_piece.move_to(new_file, new_rank)
                        # Delete/set the piece on old position
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None
                        # Delete/set the piece on new position
                        del new_state.squares[new_file, new_rank].piece
                        new_state.squares[new_file, new_rank].piece = sel_piece

                        # if piece is white, pawns go up, if black then goes down
                        if sel_piece.colour == 'w':
                            del new_state.squares[new_file, new_rank-1].piece
                            new_state.squares[new_file, new_rank-1].piece = None
                        elif sel_piece.colour == 'b':
                            del new_state.squares[new_file, new_rank+1].piece
                            new_state.squares[new_file, new_rank+1].piece = None

                        # check for checks
                        if self.check(sel_piece.colour, new_state):
                            print('Move is not allowed! King is in check E')
                            return 0

                        # Tell the board that the next move cannot be an en passant move
                        new_state.enpassant = False
                        # Set variable for rendering enpassant
                        new_state.enpass_capture = True
                        piece.move_to(new_file, new_rank)
                        return new_state
                except:
                    if piece.piece == 'K':
                        del new_state.squares[file, rank].piece
                        new_state.squares[file, rank].piece = None
                        del new_state.squares[new_file, new_rank].piece
                        sel_piece.first_move = False
                        sel_piece.check = False
                        sel_piece.move_to(new_file, new_rank)
                        new_state.squares[new_file, new_rank].piece = sel_piece

                        # Set the current position of the king
                        if sel_piece.colour == 'w':
                            new_state.wking = sel_piece
                        elif sel_piece.colour == 'b':
                            new_state.bking = sel_piece

                        if self.check(sel_piece.colour, new_state):
                            print('Move is not allowed! King is in check K')
                            return 0
                        new_state.castle = False
                        piece.first_move = False
                        piece.check = False
                        piece.move_to(new_file, new_rank)
                        return new_state
                    elif piece.piece == 'P':
                        #piece.double = False
                        pass
                del new_state.squares[file, rank].piece
                new_state.squares[file, rank].piece = None
                del new_state.squares[new_file, new_rank].piece
                sel_piece.move_to(new_file, new_rank)
                try:
                    sel_piece.first_move = False
                except:
                    pass
                new_state.squares[new_file, new_rank].piece = sel_piece

                if self.check(sel_piece.colour, new_state):
                    print('Move is not allowed! King is in check Other')
                    return 0
                piece.move_to(new_file, new_rank)
                try:
                    piece.first_move = False
                except:
                    pass
                return new_state
        print('Not a valid move')
        return 0

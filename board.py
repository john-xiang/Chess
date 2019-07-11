import pygame
from collections import defaultdict
import copy
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Square:
    """square class contains properties: colour, xy position, coordinates, piece on sq"""
    def __init__(self, colour=None, position=None, coord=None, piece=None):
        self.colour = colour
        self.position = position
        self.coord = coord
        # this is a Piece class
        self.piece = piece

    def setPiece(self, piece):
        """sets the piece"""
        self.piece = piece

    def getPiece(self):
        """returns the current piece on square"""
        return self.piece

# Class that represents the state of the board
class State:
    """State class defines the current state: contains all squares on the board and other variables"""
    def __init__(self, squares=None):
        self.squares = defaultdict()
        self.lastMove = Square()
        self.enpassant = False
        self.enpassCapture = False
        self.wKing = None
        self.bKing = None
        self.wPieces = []
        self.bPieces = []
        self.castle = False

# Class that represents the board. This class will be used to keep track of the state of the board. A state for this board will be defined to the set of all squares on the board.
#   In addition, each square contains information of any chess pieces on it.
class Board:
    """Board class initiates and renders board"""
    def __init__(self, display, cellsize):
        self.display = display
        self.cellsize = cellsize
        self.state = State()
        self.turnNum = 0


    def setBoard(self):
        boardSize = 8
        buffer = 25
        white = (238, 219, 179)
        black = (181, 135, 99)
        lines = [0, 1, 6, 7]
        placed = 0
        order = ['rookb', 'pawnb', 'pawnw', 'rookw', 'knightb', 'pawnb', 'pawnw', 'knightw', 'bishopb', 'pawnb', 'pawnw', 'bishopw', 'queenb', 'pawnb', 'pawnw', 'queenw',
            'kingb', 'pawnb', 'pawnw', 'kingw', 'bishopb', 'pawnb', 'pawnw', 'bishopw', 'knightb', 'pawnb', 'pawnw', 'knightw', 'rookb', 'pawnb', 'pawnw', 'rookw']
        # state is the set of all squares and position of all the pieces
        
        squares = defaultdict()
        switch = False
        # Draws the board and initializes starting positions of pieces
        for file in range(boardSize):
            switch = not switch
            for rank in range(boardSize):
                if switch:
                    # draw square
                    pygame.draw.rect(self.display, white,[self.cellsize*file+buffer, self.cellsize*rank+buffer, self.cellsize, self.cellsize])
                    # set property for the current square
                    squares[file, rank] = Square('w', (file, rank), (self.cellsize*file+buffer, self.cellsize*rank+buffer))
                    switch = False
                elif not switch:
                    # draw square on display
                    pygame.draw.rect(self.display, black, [self.cellsize*file+buffer, self.cellsize*rank+buffer, self.cellsize, self.cellsize])
                    # set property for current square
                    squares[file, rank] = Square('b', (file, rank), (self.cellsize*file+buffer, self.cellsize*rank+buffer))
                    switch = True
                if rank in lines:
                    currentPiece = order[placed]
                    # Initialize pieces
                    if 'rookb' in currentPiece:
                        piece = Rook(file, rank, 'b')
                    elif 'rookw' in currentPiece:
                        piece = Rook(file, rank, 'w')
                    elif 'pawnb' in currentPiece:
                        piece = Pawn(file, rank, 'b')
                    elif 'pawnw' in currentPiece:
                        piece = Pawn(file, rank, 'w')
                    elif 'knightb' in currentPiece:
                        piece = Knight(file, rank, 'b')
                    elif 'knightw' in currentPiece:
                        piece = Knight(file, rank, 'w')
                    elif 'bishopb' in currentPiece:
                        piece = Bishop(file, rank, 'b')
                    elif 'bishopw' in currentPiece:
                        piece = Bishop(file, rank, 'w')
                    elif 'queenb' in currentPiece:
                        piece = Queen(file, rank, 'b')
                    elif 'queenw' in currentPiece:
                        piece = Queen(file, rank, 'w')
                    elif 'kingb' in currentPiece:
                        piece = King(file, rank, 'b')
                        self.state.bKing = piece
                    elif 'kingw' in currentPiece:
                        piece = King(file, rank, 'w')
                        self.state.wKing = piece
                    image = pygame.image.load(piece.img)
                    # Draw piece onto the board
                    self.display.blit(image, squares[file,rank].coord)
                    # Set piece for the current square
                    squares[file, rank].piece = piece
                    # add piece to all white pieces
                    if piece.colour == 'w':
                        self.state.wPieces.append(piece)
                    elif piece.colour == 'b':
                        self.state.bPieces.append(piece)
                    # add piece to all black pieces
                    placed += 1
        pygame.display.update()
        self.state.squares = squares
        self.state.lastMove = Square()
        self.state.enpassant = False
        self.state.enpassCapture = False
        self.state.castle = False


    # returns true if there's a check in current state, otherwise false
    def isCheck(self, colour, state):
        if colour == 'w':
            king = state.squares[state.wKing.file, state.wKing.rank].piece
        elif colour == 'b':
            king = state.squares[state.bKing.file, state.bKing.rank].piece
        if king != None:
            f = king.file
            r = king.rank
            sq = state.squares[f, r]
        try:
            atks = self.attackBy(sq, state)
        except:
            atks = []
        if not atks:
            return False
        else:
            return True

    # If the piece is attacking the enemy's king, then a check is declared
    def check(self, piece, state):
        atking = self.attack(piece, state)
        for atks in atking:
            pce = state.squares[atks].piece
            # King is in check
            if pce.piece == 'K' and pce.colour != piece.colour:
                if pce.colour == 'w':
                    state.wKing.check = True
                    state.squares[state.wKing.file, state.wKing.rank].check = True
                elif pce.colour == 'b':
                    state.bKing.check = True
                    state.squares[state.bKing.file, state.bKing.rank].check = True
                return True
        return False

    # what the current piece is attacking
    def attack(self, piece, state):
        allMoves = piece.valid_moves(state)
        atkSq = []
        for move in allMoves:
            x = move[0]
            y = move[1]
            sq = state.squares[x,y]
            try:
                status = move[2]
                if status == 'E' and state.enpassant:
                    if piece.colour == 'w':
                        enpass = (x, y+1)
                    elif piece.colour == 'b':
                        enpass = (x, y-1)
                    atkSq.append((enpass))
            except:
                if sq.piece != None and sq.piece.colour != piece.colour:
                    atkSq.append((x,y))
        return atkSq

    # This function outputs all squares/pieces attacking the input square
    def attackBy(self, square, state):
        atkBySq = []
        sqPiece = square.piece
        for sq in state.squares:
            currentPiece = state.squares[sq].piece
            if currentPiece != None:
                atks = currentPiece.valid_moves(state)
                if square.position in atks:
                    #atkBySq.append(squares)
                    if sqPiece != None and sqPiece.colour != currentPiece.colour:
                        atkBySq.append(currentPiece.piece)
                    else:
                        atkBySq.append(currentPiece.piece)
        return atkBySq
    
    # This function handles castling moves (kingside/queenside)
    def castleMove(self, piece, new_file, new_rank, state):
        f = piece.file
        r = piece.rank
        col = piece.colour
        newState = state

        # Move the king
        #del newState[f, r].piece
        newState[f, r].piece = None
        newState[new_file, new_rank].piece = piece
        piece.first_move = False
        piece.move_to(new_file, new_rank)

        if col == 'w':
            self.wKing = piece
        elif piece.colour == 'b':
            self.bKing = piece

        if self.isCheck(piece.colour, newState):
            print('Move is not allowed! King is in check')
            piece.move_to(f, r)
            return 0

        # Castle Queen side
        if new_file == 2:
            # Set the rook to the right side of King
            newState[new_file+1, new_rank].piece = newState[new_file-2, new_rank].piece
            newState[new_file+1, new_rank].piece.move_to(new_file+1, new_rank)
            newState[new_file+1, new_rank].piece.first_move = False
            # remove the old rook
            #del newState[new_file-2, new_rank].piece
            newState[new_file-2, new_rank].piece = None      
        # Castle King side
        elif new_file == 6:
            # Set the rook to the left side of King
            newState[new_file-1, new_rank].piece = newState[new_file+1, new_rank].piece
            newState[new_file-1, new_rank].piece.move_to(new_file-1, new_rank)
            newState[new_file-1, new_rank].piece.first_move = False
            # remove the old rook
            #del newState[new_file+1, new_rank].piece
            newState[new_file+1, new_rank].piece = None
        return newState
    
    # This function handles a pawn's double move.
    # If a double move is made, then board will allow an enpassant capture
    def doubleMove(self, piece, new_file, new_rank, state):
        f = piece.file
        r = piece.rank
        newState = state
        # Change variables
        self.enpassant = True
        piece.double = True
        piece.first_move = False
        piece.move_to(new_file, new_rank)

        # Delete and old position and set new one
        #del newState[f, r].piece
        newState[f, r].piece = None
        newState[new_file, new_rank].piece = piece

        # CHeck for check
        if self.isCheck(piece.colour, newState):
            print('Move is not allowed! King is in check')
            self.enpassant = False
            piece.double = False
            piece.first_move = True
            piece.move_to(f, r)
            return 0
        return newState

    # This function handles enpassant moves
    def enpassantMove(self, piece, new_file, new_rank, state):
        f = piece.file
        r = piece.rank
        newState = state
        # Tell the board that the next move cannot be an en passant move
        self.enpassant = False
        # Set variable for rendering enpassant
        self.enpassCapture = True
        piece.move_to(new_file, new_rank)

        # Delete/set the piece on old position
        #del newState[f, r].piece
        newState[f, r].piece = None
        # Delete/set the piece on new position
        #del newState[new_file, new_rank].piece
        newState[new_file, new_rank].piece = piece
        
        # if piece is white, pawns go up, if black then goes down
        if piece.colour == 'w':
            #del newState[new_file, new_rank+1].piece
            newState[new_file, new_rank-1].piece = None
        elif piece.colour == 'b':
            #del newState[new_file, new_rank-1].piece
            newState[new_file, new_rank+1].piece = None

        # check for checks
        if self.isCheck(piece.colour, newState):
            print('Move is not allowed! King is in check')
            self.enpassant = True
            self.enpassCapture = False
            piece.move_to(f, r)
            return 0
        return newState

    def promotion(self, piece, new_file, new_rank, state):
        f = piece.file
        r = piece.rank
        col = piece.colour
        newState = state
        #del newState[new_file, new_rank].piece
        #del newState[f, r].piece
        newState[new_file, new_rank].piece = Queen(new_file, new_rank, col)
        newState[f, r].piece = None
        if self.isCheck(piece.colour, newState):
            print('Move is not allowed! King is in check')
            return 0
        return newState


    # If move is valid, retuns the new state. Otherwise return 0
    def move(self, piece, new_file, new_rank, state):
        file = piece.file
        rank = piece.rank
        newState = copy.deepcopy(state)
        selectedPiece = newState.squares[file, rank].piece
        moves = selectedPiece.valid_moves(newState)

        for move in moves:
            x = move[0]
            y = move[1]
            if (new_file, new_rank) == (x,y):
                ######################################################################################################
                # TODO : need to add check conditions here
                #   if king is in check, then must remove check or move is not allowed
                #   if move exposes check, then also not allowed
                #   if neither happens, or move does not result in check then follow through with rest of move logic
                ######################################################################################################
                
                # Promotion
                if selectedPiece.piece == 'P' and (new_rank == 0 or new_rank == 7):
                    newState.squares[new_file, new_rank].piece = Queen(new_file, new_rank, selectedPiece.colour)
                    del newState.squares[file, rank].piece
                    newState.squares[file, rank].piece = None
                    if self.isCheck(selectedPiece.colour, newState):
                        print('Move is not allowed! King is in check Promotion')
                        return 0
                    return newState
                # Check for special moves
                try:
                    status = move[2]
                    # Castle move
                    if status == 'C':
                        # Variable for rendering castle move
                        newState.castle = True
                        # Move the king
                        del newState.squares[file, rank].piece
                        selectedPiece.move_to(new_file, new_rank)
                        newState.squares[new_file, new_rank].piece = selectedPiece
                        newState.squares[file, rank].piece = None

                        if selectedPiece.colour == 'w':
                            newState.wKing = selectedPiece
                        elif selectedPiece.colour == 'b':
                            newState.bKing = selectedPiece

                        if self.isCheck(selectedPiece.colour, newState):
                            print('Move is not allowed! King is in check C')
                            return 0

                        # Castle Queen side
                        if new_file == 2:
                            # Set the rook to the right side of King
                            newState.squares[new_file+1, new_rank].piece = newState.squares[new_file-2, new_rank].piece
                            newState.squares[new_file+1, new_rank].piece.move_to(new_file+1, new_rank)
                            newState.squares[new_file+1, new_rank].piece.first_move = False
                            # remove the old rook
                            del newState.squares[new_file-2, new_rank].piece
                            newState.squares[new_file-2, new_rank].piece = None      
                        # Castle King side
                        elif new_file == 6:
                            # Set the rook to the left side of King
                            newState.squares[new_file-1, new_rank].piece = newState.squares[new_file+1, new_rank].piece
                            newState.squares[new_file-1, new_rank].piece.move_to(new_file-1, new_rank)
                            newState.squares[new_file-1, new_rank].piece.first_move = False
                            # remove the old rook
                            del newState.squares[new_file+1, new_rank].piece
                            newState.squares[new_file+1, new_rank].piece = None
                        
                        piece.first_move = False
                        return newState
                    # Double move
                    if status == 'D':
                        selectedPiece.double = True
                        selectedPiece.first_move = False
                        selectedPiece.move_to(new_file, new_rank)
                        # Delete and old position and set new one
                        del newState.squares[file, rank].piece
                        newState.squares[file, rank].piece = None
                        newState.squares[new_file, new_rank].piece = selectedPiece
                        # CHeck for check
                        if self.isCheck(selectedPiece.colour, newState):
                            print('Move is not allowed! King is in check D')
                            return 0
                        # Change variables
                        newState.enpassant = True
                        piece.double = True
                        piece.first_move = False
                        piece.move_to(new_file, new_rank)
                        return newState
                    # en passant
                    elif status == 'E' and newState.enpassant:
                        selectedPiece.move_to(new_file, new_rank)
                        # Delete/set the piece on old position
                        del newState.squares[file, rank].piece
                        newState.squares[file, rank].piece = None
                        # Delete/set the piece on new position
                        del newState.squares[new_file, new_rank].piece
                        newState.squares[new_file, new_rank].piece = selectedPiece
                        
                        # if piece is white, pawns go up, if black then goes down
                        if selectedPiece.colour == 'w':
                            del newState.squares[new_file, new_rank-1].piece
                            newState.squares[new_file, new_rank-1].piece = None
                        elif selectedPiece.colour == 'b':
                            del newState.squares[new_file, new_rank+1].piece
                            newState.squares[new_file, new_rank+1].piece = None

                        # check for checks
                        if self.isCheck(selectedPiece.colour, newState):
                            print('Move is not allowed! King is in check E')
                            return 0

                        # Tell the board that the next move cannot be an en passant move
                        newState.enpassant = False
                        # Set variable for rendering enpassant
                        newState.enpassCapture = True
                        piece.move_to(new_file, new_rank)
                        return newState
                except:
                    if piece.piece == 'K':
                        del newState.squares[file, rank].piece
                        newState.squares[file, rank].piece = None
                        del newState.squares[new_file, new_rank].piece
                        selectedPiece.first_move = False
                        selectedPiece.check = False
                        selectedPiece.move_to(new_file, new_rank)
                        newState.squares[new_file, new_rank].piece = selectedPiece

                        # Set the current position of the king
                        if selectedPiece.colour == 'w':
                            newState.wKing = selectedPiece
                        elif selectedPiece.colour == 'b':
                            newState.bKing = selectedPiece
                        
                        if self.isCheck(selectedPiece.colour, newState):
                            print('Move is not allowed! King is in check K')
                            return 0
                        newState.castle = False
                        piece.first_move = False
                        piece.check = False
                        piece.move_to(new_file, new_rank)
                        return newState
                    elif piece.piece == 'P':
                        #piece.double = False
                        pass
                del newState.squares[file, rank].piece
                newState.squares[file, rank].piece = None
                del newState.squares[new_file, new_rank].piece
                selectedPiece.move_to(new_file, new_rank)
                try:
                    selectedPiece.first_move = False
                except:
                    pass
                newState.squares[new_file, new_rank].piece = selectedPiece
                
                if self.isCheck(selectedPiece.colour, newState):
                    print('Move is not allowed! King is in check Other')
                    return 0
                piece.move_to(new_file, new_rank)
                try:
                    piece.first_move = False
                except:
                    pass
                return newState
        print('Not a valid move')
        return 0
import pygame
from abc import ABC, abstractmethod

# Base of the piece class

class Piece(ABC):
    
    def __init__(self, file, rank, colour, piece=None):        
        self.file = file
        self.rank = rank
        self.colour = colour
        self.piece = piece

    def moveTo(self, newFile, newRank):
        self.file = newFile
        self.rank = newRank

    @abstractmethod
    def validMoves(self, state):
        pass


# Pawn Class
class Pawn(Piece): 

    def __init__(self, file, rank, colour):
        super().__init__(file, rank, colour)
        self.piece = 'P'
        if colour == 'b':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/pawnb.png')
        elif colour == 'w':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/pawnw.png')
        self.firstMove = True
        self.double = False
    
    def validMoves(self, state):
        file = self.file
        rank = self.rank
        col = self.colour
        currentState = state
        fl = file - 1
        fr = file + 1
        moves = []

        # Promotion
        if rank == 0 or rank == 7:
            #print('You need a promotion!')
            return moves

        # Black
        if col == 'b':
            # Moves: first move can move two spaces up
            if self.firstMove:
                if currentState[file, rank+1].piece == None and currentState[file,rank+2].piece == None:
                    moves.append((file, rank+2, 'D'))
            # Pawn can normally only move one space up
            if currentState[file, rank+1].piece == None:
                moves.append((file, rank+1))
            # Captures
            if file-1 < 0:
                leftsq = None
                rightsq = currentState[file+1, rank+1].piece
            elif file+1 > 7:
                leftsq = currentState[file-1, rank+1].piece
                rightsq = None
            else:
                leftsq = currentState[file-1, rank+1].piece
                rightsq = currentState[file+1, rank+1].piece
            # Append Moves
            if leftsq != None and leftsq.colour != col:
                moves.append((file-1, rank+1))
            if rightsq != None and rightsq.colour != col:
                moves.append((file+1, rank+1))
            # En Passant
            if fl in range(0,8):
                left = currentState[fl, rank].piece
                if left != None and left.piece == 'P' and left.colour != col and left.double:
                    moves.append((file-1, rank+1, 'E'))
            if fr in range(0,8):
                right = currentState[fr, rank].piece
                if right != None and right.piece == 'P' and right.colour != col and right.double:
                    moves.append((file+1, rank+1, 'E'))
        elif col == 'w': # White
            # Moves: first move can move two spaces up
            if self.firstMove:
                if currentState[file, rank-1].piece == None and currentState[file,rank-2].piece == None:
                    moves.append((file, rank-2, 'D'))
            # Pawn can normally only move one space up
            if currentState[file,rank-1].piece==None :
                moves.append((file, rank-1))
            # Captures
            if file-1 < 0:
                leftsq = None
                rightsq = currentState[file+1, rank-1].piece
            elif file+1 > 7:
                leftsq = currentState[file-1, rank-1].piece
                rightsq = None
            else:
                leftsq = currentState[file-1, rank-1].piece
                rightsq = currentState[file+1, rank-1].piece
            # Append moves
            if leftsq != None and leftsq.colour != col:
                moves.append((file-1, rank-1))
            if rightsq != None and rightsq.colour != col:
                moves.append((file+1, rank-1))
            # En Passant
            if fl in range(0,8):
                left = currentState[fl, rank].piece
                if left != None and left.piece == 'P' and left.double and left.colour != col:
                    moves.append((file-1, rank-1, 'E'))
            if fr in range(0,8):
                right = currentState[fr, rank].piece
                if right != None and right.piece == 'P' and right.double and right.colour != col:
                    moves.append((file+1, rank-1, 'E'))
        return moves


# Rook Class
#   missing castling
class Rook(Piece):
    def __init__(self, file, rank, colour):
        super().__init__(file, rank, colour)
        self.piece = 'R'
        if colour == 'b':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/rookb.png')
        elif colour == 'w':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/rookw.png')
        self.firstMove = True
    
    # Missing Castling
    def validMoves(self, state):
        file = self.file
        rank = self.rank
        col = self.colour
        currentState = state
        moves = []

        # Keeps track of how many squares away we're looking at
        distance = 1
        # Counts which side we're checking
        sides = 0

        while sides < 4:
            # North
            if sides == 0:
                f = file
                r = rank - distance
                # check if out of bounds
                if r in range(0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # South
            if sides == 1:
                f = file
                r = rank + distance
                if r in range(0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # West
            if sides == 2:
                f = file - distance
                r = rank
                if f in range(0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # East
            if sides == 3:
                f = file + distance
                r = rank
                if f in range(0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
        return moves


# Knight Class
# completed
class Knight(Piece):
    def __init__(self, file, rank, colour):
        super().__init__(file, rank, colour)
        self.piece = 'N'
        if colour == 'b':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/knightb.png')
        elif colour == 'w':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/knightw.png')

    def validMoves(self, state):
        file = self.file
        rank = self.rank
        col = self.colour
        currentState = state
        jOrder = [-2, -1, 1, 2]
        iOrder = [1, 2, 2, 1]
        moves = []

        for index, j in enumerate(jOrder):
            f = file + j
            r1 = rank - iOrder[index]
            r2 = rank + iOrder[index]

            if f in range(0,8) and r1 in range(0,8):
                leftSq = currentState[f, r1]
                if leftSq.piece == None:
                    moves.append((f, r1))
                # capture
                elif leftSq.piece.colour != col:
                    moves.append((f, r1))
            if f in range(0,8) and r2 in range(0,8):
                rightSq = currentState[f, r2]
                if rightSq.piece == None:
                    moves.append((f, r2))
                # capture
                elif rightSq.piece.colour != col:
                    moves.append((f, r2))
        return moves


# Bishop Class
# completed
class Bishop(Piece):
    def __init__(self, file, rank, colour):
        super().__init__(file, rank, colour)
        self.piece = 'B'
        if colour == 'b':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/bishopb.png')
        elif colour == 'w':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/bishopw.png')
    
    def validMoves(self, state):
        file = self.file
        rank = self.rank
        col = self.colour
        currentState = state
        moves = []

        # Keeps track of how many squares away we're looking at
        distance = 1
        # Counts which side we're checking
        sides = 0

        while sides < 4:
            # NW
            if sides == 0:
                f = file - distance
                r = rank - distance
                # check if out of bounds
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[file-distance, rank-distance]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # SE
            if sides == 1:
                f = file + distance
                r = rank + distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[file+distance, rank+distance]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # SW
            if sides == 2:
                f = file - distance
                r = rank + distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[file-distance, rank+distance]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # NE
            if sides == 3:
                f = file + distance
                r = rank - distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[file+distance, rank-distance]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
        return moves


# Queen Class
#   Completed but might be more efficient way. Current while loop checks each side one square at a time
class Queen(Piece):
    def __init__(self, file, rank, colour):
        super().__init__(file, rank, colour)
        self.piece = 'Q'
        if colour == 'b':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/queenb.png')
        elif colour == 'w':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/queenw.png')

    def validMoves(self, state):
        file = self.file
        rank = self.rank
        col = self.colour
        currentState = state
        moves = []

        # Keeps track of how many squares away we're looking at
        distance = 1
        # Counts which side we're checking
        sides = 0

        while sides < 8:
            # North
            if sides == 0:
                f = file
                r = rank - distance
                # check if out of bounds
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # South
            if sides == 1:
                f = file
                r = rank + distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[file, rank+distance]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # West
            if sides == 2:
                f = file - distance
                r = rank
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # East
            if sides == 3:
                f = file + distance
                r = rank
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # NW
            if sides == 4:
                f = file - distance
                r = rank - distance
                # check if out of bounds
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # SE
            if sides == 5:
                f = file + distance
                r = rank + distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # SW
            if sides == 6:
                f = file - distance
                r = rank + distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
            # NE
            if sides == 7:
                f = file + distance
                r = rank - distance
                if f in range(0,8) and r in range (0,8):
                    selectedSq = currentState[f, r]
                else:
                    distance = 1
                    sides += 1
                    continue
                
                # if the square is empty, then append to possible moves
                if selectedSq.piece == None:
                    moves.append((f, r))
                    distance += 1
                    continue
                elif selectedSq.piece != None:        # if square contains a piece, check if ally
                    if col == selectedSq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((f, r))
                        distance = 1
                        sides += 1
                        continue
        return moves


# King Class
#   missing check stuff and castling
class King(Piece):
    def __init__(self, file, rank, colour):
        super().__init__(file, rank, colour)
        self.piece = 'K'
        if colour == 'b':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/kingb.png')
        elif colour == 'w':
            self.img = pygame.image.load('/home/johnx/Projects/Chess/png/kingw.png')
        self.check = False
        self.firstMove = True

    def validMoves(self, state):
        file = self.file
        rank = self.rank
        col = self.colour
        kFile = file + 3
        qFile = file - 4
        currentState = state
        jOrder = [-1, -1, -1, 0, 0, 1, 1, 1]
        iOrder = [0, 1, -1, 1, -1, 0, 1, -1]
        moves = []

        # Castling
        if self.firstMove:
            kingSide = currentState[kFile, rank].piece
            queenSide = currentState[qFile, rank].piece
            if kingSide != None and kingSide.piece == 'R' and kingSide.firstMove:
                clear = False
                f = kFile - 1
                # check if squares between king and ks rook are empty
                while f != file:
                    if currentState[f, rank].piece == None:
                        f -= 1
                        clear = True
                        continue
                    else:
                        f = file
                        clear = False
                        continue
                if clear: # can castle
                    moves.append((file+2, rank, 'C'))
            if queenSide != None and queenSide.piece == 'R' and queenSide.firstMove:
                clear = False
                f = qFile + 1
                # check if squares between king and qs rook are empty
                while f != file:
                    if currentState[f, rank].piece == None:
                        f += 1
                        clear = True
                        continue
                    else:
                        f = file
                        clear = False
                        continue
                if clear: # can castle
                    moves.append((file-2, rank, 'C'))

        # Moves
        for index, j in enumerate(jOrder):
            f = file + j
            r = rank + iOrder[index]

            if f in range(0, 8) and r in range(0,8):
                selectedSq = currentState[f, r]
                if selectedSq.piece == None:
                    moves.append((f,r))
                elif selectedSq.piece.colour != col:
                    moves.append((f,r))
        return moves
from collections import defaultdict
from pieces import *

# Class that represents the board. This class will be used to keep track of the state of the board. A state for this board will be defined to the set of all squares on the board.
#   In addition, each square contains information of any chess pieces on it.

class Board:
    # Class that defines all squares on the board
    class Square:
        # square contains properties: colour, xy position, coordinates, piece on sq
        def __init__(self, colour=None, position=None, coord=None, piece=None):
            self.colour = colour
            self.position = position
            self.coord = coord
            # this is a Piece class
            self.piece = piece

        def setPiece(self, piece):
            self.piece = piece
        

    def __init__(self, display, cellsize):
        self.display = display
        self.cellsize = cellsize
        self.state = defaultdict()
        self.turnNum = 0
        self.lastMove = self.Square()
        self.enpassant = False
        self.enpassCapture = False
        self.wKing = None
        self.bKing = None
        self.castle = False


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
        if not self.state:
            squares = defaultdict()
            switch = False
            # Draws the board and initializes starting positions of pieces
            for file in range(boardSize):
                switch = not switch
                for rank in range(boardSize):
                    if switch == True:
                        # draw square
                        pygame.draw.rect(self.display, white,[self.cellsize*file+buffer, self.cellsize*rank+buffer, self.cellsize, self.cellsize])
                        # set property for the current square
                        squares[file,rank] = self.Square('w', (file, rank), (self.cellsize*file+buffer, self.cellsize*rank+buffer))
                        switch = False
                    elif switch == False:
                        # draw square on display
                        pygame.draw.rect(self.display, black, [self.cellsize*file+buffer, self.cellsize*rank+buffer, self.cellsize, self.cellsize])
                        # set property for current square
                        squares[file,rank] = self.Square('b', (file, rank), (self.cellsize*file+buffer, self.cellsize*rank+buffer))
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
                            self.bKing = piece
                        elif 'kingw' in currentPiece:
                            piece = King(file, rank, 'w')
                            self.wKing = piece
                        # Draw piece onto the board
                        self.display.blit(piece.img, squares[file,rank].coord)
                        # Set piece for the current square
                        squares[file, rank].piece = piece
                        placed += 1
                pygame.display.update()
            self.state[self.turnNum] = squares

    def notation(self, position):
        fileNote = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        rankNote = ['8', '7', '6', '5', '4', '3', '2', '1']
        note = fileNote[position[0]] + rankNote[position[1]] + " "
        return note

    # returns true if there's a check in current state, otherwise false
    def isCheck(self, colour, state):
        if colour == 'w':
            king = self.wKing
        elif colour == 'b':
            king = self.bKing
        f = king.file
        r = king.rank
        atks = self.attackBy(state[f, r], state)
        if not atks:
            return False
        else:
            return True

    # If the piece is attacking the enemy's king, then a check is declared
    def check(self, piece, state):
        if piece.colour == 'w':
            king = self.bKing
        elif piece.colour == 'b':
            king = self.wKing
        atking = self.attack(piece, state)
        for squares in atking:
            pce = state[squares].piece
            if pce == king and pce.colour != piece.colour:
                print('Enemy King is in check!')
                return True
        return False

    # what the current piece is attacking
    def attack(self, piece, state):
        allMoves = piece.validMoves(state)
        atkSq = []
        for move in allMoves:
            # special check for enpassant if piece is a pawn
            if piece.piece == 'P':
                x = move[0]
                y = move[1]
                sq = state[x,y]
                try:     # check for enpassant
                    status = move[2]
                    if status == 'E' and self.enpassant:
                        if piece.colour == 'w':
                            enpass = (x, y+1)
                        elif piece.colour == 'b':
                            enpass = (x, y-1)
                        atkSq.append((enpass))
                except:
                    curPiece = sq.piece
                    if curPiece != None:
                        if curPiece.colour != piece.colour:
                            atkSq.append((x,y))
            else:   # piece is not a pawn
                x = move[0]
                y = move[1]
                sq = state[x,y]
                curPiece = sq.piece
                if curPiece != None:
                    if curPiece.colour != piece.colour:
                        atkSq.append((move))
        return atkSq

    # This function outputs all squares/pieces attacking the input square
    def attackBy(self, square, state):
        atkBySq = []
        sqPiece = square.piece
        for squares in state:
            currentPiece = state[squares].piece
            if currentPiece != None:
                atks = currentPiece.validMoves(state)
                if square.position in atks:
                    #atkBySq.append(squares)
                    if sqPiece != None and sqPiece.colour != currentPiece.colour:
                        atkBySq.append(currentPiece.piece)
                    else:
                        atkBySq.append(currentPiece.piece)
        return atkBySq

    def castleMove(self, piece, newFile, newRank, state):
        f = piece.file
        r = piece.rank
        col = piece.colour
        # Castle Queen side
        if newFile == 2:
            # Set the rook to the right side of King
            state[newFile+1, newRank].piece = Rook(newFile+1, newRank, col)
            state[newFile+1, newRank].piece.firstMove = False
            # remove the old rook
            del state[newFile-2, newRank].piece
            state[newFile-2, newRank].piece = None
            # Move the king
            del state[f, r].piece
            state[f, r].piece = None
            state[newFile, newRank].piece = piece
            piece.moveTo(newFile, newRank)
            piece.firstMove = False\
        # Castle King side
        elif newFile == 6:
            # Set the rook to the left side of King
            state[newFile-1, newRank].piece = Rook(newFile-1, newRank, col)
            state[newFile-1, newRank].piece.firstMove = False
            # remove the old rook
            del state[newFile+1, newRank].piece
            state[newFile+1, newRank].piece = None
            # Move the king
            del state[f, r].piece
            state[f, r].piece = None
            state[newFile, newRank].piece = piece
            piece.moveTo(newFile, newRank)
            piece.firstMove = False
        return state
            
    def doubleMove(self, piece, newFile, newRank, state):
        f = piece.file
        r = piece.rank

        self.enpassant = True
        piece.double = True
        piece.firstMove = False
        del state[f, r].piece
        state[f, r].piece = None
        state[newFile, newRank].piece = piece
        piece.moveTo(newFile, newRank)
        return state

    def enpassantMove(self, piece, newFile, newRank, state):
        f = piece.file
        r = piece.rank
        self.enpassant = False
        self.enpassCapture = True
        piece.firstMove = False
        del state[f, r].piece
        state[f, r].piece = None
        state[newFile, newRank].piece = piece
        piece.moveTo(newFile, newRank)
        if piece.colour == 'w':
            del newState[newFile, newRank+1].piece
            newState[newFile, newRank+1].piece = None
        elif piece.colour == 'b':
            del newState[newFile, newRank-1].piece
            newState[newFile, newRank-1].piece = None

    # If move is valid, retuns the new state. Otherwise return 0
    def move(self, piece, newFile, newRank, state):
        turnNum = self.turnNum
        file = piece.file
        rank = piece.rank
        col = piece.colour
        newState = state[turnNum]
        moves = piece.validMoves(newState)

        # check if enpassant avaiable
        if piece.piece == 'P':
            for move in moves:
                x = move[0]
                y = move[1]
                if (newFile, newRank) == (x,y):
                    if newRank == 0 or newRank == 7:
                        del (newState[newFile, newRank].piece)
                        newState[newFile, newRank].piece = Queen(newFile, newRank, col)
                        return newState
                    try:
                        status = move[2]
                        # Double move
                        if status == 'D':
                            newState = self.doubleMove(piece, newFile, newRank, newState)
                            return newState
                        # en passant
                        elif status == 'E' and self.enpassant:
                            self.enpassant = False
                            self.enpassCapture = True
                            piece.firstMove = False
                            del newState[file, rank].piece
                            newState[file, rank].piece = None
                            newState[newFile, newRank].piece = piece
                            piece.moveTo(newFile, newRank)
                            if piece.colour == 'w':
                                del newState[newFile, newRank+1].piece
                                newState[newFile, newRank+1].piece = None
                            elif piece.colour == 'b':
                                del newState[newFile, newRank-1].piece
                                newState[newFile, newRank-1].piece = None
                            return newState
                    except:
                        piece.double = False
                        pass
        # Update current placement of King
        if piece.piece == 'K':
            # Castle
            for move in moves:
                x = move[0]
                y = move[1]
                if (newFile, newRank) == (x,y):
                    if piece.colour == 'w':
                        self.wKing = piece
                    elif piece.colour == 'b':
                        self.bKing = piece
                    try:
                        status = move[2]
                        if status == 'C':
                            self.castle = True
                            newState = self.castleMove(piece, newFile, newRank, newState)
                            return newState
                    except:
                        pass
        # All other pieces
        if (newFile, newRank) in moves:
            try:
                if piece.firstMove:
                    piece.firstMove = False
            except:
                pass
            self.enpassant = False
            del newState[file, rank].piece
            newState[file, rank].piece = None
            newState[newFile, newRank].piece = piece
            piece.moveTo(newFile, newRank)
            return newState
        else:
            print('Not a valid move')
            return 0
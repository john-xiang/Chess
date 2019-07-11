"""
This file contains the piece class (abstract)

Since each piece has differnt movement rules, they each have their own class
"""
from abc import ABC, abstractmethod

class Piece(ABC):
    """
    An abstract class that reprsents pieces
    """
    def __init__(self, file, rank, colour, piece=None):
        """
        Init method that instantiates a piece ojbect
        atributes:
        file, rank, colour, piece
        """
        self.file = file
        self.rank = rank
        self.colour = colour
        self.piece = piece

    def move_to(self, new_file, new_rank):
        """Method that changes the file and rank of a piece object"""
        self.file = new_file
        self.rank = new_rank

    @abstractmethod
    def valid_moves(self, state):
        """Abstract method that returns all valid moves"""
        return


class Pawn(Piece):
    """Pawn Class"""
    def __init__(self, file, rank, colour):
        """
        init method initializes pawn object
        atributes:
        img
        first_move
        double
        """
        super().__init__(file, rank, colour)
        self.piece = 'P'
        if colour == 'b':
            self.img = '/home/johnx/Projects/chess/png/pawnb.png'
        elif colour == 'w':
            self.img = '/home/johnx/Projects/chess/png/pawnw.png'
        self.first_move = True
        self.double = False

    def valid_moves(self, state):
        """
        Returns all valid moves for the pawn piece
        """
        file = self.file
        rank = self.rank
        current_state = state.squares
        file_left = file - 1
        file_right = file + 1
        moves = []

        # Black
        if self.colour == 'b':
            # Moves
            # Pawn can normally only move one space up
            if current_state[file, rank+1].piece is None:
                moves.append((file, rank+1))
                # first move can move two spaces up
                if self.first_move and current_state[file, rank+2].piece is None:
                    moves.append((file, rank+2, 'D'))
            # Captures
            if file-1 < 0:
                leftsq = None
                rightsq = current_state[file+1, rank+1].piece
            elif file+1 > 7:
                leftsq = current_state[file-1, rank+1].piece
                rightsq = None
            else:
                leftsq = current_state[file-1, rank+1].piece
                rightsq = current_state[file+1, rank+1].piece
            # Append Moves
            if leftsq is not None and leftsq.colour != self.colour:
                moves.append((file-1, rank+1))
            if rightsq is not None and rightsq.colour != self.colour:
                moves.append((file+1, rank+1))
            # En Passant
            if file_left in range(0, 8):
                left = current_state[file_left, rank].piece
                if left is not None and left.piece == 'P' and left.colour != self.colour and left.double:
                    moves.append((file-1, rank+1, 'E'))
            if file_right in range(0, 8):
                right = current_state[file_right, rank].piece
                if right is not None and right.piece == 'P' and right.colour != self.colour and right.double:
                    moves.append((file+1, rank+1, 'E'))
        elif self.colour == 'w': # White
            # Moves
            # Pawn can normally only move one space up
            if current_state[file, rank-1].piece is None:
                moves.append((file, rank-1))
                # first move can move two spaces up
                if self.first_move and current_state[file, rank-2].piece is None:
                    moves.append((file, rank-2, 'D'))
            # Captures
            if file-1 < 0:
                leftsq = None
                rightsq = current_state[file+1, rank-1].piece
            elif file+1 > 7:
                leftsq = current_state[file-1, rank-1].piece
                rightsq = None
            else:
                leftsq = current_state[file-1, rank-1].piece
                rightsq = current_state[file+1, rank-1].piece
            # Append moves
            if leftsq is not None and leftsq.colour != self.colour:
                moves.append((file-1, rank-1))
            if rightsq is not None and rightsq.colour != self.colour:
                moves.append((file+1, rank-1))
            # En Passant
            if file_left in range(0, 8):
                left = current_state[file_left, rank].piece
                if left is not None and left.piece == 'P' and left.double and left.colour != self.colour:
                    moves.append((file-1, rank-1, 'E'))
            if file_right in range(0, 8):
                right = current_state[file_right, rank].piece
                if right is not None and right.piece == 'P' and right.double and right.colour != self.colour:
                    moves.append((file+1, rank-1, 'E'))
        return moves


class Rook(Piece):
    """Rook Class"""
    def __init__(self, file, rank, colour):
        """
        init method instantiates rook object
        atributes:
        img
        first_move
        """
        super().__init__(file, rank, colour)
        self.piece = 'R'
        if colour == 'b':
            self.img = '/home/johnx/Projects/chess/png/rookb.png'
        elif colour == 'w':
            self.img = '/home/johnx/Projects/chess/png/rookw.png'
        self.first_move = True

    def valid_moves(self, state):
        """
        Method returns all valid moves for the rook piece
        """
        file = self.file
        rank = self.rank
        current_state = state.squares
        moves = []

        # Keeps track of how many squares away we're looking at
        distance = 1
        # Counts which side we're checking
        sides = 0

        while sides < 4:
            # North
            if sides == 0:
                sel_file = file
                sel_rank = rank - distance
                # check if out of bounds
                if sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue
                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # South
            if sides == 1:
                sel_file = file
                sel_rank = rank + distance
                if sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue
                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                # if square contains a piece, check if ally
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # West
            if sides == 2:
                sel_file = file - distance
                sel_rank = rank
                if sel_file in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue
                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                # if square contains a piece, check if ally
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # East
            if sides == 3:
                sel_file = file + distance
                sel_rank = rank
                if sel_file in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue
                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
        return moves


class Knight(Piece):
    """Knight Class"""
    def __init__(self, file, rank, colour):
        """
        init method instantiates knight object
        atribute:
        img
        """
        super().__init__(file, rank, colour)
        self.piece = 'N'
        if colour == 'b':
            self.img = '/home/johnx/Projects/chess/png/knightb.png'
        elif colour == 'w':
            self.img = '/home/johnx/Projects/chess/png/knightw.png'

    def valid_moves(self, state):
        """
        Returns all valid moves for Knight piece
        """
        current_state = state.squares
        j_order = [-2, -1, 1, 2]
        i_order = [1, 2, 2, 1]
        moves = []

        for index, j in enumerate(j_order):
            sel_file = self.file + j
            rank_left = self.rank - i_order[index]
            rank_right = self.rank + i_order[index]

            if sel_file in range(0, 8) and rank_left in range(0, 8):
                leftsq = current_state[sel_file, rank_left]
                if leftsq.piece is None:
                    moves.append((sel_file, rank_left))
                # capture
                elif leftsq.piece.colour != self.colour:
                    moves.append((sel_file, rank_left))
            if sel_file in range(0, 8) and rank_right in range(0, 8):
                rightsq = current_state[sel_file, rank_right]
                if rightsq.piece is None:
                    moves.append((sel_file, rank_right))
                # capture
                elif rightsq.piece.colour != self.colour:
                    moves.append((sel_file, rank_right))
        return moves


class Bishop(Piece):
    """Bishop Class"""
    def __init__(self, file, rank, colour):
        """
        init method instantiates Bishop object
        atributes:
        img
        """
        super().__init__(file, rank, colour)
        self.piece = 'B'
        if colour == 'b':
            self.img = '/home/johnx/Projects/chess/png/bishopb.png'
        elif colour == 'w':
            self.img = '/home/johnx/Projects/chess/png/bishopw.png'

    def valid_moves(self, state):
        """Returns all valid moves for bishop piece"""
        current_state = state.squares
        moves = []
        # Keeps track of how many squares away we're looking at
        distance = 1
        # Counts which side we're checking
        sides = 0

        while sides < 4:
            # NW
            if sides == 0:
                sel_file = self.file - distance
                sel_rank = self.rank - distance
                # check if out of bounds
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # SE
            if sides == 1:
                sel_file = self.file + distance
                sel_rank = self.rank + distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       #if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # SW
            if sides == 2:
                sel_file = self.file - distance
                sel_rank = self.rank + distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # NE
            if sides == 3:
                sel_file = self.file + distance
                sel_rank = self.rank - distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                # if square contains a piece, check if ally
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
        return moves


class Queen(Piece):
    """Queen Class"""
    def __init__(self, file, rank, colour):
        """
        init method instantiates a Queen object
        atribute:
        img
        """
        super().__init__(file, rank, colour)
        self.piece = 'Q'
        if colour == 'b':
            self.img = '/home/johnx/Projects/chess/png/queenb.png'
        elif colour == 'w':
            self.img = '/home/johnx/Projects/chess/png/queenw.png'

    def valid_moves(self, state):
        """
        Return all valid moves for Queen piece
        note: might be more efficient way. Current while loop checks each side one square at a time
        """
        file = self.file
        rank = self.rank
        current_state = state.squares
        moves = []

        # Keeps track of how many squares away we're looking at
        distance = 1
        # Counts which side we're checking
        sides = 0

        while sides < 8:
            # North
            if sides == 0:
                sel_file = file
                sel_rank = rank - distance
                # check if out of bounds
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # South
            if sides == 1:
                sel_file = file
                sel_rank = rank + distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[file, rank+distance]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # West
            if sides == 2:
                sel_file = file - distance
                sel_rank = rank
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # East
            if sides == 3:
                sel_file = file + distance
                sel_rank = rank
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # NW
            if sides == 4:
                sel_file = file - distance
                sel_rank = rank - distance
                # check if out of bounds
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # SE
            if sides == 5:
                sel_file = file + distance
                sel_rank = rank + distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # SW
            if sides == 6:
                sel_file = file - distance
                sel_rank = rank + distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
            # NE
            if sides == 7:
                sel_file = file + distance
                sel_rank = rank - distance
                if sel_file in range(0, 8) and sel_rank in range(0, 8):
                    selectedsq = current_state[sel_file, sel_rank]
                else:
                    distance = 1
                    sides += 1
                    continue

                # if the square is empty, then append to possible moves
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                    distance += 1
                    continue
                elif selectedsq.piece is not None:       # if square contains a piece, check if ally
                    if self.colour == selectedsq.piece.colour:
                        distance = 1
                        sides += 1
                        continue
                    else: # Capture
                        moves.append((sel_file, sel_rank))
                        distance = 1
                        sides += 1
                        continue
        return moves


class King(Piece):
    """King Class"""
    def __init__(self, file, rank, colour):
        """
        init method instantiates King object
        atributes:
        img
        check
        first_move
        """
        super().__init__(file, rank, colour)
        self.piece = 'K'
        if colour == 'b':
            self.img = '/home/johnx/Projects/chess/png/kingb.png'
        elif colour == 'w':
            self.img = '/home/johnx/Projects/chess/png/kingw.png'
        self.check = False
        self.first_move = True

    def valid_moves(self, state):
        """
        returns all valid moves for King piece
        """
        k_file = self.file + 3
        q_file = self.file - 4
        current_state = state.squares
        # The move to consider is (jorder, iorder)
        j_order = [-1, -1, -1, 0, 0, 1, 1, 1]
        i_order = [0, 1, -1, 1, -1, 0, 1, -1]
        moves = []

        # Castling
        if self.first_move and not self.check:
            try:
                king_side = current_state[k_file, self.rank].piece
            except:
                king_side = None
            try:
                queen_side = current_state[q_file, self.rank].piece
            except:
                queen_side = None

            if king_side is not None and king_side.piece == 'R' and king_side.first_move:
                clear = False
                sel_file = k_file - 1
                # check if squares between king and ks rook are empty and not attacked
                while sel_file != self.file:
                    if current_state[sel_file, self.rank].piece is None:
                        sel_file -= 1
                        clear = True
                        continue
                    else:
                        sel_file = self.file
                        clear = False
                        continue
                if clear: # can castle
                    moves.append((self.file+2, self.rank, 'C'))
            if queen_side is not None and queen_side.piece == 'R' and queen_side.first_move:
                clear = False
                sel_file = q_file + 1
                # check if squares between king and qs rook are empty
                while sel_file != self.file:
                    if current_state[sel_file, self.rank].piece is None:
                        sel_file += 1
                        clear = True
                        continue
                    else:
                        sel_file = self.file
                        clear = False
                        continue
                if clear: # can castle
                    moves.append((self.file-2, self.rank, 'C'))

        # Moves
        for index, j in enumerate(j_order):
            sel_file = self.file + j
            sel_rank = self.rank + i_order[index]

            if sel_file in range(0, 8) and sel_rank in range(0, 8):
                selectedsq = current_state[sel_file, sel_rank]
                if selectedsq.piece is None:
                    moves.append((sel_file, sel_rank))
                elif selectedsq.piece.colour != self.colour:
                    moves.append((sel_file, sel_rank))
        return moves

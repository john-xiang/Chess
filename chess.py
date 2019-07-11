"""
The main file:
Handles starting the game
"""
import pygame
import pygame.freetype
#from collections import defaultdict
from board import Board
from player import Player

def notation(position):
    """
    rewrites board matrix to UCI notation
    """
    fnote = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    rnote = ['8', '7', '6', '5', '4', '3', '2', '1']
    note = fnote[position[0]] + rnote[position[1]] + " "
    return note

DEBUG = True

# initiate pygame
pygame.init()

# Board and display variables
BOARDSIZE = 8
CELLSIZE = 64
BUFFER = 25
DIMX = (BOARDSIZE*CELLSIZE)+(2*BUFFER)+ 150
DIMY = (BOARDSIZE*CELLSIZE)+(2*BUFFER)
FILE_NAME = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
RANK_NAME = ['1', '2', '3', '4', '5', '6', '7', '8']

# set colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
LIGHT_WOOD = (238, 219, 179)
DARK_WOOD = (181, 135, 99)

LIGHTSQ = LIGHT_WOOD
DARKSQ = DARK_WOOD

# load FONT
FONT = pygame.freetype.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 15)

# initiate game display
GAME_DISPLAY = pygame.display.set_mode((DIMX, DIMY))
pygame.display.set_caption('Chess')

# label the axis
FILES = (CELLSIZE/2) + 20
RANKS = (BUFFER + BOARDSIZE*CELLSIZE) - (CELLSIZE/2)
for order in range(0, BOARDSIZE):
    FONT.render_to(GAME_DISPLAY, (FILES, 545), FILE_NAME[order], WHITE)
    FONT.render_to(GAME_DISPLAY, (9, RANKS), RANK_NAME[order], WHITE)
    FILES += CELLSIZE
    RANKS -= CELLSIZE

# Initializes and draws chess board
BOARD = Board(GAME_DISPLAY, CELLSIZE)
BOARD.set_board()

# Initiate players and TURN variable
TURN = 0
PLAYER_1 = Player('w')
PLAYER_2 = Player('b')

# game loop
GAME_EXIT = False
STATES = []
CURRENT_STATE = BOARD.state
LAST_MOVE = BOARD.state.last_move
SEL_SQ = None
SEL_PIECE = None
PIECE_SEL = False

while not GAME_EXIT:
    # quits the game when exit is pressed
    for event in pygame.event.get():
        #####################################
        #print(event)
        #####################################

        # Exit game
        if event.type == pygame.QUIT:
            GAME_EXIT = True

        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Mouse out of bounds
            pos1 = event.pos[0]
            pos2 = event.pos[1]
            if pos1 < BUFFER or pos2 < BUFFER or pos1 > (BOARDSIZE*CELLSIZE+BUFFER) or pos2 > (BOARDSIZE*CELLSIZE+BUFFER):
                PIECE_SEL = False
                continue
            # Get the coordinates of where the mouse clicked
            x, y = int((pos1-BUFFER)/CELLSIZE), int((pos2-BUFFER)/CELLSIZE)

            if PIECE_SEL:
                if (x, y) != SEL_SQ.position:
                    # Check if the move is valid before doing it
                    newState = BOARD.move(SEL_PIECE, x, y, CURRENT_STATE)

                    if newState != 0:
                        PIECE_SEL = False
                        newSquare = newState.squares[x, y]
                        newPiece = newSquare.piece
                        if SEL_SQ.colour == 'b':
                            col = DARKSQ
                        elif SEL_SQ.colour == 'w':
                            col = LIGHTSQ
                        if newSquare.colour == 'b':
                            colr = DARKSQ
                        elif newSquare.colour == 'w':
                            colr = LIGHTSQ

                        # Draws the new state. Erases old square
                        pygame.draw.rect(GAME_DISPLAY, col, [CELLSIZE*SEL_SQ.position[0]+BUFFER, CELLSIZE*SEL_SQ.position[1]+BUFFER, CELLSIZE, CELLSIZE])
                        # Capture: Erase the piece on captured square
                        if newPiece is not None:
                            pygame.draw.rect(GAME_DISPLAY, colr, [CELLSIZE*newSquare.position[0]+BUFFER, CELLSIZE*newSquare.position[1]+BUFFER, CELLSIZE, CELLSIZE])
                        # En Passant
                        if newState.enpass_capture:
                            newState.enpass_capture = False
                            f = newPiece.file
                            if newPiece.colour == 'b':
                                r = newPiece.rank - 1
                            elif newPiece.colour == 'w':
                                r = newPiece.rank + 1
                            if SEL_SQ.colour == 'w':
                                clr = DARKSQ
                            elif SEL_SQ.colour == 'b':
                                clr = LIGHTSQ
                            pygame.draw.rect(GAME_DISPLAY, clr, [CELLSIZE*f+BUFFER, CELLSIZE*r+BUFFER, CELLSIZE, CELLSIZE])
                        # Castle
                        if newState.castle:
                            newState.castle = False
                            if x == 2:
                                rook = newState.squares[x+1, y].piece
                                image = pygame.image.load(rook.img)
                                GAME_DISPLAY.blit(image, ((CELLSIZE*(x+1))+BUFFER, CELLSIZE*y+BUFFER))
                                if newState.squares[x+1, y].colour == 'w':
                                    col = DARKSQ
                                elif newState.squares[x+1, y].colour == 'b':
                                    col = LIGHTSQ
                                pygame.draw.rect(GAME_DISPLAY, col, [(CELLSIZE*(newSquare.position[0]-2))+BUFFER, CELLSIZE*newSquare.position[1]+BUFFER, CELLSIZE, CELLSIZE])
                            elif x == 6:
                                rook = newState.squares[x-1, y].piece
                                image = pygame.image.load(rook.img)
                                GAME_DISPLAY.blit(image, ((CELLSIZE*(x-1))+BUFFER, CELLSIZE*y+BUFFER))
                                if newState.squares[x-1, y].colour == 'w':
                                    col = LIGHTSQ
                                elif newState.squares[x-1, y].colour == 'b':
                                    col = DARKSQ
                                pygame.draw.rect(GAME_DISPLAY, col, [(CELLSIZE*(newSquare.position[0]+1))+BUFFER, CELLSIZE*newSquare.position[1]+BUFFER, CELLSIZE, CELLSIZE])
                        # Draws the current piece onto new square
                        image = pygame.image.load(newPiece.img)
                        GAME_DISPLAY.blit(image, (CELLSIZE*x+BUFFER, CELLSIZE*y+BUFFER))

                        # Increment TURN counter
                        BOARD.turn_num += 1
                        # set the last move
                        pos = LAST_MOVE.position
                        # check if enemy king is in check
                        status = BOARD.checking(newPiece, newState)
                        if status:
                            if newPiece.colour == 'w':
                                newState.bking.check = True
                                newState.squares[newState.bking.file, newState.bking.rank].piece.check = True
                            elif newPiece.colour == 'b':
                                newState.wking.check = True
                                newState.squares[newState.wking.file, newState.wking.rank].piece.check = True
                        try: # Sets variable so en passant capture only availble for one turn
                            newState.squares[pos].piece.double = False
                            LAST_MOVE = newSquare
                            newState.last_move = newSquare
                        except:
                            LAST_MOVE = newSquare
                            newState.last_move = newSquare
                        # save new state
                        STATES.append(newState)
                        CURRENT_STATE = newState

                        # Update the turn counter
                        if TURN == 0:
                            TURN += 1
                        elif TURN == 1:
                            TURN -= 1
                        if DEBUG:
                            print(SEL_PIECE.piece, 'moved to', notation((x, y)))
                            if status:
                                print('Enemy King is in check')
                    else:
                        PIECE_SEL = False

                # if clicked on the same square then do nothing
                else:
                    PIECE_SEL = False
            else:       #click
                SEL_SQ = CURRENT_STATE.squares[x, y]
                SEL_PIECE = SEL_SQ.piece

                #if DEBUG:
                    #attackedBy = BOARD.attack_by(SEL_SQ, CURRENT_STATE)
                    #print('\nSquare', notation((x, y)), 'is under attack by:', attackedBy)

                # Do nothing if there's no piece on the square
                if SEL_PIECE is not None:
                    PIECE_SEL = True

                    # Check which Player's turn it is
                    if TURN == 0:
                        # Player 1's turn : White
                        if SEL_PIECE.colour != PLAYER_1.colour:
                            PIECE_SEL = False
                            continue
                    elif TURN == 1:
                        # Player 2's turn : Black
                        if SEL_PIECE.colour != PLAYER_2.colour:
                            PIECE_SEL = False
                            continue

                    # Check if under check
                    status = BOARD.check(SEL_PIECE.colour, CURRENT_STATE)

                    ###############################################################################
                    if DEBUG:
                        # print location of current kings
                        #print('White king is located on', notation((CURRENT_STATE.wking.file, CURRENT_STATE.wking.rank)))
                        #print('Black king is located on', notation((CURRENT_STATE.bking.file, CURRENT_STATE.bking.rank)))

                        # Under check
                        if status:
                            print('Your king is under check!')

                        #wp = []
                        #bp = []
                        #for pieces in BOARD.wPieces:
                        #    wp.append(pieces.piece)
                        #for pieces in BOARD.bPieces:
                        #    bp.append(pieces.piece)
                        #print('all WHITE pieces', wp)
                        #print('all black pieces', bp)

                        # show what the last move was
                        if LAST_MOVE.piece is not None:
                            print('The last move was', LAST_MOVE.piece.piece, 'on', notation(LAST_MOVE.position))

                        # Print Current piece on square
                        print('\nCurrent piece:', SEL_PIECE.piece)

                        # Print valid moves and all possible attacks
                        valid_moves = SEL_PIECE.valid_moves(CURRENT_STATE)
                        atttackingSq = BOARD.attack(SEL_PIECE, CURRENT_STATE)
                        sentence = ''
                        sentence2 = ''
                        for move in valid_moves:
                            sentence += notation(move)
                        print('Valid moves:', sentence)
                        for move in atttackingSq:
                            sentence2 += notation(move)
                        print('attacking:', sentence2)
                    ################################################################################

        # # Mouse unclicked
        # elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        #     # Mouse out of bounds
        #     pos1 = event.pos[0]
        #     pos2 = event.pos[1]
        #     if pos1 < BUFFER or pos2 < BUFFER or pos1 > (BOARDSIZE*CELLSIZE+BUFFER) or pos2 > (BOARDSIZE*CELLSIZE+BUFFER):
        #         PIECE_SEL = False
        #         continue

    pygame.display.update()
# closes pygame
pygame.quit()
quit()

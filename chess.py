"""
The main file:
Handles starting the game
"""
import pygame
import pygame.freetype
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


def text_objects(text, font):
    """
    Function returns the text to render and the rectangle it covers
    """
    textsurface = font.render(text, True, BLACK)
    return textsurface, textsurface.get_rect()


def quit_game():
    """Quits the game"""
    pygame.quit()
    quit()


def button(xposition, yposition, buttonx, buttony, action=None):
    """
    Function that deals with rendering hovering buttons
    """
    #undo = text_objects('Undo', buttonfont)
    #quit_ = text_objects('Quit', buttonfont)

    if (buttonx+175) > xposition > buttonx and (buttony+60) > yposition > buttony:
        pygame.draw.rect(GAME_DISPLAY, PEACH, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(RESET[0], RESET[1])
        if action:
            action()
    #elif (buttonx+175) > xposition > buttonx and (buttony+145) > yposition > (buttony+85):
    #    pygame.draw.rect(GAME_DISPLAY, BRIGHT_DRK_WOOD, [buttonx, buttony+85, 175, 60])
    #elif (buttonx+175) > xposition > buttonx and (buttony+230) > yposition > (buttony+170):
    #    pygame.draw.rect(GAME_DISPLAY, BRIGHT_DRK_WOOD, [buttonx, buttony+170, 175, 60])
    else:
        pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(RESET[0], RESET[1])
    #    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony+85, 175, 60])
    #    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony+170, 175, 60])


def lit_square(xposition, yposition, state, all=None):
    """Function that highlights square when hovering over it"""
    for squares in state:
        sqr = state[squares]
        pce = state[squares].piece
        (x_sq, y_sq) = sqr.coord
        if (x_sq+CELLSIZE) > xposition > x_sq and (y_sq+CELLSIZE) > yposition > y_sq:
            if all:
                pygame.draw.rect(GAME_DISPLAY, GREEN, [x_sq, y_sq, CELLSIZE, CELLSIZE])
                if pce is not None:
                    image = pygame.image.load(pce.img)
                    GAME_DISPLAY.blit(image, (x_sq, y_sq))
            elif pce is not None:
                pygame.draw.rect(GAME_DISPLAY, GREEN, [x_sq, y_sq, CELLSIZE, CELLSIZE])
                image = pygame.image.load(pce.img)
                GAME_DISPLAY.blit(image, (x_sq, y_sq))
        else:
            pygame.draw.rect(GAME_DISPLAY, sqr.sqrcolour, [x_sq, y_sq, CELLSIZE, CELLSIZE])
            if pce is not None:
                image = pygame.image.load(pce.img)
                GAME_DISPLAY.blit(image, (x_sq, y_sq))


def lit_check(piece, state):
    """Hilights king when in check"""
    file = piece.file
    rank = piece.rank
    sqr = state.squares[file, rank]
    (x_sq, y_sq) = sqr.coord

    pygame.draw.rect(GAME_DISPLAY, RED, [x_sq, y_sq, CELLSIZE, CELLSIZE])
    image = pygame.image.load(piece.img)
    GAME_DISPLAY.blit(image, (x_sq, y_sq))


def render_move(file, rank, current_square, new_state):
    """function that makes moves and renders moves"""
    xold = CELLSIZE*current_square.position[0]+BUFFER
    yold = CELLSIZE*current_square.position[1]+BUFFER
    xnew = CELLSIZE*new_state.squares[file, rank].position[0]+BUFFER
    ynew = CELLSIZE*new_state.squares[file, rank].position[1]+BUFFER
    if current_square.colour == 'b':
        col = DARKSQ
        clr = LIGHTSQ
    elif current_square.colour == 'w':
        col = LIGHTSQ
        clr = DARKSQ
    if new_state.squares[file, rank].colour == 'b':
        colr = DARKSQ
    elif new_state.squares[file, rank].colour == 'w':
        colr = LIGHTSQ

    # Erases old square
    pygame.draw.rect(GAME_DISPLAY, col, [xold, yold, CELLSIZE, CELLSIZE])
    # Capture: Erase the piece on captured square
    if new_state.squares[file, rank].piece is not None:
        pygame.draw.rect(GAME_DISPLAY, colr, [xnew, ynew, CELLSIZE, CELLSIZE])
    # En Passant (Maybe need new function)
    if new_state.enpass_capture:
        new_state.enpass_capture = False
        if new_state.squares[file, rank].piece.colour == 'b':
            ypos = (CELLSIZE*(new_state.squares[file, rank].piece.rank-1))+BUFFER
        elif new_state.squares[file, rank].piece.colour == 'w':
            ypos = (CELLSIZE*(new_state.squares[file, rank].piece.rank+1))+BUFFER
        xpos = (CELLSIZE*new_state.squares[file, rank].piece.file)+BUFFER
        pygame.draw.rect(GAME_DISPLAY, clr, [xpos, ypos, CELLSIZE, CELLSIZE])
    # Castle (need to make new function for this)
    if new_state.castle:
        new_state.castle = False
        if file == 2:
            rook = new_state.squares[file+1, rank].piece
            image = pygame.image.load(rook.img)
            xpos = (CELLSIZE*(new_state.squares[file, rank].position[0]-2))+BUFFER
            ypos = (CELLSIZE*new_state.squares[file, rank].position[1])+BUFFER
            if new_state.squares[file+1, rank].colour == 'w':
                clr = DARKSQ
            elif new_state.squares[file+1, rank].colour == 'b':
                clr = LIGHTSQ
            GAME_DISPLAY.blit(image, ((CELLSIZE*(file+1))+BUFFER, CELLSIZE*rank+BUFFER))
            pygame.draw.rect(GAME_DISPLAY, clr, [xpos, ypos, CELLSIZE, CELLSIZE])
        elif file == 6:
            rook = new_state.squares[file-1, rank].piece
            image = pygame.image.load(rook.img)
            xpos = (CELLSIZE*(new_state.squares[file, rank].position[0]+1))+BUFFER
            ypos = CELLSIZE*new_state.squares[file, rank].position[1]+BUFFER
            if new_state.squares[file-1, rank].colour == 'w':
                clr = LIGHTSQ
            elif new_state.squares[file-1, rank].colour == 'b':
                clr = DARKSQ
            GAME_DISPLAY.blit(image, ((CELLSIZE*(file-1))+BUFFER, CELLSIZE*rank+BUFFER))
            pygame.draw.rect(GAME_DISPLAY, clr, [xpos, ypos, CELLSIZE, CELLSIZE])
    # Draws the current piece onto new square
    image = pygame.image.load(new_state.squares[file, rank].piece.img)
    GAME_DISPLAY.blit(image, (CELLSIZE*file+BUFFER, CELLSIZE*rank+BUFFER))


def gameloop():
    """Main game function"""
    # label the axis
    axis_file = (CELLSIZE/2) + 20
    axis_rank = (BUFFER + BOARDSIZE*CELLSIZE) - (CELLSIZE/2)
    for order in range(0, BOARDSIZE):
        FONT.render_to(GAME_DISPLAY, (axis_file, 545), FILE_NAME[order], WHITE)
        FONT.render_to(GAME_DISPLAY, (9, axis_rank), RANK_NAME[order], WHITE)
        axis_file += CELLSIZE
        axis_rank -= CELLSIZE

    # Render buttons
    buttonx = (BOARDSIZE*CELLSIZE)+(2*BUFFER)
    buttony = (CELLSIZE*2) + BUFFER + 13
    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
    RESET[1].center = ((buttonx+(175/2)), (buttony+(60/2)))
    GAME_DISPLAY.blit(RESET[0], RESET[1])
    #pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, (buttony + 85), 175, 60])
    #pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, (buttony + 170), 175, 60])

    # Initializes and draws chess board
    board = Board(GAME_DISPLAY, CELLSIZE)
    board.set_board()

    # game loop
    game_exit = False
    states = []
    # current state, current square and current piece
    curr_state = board.state
    curr_sq = None
    curr_piece = None
    # last move made on the board legal moves
    lastmove = board.state.last_move
    # check mate variables
    checkmate = False
    checked_for_checkmate = False
    checkmate_king = None
    # piece clicked and turn variables
    piece_clicked = False
    turn = 0

    while not game_exit:
        # determines if player is in check mate
        if not checkmate and not checked_for_checkmate:
            checked_for_checkmate = True
            if curr_state.wking.check:
                if curr_state.checkmate('w'):
                    print('White King is mated: BLACK WINS')
                    checkmate = True
                    checkmate_king = curr_state.wking
            elif curr_state.bking.check:
                if curr_state.checkmate('b'):
                    print('Black King is mated: WHITE WINS')
                    checkmate = True
                    checkmate_king = curr_state.bking

        # quits the game when exit is pressed
        for event in pygame.event.get():
            # Exit game
            if event.type == pygame.QUIT:
                print('Thanks for playing!')
                game_exit = True

            if not checkmate:
                # mouse position
                (x_pos, y_pos) = pygame.mouse.get_pos()

                # Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Reset Game Board
                    button(x_pos, y_pos, buttonx, buttony, gameloop)
                    # Mouse out of bounds
                    minimum = BUFFER
                    maximum = (BOARDSIZE*CELLSIZE) + BUFFER
                    if x_pos < minimum or y_pos < minimum or x_pos >= maximum or y_pos >= maximum:
                        piece_clicked = False
                        continue
                    # Get the coordinates of where the mouse clicked
                    (file, rank) = int((x_pos-BUFFER)/CELLSIZE), int((y_pos-BUFFER)/CELLSIZE)

                    if piece_clicked:
                        piece_clicked = False
                        if (file, rank) != curr_sq.position:
                            # Generate set of legal moves
                            legalmoves = curr_state.legal_moves(curr_piece.colour)

                            if (file, rank) in legalmoves[curr_sq.position]:
                                checked_for_checkmate = False
                                new_state = board.move(curr_piece, file, rank, curr_state) 
                                new_sq = new_state.squares[file, rank]
                                new_piece = new_sq.piece
                                render_move(file, rank, curr_sq, new_state)

                                # Increment turn counter
                                board.turn_num += 1
                                # set the last move
                                pos = lastmove.position
                                # check if enemy king is in check
                                status = new_state.checking(new_piece)
                                if status and new_piece.colour == 'w':
                                    new_state.bking.check = True
                                elif status and new_piece.colour == 'b':
                                    new_state.wking.check = True
                                else:
                                    if new_piece.colour == 'w':
                                        new_state.bking.check = False
                                    elif new_piece.colour == 'b':
                                        new_state.wking.check = False
                                try: # Sets variable so en passant capture only availble for one turn
                                    new_state.squares[pos].piece.double = False
                                    lastmove = new_sq
                                    new_state.last_move = new_sq
                                except (AttributeError, KeyError):
                                    lastmove = new_sq
                                    new_state.last_move = new_sq
                                # save new state
                                states.append(new_state)
                                curr_state = new_state

                                # Update the turn counter
                                if turn == 0:
                                    turn += 1
                                elif turn == 1:
                                    turn -= 1
                                if DEBUG:
                                    print(curr_piece.piece, 'moved to', notation((file, rank)))
                                    if status:
                                        print('Enemy King is in check')
                        else:
                            piece_clicked = True
                    else:       #click
                        curr_sq = curr_state.squares[file, rank]
                        curr_piece = curr_sq.piece

                        if DEBUG:
                            if turn == 0:
                                atkedby = curr_state.attack_by('w', curr_sq)
                            elif turn == 1:
                                atkedby = curr_state.attack_by('b', curr_sq)
                            print('\nSquare', notation((file, rank)), 'is under attack by:', atkedby)

                        # Do nothing if there's no piece on the square
                        if curr_piece is not None:
                            piece_clicked = True

                            # Check which Player's turn it is
                            if turn == 0:
                                # Player 1's turn : White
                                if curr_piece.colour != PLAYER_1.colour:
                                    piece_clicked = False
                                    continue
                            elif turn == 1:
                                # Player 2's turn : Black
                                if curr_piece.colour != PLAYER_2.colour:
                                    piece_clicked = False
                                    continue
                            ########################################################################
                            if DEBUG:
                                # print location of current kings
                                #wkingfile = curr_state.wking.file
                                #wkingrank = curr_state.wking.rank
                                #bkingfile = curr_state.bking.file
                                #bkingrank = curr_state.bking.rank
                                #print('White king is located on', notation((wkingfile, wkingrank)))
                                #print('Black king is located on', notation((bkingfile, bkingrank)))

                                # Check if under check
                                status = curr_state.check(curr_piece.colour)
                                # Under check
                                if status:
                                    print('Your king is under check!')

                                # show what the last move was
                                if lastmove.piece is not None:
                                    print('The last move was', lastmove.piece.piece, 'on', notation(lastmove.position))

                                # Print Current piece on square
                                print('Current piece:', curr_piece.piece)

                                # Print valid moves and all possible attacks
                                valid_moves = curr_piece.valid_moves(curr_state)
                                atkingsq = curr_state.attack(curr_piece)
                                sentence = ''
                                sentence2 = ''
                                for move in valid_moves:
                                    sentence += notation(move)
                                print('Valid moves:', sentence)
                                for move in atkingsq:
                                    sentence2 += notation(move)
                                print('attacking:', sentence2)
                            ########################################################################

                if piece_clicked:
                    lit_square(x_pos, y_pos, curr_state.squares, True)
                else:
                    lit_square(x_pos, y_pos, curr_state.squares)
            else:
                # mouse position
                (x_pos, y_pos) = pygame.mouse.get_pos()

                # Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Reset Game Board
                    button(x_pos, y_pos, buttonx, buttony, gameloop)
                lit_check(checkmate_king, curr_state)
            button(x_pos, y_pos, buttonx, buttony)
        pygame.display.update()
    # closes pygame
    pygame.quit()
    quit()

# initiate pygame
pygame.init()

# DEBUG VARIABLE
DEBUG = False

# load FONT
FONT = pygame.freetype.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 15)
BUTTONFONT = pygame.font.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 20)

# set colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 99, 71)
GRAY = (192, 192, 192)
MARRON = (175, 100, 80)
GREEN = (46, 139, 87)
#GREEN = (60, 179, 113)
PEACH = (205, 175, 149)
GOLD = (255, 215, 0)
LIGHT_WOOD = (238, 219, 179)
DARK_WOOD = (181, 135, 99)

# Square colours
LIGHTSQ = LIGHT_WOOD
DARKSQ = DARK_WOOD

# Board and display variables
BOARDSIZE = 8
CELLSIZE = 64
BUFFER = 25
DIMX = (BOARDSIZE*CELLSIZE)+(2*BUFFER) + 200
DIMY = (BOARDSIZE*CELLSIZE)+(2*BUFFER)
FILE_NAME = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
RANK_NAME = ['1', '2', '3', '4', '5', '6', '7', '8']

# Button variables
RESET = text_objects('New Game', BUTTONFONT)

# Initiate players and turn variable
TURN = 0
PLAYER_1 = Player('w')
PLAYER_2 = Player('b')

# initiate game display
GAME_DISPLAY = pygame.display.set_mode((DIMX, DIMY))
pygame.display.set_caption('Chess')

# Start game loop
gameloop()




# Mouse unclicked code
# elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
#     # Mouse out of bounds
#     minimum = BUFFER
#     maximum = (BOARDSIZE*CELLSIZE) + BUFFER
#     if x_pos < minimum or y_pos < minimum or x_pos >= maximum or y_pos >= maximum:
#         piece_clicked = False
#         continue
#     # Get the coordinates of where the mouse clicked
#     (file, rank) = int((x_pos-BUFFER)/CELLSIZE), int((y_pos-BUFFER)/CELLSIZE)

#     if piece_clicked:
#         if (file, rank) != curr_sq.position:
#             piece_clicked = False
#             # Check if the move is valid before doing it
#             new_state = board.move(curr_piece, file, rank, curr_state)

#             if new_state != 0:
#                 piece_clicked = False
#                 new_sq = new_state.squares[file, rank]
#                 new_piece = new_sq.piece
#                 render_move(file, rank, curr_sq, new_state)

#                 # Increment turn counter
#                 board.turn_num += 1
#                 # set the last move
#                 pos = lastmove.position
#                 # check if enemy king is in check
#                 status = new_state.checking(new_piece)
#                 if status and new_piece.colour == 'w':
#                     new_state.bking.check = True
#                 elif status and new_piece.colour == 'b':
#                     new_state.wking.check = True
#                 else:
#                     if new_piece.colour == 'w':
#                         new_state.bking.check = False
#                     elif new_piece.colour == 'b':
#                         new_state.wking.check = False
#                 try: # Sets variable so en passant capture only availble for one turn
#                     new_state.squares[pos].piece.double = False
#                     lastmove = new_sq
#                     new_state.last_move = new_sq
#                 except:
#                     lastmove = new_sq
#                     new_state.last_move = new_sq
#                 # save new state
#                 states.append(new_state)
#                 curr_state = new_state

#                 # Update the turn counter
#                 if turn == 0:
#                     turn += 1
#                 elif turn == 1:
#                     turn -= 1
#                 if DEBUG:
#                     print(curr_piece.piece, 'moved to', notation((file, rank)))
#                     if status:
#                         print('Enemy King is in check')
#         else:
#             piece_clicked = True

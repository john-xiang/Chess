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

def reset_button(xposition, yposition, buttonx, buttony, clicked=False):
    """
    Function that deals with rendering hovering buttons
    """
    buttonfont = pygame.font.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 20)
    newgame = text_objects('New Game', buttonfont)
    #undo = text_objects('Undo', buttonfont)
    #quit_ = text_objects('Quit', buttonfont)

    if (buttonx+175) > xposition > buttonx and (buttony+60) > yposition > buttony:
        pygame.draw.rect(GAME_DISPLAY, BRIGHT_DRK_WOOD, [buttonx, buttony, 175, 60])
        if clicked:
            print('pressed new game button')
            gameloop()
    #elif (buttonx+175) > xposition > buttonx and (buttony+145) > yposition > (buttony+85):
    #    pygame.draw.rect(GAME_DISPLAY, BRIGHT_DRK_WOOD, [buttonx, buttony+85, 175, 60])
    #elif (buttonx+175) > xposition > buttonx and (buttony+230) > yposition > (buttony+170):
    #    pygame.draw.rect(GAME_DISPLAY, BRIGHT_DRK_WOOD, [buttonx, buttony+170, 175, 60])
    else:
        pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
    #    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony+85, 175, 60])
    #    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony+170, 175, 60])
    newgame[1].center = ((buttonx+(175/2)), (buttony+(60/2)))
    GAME_DISPLAY.blit(newgame[0], newgame[1])

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
    #pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, (buttony + 85), 175, 60])
    #pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, (buttony + 170), 175, 60])

    # Initializes and draws chess board
    board = Board(GAME_DISPLAY, CELLSIZE)
    board.set_board()

    # game loop
    game_exist = False
    states = []
    current_state = board.state
    lastmove = board.state.last_move
    curr_sq = None
    curr_piece = None
    piece_selected = False
    turn = 0

    while not game_exist:
        # quits the game when exit is pressed
        for event in pygame.event.get():
            #####################################
            #print(event)
            #####################################
            # mouse position
            (x_pos, y_pos) = pygame.mouse.get_pos()

            # Exit game
            if event.type == pygame.QUIT:
                game_exist = True

            # Mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Reset Game Board
                reset_button(x_pos, y_pos, buttonx, buttony, True)
                # Mouse out of bounds
                minimum = BUFFER
                maximum = (BOARDSIZE*CELLSIZE) + BUFFER
                if x_pos < minimum or y_pos < minimum or x_pos >= maximum or y_pos >= maximum:
                    piece_selected = False
                    continue
                # Get the coordinates of where the mouse clicked
                x, y = int((x_pos-BUFFER)/CELLSIZE), int((y_pos-BUFFER)/CELLSIZE)

                if piece_selected:
                    if (x, y) != curr_sq.position:
                        # Check if the move is valid before doing it
                        new_state = board.move(curr_piece, x, y, current_state)

                        if new_state != 0:
                            piece_selected = False
                            new_sq = new_state.squares[x, y]
                            new_piece = new_sq.piece
                            xold = CELLSIZE*curr_sq.position[0]+BUFFER
                            yold = CELLSIZE*curr_sq.position[1]+BUFFER
                            xnew = CELLSIZE*new_sq.position[0]+BUFFER
                            ynew = CELLSIZE*new_sq.position[1]+BUFFER
                            if curr_sq.colour == 'b':
                                col = DARKSQ
                            elif curr_sq.colour == 'w':
                                col = LIGHTSQ
                            if new_sq.colour == 'b':
                                colr = DARKSQ
                            elif new_sq.colour == 'w':
                                colr = LIGHTSQ

                            # Erases old square
                            pygame.draw.rect(GAME_DISPLAY, col, [xold, yold, CELLSIZE, CELLSIZE])
                            # Capture: Erase the piece on captured square
                            if new_piece is not None:
                                pygame.draw.rect(GAME_DISPLAY, colr, [xnew, ynew, CELLSIZE, CELLSIZE])
                            # En Passant
                            if new_state.enpass_capture:
                                new_state.enpass_capture = False
                                if new_piece.colour == 'b':
                                    r = new_piece.rank - 1
                                elif new_piece.colour == 'w':
                                    r = new_piece.rank + 1
                                if curr_sq.colour == 'w':
                                    clr = DARKSQ
                                elif curr_sq.colour == 'b':
                                    clr = LIGHTSQ
                                xpos = (CELLSIZE*new_piece.file)+BUFFER
                                ypos = CELLSIZE*r+BUFFER
                                pygame.draw.rect(GAME_DISPLAY, clr, [xpos, ypos, CELLSIZE, CELLSIZE])
                            # Castle
                            if new_state.castle:
                                new_state.castle = False
                                if x == 2:
                                    rook = new_state.squares[x+1, y].piece
                                    image = pygame.image.load(rook.img)
                                    xpos = (CELLSIZE*(new_sq.position[0]-2))+BUFFER
                                    ypos = (CELLSIZE*new_sq.position[1])+BUFFER
                                    if new_state.squares[x+1, y].colour == 'w':
                                        col = DARKSQ
                                    elif new_state.squares[x+1, y].colour == 'b':
                                        col = LIGHTSQ
                                    GAME_DISPLAY.blit(image, ((CELLSIZE*(x+1))+BUFFER, CELLSIZE*y+BUFFER))
                                    pygame.draw.rect(GAME_DISPLAY, col, [xpos, ypos, CELLSIZE, CELLSIZE])
                                elif x == 6:
                                    rook = new_state.squares[x-1, y].piece
                                    image = pygame.image.load(rook.img)
                                    xpos = (CELLSIZE*(new_sq.position[0]+1))+BUFFER
                                    ypos = CELLSIZE*new_sq.position[1]+BUFFER
                                    if new_state.squares[x-1, y].colour == 'w':
                                        col = LIGHTSQ
                                    elif new_state.squares[x-1, y].colour == 'b':
                                        col = DARKSQ
                                    GAME_DISPLAY.blit(image, ((CELLSIZE*(x-1))+BUFFER, CELLSIZE*y+BUFFER))
                                    pygame.draw.rect(GAME_DISPLAY, col, [xpos, ypos, CELLSIZE, CELLSIZE])
                            # Draws the current piece onto new square
                            image = pygame.image.load(new_piece.img)
                            GAME_DISPLAY.blit(image, (CELLSIZE*x+BUFFER, CELLSIZE*y+BUFFER))

                            # Increment turn counter
                            board.turn_num += 1
                            # set the last move
                            pos = lastmove.position
                            # check if enemy king is in check
                            status = board.checking(new_piece, new_state)
                            if status:
                                if new_piece.colour == 'w':
                                    new_state.bking.check = True
                                elif new_piece.colour == 'b':
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
                            except:
                                lastmove = new_sq
                                new_state.last_move = new_sq
                            # save new state
                            states.append(new_state)
                            current_state = new_state

                            # Update the turn counter
                            if turn == 0:
                                turn += 1
                            elif turn == 1:
                                turn -= 1
                            if DEBUG:
                                print(curr_piece.piece, 'moved to', notation((x, y)))
                                if status:
                                    print('Enemy King is in check')
                        else:
                            piece_selected = False

                    # if clicked on the same square then do nothing
                    else:
                        piece_selected = False
                else:       #click
                    curr_sq = current_state.squares[x, y]
                    curr_piece = curr_sq.piece

                    if DEBUG:
                        atkedby = board.attack_by(curr_sq, current_state)
                        print('\nSquare', notation((x, y)), 'is under attack by:', atkedby)

                    # Do nothing if there's no piece on the square
                    if curr_piece is not None:
                        piece_selected = True

                        # Check which Player's turn it is
                        if turn == 0:
                            # Player 1's turn : White
                            if curr_piece.colour != PLAYER_1.colour:
                                piece_selected = False
                                continue
                        elif turn == 1:
                            # Player 2's turn : Black
                            if curr_piece.colour != PLAYER_2.colour:
                                piece_selected = False
                                continue

                        # Check if under check
                        status = board.check(curr_piece.colour, current_state)

                        ###############################################################################
                        if DEBUG:
                            # print location of current kings
                            #wkingfile = current_state.wking.file
                            #wkingrank = current_state.wking.rank
                            #bkingfile = current_state.bking.file
                            #bkingrank = current_state.bking.rank
                            #print('White king is located on', notation((wkingfile, wkingrank)))
                            #print('Black king is located on', notation((bkingfile, bkingrank)))

                            # Under check
                            if status:
                                print('Your king is under check!')

                            #wp = []
                            #bp = []
                            #for pieces in board.wpieces:
                            #    wp.append(pieces.piece)
                            #for pieces in board.bpieces:
                            #    bp.append(pieces.piece)
                            #print('all WHITE pieces', wp)
                            #print('all black pieces', bp)

                            # show what the last move was
                            if lastmove.piece is not None:
                                print('The last move was', lastmove.piece.piece, 'on', notation(lastmove.position))

                            # Print Current piece on square
                            print('\nCurrent piece:', curr_piece.piece)

                            # Print valid moves and all possible attacks
                            valid_moves = curr_piece.valid_moves(current_state)
                            atkingsq = board.attack(curr_piece, current_state)
                            sentence = ''
                            sentence2 = ''
                            for move in valid_moves:
                                sentence += notation(move)
                            print('Valid moves:', sentence)
                            for move in atkingsq:
                                sentence2 += notation(move)
                            print('attacking:', sentence2)
                        ################################################################################

            # # Mouse unclicked
            # elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            #     # Mouse out of bounds
            #     x_pos = event.pos[0]
            #     y_pos = event.pos[1]
            #     if x_pos < BUFFER or y_pos < BUFFER or x_pos > (BOARDSIZE*CELLSIZE+BUFFER) or y_pos > (BOARDSIZE*CELLSIZE+BUFFER):
            #         piece_selected = False
            #         continue

            reset_button(x_pos, y_pos, buttonx, buttony)

        pygame.display.update()
    # closes pygame
    pygame.quit()
    quit()

# initiate pygame
pygame.init()
# load FONT
FONT = pygame.freetype.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 15)

DEBUG = True

# Board and display variables
BOARDSIZE = 8
CELLSIZE = 64
BUFFER = 25
DIMX = (BOARDSIZE*CELLSIZE)+(2*BUFFER) + 200
DIMY = (BOARDSIZE*CELLSIZE)+(2*BUFFER)
FILE_NAME = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
RANK_NAME = ['1', '2', '3', '4', '5', '6', '7', '8']

# set colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
LIGHT_WOOD = (238, 219, 179)
DARK_WOOD = (181, 135, 99)
BRIGHT_DRK_WOOD = (231, 185, 149)

LIGHTSQ = LIGHT_WOOD
DARKSQ = DARK_WOOD

# Initiate players and turn variable
TURN = 0
PLAYER_1 = Player('w')
PLAYER_2 = Player('b')

# initiate game display
GAME_DISPLAY = pygame.display.set_mode((DIMX, DIMY))
pygame.display.set_caption('Chess')

gameloop()

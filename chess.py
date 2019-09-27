"""
The main file:
Handles starting the game
"""
import math
import pygame
import pygame.freetype
from board import Board
from search import ab_negamax
from player import Player

def notation(position):
    """
    rewrites board matrix standard file, rank notation
    """
    fnote = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    rnote = ['8', '7', '6', '5', '4', '3', '2', '1']
    note = fnote[position[0]] + rnote[position[1]] + " "
    return note


def text_objects(text, font):
    """
    Function returns the text to render and the rectangle it covers
    """
    textsurface = font.render(text, True, BLACK)
    return textsurface, textsurface.get_rect()


def undo_move(states, movelist, board):
    """Undo the last move"""
    if board.turn_num < 1:
        print('No more moves to undo')
        return
    curr, new = states[board.turn_num].last_move
    del states[board.turn_num]
    del movelist[board.turn_num-1]
    board.turn_num -= 1
    square1 = states[board.turn_num].squares[curr.position]
    square2 = states[board.turn_num].squares[new.position]
    pygame.draw.rect(GAME_DISPLAY, square2.sqrcolour, [square2.coord[0], square2.coord[1], CELLSIZE, CELLSIZE])
    pygame.draw.rect(GAME_DISPLAY, square1.sqrcolour, [square1.coord[0], square1.coord[1], CELLSIZE, CELLSIZE])
    image = pygame.image.load(square1.piece.img)
    GAME_DISPLAY.blit(image, square1.coord)


def quit_game():
    """Quits the game"""
    pygame.quit()
    quit()


def reset_(xposition, yposition, buttonx, buttony, action=None):
    """
    Function that deals with rendering reset button
    """
    if (buttonx+175) > xposition > buttonx and (buttony+60) > yposition > buttony:
        pygame.draw.rect(GAME_DISPLAY, PEACH, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(RESET[0], RESET[1])
        if action:
            print('Starting new game...')
            action()
    else:
        pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(RESET[0], RESET[1])


def undo_(xposition, yposition, buttonx, buttony, states=None, movelist=None, board=None, action=None):
    """Function that deals with rendering undo button"""
    if (buttonx+175) > xposition > buttonx and (buttony+60) > yposition > buttony:
        pygame.draw.rect(GAME_DISPLAY, PEACH, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(UNDO[0], UNDO[1])
        if action:
            pass
            #action(states, movelist, board)
    else:
        pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(UNDO[0], UNDO[1])


def quit_(xposition, yposition, buttonx, buttony, action=None):
    """Function that deals with rendering quit button"""
    if (buttonx+175) > xposition > buttonx and (buttony+60) > yposition > buttony:
        pygame.draw.rect(GAME_DISPLAY, PEACH, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(QUIT[0], QUIT[1])
        if action:
            print('Quitting game...')
            action()
    else:
        pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
        GAME_DISPLAY.blit(QUIT[0], QUIT[1])


def lit_square(xposition, yposition, current_piece, state, clicked=False):
    """Function that highlights square when hovering over it"""
    if current_piece is not None:
        moves = current_piece.valid_moves(state)
    else:
        moves = []

    for square in state.squares:
        sqr = state.squares[square]
        pce = state.squares[square].piece
        (x_sq, y_sq) = sqr.coord
        if (x_sq+CELLSIZE) > xposition > x_sq and (y_sq+CELLSIZE) > yposition > y_sq:
            if clicked:
                for move in moves:
                    file = move[0]
                    rank = move[1]
                    if sqr.position == (file, rank):
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


def move_notation(state, piece, square, checkmate, stalemate, status):
    """Function converts the move to algebraic notation"""
    if state.status == '0-0' or state.status == '0-0-0':
        movestr = state.status
    elif state.status == '=':
        movestr = notation(square.position).strip() + state.status + piece.piece
    elif checkmate:
        movestr = piece.piece + state.status + notation(square.position).strip() + '#'
    elif stalemate:
        movestr = piece.piece + state.status + notation(square.position).strip() + '~'
    elif status:
        movestr = piece.piece + state.status + notation(square.position).strip() + '+'
    else:
        movestr = piece.piece + state.status + notation(square.position).strip()
    return movestr


def render_buttons(buttonx, buttony):
    """This function renders the buttons"""
    # Reset button
    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, buttony, 175, 60])
    RESET[1].center = ((buttonx+(175/2)), (buttony+(60/2)))
    GAME_DISPLAY.blit(RESET[0], RESET[1])
    # Undo Button
    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, (buttony + 85), 175, 60])
    UNDO[1].center = ((buttonx+(175/2)), ((buttony + 85)+(60/2)))
    GAME_DISPLAY.blit(UNDO[0], UNDO[1])
    # Quit Button
    pygame.draw.rect(GAME_DISPLAY, DARK_WOOD, [buttonx, (buttony + 170), 175, 60])
    QUIT[1].center = ((buttonx+(175/2)), ((buttony + 170)+(60/2)))
    GAME_DISPLAY.blit(QUIT[0], QUIT[1])


def render_move(file, rank, current_square, new_state, board):
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
    if board.enpass_capture:
        board.enpass_capture = False
        if new_state.squares[file, rank].piece.colour == 'b':
            ypos = (CELLSIZE*(new_state.squares[file, rank].piece.rank-1))+BUFFER
        elif new_state.squares[file, rank].piece.colour == 'w':
            ypos = (CELLSIZE*(new_state.squares[file, rank].piece.rank+1))+BUFFER
        xpos = (CELLSIZE*new_state.squares[file, rank].piece.file)+BUFFER
        pygame.draw.rect(GAME_DISPLAY, clr, [xpos, ypos, CELLSIZE, CELLSIZE])
    # Castle (need to make new function for this)
    if board.castle:
        board.castle = False
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


def start_game():
    """Main game function"""
    # label the axis
    axis_file = (CELLSIZE/2) + 20
    axis_rank = (BUFFER + BOARDSIZE*CELLSIZE) - (CELLSIZE/2)
    for order in range(0, BOARDSIZE):
        LABELFONT.render_to(GAME_DISPLAY, (axis_file, 545), FILE_NAME[order], WHITE)
        LABELFONT.render_to(GAME_DISPLAY, (9, axis_rank), RANK_NAME[order], WHITE)
        axis_file += CELLSIZE
        axis_rank -= CELLSIZE

    # Render buttons
    # Render buttons
    buttonx = (BOARDSIZE*CELLSIZE)+(2*BUFFER)
    buttony = (CELLSIZE*2) + BUFFER + 13
    render_buttons(buttonx, buttony)

    # Initializes and draws chess board
    board = Board(GAME_DISPLAY, CELLSIZE)
    board.set_board()

    # game loop
    game_exit = False
    # current state, current square and current piece
    curr_state = board.state
    curr_sq = None
    curr_piece = None
    # all states and all moves
    states = []
    allmoves = []
    states.append(curr_state)
    # check mate variables
    checkmate = False
    stalemate = False
    checkmate_king = None
    # piece clicked and turn variables
    piece_clicked = False
    turn = 'w'

    while not game_exit:
        # quits the game when exit is pressed
        for event in pygame.event.get():
            # Exit game
            if event.type == pygame.QUIT:
                print('Quitting game...')
                game_exit = True

            if not checkmate and not stalemate:
                # mouse position
                (x_pos, y_pos) = pygame.mouse.get_pos()

                # Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Buttons: reset and quit buttons
                    reset_(x_pos, y_pos, buttonx, buttony, start_game)
                    undo_(x_pos, y_pos, buttonx, (buttony+85), states, allmoves, board, undo_move)
                    quit_(x_pos, y_pos, buttonx, (buttony+170), quit_game)

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
                            # Only make move if intended move is in set of legal moves
                            if (file, rank) in legalmoves[curr_sq.position][0]:
                                new_state = board.move(curr_piece, file, rank, curr_state)
                                new_sq = new_state.squares[file, rank]
                                new_piece = new_sq.piece
                                render_move(file, rank, curr_sq, new_state, board)

                                # Increment turn counter
                                board.turn_num += 1
                                
                                # Sets variable so en passant capture only availble for one turn
                                try:
                                    # set the last move
                                    pos = new_state.last_move[1].position
                                    new_state.squares[pos].piece.double = False
                                except (AttributeError, KeyError, IndexError):
                                    pass
                                
                                # check if enemy king is in check
                                status = new_state.checking(new_piece)
                                if status and new_piece.colour == 'w':
                                    new_state.bking.checked = True
                                    ismate = new_state.checkmate('b')
                                    if ismate:
                                        print('Black King is mated: WHITE WINS')
                                        checkmate = True
                                        checkmate_king = new_state.bking
                                elif status and new_piece.colour == 'b':
                                    new_state.wking.checked = True
                                    ismate = new_state.checkmate('w')
                                    if ismate:
                                        print('White King is mated: BLACK WINS')
                                        checkmate = True
                                        checkmate_king = new_state.wking
                                else:
                                    if new_piece.colour == 'w':
                                        new_state.bking.checked = False
                                        ismate = new_state.checkmate('b')
                                        if ismate:
                                            print('Stalemate')
                                            stalemate = True
                                            checkmate_king = new_state.bking
                                    elif new_piece.colour == 'b':
                                        new_state.wking.checked = False
                                        ismate = new_state.checkmate('w')
                                        if ismate:
                                            print('Stalemate')
                                            stalemate = True
                                            checkmate_king = new_state.wking
                                # record move to move list
                                allmoves.append(move_notation(new_state, new_piece, new_sq, checkmate, stalemate, status))

                                new_state.last_move = (curr_sq, new_sq)
                                # save new state
                                states.append(new_state)
                                del curr_state
                                curr_state = new_state

                                # Update the turn counter
                                if turn == 'w':
                                    turn = 'b'
                                elif turn == 'b':
                                    turn = 'w'

                                if DEBUG:
                                    if status:
                                        print('Enemy King is in check')
                        else:
                            piece_clicked = True
                    else:       #click
                        curr_sq = curr_state.squares[file, rank]
                        curr_piece = curr_sq.piece

                        if DEBUG:
                            atkedby = curr_state.attack_by(turn, curr_sq)
                            legalmoves = curr_state.legal_moves(turn)
                            print('Square', notation((file, rank)), 'under attack by:', atkedby)
                            #print('Legal moves:', legalmoves)

                        # Do nothing if there's no piece on the square
                        if curr_piece is not None:
                            piece_clicked = True

                            # Check which Player's turn it is
                            # if turn is not same colour as piece, then do nothing
                            if curr_piece.colour != turn:
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
                                try:
                                    if curr_state.last_move[1].piece is not None:
                                        print('The last move was', curr_state.last_move[1].piece.piece, 'on', notation(curr_state.last_move[1].position))
                                except IndexError:
                                    print('No last move')

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
                            if SCORE:
                                #thescore = score_all(curr_state)
                                #sort = [(key, thescore[key]) for key in sorted(thescore, key=thescore.get, reverse=True)]
                                #sort = sorted(thescore.items(), key=lambda x: x[1], reverse=True)
                                #for key, value in sort:
                                #    print(key[0], notation(key[1]), ':', value)
                                #print('\n')
                                bestscr, bestmove = ab_negamax(curr_state, turn, -100000, 100000, 2)
                                print(bestmove, bestscr)
                if piece_clicked:
                    lit_square(x_pos, y_pos, curr_piece, curr_state, True)
                else:
                    lit_square(x_pos, y_pos, curr_piece, curr_state,)
            else:
                # mouse position
                (x_pos, y_pos) = pygame.mouse.get_pos()

                # Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Buttons: reset and quit
                    reset_(x_pos, y_pos, buttonx, buttony, start_game)
                    undo_(x_pos, y_pos, buttonx, (buttony+85), states, allmoves, board, undo_move)
                    quit_(x_pos, y_pos, buttonx, (buttony+170), quit_game)
                lit_check(checkmate_king, curr_state)
            # Buttons
            reset_(x_pos, y_pos, buttonx, buttony)
            undo_(x_pos, y_pos, buttonx, (buttony+85))
            quit_(x_pos, y_pos, buttonx, (buttony+170))
        pygame.display.update()
    # closes pygame
    pygame.quit()
    quit()


def cpu_plays():
    """Function that lets two CPUs play against each other"""
    # label the axis
    axis_file = (CELLSIZE/2) + 20
    axis_rank = (BUFFER + BOARDSIZE*CELLSIZE) - (CELLSIZE/2)
    for order in range(0, BOARDSIZE):
        LABELFONT.render_to(GAME_DISPLAY, (axis_file, 545), FILE_NAME[order], WHITE)
        LABELFONT.render_to(GAME_DISPLAY, (9, axis_rank), RANK_NAME[order], WHITE)
        axis_file += CELLSIZE
        axis_rank -= CELLSIZE

    # Render buttons
    # Render buttons
    buttonx = (BOARDSIZE*CELLSIZE)+(2*BUFFER)
    buttony = (CELLSIZE*2) + BUFFER + 13
    render_buttons(buttonx, buttony)

    # Initializes and draws chess board
    board = Board(GAME_DISPLAY, CELLSIZE)
    board.set_board()

    # game loop
    game_exit = False
    # current state, current square and current piece
    curr_state = board.state
    curr_sq = None
    curr_piece = None
    # all states and all moves
    states = []
    allmoves = []
    states.append(curr_state)
    # check mate variables
    checkmate = False
    stalemate = False
    checkmate_king = None
    # piece clicked and turn variables
    turn = 'w'

    while not game_exit:
        if not checkmate and not stalemate:
            # Calculate best move
            best_move = ab_negamax(curr_state, turn, -math.inf, math.inf, 1)

            # perform move
            curr_sq = curr_state.squares[best_move[1][0]]
            curr_piece = curr_state.squares[best_move[1][0]].piece
            file = best_move[1][1][0][0]
            rank = best_move[1][1][0][1]
            print(board.turn_num, '- Piece', (turn, curr_piece.piece), 'moved to', notation((file, rank)))
            new_state = board.move(curr_piece, file, rank, curr_state)
            new_sq = new_state.squares[file, rank]
            new_piece = new_sq.piece
            render_move(file, rank, curr_sq, new_state, board)

            # Increment turn counter
            board.turn_num += 1

            # Sets variable so en passant capture only availble for one turn
            try:
                # set the last move
                pos = new_state.last_move[1].position
                new_state.squares[pos].piece.double = False
            except (AttributeError, KeyError, IndexError):
                pass

            # check if enemy king is in check
            status = new_state.checking(new_piece)
            if status and new_piece.colour == 'w':
                new_state.bking.checked = True
                ismate = new_state.checkmate('b')
                if ismate:
                    print('Black King is mated: WHITE WINS')
                    checkmate = True
                    checkmate_king = new_state.bking
            elif status and new_piece.colour == 'b':
                new_state.wking.checked = True
                ismate = new_state.checkmate('w')
                if ismate:
                    print('White King is mated: BLACK WINS')
                    checkmate = True
                    checkmate_king = new_state.wking
            else:
                if new_piece.colour == 'w':
                    new_state.bking.checked = False
                    ismate = new_state.checkmate('b')
                    if ismate:
                        print('Stalemate')
                        stalemate = True
                        checkmate_king = new_state.bking
                elif new_piece.colour == 'b':
                    new_state.wking.checked = False
                    ismate = new_state.checkmate('w')
                    if ismate:
                        print('Stalemate')
                        stalemate = True
                        checkmate_king = new_state.wking
            # record move to move list
            allmoves.append(move_notation(new_state, new_piece, new_sq, checkmate, stalemate, status))

            new_state.last_move = (curr_sq, new_sq)
            # save new state
            states.append(new_state)
            del curr_state
            curr_state = new_state

            # Update the turn counter
            if turn == 'w':
                turn = 'b'
            elif turn == 'b':
                turn = 'w'
        else:
            # mouse position
            (x_pos, y_pos) = pygame.mouse.get_pos()

            # Mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Buttons: reset and quit
                reset_(x_pos, y_pos, buttonx, buttony, start_game)
                undo_(x_pos, y_pos, buttonx, (buttony+85), states, allmoves, board, undo_move)
                quit_(x_pos, y_pos, buttonx, (buttony+170), quit_game)
            lit_check(checkmate_king, curr_state)
        pygame.display.update()
    # closes pygame
    pygame.quit()
    quit()



# initiate pygame
pygame.init()

# DEBUG VARIABLE
DEBUG = False
SCORE = True

# load font
LABELFONT = pygame.freetype.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 15)
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
UNDO = text_objects('coming soon', BUTTONFONT)
QUIT = text_objects('Quit', BUTTONFONT)

# Initiate players and turn variable
TURN = 0
PLAYER_1 = Player('w')
PLAYER_2 = Player('b')

# initiate game display
GAME_DISPLAY = pygame.display.set_mode((DIMX, DIMY))
pygame.display.set_caption('Chess')

# Start game
#start_game()
cpu_plays()

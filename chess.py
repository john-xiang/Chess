import pygame
import pygame.freetype
#from collections import defaultdict
from board import Board
from player import Player

def notation(position):
    """
    rewrites board matrix to UCI notation
    """
    fileNote = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    rankNote = ['8', '7', '6', '5', '4', '3', '2', '1']
    note = fileNote[position[0]] + rankNote[position[1]] + " "
    return note

debug = True

# initiate pygame
pygame.init()

# Board and display variables
boardsize = 8
cellsize = 64
buffer = 25
dimX = (boardsize*cellsize)+(2*buffer)+ 150
dimY = (boardsize*cellsize)+(2*buffer)
fileName = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
rankName = ['1', '2', '3', '4', '5', '6', '7', '8']

# set colours
white = (255, 255, 255)
black = (0, 0, 0)
gray = (192, 192, 192)
lightWood = (238, 219, 179)
darkWood = (181, 135, 99)

lightsq = lightWood
darksq = darkWood

# load font
font = pygame.freetype.Font('/home/johnx/Projects/chess/font/OpenSans-Semibold.ttf', 15)

# initiate game display
gameDisplay = pygame.display.set_mode((dimX, dimY))
pygame.display.set_caption('Chess')

# label the axis
files = (cellsize/2) + 20
ranks = (buffer + boardsize*cellsize) - (cellsize/2)
for order in range(0,boardsize):
    font.render_to(gameDisplay, (files, 545), fileName[order], white)
    font.render_to(gameDisplay, (9, ranks), rankName[order], white)
    files += cellsize
    ranks -= cellsize

# Initializes and draws chess board
brd = Board(gameDisplay, cellsize)
brd.setBoard()

# Initiate players and turn variable
turn = 0
player_1 = Player('w')
player_2 = Player('b')

# game loop
gameExit = False
states = []
currentState = brd.state
lastMoveSquare = brd.state.lastMove
selectedSquare = None
selectedPiece = None
pieceSelected = False

while not gameExit:
    # quits the game when exit is pressed
    for event in pygame.event.get():
        #####################################
        #print(event)
        #####################################

        # Exit game
        if event.type == pygame.QUIT:
            gameExit = True

        # Mouse click 
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Mouse out of bounds
            pos1 = event.pos[0]
            pos2 = event.pos[1]
            if pos1 < buffer or pos2 < buffer or pos1 > (boardsize*cellsize+buffer) or pos2 > (boardsize*cellsize+buffer):
                pieceSelected = False
                continue
            # Get the coordinates of where the mouse clicked
            x,y = int((pos1-buffer)/cellsize), int((pos2-buffer)/cellsize)

            if pieceSelected:
                if (x,y) != selectedSquare.position:
                    # Check if the move is valid before doing it
                    newState = brd.move(selectedPiece, x, y, currentState)

                    if newState != 0:
                        pieceSelected = False
                        newSquare = newState.squares[x,y]
                        newPiece = newSquare.piece
                        if selectedSquare.colour == 'b':
                            col = darksq
                        elif selectedSquare.colour == 'w':
                            col = lightsq
                        if newSquare.colour == 'b':
                            colr = darksq
                        elif newSquare.colour == 'w':
                            colr = lightsq

                        # Draws the new state. Erases old square
                        pygame.draw.rect(gameDisplay, col, [cellsize*selectedSquare.position[0]+buffer, cellsize*selectedSquare.position[1]+buffer, cellsize, cellsize])
                        # Capture: Erase the piece on captured square
                        if newPiece != None:
                            pygame.draw.rect(gameDisplay, colr, [cellsize*newSquare.position[0]+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
                        # En Passant
                        if newState.enpassCapture:
                            newState.enpassCapture = False
                            f = newPiece.file
                            if newPiece.colour == 'b':
                                r = newPiece.rank - 1
                            elif newPiece.colour == 'w':
                                r = newPiece.rank + 1
                            if selectedSquare.colour == 'w':
                                clr = darksq
                            elif selectedSquare.colour == 'b':
                                clr = lightsq
                            pygame.draw.rect(gameDisplay, clr, [cellsize*f+buffer, cellsize*r+buffer, cellsize, cellsize])
                        # Castle
                        if newState.castle:
                            newState.castle = False
                            if x == 2:
                                rook = newState.squares[x+1, y].piece
                                image = pygame.image.load(rook.img)
                                gameDisplay.blit(image, ((cellsize*(x+1))+buffer, cellsize*y+buffer))
                                if newState.squares[x+1, y].colour == 'w':
                                    col = darksq
                                elif newState.squares[x+1, y].colour == 'b':
                                    col = lightsq
                                pygame.draw.rect(gameDisplay, col, [(cellsize*(newSquare.position[0]-2))+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
                            elif x == 6:
                                rook = newState.squares[x-1, y].piece
                                image = pygame.image.load(rook.img)
                                gameDisplay.blit(image, ((cellsize*(x-1))+buffer, cellsize*y+buffer))
                                if newState.squares[x-1, y].colour == 'w':
                                    col = lightsq
                                elif newState.squares[x-1, y].colour == 'b':
                                    col = darksq
                                pygame.draw.rect(gameDisplay, col, [(cellsize*(newSquare.position[0]+1))+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
                        # Draws the current piece onto new square
                        image = pygame.image.load(newPiece.img)
                        gameDisplay.blit(image, (cellsize*x+buffer, cellsize*y+buffer))

                        # Increment turn counter
                        brd.turnNum += 1
                        # set the last move
                        pos = lastMoveSquare.position
                        # check if enemy king is in check
                        status = brd.check(newPiece, newState)
                        if status:
                            if newPiece.colour == 'w':
                                newState.bKing.check = True
                                newState.squares[newState.bKing.file, newState.bKing.rank].piece.check = True
                            elif newPiece.colour == 'b':
                                newState.wKing.check = True
                                newState.squares[newState.wKing.file, newState.wKing.rank].piece.check = True
                        try: # Sets variable so en passant capture only availble for one turn
                            newState.squares[pos].piece.double = False
                            lastMoveSquare = newSquare
                            newState.lastMove = newSquare
                        except:
                            lastMoveSquare = newSquare
                            newState.lastMove = newSquare
                        # save new state
                        states.append(newState)
                        currentState = newState

                        # Update the turn counter
                        if turn == 0:
                            turn += 1
                        elif turn == 1:
                            turn -= 1
                        if debug:
                            print(selectedPiece.piece, 'moved to', notation((x,y)))
                            if status:
                                print('Enemy King is in check')
                    else:
                        pieceSelected = False

                # if clicked on the same square then do nothing
                else:
                    pieceSelected = False
            else:       #click
                selectedSquare = currentState.squares[x,y]
                selectedPiece = selectedSquare.piece
                
                if debug:
                    attackedBy = brd.attackBy(selectedSquare, currentState)
                    print('\nSquare', notation((x,y)), 'is under attack by:', attackedBy)

                # Do nothing if there's no piece on the square
                if selectedPiece != None:
                    pieceSelected = True
                    
                    # Check which Player's turn it is
                    if turn == 0:
                        # Player 1's turn : White
                        if selectedPiece.colour != player_1.colour:
                            pieceSelected = False
                            continue
                    elif turn == 1:
                        # Player 2's turn : Black
                        if selectedPiece.colour != player_2.colour:
                            pieceSelected = False
                            continue
                    
                    # Check if under check
                    status = brd.isCheck(selectedPiece.colour, currentState)

                    ###############################################################################################
                    if debug:
                        # print location of current kings
                        #print('White king is located on', notation((currentState.wKing.file, currentState.wKing.rank)))
                        #print('Black king is located on', notation((currentState.bKing.file, currentState.bKing.rank)))

                        # Under check
                        if status:
                            print('Your king is under check!')
                        
                        #wp = []
                        #bp = []
                        #for pieces in brd.wPieces:
                        #    wp.append(pieces.piece)
                        #for pieces in brd.bPieces:
                        #    bp.append(pieces.piece)
                        #print('all white pieces', wp)
                        #print('all black pieces', bp)

                        # show what the last move was
                        if lastMoveSquare.piece != None:
                            print('The last move was', lastMoveSquare.piece.piece, 'on', notation(lastMoveSquare.position))
                        
                        # Print Current piece on square
                        print('\nCurrent piece:', selectedPiece.piece)
                        
                        # Print valid moves and all possible attacks
                        valid_moves = selectedPiece.valid_moves(currentState)
                        atttackingSq = brd.attack(selectedPiece, currentState)
                        sentence = ''
                        sentence2 = ''
                        for move in valid_moves:
                            sentence += notation(move)
                        print('Valid moves:', sentence)
                        for move in atttackingSq:
                            sentence2 += notation(move)
                        print('attacking:', sentence2)
                    ################################################################################################

        # # Mouse unclicked
        # elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        #     # Mouse out of bounds
        #     pos1 = event.pos[0]
        #     pos2 = event.pos[1]
        #     if pos1 < buffer or pos2 < buffer or pos1 > (boardsize*cellsize+buffer) or pos2 > (boardsize*cellsize+buffer):
        #         pieceSelected = False
        #         continue
            
        #     if pieceSelected:
        #         # Get coordinates of where the mouse unclicked)
        #         (x,y) = (int((pos1-buffer)/cellsize), int((pos2-buffer)/cellsize))
        #         if (x,y) != selectedSquare.position:
        #             # Check if the move is valid before doing it
        #             checkPiece = selectedPiece
        #             checkState = currentState
        #             checkbrd = brd
        #             checkMove = checkbrd.move(checkPiece, x, y, checkState)

        #             ##################################################################################################
        #             # BUG: The move is still being performed because of brd.move function earlier
        #             # # if the move results in the king in check, then move is not allowed
        #             if checkMove != 0:
        #                 inCheck = checkbrd.isCheck(checkPiece.colour, checkMove)
        #                 if inCheck:
        #                     print('Move leaves king in check! Not allowed')
        #                     pieceSelected = False
        #                     newState = 0
        #                 else:
        #                     newState = brd.move(selectedPiece, x, y, currentState)
        #                     if selectedPiece.colour == 'w':
        #                         brd.wKing.check = False
        #                     elif selectedPiece.colour == 'b':
        #                         brd.bKing.check = False
        #             else:
        #                 newState = 0
        #             ###################################################################################################

        #             if newState != 0:
        #                 newSquare = newState[x,y]
        #                 newPiece = newSquare.piece
        #                 pieceSelected = False
        #                 if selectedSquare.colour == 'b':
        #                     col = darksq
        #                 elif selectedSquare.colour == 'w':
        #                     col = lightsq
        #                 if newSquare.colour == 'b':
        #                     colr = darksq
        #                 elif newSquare.colour == 'w':
        #                     colr = lightsq

        #                 # Draws the new state. Erases old square
        #                 pygame.draw.rect(gameDisplay, col, [cellsize*selectedSquare.position[0]+buffer, cellsize*selectedSquare.position[1]+buffer, cellsize, cellsize])
        #                 # Capture: Erase the piece on captured square
        #                 if newPiece != None:
        #                     pygame.draw.rect(gameDisplay, colr, [cellsize*newSquare.position[0]+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
        #                 # En Passant
        #                 if brd.enpassCapture:
        #                     brd.enpassCapture = False
        #                     if newPiece.colour == 'b':
        #                         r = newPiece.rank - 1
        #                     elif newPiece.colour == 'w':
        #                         r = newPiece.rank + 1
        #                     if selectedSquare.colour == 'w':
        #                         clr = darksq
        #                     elif selectedSquare.colour == 'b':
        #                         clr = lightsq
        #                     f = newPiece.file
        #                     pygame.draw.rect(gameDisplay, clr, [cellsize*f+buffer, cellsize*r+buffer, cellsize, cellsize])
        #                 # Castle
        #                 if brd.castle:
        #                     brd.castle = False
        #                     if x == 2:
        #                         rook = newState[x+1, y].piece
        #                         gameDisplay.blit(rook.img, ((cellsize*(x+1))+buffer, cellsize*y+buffer))
        #                         if newState[x+1, y].colour == 'w':
        #                             col = darksq
        #                         elif newState[x+1, y].colour == 'b':
        #                             col = lightsq
        #                         pygame.draw.rect(gameDisplay, col, [(cellsize*(newSquare.position[0]-2))+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
        #                     elif x == 6:
        #                         rook = newState[x-1, y].piece
        #                         gameDisplay.blit(rook.img, ((cellsize*(x-1))+buffer, cellsize*y+buffer))
        #                         if newState[x-1, y].colour == 'w':
        #                             col = lightsq
        #                         elif newState[x-1, y].colour == 'b':
        #                             col = darksq
        #                         pygame.draw.rect(gameDisplay, col, [(cellsize*(newSquare.position[0]+1))+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
        #                 # Draws the current piece onto new square
        #                 gameDisplay.blit(newPiece.img, (cellsize*x+buffer, cellsize*y+buffer))

        #                 # Increment turn counter
        #                 brd.turnNum += 1
        #                 # set the last move
        #                 pos = lastMoveSquare.position
        #                 # check if enemy king is in check
        #                 status = brd.check(newPiece, newState)
        #                 if status:
        #                     if newPiece.colour == 'w':
        #                         brd.bKing.check = True
        #                     elif newPiece.colour == 'b':
        #                         brd.wKing.check = True
        #                 try: # Sets variable so en passant capture only availble for one turn
        #                     newState[pos].piece.double = False
        #                     lastMoveSquare = newSquare
        #                     brd.lastMove = newSquare
        #                 except:
        #                     lastMoveSquare = newSquare
        #                     brd.lastMove = newSquare
        #                 # save new state
        #                 brd.state[brd.turnNum] = newState
        #                 currentState = newState

        #                 # Update the turn counter
        #                 if turn == 0:
        #                     turn += 1
        #                 elif turn == 1:
        #                     turn -= 1
                        
        #                 if debug:
        #                     print(selectedPiece.piece, 'moved to', notation((x,y)))
        #                     if status:
        #                         print('Enemy King is in check')
        #         # if clicked or unclicked on th same square then do nothing
        #         else:
        #             pass
            
    pygame.display.update()
# closes pygame
pygame.quit()
quit()
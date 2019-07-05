import pygame
import pygame.freetype
from collections import defaultdict
from board import Board
from player import Player

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
white = (255,255,255)
black = (0,0,0)
gray = (192,192,192)
lightWood = (238, 219, 179)
darkWood = 	(181, 135, 99)

lightsq = lightWood
darksq = darkWood

# load font
font = pygame.freetype.Font('/home/johnx/Projects/Chess/font/OpenSans-Semibold.ttf', 15)

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
clicked = False
currentState = brd.state[brd.turnNum]
currentSquare = None
currentPiece = None
lastMoveSquare = brd.lastMove
#lastMovePiece = lastMoveSquare.piece

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse out of bounds
            pos1 = event.pos[0]
            pos2 = event.pos[1]
            if pos1 < buffer or pos2 < buffer or pos1 > (boardsize*cellsize+buffer) or pos2 > (boardsize*cellsize+buffer):
                pieceSelected = False
                continue
            # Get the coordinates of where the mouse clicked
            x,y = int((pos1-buffer)/cellsize), int((pos2-buffer)/cellsize)
            currentSquare = currentState[x,y]
            currentPiece = currentSquare.piece
            
            if debug:
                attackedBy = brd.attackBy(currentSquare, currentState)
                print('\nSquare', brd.notation((x,y)), 'is under attack by:', attackedBy)

            # Do nothing if there's no piece on the square
            if currentPiece != None:
                pieceSelected = True
                
                # Check which Player's turn it is
                if turn == 0:
                    # Player 1's turn : White
                    if currentPiece.colour != player_1.colour:
                        pieceSelected = False
                        continue
                elif turn == 1:
                    # Player 2's turn : Black
                    if currentPiece.colour != player_2.colour:
                        pieceSelected = False
                        continue
                
                # Check if under check
                status = brd.isCheck(currentPiece.colour, currentState)
                ###############################################################################################
                if debug:
                    # # print location of current kings
                    # print('White king is located on', brd.notation((brd.wKing.file, brd.wKing.rank)))
                    # print('Black king is located on', brd.notation((brd.bKing.file, brd.bKing.rank)))

                    # Under check
                    if status:
                        print('Your king is under check!')

                    # show what the last move was
                    if lastMoveSquare.piece != None:
                        print('The last move was', lastMoveSquare.piece.piece, 'on', brd.notation(lastMoveSquare.position))
                    
                    # Print Current piece on square
                    print('Current piece:', currentPiece.piece)
                    
                    # Print valid moves and all possible attacks
                    validMoves = currentPiece.validMoves(currentState)
                    atttackingSq = brd.attack(currentPiece, currentState)
                    sentence = ''
                    sentence2 = ''
                    for move in validMoves:
                        sentence += brd.notation(move)
                    print('Valid moves:', sentence)
                    for move in atttackingSq:
                        sentence2 += brd.notation(move)
                    print('attacking:', sentence2)
                ################################################################################################
            else:
                pieceSelected = False

        # Mouse unclicked
        elif event.type == pygame.MOUSEBUTTONUP:
            # Mouse out of bounds
            pos1 = event.pos[0]
            pos2 = event.pos[1]
            if pos1 < buffer or pos2 < buffer or pos1 > (boardsize*cellsize+buffer) or pos2 > (boardsize*cellsize+buffer):
                pieceSelected = False
                continue
            
            if pieceSelected:
                # Get coordinates of where the mouse unclicked
                (x,y) = (int((pos1-buffer)/cellsize), int((pos2-buffer)/cellsize))
                if (x,y) != currentSquare.position:
                    # Check if the move is valid before doing it
                    newState = brd.move(currentPiece, x, y, brd.state)
                    if newState != 0:
                        newSquare = newState[x,y]
                        newPiece = newSquare.piece
                        if currentSquare.colour == 'b':
                            col = darksq
                        elif currentSquare.colour == 'w':
                            col = lightsq
                        if newSquare.colour == 'b':
                            colr = darksq
                        elif newSquare.colour == 'w':
                            colr = lightsq

                        # Draws the new state. Erases old square
                        pygame.draw.rect(gameDisplay, col, [cellsize*currentSquare.position[0]+buffer, cellsize*currentSquare.position[1]+buffer, cellsize, cellsize])
                        # Capture: Erase the piece on captured square
                        if newPiece != None:
                            pygame.draw.rect(gameDisplay, colr, [cellsize*newSquare.position[0]+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
                        # En Passant
                        if brd.enpassCapture:
                            brd.enpassCapture = False
                            if newPiece.colour == 'b':
                                r = newPiece.rank - 1
                            elif newPiece.colour == 'w':
                                r = newPiece.rank + 1
                            if currentSquare.colour == 'w':
                                clr = darksq
                            elif currentSquare.colour == 'b':
                                clr = lightsq
                            f = newPiece.file
                            pygame.draw.rect(gameDisplay, clr, [cellsize*f+buffer, cellsize*r+buffer, cellsize, cellsize])

                        if brd.castle:
                            brd.castle = False
                            if x == 2:
                                rook = newState[x+1, y].piece
                                print(rook.piece)
                                gameDisplay.blit(rook.img, ((cellsize*(x+1))+buffer, cellsize*y+buffer))
                                if newState[x+1, y].colour == 'w':
                                    col = darksq
                                elif newState[x+1, y].colour == 'b':
                                    col = lightsq
                                pygame.draw.rect(gameDisplay, col, [(cellsize*(newSquare.position[0]-2))+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
                            elif x == 6:
                                rook = newState[x-1, y].piece
                                print(rook.piece)
                                gameDisplay.blit(rook.img, ((cellsize*(x-1))+buffer, cellsize*y+buffer))
                                if newState[x-1, y].colour == 'w':
                                    col = lightsq
                                elif newState[x-1, y].colour == 'b':
                                    col = darksq
                                pygame.draw.rect(gameDisplay, col, [(cellsize*(newSquare.position[0]+1))+buffer, cellsize*newSquare.position[1]+buffer, cellsize, cellsize])
                        # Draws the current piece onto new square
                        gameDisplay.blit(newPiece.img, (cellsize*x+buffer, cellsize*y+buffer))

                        # Increment turn counter
                        brd.turnNum += 1
                        # set the last move
                        pos = lastMoveSquare.position
                        try:
                            newState[pos].piece.double = False
                            lastMoveSquare = newSquare
                            brd.lastMove = newSquare
                        except:
                            lastMoveSquare = newSquare
                            brd.lastMove = newSquare
                        # save new state
                        brd.state[brd.turnNum] = newState
                        currentState = newState

                        #Change the turn counter
                        if turn == 0:
                            turn += 1
                        elif turn == 1:
                            turn -= 1
                        
                        if debug:
                            print(currentPiece.piece, 'moved to', brd.notation((x,y)))
                            brd.check(newPiece, newState)
                # if clicked or unclicked on th same square then do nothing
                else:
                    pass
            pieceSelected = False
        
    pygame.display.update()

# closes pygame
pygame.quit()
quit()
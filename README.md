# chess
Chess engine using pygame


I implemented the engine with object oriented programming as a guide. I felt that this made sense because chess can be broken down into the board, chess pieces, and players (which each could be an object). This program consists of three main files, chess.py, board.py and pieces.py.


Board object:
	game display (used for rendering chess pieces)
	cell size, size of each square (a x a)
	state, holds information about the current state (also an object)
	turn number

	Square object:
		square colour (w, b)
		square RGB colour
		square position (file, rank)
		square coordinates (pixel x, pixel y)
		chess piece (also an object)

	state object:
		all squares of the board (8 x 8)
		last piece that moved (square position)
		variable to tell board that enpassant is available
		variable to render enpassant
		variable let board know castle is possible
		white king status
		black king status

piece object:
	file position
	rank position
	piece colour
	piece string

	pawn object
		image file for rendering
		variable to say that it's the first move
		variable to say that a double move was performed

	rook object
		variable to say that it's the first move

	knight object

	bishop object

	queen object

	king object
		variable to calculate check
		variable to say that it's the first move
		
		
	

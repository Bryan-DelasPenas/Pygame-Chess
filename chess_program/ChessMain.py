"""
This is the main driver file. Responsible for handing user input. 
"""

import pygame as p 
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8                  # Chessboards are 8 x 8 
SQ_SIZE = HEIGHT // DIMENSION  # Size of the square 
MAX_FPS = 15                   # Used for animations 
IMAGES = {}                    # Dictionary of images for the pieces 

'''
Initalize a global dictionary of images. This will only be called once inside of main function
'''
def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bP','wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR', 'wP']
    
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Images/" + piece + ".png").convert_alpha(),(SQ_SIZE,SQ_SIZE))

"""
Responsible for all the graphics within a current game state
"""
def drawGameState(screen,gs):
    drawBoard(screen)            # Draw squares on the board     
    drawPieces(screen, gs.board) # Draw the sequence on top of those squares 
    

"""
Draw squares on the board; The top left sqaure is always light 
"""
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("grey")]
    
    # Used a nested for loop to loop through the 2 dimensional array 
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            
            # Looks at the array, Since each squares alternates, mod can be used to alternate; 
            # If a square coordinate added is even, it will always be light
            # If a square coordinate added is odd, it will always be dark 
            color = colors[((c + r) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using the current GameState.board 
"""
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
 
            # Checks to see if it is not an empty square 
            if piece != "--": 
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            

"""
Main Drive for the code, hands the user inputs and updating the graphics 
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT), p.RESIZABLE)
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()  # Only load once
    moveMade = False                 # Flag for when a moves is made
    loadImages()                     # Only load once

    running = True 
    sqSelected = ()   # No square is selected, kepts track of the last click of the user(tuple: (row, col)) 
    playerClicks = [] # Kepts track of player clicks (two tuples: [(6,4), (4,4)]) 
    
    # Main game loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()   # Gets (x,y) location of mouse 
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                # Checks to see if the user clicked the same square twice 
                if sqSelected == (row,col):
                    sqSelected = ()   # Deselects square
                    playerClicks = [] # Clear player clicks 
                    print(sqSelected)
        
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected) # append for both 1st and 2nd clicks 
                
                # After the second square 
                if(len(playerClicks) == 2): 
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True 
                            sqSelected = () # Reset user clicks 
                            playerClicks = []

                    if not moveMade:
                        playerClicks = [sqSelected]
            
            # Any key
            elif e.type == p.KEYDOWN:
                
                # Undo when z key is pressed 
                if e.key == p.K_z: 
                    gs.undoMove()
                    moveMade = True
       
        # Checks if a move was made
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == "__main__":
    main()
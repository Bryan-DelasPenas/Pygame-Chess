"""
This class is responsible for storing information about the game state of a chess game. 
Responsible for determing the valid moves at the current state
Contains a move log 
"""
import numpy as np 

class GameState():
    def __init__(self):
        
        # Board is a 8 x 8, 2d list, each element has 2 characters, 
        # The first character is the color of the piece, 'b' or 'w'.
        # The second character is the type of piece, 'K', 'Q', 'B', 'K', 'R' 'P'.
        # "--" represents an empty space without no piece. 
        self.board = np.array(
            [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],  
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],                                           
            ]
        )
        self.moveFunctions = {'P': self.getPawnMoves, 'R':self.getRookMoves, 'N': self.getKnightMoves, 
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        self.whiteToMove = True 
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.isCheck = False
        self.pins = []
        self.checks = []
    
    """
    Takes a move as a parameter and moves it (This does not work for castling, pawn premotion and en-passant)
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)               # Logs the move 
        self.whiteToMove = not self.whiteToMove # Swap Players
        
        # Update king's position 
        if move.pieceMoved == "wk":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bk":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion 
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        
    """
    Undo the last move 
    """
    def undoMove(self):
        
        # Check to see if the move log is empty 
        if len(self.moveLog) != 0: 
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turn back
    
        # Update king's position 
        if move.pieceMoved == "wk":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bk":
            self.blackKingLocation = (move.endRow, move.endCol)

    """
    All moves considering checks 
    """
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
 
            # Only one check 
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                
                # To block a check you must move a piece into one of the squares between the enemy piece and king 
                check = self.checks[0] # Check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # Enemy piece that causing check
                validSquares = [] # Squares that piece can move to 

                # If knight, must capture knight or move king, other pieces can be blocked 
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2] and check[3] are the check directions 
                        validSquares.append(validSquare)
                        
                        # Once you get to piece end checks 
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                
                # Get rid of any moves that don't block check or move king 
                for i in range(len(moves) -1, -1, -1): # go through backwards when removing from a list as iterating 

                    # Moved doesn't move king so it must block or capture
                    if moves[i].pieceMoved[1] != "K": 

                        # move doesn't block check or capture piece 
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            # Double check
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        # not in check so all moves are fine 
        else:
            moves = self.getAllPossibleMoves()
        return moves
    """
    All moves without considering checks 
    """
    def getAllPossibleMoves(self):
        moves = []

        # Checks every single elements 
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0] 
                
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    
                    # Calls apporitate move function
                    self.moveFunctions[piece](r, c, moves)
        return moves
   
   
    """                     
    Gets all the pawn moves for the pawn located at row, col and add these moves to the list 
    """
    def getPawnMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        # Check if white turn 
        if self.whiteToMove: 
            
            # One square pawn advance
            if self.board[r - 1][c] == "--":
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c), (r - 1, c), self.board))
                    # Two square pawn advance 
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r,c), (r - 2, c), self.board))       

            # Stay inside of the board, if capturing left 
            if c - 1 >= 0:

                # Enemy piece to capture 
                if self.board[r - 1][c - 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r,c), (r - 1, c - 1), self.board))
            
            # Stay inside of the board, if capturing right 
            if c + 1 <= 7:

               # Enemy piece to capture 
                if self.board[r - 1][c + 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r,c), (r - 1, c + 1), self.board))
        
        # Checks for black turn 
        else: 

            # One square pawn advance 
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c), (r + 1, c), self.board))
   
                    # Two square advance 
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r,c), (r + 2, c), self.board))

            if c - 1 >= 0:

                # Enemy piece to capture 
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r,c), (r + 1, c - 1), self.board))

            # Stay inside of the board, if capturing right 
            if c + 1 <= 7:

               # Enemy piece to capture 
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r,c), (r + 1, c + 1), self.board))


    """         
    Gets all the rook moves for the rook located at row, col and add these moves to the list 
    """
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])

                # Can't remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[r][c][1] != 'Q': 
                    self.pins.remove(self.pins[i])
                break
        
        # up, left, down, right
        directions = ((-1,0), (0,-1), (1,0), (0,1))
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions: 
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i 

                # Checks to see if pasting board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]

                        # Empty space is balid 
                        if endPiece == "--":
                            moves.append(Move((r,c), (endRow,endCol), self.board))

                        # Enemy piece is valid 
                        elif endPiece[0] == enemyColor: 
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
        
    """         
    Gets all the knight moves for the rook located at row, col and add these moves to the list 
    """
    def getKnightMoves(self, r , c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        # 8 ways a knight can move 
        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        
        for m in knightMoves: 
            endRow = r + m[0]
            endCol = c + m[1]
        
            # Checks to see if you stay on the board  
            if 0 <= endRow < 8 and 0 <= endCol < 8:            
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]

                    # Not an ally piece, empty or enemy piece 
                    if(endPiece[0] != allyColor):
                        moves.append(Move((r,c), (endRow,endCol), self.board))
        
    """       
    Gets all the Bishop moves for the rook located at row, col and add these moves to the list 
    """
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        # 4 diagonals
        directions = ((-1,-1), (-1,1), (1,-1), (1,1))
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions: 
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i 

                # Checks to see if pasting board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):                    
                        endPiece = self.board[endRow][endCol]

                        # Empty space is balid 
                        if endPiece == "--":
                            moves.append(Move((r,c), (endRow,endCol), self.board))

                        # Enemy piece is valid 
                        elif endPiece[0] == enemyColor: 
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    """         
    Gets all the Queen moves for the rook located at row, col and add these moves to the list 
    """
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    """         
    Gets all the king moves for the rook located at row, col and add these moves to the list, no castling  
    """
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1, -1), (1,0), (1,1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]

            # Check to see if it is out of the board 
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                # Only moves if there is empty space or enemy piece to capture 
                if(endPiece[0] != allyColor):
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow,endCol), self.board)) 
                    if allyColor == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)

    """
    Returns if the player is check
    """
    def checkForPinsAndChecks(self):
        pins = []   # Squares where the allied pinned piece is and direction pinned from
        checks = [] # Squares where enemy is applying check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # Check outward from king from king for pins and checks, kept track of pins 
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # Reset for each loop 
            
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        # 1st allied piece could be pinned         
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                    
                        # 2nd allied piece, so no pin or check possible in this direction 
                        else:
                            break

                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possiblities here in this complex conditional
                        # 1) orthogonally away from king and piece is a rook
                        # 2) diagonally away from the king and piece is a bishop
                        # 3) 1 sqaure awat diagonally from king and piece is a pawn
                        # 4) any direction and piece is a queen 
                        # 5) any direction 1 square away and piece is a king(Neccessary to preven a king to move a square controled by enemy king)
                        if(0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == "B") or (i == 1 and type == 'P' and  
                        ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or (type == 'Q') or (i == 1 and type == 'K'):  
                            
                            # No piece is blocking 
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break 

                            # Piece blocking is a pin
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break 

        #Check for knights moves
        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves: 
            endRow = startRow + m[0]
            endCol = startCol + m[1]
        
            # Checks to see if you stay on the board  
            if 0 <= endRow < 8 and 0 <= endCol < 8:            
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

class Move():
    # maps keys to value 
    # key : value 
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0} 
    rowsToTanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    '''
    Takes in a self, a tuple(r, c), tupple(r,c) and board
    '''
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False

        if(self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol # Hash function

    """
    OverLoading the equals method 
    """
    def __eq__(self, other):
        
        # Checks if both are moves 
        if isinstance(other, Move):
            return self.moveID == other.moveID

        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToTanks[r]
from checkers_graphics import *

def startcol(place):
    return (place[0]+place[1])%2*(-1) if place[0]>4 else (place[0]+place[1])%2

def is_valid(place):
    return 0<=place[0]<8 and 0<=place[1]<8

## pieces for the bot
class piece(object):
    def __init__(self, GFX, pos, col, crowned = False):
        self.col = col # color
        self.options = [] # available positions to move to
        self.det_opt = dict() # detailed options: {newpos:[#pieces took, [pieces took], got_crowned]}
        self.crowned = crowned # if the piece is crowned
        self.can_take = False # can the piece take
        self.pos = pos # current position

        self.GFX = GFX
        self.gfx = PieceGFX(
            self.pos,
            True if col == 1 else False,
            self.crowned,
            GFX
        )

    def __del__(self):
        self.gfx.remove(self.GFX)

    def __str__(self):
        if not self.crowned:
            return " 1" if self.col==1 else "-1"
        else:
            return " Q" if self.col==1 else "-Q"
    
    def update(self, board):
        '''
        Updates the following attributes of the piece:
        self.options (where can the piece move)
        self.det_opt (what pieces get taken for each move)
        self.can_take (can the piece take)
        '''
        self.options = []
        self.det_opt = dict() ## the detailed information for the options
        self.can_take = False
        if self.crowned:
            for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]: # for each direction
                self.check_take(board, direction, self.pos, [(1,1),(1,-1),(-1,1),(-1,-1)])

            if not self.can_take: # adds any direction that is not used if the piece cant take
                for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                    self.no_take(board, direction)

        else:
            # checking if the piece can take
            for direction in [(self.col, 1), (self.col, -1)]: ## checks if the piece can take in the right direction
                self.check_take(board, direction, self.pos, [(self.col, 1), (self.col, -1)])

            ## Uteskenyszer miatt
            if not self.can_take:
                for direction in [(self.col, 1), (self.col, -1)]: ## checks if the piece can take in the right direction
                    self.no_take(board, direction)

        for opt in self.det_opt.keys():
            self.options.append(opt)

        self.crowned_bonus() ## gives bonus points for crowning a piece
        self.game_end_bonus(board)


    def check_take(self, board, direction, pos, dirs, prev_dir = (9,9)):
        '''
        Checks if the piece can take in the given direction and if it can then it tries going further from there
        board: current board state
        direction: direction to check
        pos: current position of the piece
        dirs: all the directions the piece can move: used for recursion
        prev_dir: direction the piece came from (used if this is not the first step)
        '''

        if prev_dir == direction: # it cant go back in the direction it came from
            return set()
        ## checks if the piece can take in the given direction in a given board state
        check_pos = (pos[0]+direction[0], pos[1]+direction[1]) ## position to check
        if check_pos in board.keys(): #if there is a piece in that direction
            if (board[check_pos].col != self.col # and its an enemy
            and (check_pos[0]+direction[0], check_pos[1]+direction[1]) not in board.keys() # and the next place is free
            and is_valid((check_pos[0]+direction[0], check_pos[1]+direction[1]))): # and its on the board
                self.can_take = True
                newpos = (check_pos[0]+direction[0], check_pos[1]+direction[1]) # the pos the piece will land on

                if (newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1): ## treat the piece as a queen if las row reached
                    dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]

                if not self.can_take_more(board, newpos, dirs, (direction[0]*(-1),direction[1]*(-1))): ## if the piece cant take more
                    self.det_opt[newpos] = [1, [(newpos[0]-direction[0], newpos[1]-direction[1])], False] ## this is the last piece we will take
                    if board[(newpos[0]-direction[0], newpos[1]-direction[1])].crowned: # extra point if the taken piece was crowned
                        self.det_opt[newpos][0]+=1
                        
                    self.det_opt[newpos][2] = ((newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1)) ## check if it gets crowned
                    return {newpos} ## returns it as a set so it can be added later
                
                else:
                    final_positions = set()
                    for next_dir in dirs: # finding all the final positions that could be reached from here
                        dir_finals = self.check_take(board, next_dir, newpos, dirs, (direction[0]*(-1),direction[1]*(-1))) # ending positions in this direction
                        for fin in dir_finals:
                            self.det_opt[fin][0]+=1 ## adds 1 to the number of pieces that will be taken if we go to this pos
                            self.det_opt[fin][1].append((newpos[0]-direction[0], newpos[1]-direction[1]))## expands the list on how to reach it
                            if board[(newpos[0]-direction[0], newpos[1]-direction[1])].crowned: # extra point if the taken piece was crowned
                                self.det_opt[fin][0]+=1

                            if (newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1):
                                self.det_opt[fin][2]=True ## Check if the moving piece got crowned
                                

                        final_positions = final_positions | dir_finals

                return final_positions
            
        return set()

    def no_take(self,board, direction): 
        '''
        Lists all the free positions in the given direction and adds them to self.det_opt
        Only called if the piece can't take, so there is no need to check any further
        '''
        ## used to list options if the piece cant take
        ## adds the position in the given direction to options if not occupied
        newpos = (self.pos[0]+direction[0], self.pos[1]+direction[1]) ## position to check
        if newpos not in board.keys() and is_valid(newpos): ## if its not occupied or off the board
            self.det_opt[newpos] = [0, [], False]
            self.det_opt[newpos][2] = ((newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1))

    def can_take_more(self,board,pos,dirs, prev_dir = (9,9)):
        '''
        Checks if the piece can take someting from [pos] position given [board] boardstate in one of the [dirs] directions except for [prev_dir]
        This is used when checking for sequential takes, so the pos argument is not necessarily the same as self.pos
        The piece obviously cant move back where it came from, because it just took a piece from that direction, but the taken piece is still on the board (because the step was not taken yet), so forbiding that direction is done by prev_dir
        '''
         ## can the piece take sg? - used for the depth search
        for direction in dirs:
            if direction != prev_dir:
                check_pos = (pos[0]+direction[0], pos[1]+direction[1])
                if check_pos in board.keys(): #if there is a piece in that direction
                    if (board[check_pos].col != self.col # and its an enemy
                    and (check_pos[0]+direction[0], check_pos[1]+direction[1]) not in board.keys() # and the next place is free
                    and is_valid((check_pos[0]+direction[0], check_pos[1]+direction[1]))):
                        return True
                
        return False

    def crowned_bonus(self):
        '''
        gives extra points for moves that give the piece a crown
        '''
        for newpos in self.options:
            if not self.crowned and self.det_opt[newpos][2]: ## in not yet crowned and it gets crowned during moving
                self.det_opt[newpos][0]+=1 # extra point

    def game_end_bonus(self, board):
        '''
        gives +100 points to the move that ends the game
        '''
        n_enemies = sum([board[key].col!=self.col for key in board.keys()])
        for newpos in self.options:
            if len(self.det_opt[newpos][1]) == n_enemies:
                self.det_opt[newpos][0]+=100

class game(object):
    def __init__(self):
        self.GFX = CheckersGraphics()
        self.board = {pos: piece(self.GFX, pos, startcol(pos))
                       for pos in [(i,j) for i in range(8) for j in range(8) if (i+j)%2==1 and (i<3 or i>4)]}
        self.turn = 1
        self.can_move = []

    def __str__(self): # its ugly af but it works
        return "\n".join([str([str(self.board[(i,j)]) if (i,j) in self.board.keys() else " 0" for j in range(8)]).replace("'", "").replace(",", "")
                          for i in range(8)])
    
    def list_can_move(self):
        '''
        Lists all the pieces the current player can move: Refreshes the self.can_move list
        '''

        self.can_move = []
        for p in self.board.values():
            if p.col == self.turn and p.can_take: #listing all the pieces of the current player that can take
                self.can_move.append(p.pos)

        if len(self.can_move) == 0: # if the current cant take then we list all the pieces that can move
            for p in self.board.values():
                if p.col == self.turn and len(p.options)!=0: # selecting pieces that have the current player's color and have somewhere to go
                    self.can_move.append(p.pos)

    def update_all(self):
        '''
        Updates the attribures of all the pieces:
        piece.options
        piece.det_opt
        piece.can_take

        Then lists all of them that can move to self.can_move
        '''

        for p in self.board.values():
            p.update(self.board)

        self.list_can_move()

    def import_boardstate(self, board, turn):
        '''
        A function to start the game from a custom board state:
        1,-1 for normal pieces
        2,-2 for queens
        '''
        self.turn = turn
        self.board = dict()
        for i in range(8):
            for j in range(8):
                if board[i][j] != 0:
                    self.board[(i,j)] = piece(self.GFX, (i,j), int(abs(board[i][j])/board[i][j]), abs(board[i][j])>1)

        self.update_all()

    def export_boardstate(self):
        '''
        A function to export the current game state in the same format the import works on.
        '''
        exp_state = [[0 for j in range(8)] for i in range(8)]
        for piece in self.board:
            exp_state[piece[0]][piece[1]] = self.board[piece].col*(1+self.board[piece].crowned)

        return exp_state, self.turn

    def step(self, pos, newpos):
        '''
        The selected piece (pos) is moved to newpos and all the taken pieces get removed
        The piece also gets crowned if it reached the last row in the process

        Then changes the turn to the other player and updates the pieces that can move
        '''
        ## taking an enemy piece
        if self.board[pos].can_take:
            for enemy_pos in self.board[pos].det_opt[newpos][1]: # removing the piece that got taken
                del self.board[enemy_pos]

            if self.board[pos].det_opt[newpos][2]: # crown if last row reached
                self.board[pos].crowned = True
            self.board[newpos] = self.board[pos] ### we move our piece in these 3 steps:
            self.board[newpos].pos = newpos###
            del self.board[pos]###
            self.board[newpos].update(self.board) # we check if the piece can take another (it will be done elsewhere)

        ## not taking an enemy piece
        else:
            self.board[newpos] = self.board[pos] ### moving the piece in 3 steps
            self.board[newpos].pos = newpos###
            del self.board[pos]###
            if (newpos[0] == 7 and self.board[newpos].col == 1) or (newpos[0] == 0 and self.board[newpos].col == -1): # crown if last row reached
                self.board[newpos].crowned = True
        self.turn = self.turn*(-1)
        self.update_all()

    def simulate_step(self, pos, newpos):
        '''
        This function is used to create a simualtion game with the step taken.
        It is just to make 
        '''
        newgame = game() ### create a simulation where we make this step
        prev_game = self.export_boardstate()### export the game data from the current game
        newgame.import_boardstate(prev_game[0],prev_game[1])### import the data to the new game
        newgame.step(pos, newpos)### take the step
        return  newgame

    def evaluate_step(self, pos, newpos, depth):
        '''
        This function calcualtes the value of a (pos -> newpos) step based on the following:
        +1 for taking a piece
        +2 for taking a queen
        +1 for transforming into a queen
        +100 for winning the game
        (these values are calculated for each single step while calling the check_take function)
        Then it searches for the best possible answers of the player (who is the opponent of the bot using the algorithm)
        and return the value (maximum points collected by the bot) - (maximum points collected by the player)

        depth = 1 means that the player takes one step after the bot
        depth = n means that the player takes n moves and the bot n-1 other moves, because this move counts as the last one
        '''
        newgame = self.simulate_step(pos, newpos) # the bot took its step, now its the players turn in this simulation
        if newgame.can_move == []: ## if the player cant make another move
            return 100
        
        if depth == 1: ## if this is the last depth layer 
            return self.board[pos].det_opt[newpos][0] - max(
                [max([option[0] for option in newgame.board[piece].det_opt.values()]) for piece in newgame.can_move])
            ## this returns the number of pieces taken minus the maximum number of pieces the player can take with their next step
        
        worst = 1000 ## the number of points the bot will lose if the player playes their best move (this value is minimized)
        for piece in newgame.can_move: ## check every piece of the player
            for option in newgame.board[piece].options: # and their every move
                new_newgame = newgame.simulate_step(piece, option) ## simulate that move
                best = -1000 # the best score the bot can achieve in this situation (this value is maximized)
                if new_newgame.can_move == []: ## if this the player can beat the bot in their next move
                    return -100
                for pos2 in new_newgame.can_move: ## check the bots every piece to move
                    for newpos2 in new_newgame.board[pos2].options: # and their every option
                        best = max(best, new_newgame.evaluate_step(pos2, newpos2, depth-1))
                        # recursively asks for the score of the move and checks if it is the best yet

                worst = min(worst, best-newgame.board[piece].det_opt[option][0]) ## the maximum number of points to lose (multilpied by -1)

        return self.board[pos].det_opt[newpos][0] + worst

    def find_best_step(self, depth):
        '''
        Finds the best posible step given the boars state and returns it
        '''

        best = -1000
        for pos in self.can_move:
            for newpos in self.board[pos].options:
                x = self.evaluate_step(pos, newpos, depth)
                if x>best:
                    best, best_pos, best_newpos = x, pos, newpos
        
        return best_pos, best_newpos



    def player_turn(self): ## this function takes input from the user and makes changes to the board based on it
        ## obv the mode of input will be needed to be changed with the ui
        pos = '*'
        if len(self.can_move) == 0:
            print(f"GAME OVER \n {self.turn*(-1)} WINS")
            print(self)
            return 0

        print(self)
        print('---')
        while True: # cycle ensuring that the player can retry their input
            while pos not in self.can_move:
                print(f"pieces to move: {self.can_move}")
                pos = tuple(int(i) for i in input()) ## currently takes input as a two digit number: e.g. 03 for (0,3)

                if pos == (9,9): #exit button
                    return 0

            newpos = '*'
            while newpos not in self.board[pos].options:
                print(f"places to move to: {self.board[pos].options}")
                print(self.board[pos].det_opt)
                newpos = tuple(int(i) for i in input())
                if newpos in self.can_move: ## you can re-enter another pos if you want to move another piece
                    pos = newpos ##                                 ## but only if its not a sequential take
                    break

                if newpos == (9,9): # exit button
                    return 0

            if newpos in self.can_move: ## this makes so that you can enter the newpos for the changed pos
                continue## goes to asking for the newpos again bc pos = newpos as of now

            self.step(pos, newpos) # the player takes their step
                
            break

        return 1

    def bot_turn(self):
        pos = '*'
        if len(self.can_move) == 0:
            print(f"GAME OVER \n {self.turn*(-1)} WINS")
            print(self)
            return 0

        print(self)
        print('---')

        pos, newpos = self.find_best_step(2)

        print(pos, newpos)

        pc = self.board[pos].gfx
        motion = GFXMotion(pc, pos, newpos)
        self.GFX.motion_cue.append(motion)
        self.step(pos, newpos) # the player takes their step
        return 1

    def game_start(self):
        game_state = 1
        self.update_all()
        while game_state != 0:
            print(f"Current player: {self.turn}")
            game_state = self.bot_turn()
            
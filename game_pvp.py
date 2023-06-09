from checkers_graphics import *
from random import randint
from player_movement import MovingPiece

def startcol(place): ## A function to determine the color of each piece when initializing the board
    return (place[0]+place[1])%2*(-1) if place[0]>4 else (place[0]+place[1])%2

def is_valid(pos, board, start): ## a place is valid if its not occupied or off the board
    if pos not in board or pos == start: ## but it is valid, if it was the original position of a piece is a recursion (it can move in a circle)
        return 0<=pos[0]<8 and 0<=pos[1]<8
    return False

class Piece():
    '''
    Represents a piece on the board.

    Attributes:
        GFX: Graphics object.
        pos (tuple): Current position of the piece.
        col (int): Color of the piece (-1 for black, 1 for white).
        crowned (bool): Indicates if the piece is crowned.
        options (list): Available positions to move to.
        det_opt (dict): Detailed options for each move.
        can_take (bool): Indicates if the piece can take another piece.
        piece_gfx: Graphics object for the piece.

    Methods:
        __init__: Initializes a new piece object.
        __str__: Returns a string representation of the piece.
        update: Updates the attributes of the piece.
        check_take: Checks if the piece can take in a given direction.
        no_take: Lists all the free positions in a given direction.
        can_take_more: Checks if the piece can take additional pieces.
        crowned_bonus: Gives bonus points for crowning a piece.
        game_end_bonus: Gives bonus points for winning the game.
    '''

    def __init__(self, GFX, pos, col, crowned = False):
        self.col = col # color
        self.options = [] # available positions to move to
        self.det_opt = dict() # detailed options: {newpos:[value, [pieces took], got_crowned, [path]]} 
        # value = #pieces took + 1 if it crowns the piece + 100 if the move wins the game
        self.crowned = crowned # if the piece is crowned
        self.can_take = False # can the piece take
        self.pos = pos # current position

        self.GFX = GFX
        self.piece_gfx = PieceGFX(
            self.pos,
            True if col == 1 else False,
            self.crowned,
            GFX
        )

    # def __del__(self):
    #     self.piece_gfx.remove_from(self.GFX)

    def __str__(self):
        '''
        The gamestate is also printed in the terminal when running the game
        '''
        if not self.crowned:
            return " 1" if self.col==1 else "-1"
        else:
            return " Q" if self.col==1 else "-Q"
    
    def update(self, board):
        '''
        Updates the following attributes of the piece:
        self.options (where can the piece move)
        self.det_opt (what pieces get taken for each move, what positions are visited, the value of the move, and if the piece got crowned while moving)
        self.can_take (can the piece take)
        '''
        self.options = []
        self.det_opt = dict() ## the detailed information for the options
        self.can_take = False
        if self.crowned:
            for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]: # for each direction
                self.check_take(board, direction, self.pos, [(1,1),(1,-1),(-1,1),(-1,-1)], self.pos)

            if not self.can_take: # adds any direction that is not used if the piece cant take
                for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                    self.no_take(board, direction)

        else:
            # checking if the piece can take
            for direction in [(self.col, 1), (self.col, -1)]: ## checks if the piece can take in the right direction
                self.check_take(board, direction, self.pos, [(self.col, 1), (self.col, -1)], self.pos)

            ## it adds its neighbors only if it can't take
            if not self.can_take:
                for direction in [(self.col, 1), (self.col, -1)]: ## checks if the piece can take in the right direction
                    self.no_take(board, direction)

        for opt in self.det_opt.keys(): ## adds all the options to the self.options list
            self.options.append(opt)

        self.crowned_bonus() ## gives bonus points for crowning a piece
        self.game_end_bonus(board) ## gives bonus points for winning the game


    def check_take(self, board, direction, pos, dirs, start, already_taken = []):
        '''
        Checks if the piece can take in the given direction and if it can then it tries going further from there
        board: current board state
        direction: direction to check
        pos: current position of the piece
        dirs: all the directions the piece can move: used for recursion
        already_taken: pieces that got taken - you cant take them a second time
        start: the place where the piece started from (that place is not counted as occupied when checking if a piece is there on the board)
        '''
        check_pos = (pos[0]+direction[0], pos[1]+direction[1]) ## position to check

        if check_pos in already_taken: ## it cant take the same piece twice 
            return set() # (and it also cant make a normal move after taking)

        ## checks if the piece can take in the given direction in a given board state
        if check_pos in board.keys(): #if there is a piece in that direction
            if (board[check_pos].col != self.col # and its an enemy
            and is_valid((check_pos[0]+direction[0], check_pos[1]+direction[1]), board.keys(), start)): # and its on the board
                self.can_take = True
                already_taken_new = already_taken.copy()
                already_taken_new.append(check_pos)
                newpos = (check_pos[0]+direction[0], check_pos[1]+direction[1]) # the pos the piece will land on

                if (newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1): ## treat the piece as a queen if las row reached
                    dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]

                if not self.can_take_more(board, newpos, dirs, start, already_taken_new): ## if the piece cant take more
                    self.det_opt[newpos] = [1, [(newpos[0]-direction[0], newpos[1]-direction[1])], False, [newpos]] ## this is the last piece we will take
                    if board[(newpos[0]-direction[0], newpos[1]-direction[1])].crowned: # extra point if the taken piece was crowned
                        self.det_opt[newpos][0]+=1.5
                        
                    self.det_opt[newpos][2] = ((newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1)) ## check if it gets crowned
                    return {newpos} ## returns it as a set so it can be added later
                
                else:
                    final_positions = set()
                    for next_dir in dirs: # finding all the final positions that could be reached from here
                        dir_finals = self.check_take(board, next_dir, newpos, dirs, start, already_taken_new) # ending positions in this direction
                        for fin in dir_finals:
                            self.det_opt[fin][0]+=1 ## adds 1 to the number of pieces that will be taken if we go to this pos
                            self.det_opt[fin][3].append(newpos)## expands the list of visited places
                            self.det_opt[fin][1].append((newpos[0]-direction[0], newpos[1]-direction[1]))## expands the list of the taken pieces
                            if board[(newpos[0]-direction[0], newpos[1]-direction[1])].crowned: # extra point if the taken piece was crowned
                                self.det_opt[fin][0]+=1.5

                            if (newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1):
                                self.det_opt[fin][2]=True ## Check if the moving piece got crowned
                                

                        final_positions = final_positions | dir_finals

                return final_positions
            
        return set()

    def no_take(self,board, direction): 
        '''
        Lists all the free positions in the given direction and adds them to self.det_opt.
        Only called if the piece can't take.
        '''
        newpos = (self.pos[0]+direction[0], self.pos[1]+direction[1]) ## position to check
        if is_valid(newpos, board.keys(), (9,9)): ## if its not occupied or off the board; (9,9) because there is no need to check for circles in this case
            self.det_opt[newpos] = [0, [], False]
            self.det_opt[newpos][2] = ((newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1))

    def can_take_more(self,board,pos,dirs,start, already_taken = []):
        '''
        Checks if the piece can take someting from [pos] position given [board] boardstate in one of the [dirs], but it can't take pieces in [already_taken], because they were taken in one of the previous steps.
        This is used when checking for sequential takes, so the pos argument is not necessarily the same as self.pos, which is the starting point.
        '''
        for direction in dirs: #checks every direction
            check_pos = (pos[0]+direction[0], pos[1]+direction[1])
            if check_pos not in already_taken and check_pos in board.keys(): #if there is a piece in that direction that we didnt take yet
                if (board[check_pos].col != self.col # and its an enemy
                and is_valid((check_pos[0]+direction[0], check_pos[1]+direction[1]), board.keys(), start)): ## and the next place is a valid place to go to (not occupied or off the board)
                    return True
                    
        return False

    def crowned_bonus(self):
        '''
        Gives an extra 1.5 points for moves that give the piece a crown
        '''
        for newpos in self.options:
            if not self.crowned and self.det_opt[newpos][2]: ## in not yet crowned and it gets crowned during moving
                self.det_opt[newpos][0]+=1.5 # extra point

    def game_end_bonus(self, board):
        '''
        gives +100 points to the move that ends the game
        '''
        n_enemies = sum([board[key].col!=self.col for key in board.keys()])
        for newpos in self.options:
            if len(self.det_opt[newpos][1]) == n_enemies:
                self.det_opt[newpos][0]+=100

class game():
    '''
    The main object of the game.

    Attributes:
        GFX: Graphics object.
        kill_move_thread (list): Flag for terminating the move thread.
        board (dict): Dictionary representing the board state.
        turn (int): Current player's turn (-1 for black, 1 for white).
        can_move (list): List of pieces that can move in the current turn.
        mode (str): Game mode ('bvb' for player vs. bot, 'pvp' for player vs. player).

    Methods:
        __init__: Initializes a new game object.
        __str__: Returns a string representation of the board state.
        list_can_move: Lists all the pieces the current player can move.
        update_all: Updates the attributes of all the pieces.
        import_boardstate: Starts the game from a custom board state.
        export_boardstate: Exports the current game state.
        step: Moves a piece to a new position and updates the board.
        simulate_step(pos, newpos):
            This function is used to create a simulation game with the step taken.
        evaluate_step(pos, newpos, depth):
            This function calculates the value of a (pos -> newpos) step based on the game state and depth.
        find_best_step(depth):
            Finds the best possible step given the board state and returns it.
        player_turn():
            Takes input from the user and makes changes to the board based on it.
        bot_turn():
            Searches for the best step to take and then moves the bot accordingly.
        move():
            Executes a move in the game based on the current player and mode.

    '''

    def __init__(self, mode='bvb'):
        self.GFX = CheckersGraphics()
        self.kill_move_thread: list[bool, ] = [False, ]

        self.board = {pos: Piece(self.GFX, pos, startcol(pos))
                       for pos in [(i,j) for i in range(8) for j in range(8) if (i+j)%2==1 and (i<3 or i>4)]}
        self.turn = 1 ## values: -1, 1: which players turn is it
        self.can_move = [] ## pieces that can move in the current turn
        self.mode = mode ## the gamemode: player vs player/ player vs bot/ bot vs bot

        self.game_state = 1 ## values: 1 if the game is running, 0 if it is over
        self.update_all()

    def __str__(self): # prints the board in the terminal
        return "\n".join([str([str(self.board[(i,j)]) if (i,j) in self.board.keys() else " 0" for j in range(8)]).replace("'", "").replace(",", "")
                          for i in range(8)])
    
    def list_can_move(self):
        '''
        Lists all the pieces the current player can move by refreshing the self.can_move list
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

        Then lists all of those that can move into self.can_move
        '''
        for p in self.board.values():
            if self.kill_move_thread[0]: return
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
                    self.board[(i,j)] = Piece(self.GFX, (i,j), int(abs(board[i][j])/board[i][j]), abs(board[i][j])>1)

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
        The selected piece (pos) is moved to newpos and all the taken pieces get removed.
        The piece also gets crowned if it reached the last row in the process.

        Then changes the turn to the other player and updates the pieces that can move

        Game loop:
            calls self.move() that acts based on what the type of the current player is:
                if it is a player, then it takes an input, then updates the board
                if it is a bot, then it calculates an optimal step, takes it and then updates the board
        '''

        ## the part responsibe for the graphics
        piece_gfx = self.board[pos].piece_gfx
        if (len(self.board[pos].det_opt[newpos][1]) == 0):
            motion = GFXMotion(piece_gfx, pos, newpos)
            self.GFX.motion_cue.append(motion)
        else:
            temp_pos = pos
            for captured_pos in self.board[pos].det_opt[newpos][1][::-1]:
                temp_newpos = (2*captured_pos[0] - temp_pos[0],
                               2*captured_pos[1] - temp_pos[1])
                self.GFX.destroy_cue.append(self.board[captured_pos].piece_gfx)
                motion = GFXMotion(piece_gfx, temp_pos, temp_newpos)
                self.GFX.motion_cue.append(motion)
                temp_pos = temp_newpos

        if self.board[pos].can_take:
            for enemy_pos in self.board[pos].det_opt[newpos][1]: # removing the piece that got taken
                del self.board[enemy_pos]

            if self.board[pos].det_opt[newpos][2]: # crown if last row reached
                self.board[pos].crowned = True
                self.board[pos].piece_gfx.crowned = True
            
            if newpos!= pos: # so we can move in a circle
                self.board[newpos] = self.board[pos] ### we move our piece in these 3 steps:
                self.board[newpos].pos = newpos###
                del self.board[pos]###
            self.board[newpos].update(self.board) # we check if the piece can take another 

        ## not taking an enemy piece
        else:
            self.board[newpos] = self.board[pos] ### moving the piece in 3 steps
            self.board[newpos].pos = newpos###
            del self.board[pos]###
            if (newpos[0] == 7 and self.board[newpos].col == 1) or (newpos[0] == 0 and self.board[newpos].col == -1): # crown if last row reached
                self.board[newpos].crowned = True
                self.board[newpos].piece_gfx.crowned = True
        self.turn = self.turn*(-1)
        self.update_all()

    def simulate_step(self, pos, newpos):
        '''
        This function is used to create a simualtion game with the step taken.
        '''
        newgame = game() ### create a simulation where we make this step
        prev_game = self.export_boardstate()### export the game data from the current game
        newgame.import_boardstate(prev_game[0],prev_game[1])### import the data to the new game
        newgame.kill_move_thread = self.kill_move_thread
        newgame.step(pos, newpos)### take the step
        return  newgame

    def evaluate_step(self, pos, newpos, depth):
        '''
        This function calcualtes the value of a (pos -> newpos) step based on the following:
        +1 for taking a piece
        +2.5 for taking a queen
        +1.5 for transforming into a queen
        +100 for winning the game
        (these values are calculated for each single step while calling the check_take function)
        Then it searches for the best possible answers of the player (who is the opponent of the bot using the algorithm)
        and return the value (maximum points collected by the bot) - (maximum points collected by the player)

        depth = 1 means that the player takes one step after the bot
        depth = n means that the player takes n moves and the bot n-1 other moves after this
        '''
        if self.kill_move_thread[0]: return 0
        newgame = self.simulate_step(pos, newpos) # the bot took its step, now its the players turn in this simulation
        if newgame.can_move == []: ## if the player cant make another move
            return 100
        
        if depth == 1: ## if this is the last depth layer 
            return self.board[pos].det_opt[newpos][0] - max(
                [max([option[0] for option in newgame.board[piece].det_opt.values()]) for piece in newgame.can_move])
            # this returns the number of pieces taken minus the maximum number of pieces the player can take with their next step

        worst = 1000 ## the number of points the bot will lose if the player playes their best move (this value is minimized)
        for piece in newgame.can_move: ## check every piece of the player
            sleep(0.001)
            for option in newgame.board[piece].options: # and their every move
                if self.kill_move_thread[0]: return 0
                new_newgame = newgame.simulate_step(piece, option) ## simulate that move
                best = -1000 # the best score the bot can achieve in this situation (this value is maximized)
                if new_newgame.can_move == []: ## if this the player can beat the bot in their next move
                    return -100
                for pos2 in new_newgame.can_move: ## check the bots every piece to move
                    if self.kill_move_thread[0]: return 0 
                    for newpos2 in new_newgame.board[pos2].options: # and their every option
                        best = max(best, new_newgame.evaluate_step(pos2, newpos2, depth-1))
                        # recursively asks for the score of the move and checks if it is the best yet

                worst = min(worst, best-newgame.board[piece].det_opt[option][0]) ## the maximum number of points to lose (multilpied by -1)

        return self.board[pos].det_opt[newpos][0] + worst

    def find_best_step(self, depth):
        '''
        in: depth: how far should it search
        out: suggested step: pos, newpos
        Finds the best posible step given the boars state and returns it
        If there are multiple best states, it chooses randomly.
        '''

        best = -1000
        best_list = []
        for pos in self.can_move: ## all pieces that can move
            for newpos in self.board[pos].options: ## and where they can move
                if self.kill_move_thread[0]: return (0,0), (0,0)
                x = self.evaluate_step(pos, newpos, depth) ### see the value of the step
                if x>best:## if its better than everything until now it will be the only element of the best list
                    best = x
                    best_list = [[pos,newpos]]

                elif x==best: ## if it is as good as everything until now, it is added to the best list
                    best_list.append([pos, newpos])
        
        c = randint(0, len(best_list)-1) ## choose a random step from the best posibble steps
        
        return best_list[c][0], best_list[c][1]

    def player_turn(self):
        '''
        This function takes input from the user and makes changes to the board based on it while making the necessary changes on the UI
        '''
        pos = '*'
        if len(self.can_move) == 0:
            print(f"GAME OVER \n {self.turn*(-1)} WINS")
            print(self)
            return 0

        print(self)
        print('---')
        print(self.can_move)

        piece = self.board[self.can_move[0]]
        if piece.can_take: forced_capture = True
        else: forced_capture = False
        
        while True:
            pos = (-1,-1)
            self.GFX.possible_choices = self.can_move
            while pos not in self.can_move:
                if self.kill_move_thread[0]: return
                # print(f"{pos} waiting for pos, {self.can_move}")
                pos = self.GFX.clicked_pos
                # print(f"pieces to move: {self.can_move}")
                sleep(0.01)
            self.GFX.possible_choices = []
            self.GFX.clicked_pos = (-1,-1)
            print(pos)

            mpiece = MovingPiece(self, self.board[pos])
            mpiece.find_steps()

            self.GFX.phantom_pieces = mpiece.possible_steps
            self.GFX.active_piece = mpiece.piece.piece_gfx

            newpos = (-1, -1)
            while newpos == (-1, -1):
                if self.kill_move_thread[0]: return
                # print(f"{pos}, waiting for newpos")
                newpos = self.GFX.clicked_pos
                sleep(0.01)
            self.GFX.clicked_pos = (-1, -1)
            print(f"{pos}, {newpos}")

            self.GFX.phantom_pieces = []
            self.GFX.active_piece = None

            if newpos not in mpiece.possible_steps:
                continue

            mpiece.make_step(newpos)
            if not forced_capture:
                self.turn *= -1
                self.update_all()
                return 
            break
        
        mpiece.find_steps()
        while len(mpiece.possible_steps) != 0:
            self.GFX.phantom_pieces = mpiece.possible_steps
            self.GFX.active_piece = mpiece.piece.piece_gfx

            newpos = (-1, -1)
            while not (newpos in mpiece.possible_steps):
                if self.kill_move_thread[0]: return
                newpos = self.GFX.clicked_pos
                sleep(0.01)
            self.GFX.clicked_pos = (-1, -1)

            mpiece.make_step(newpos)
            mpiece.find_steps()

        self.turn *= -1
        self.update_all()
        
        self.GFX.active_piece = None
        self.GFX.phantom_pieces = []
        return

    def bot_turn(self):
        '''
        This function searches for the best step to take and the moves the bot accordingly
        '''

        pos = '*'
        if len(self.can_move) == 0:
            print(f"GAME OVER \n {self.turn*(-1)} WINS")
            print(self)
            return 0

        print(self)
        pos, newpos = self.find_best_step(3)
        if self.kill_move_thread[0]: return 1
        print(pos, newpos)
        print(self.board[pos].det_opt[newpos])

        self.step(pos, newpos) # the player takes their step
        return 1

    def move(self):
        print(f"Current player: {self.turn}")
        if len(self.can_move) == 0:
            self.game_state = 0
            print(f"GAME OVER \n {self.turn*(-1)} WINS")
            return

        if self.mode == 'pvp':
            self.game_state = self.player_turn()

        elif self.mode == 'pvb':
            print(f"Current player: {self.turn}")
            if self.turn == 1:
                self.game_state = self.player_turn()
            elif self.turn == -1:
                self.game_state = self.bot_turn()
        
        elif self.mode == 'bvb':
            print(f"Current player: {self.turn}")
            self.game_state = self.bot_turn()

def startcol(place):
    return (place[0]+place[1])%2*(-1) if place[0]>4 else (place[0]+place[1])%2

def is_valid(place):
    return 0<=place[0]<8 and 0<=place[1]<8

def between(pos, newpos):
    return (newpos[0]-pos[0], newpos[1]-pos[1])

class piece(object):
    def __init__(self, pos, col, crowned = False):
        self.col = col # color
        self.options = [] # available positions
        self.det_opt = dict() # detailed options: [#pieces took, [pieces took], got_crowned]
        self.crowned = crowned # if the piece is crowned
        self.can_take = False # can the ciece take
        self.pos = pos # current position

    def __str__(self):
        if not self.crowned:
            return " 1" if self.col==1 else "-1"
        else:
            return " Q" if self.col==1 else "-Q"
    
    def update(self, board):
        ## updates can_take and options attributes
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
                    self.det_opt[newpos][2] = ((newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1)) ## check if it gets crowned
                    return {newpos} ## returns it as a set so it can be added later
                
                else:
                    final_positions = set()
                    for next_dir in dirs: # finding all the final positions that could be reached from here
                        dir_finals = self.check_take(board, next_dir, newpos, dirs, (direction[0]*(-1),direction[1]*(-1))) # ending positions in this direction
                        for fin in dir_finals:
                            self.det_opt[fin][0]+=1 ## adds 1 to the number of pieces that will be taken if we go to this pos
                            self.det_opt[fin][1].append((newpos[0]-direction[0], newpos[1]-direction[1]))## expands the list on how to reach it
                            if (newpos[0]==0 and self.col == -1) or (newpos[0]==7 and self.col == 1):
                                self.det_opt[fin][2]=True ## Check it if got crowned

                        final_positions = final_positions | dir_finals

                return final_positions
            
        return set()

    def no_take(self,board, direction): ## used to list options if the piece cant take
        ## adds the position in the given direction to options if not occupied
        check_pos = (self.pos[0]+direction[0], self.pos[1]+direction[1]) ## position to check
        if check_pos not in board.keys() and is_valid(check_pos): ## if its not occupied or off the board
            self.det_opt[check_pos] = [1, [check_pos]]

    def can_take_more(self,board,pos,dirs, prev_dir = (9,9)): ## can the piece take sg? - used for the depth search
        for direction in dirs:
            if direction != prev_dir:
                check_pos = (pos[0]+direction[0], pos[1]+direction[1])
                if check_pos in board.keys(): #if there is a piece in that direction
                    if (board[check_pos].col != self.col # and its an enemy
                    and (check_pos[0]+direction[0], check_pos[1]+direction[1]) not in board.keys() # and the next place is free
                    and is_valid((check_pos[0]+direction[0], check_pos[1]+direction[1]))):
                        return True
                
        return False

class game(object):
    def __init__(self):
        # self.board = np.array([[ (i+j)%2*(-1) if j>4 else (i+j)%2 if j<3 else 0 for i in range(8)] for j in range(8)])
        self.board = {pos: piece(pos, startcol(pos))
                       for pos in [(i,j) for i in range(8) for j in range(8) if (i+j)%2==1 and (i<3 or i>4)]}
        self.turn = 1
        self.can_move = []

    def __str__(self): # its ugly af but it works
        return "\n".join([str([str(self.board[(i,j)]) if (i,j) in self.board.keys() else " 0" for j in range(8)]).replace("'", "").replace(",", "")
                          for i in range(8)])
    
    def update_all(self):
        for p in self.board.values():
            p.update(self.board)

    def add_custom_boardstate(self, board, turn): ## 1,-1 for normal pieces; 2,-2 for Queens
        self.turn = turn
        self.board = dict()
        for i in range(8):
            for j in range(8):
                if board[i][j] != 0:
                    self.board[(i,j)] = piece((i,j), int(abs(board[i][j])/board[i][j]), abs(board[i][j])>1)

        self.update_all()

    def list_can_move(self):
        self.can_move = []
        for p in self.board.values():
            if p.col == self.turn and p.can_take: #listing all the pieces of the current player that can take
                self.can_move.append(p.pos)

        if len(self.can_move) == 0: # if the current cant take then we list all the pieces that can move
            for p in self.board.values():
                if p.col == self.turn and len(p.options)!=0: # selecting pieces that have the current player's color and have somewhere to go
                    self.can_move.append(p.pos)

    def step(self, pos, newpos):
        ## taking an enemy piece
        if self.board[pos].can_take:
            print(self.board[pos].det_opt)
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


                

    def player_turn(self): ## this function takes input from the user and makes changes to the board based on it
        ## obv the mode of input will be needed to be changed with the ui
        pos = '*'
        self.update_all()
        self.list_can_move()
        if len(self.can_move) == 0:
            print(f"GAME OVER \n {self.turn*(-1)} WINS")
            print(self)
            return 0

        print(self)
        print('---')
        sequential_take = False
        while True: # cycle ensuring that the player takes multiple times if needed
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
                if newpos in self.can_move and not sequential_take: ## you can re-enter another pos if you want to move another piece
                    pos = newpos ##                                 ## but only if its not a sequential take
                    break

                if newpos == (9,9): # exit button
                    return 0

            if newpos in self.can_move: ## this makes so that you can enter the newpos for the changed pos
                continue## goes to asking for the newpos again bc pos = newpos as of now

            self.step(pos, newpos) # the player takes their step

            if abs(pos[0]-newpos[0])>1 and self.board[newpos].can_take: ## the player took a piece and can still take
                print(self)
                sequential_take = True ## this is so that the player cant change the piece they are moving
                pos = newpos
                self.can_move = [pos] ## this is so that the player cant change the piece they are moving
                continue
                
            break

        self.turn = self.turn*(-1)
        return 1

    def game_start(self):
        game_state = 1
        while game_state != 0:
            print(f"Current player: {self.turn}")
            game_state = self.player_turn()
            
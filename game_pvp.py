def startcol(place):
    return (place[0]+place[1])%2*(-1) if place[0]>4 else (place[0]+place[1])%2

def is_valid(place):
    return 0<=place[0]<8 and 0<=place[1]<8

class piece(object):
    def __init__(self, pos, col, crowned = False):
        self.col = col
        self.options = []
        self.crowned = crowned
        self.can_take = False
        self.pos = pos

    def __str__(self):
        if not self.crowned:
            return " 1" if self.col==1 else "-1"
        else:
            return " Q" if self.col==1 else "-Q"
    
    def update(self, board):
        self.options = []
        self.can_take = False
        if self.crowned:
            for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                self.check_take_dir(board, direction)

            if not self.can_take:
                for direction in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                    self.add_all_dir(board, direction)

        else:
            # checking if the piece can take
            # to the right (self.col adds the right direction vertically)
            if ((self.pos[0]+self.col, self.pos[1]+1) in board.keys() # there is sg to take
            and board[(self.pos[0]+self.col, self.pos[1]+1)].col != self.col  # its an opposing piece
            and (self.pos[0]+2*self.col, self.pos[1]+2) not in board.keys() # the next pos is not occupied
            and is_valid((self.pos[0]+2*self.col, self.pos[1]+2))): # and its not off the board
                self.options.append((self.pos[0]+2*self.col, self.pos[1]+2))
                self.can_take = True

            # same to the left
            if ((self.pos[0]+self.col, self.pos[1]-1) in board.keys()
            and board[(self.pos[0]+self.col, self.pos[1]-1)].col != self.col
            and (self.pos[0]+2*self.col, self.pos[1]-2) not in board.keys()
            and is_valid((self.pos[0]+2*self.col, self.pos[1]-2))):
                self.options.append((self.pos[0]+2*self.col, self.pos[1]-2))
                self.can_take = True

            ## Uteskenyszer miatt
            if not self.can_take:
                if ((self.pos[0]+self.col, self.pos[1]+1) not in board.keys() # there is nothing to the right
                and is_valid((self.pos[0]+self.col, self.pos[1]+1))): # and its not off the board
                    self.options.append((self.pos[0]+self.col, self.pos[1]+1))

                # same to the left
                if ((self.pos[0]+self.col, self.pos[1]-1) not in board.keys()
                and is_valid((self.pos[0]+self.col, self.pos[1]-1))):
                    self.options.append((self.pos[0]+self.col, self.pos[1]-1))

    def check_take_dir(self, board, direction):
        check_pos = (self.pos[0]+direction[0], self.pos[1]+direction[1])
        while check_pos not in board.keys() and is_valid(check_pos):
            check_pos = (check_pos[0]+direction[0], check_pos[1]+direction[1]) #iterating until  we hit a piece or a wall

        if not is_valid(check_pos):
            return

        if (board[check_pos].col != self.col 
            and (check_pos[0]+direction[0], check_pos[1]+direction[1]) not in board.keys()): # if the next space is free and we hit an enemy piece
            self.can_take = True
            self.options.append((check_pos[0]+direction[0], check_pos[1]+direction[1]))

    def add_all_dir(self, board, direction):
        check_pos = (self.pos[0]+direction[0], self.pos[1]+direction[1])
        while check_pos not in board.keys() and is_valid(check_pos):
            self.options.append(check_pos)
            check_pos = (check_pos[0]+direction[0], check_pos[1]+direction[1])

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

    def player_step(self, pos, newpos):
        ## refusing illegal moves
        if pos not in self.can_move:
            return
        
        if newpos not in self.board[pos].options:
            return
        
        ## taking an enemy piece
        if self.board[pos].can_take:
            direction = 1 if pos[1] < newpos[1] else -1 
            del self.board[(newpos[0] - self.board[pos].col, newpos[1] - direction)] # removing the piece between the two places
            self.board[newpos] = self.board[pos] ### we move the piece in these 3 steps:
            self.board[newpos].pos = newpos###
            del self.board[pos]###
            if (newpos[0] == 7 and self.board[newpos].col == 1) or (newpos[0] == 0 and self.board[newpos].col == -1): # crown if last row reached
                self.board[newpos].crowned = True
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
                newpos = tuple(int(i) for i in input()) 
                if newpos in self.can_move and not sequential_take: ## you can re-enter another pos if you want to move another piece
                    pos = newpos ##                                 ## but only if its not a sequential take
                    break

                if newpos == (9,9): # exit button
                    return 0

            if newpos in self.can_move: ## this makes so that you can enter the newpos for the changed pos
                continue

            self.player_step(pos, newpos)

            if abs(pos[0]-newpos[0])>1 and self.board[newpos].can_take: ## the player took a piece and can still take
                print(self)
                sequential_take = True
                pos = newpos
                self.can_move = [pos]
                continue
                
            break

        self.turn = self.turn*(-1)
        return 1

    def game_start(self):
        game_state = 1
        while game_state != 0:
            print(f"Current player: {self.turn}")
            game_state = self.player_turn()
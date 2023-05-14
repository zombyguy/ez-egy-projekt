from checkers_graphics import *

class MovingPiece:
    def __init__(self,
                 G: 'game',
                 piece: 'Piece'):
        self.piece = piece
        self.G = G
        self.possible_steps = []
        self.captured_poss = []

    def find_steps(self):
        if self.piece.crowned: dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
        else: dirs = [(self.piece.col, 1), (self.piece.col, -1)]

        self.possible_steps = []
        pos = self.piece.pos
        for dir in dirs:
            enemypos = (pos[0] + dir[0], pos[1] + dir[1])
            if not (enemypos in self.G.board): continue
            enemypiece = self.G.board[enemypos]
            
            if not (enemypiece.col != self.piece.col): continue
            newpos = (pos[0] + 2*dir[0], pos[1] + 2*dir[1])
            if valid_pos(newpos, self.G.board, pos):
                self.possible_steps.append(newpos)

    def make_step(self, newpos):
        self.forced_to_move = True
        motion = GFXMotion(self.piece.piece_gfx,
                           self.piece.pos,
                           newpos)
        self.G.GFX.motion_cue.append(motion)
        jump_pos = ((self.piece.pos[0] + newpos[0])//2,
                    (self.piece.pos[1] + newpos[1])//2)
        self.G.GFX.destroy_cue.append(self.G.board[jump_pos].piece_gfx)
        self.G.board.pop(jump_pos)

        self.G.board.pop(self.piece.pos)
        self.piece.pos = newpos
        self.G.board[newpos] = self.piece

def valid_pos(pos, board, start): 
    if pos not in board or pos == start: 
        return 0<=pos[0]<8 and 0<=pos[1]<8
    return False
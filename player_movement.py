from checkers_graphics import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_pvp import game, Piece

class MovingPiece:
    def __init__(self,
                 G: 'game',
                 piece: 'Piece'):
        self.piece = piece
        self.G = G
        self.possible_steps = []
        self.captured_poss = []
        self.forced_to_take = piece.can_take

    def find_steps(self):
        if self.piece.crowned: dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
        else: dirs = [(self.piece.col, 1), (self.piece.col, -1)]

        self.possible_steps = []
        pos = self.piece.pos
        for dir in dirs:
            if self.forced_to_take:
                enemypos = (pos[0] + dir[0], pos[1] + dir[1])
                if not (enemypos in self.G.board): continue
                enemypiece = self.G.board[enemypos]
                
                if not (enemypiece.col != self.piece.col): continue
                newpos = (pos[0] + 2*dir[0], pos[1] + 2*dir[1])
                if valid_pos(newpos, self.G.board):
                    self.possible_steps.append(newpos)
            else:
                newpos = (pos[0] + dir[0], pos[1] + dir[1])
                if (not (newpos in self.G.board)) and valid_pos(newpos, self.G.board):
                    self.possible_steps.append(newpos)

    def make_step(self, newpos):
        # self.forced_to_move = True
        motion = GFXMotion(self.piece.piece_gfx,
                           self.piece.pos,
                           newpos)
        # self.G.GFX.motion_cue.append(motion)
        
        if self.forced_to_take:
            jump_pos = ((self.piece.pos[0] + newpos[0])//2,
                        (self.piece.pos[1] + newpos[1])//2)
            self.G.GFX.destroy_cue.append(self.G.board[jump_pos].piece_gfx)
            self.G.board.pop(jump_pos)

        while py5.has_thread('gfx_motion'):
            pass
        py5.launch_thread(motion.animate, 'gfx_motion')

        self.G.board.pop(self.piece.pos)
        self.piece.pos = newpos
        self.G.board[newpos] = self.piece

def valid_pos(pos, board): 
    if pos not in board: 
        return 0<=pos[0]<8 and 0<=pos[1]<8
    return False
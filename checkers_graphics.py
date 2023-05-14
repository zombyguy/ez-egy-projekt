import py5
from collections import deque 
from typing import Tuple, Deque

TILE_SIZE = 40
GAME_WINDOW_SIZE = TILE_SIZE * 10
EVEN_CELL_COLOR = (248,231,179)
ODD_CELL_COLOR = (170,76,35)

# GFX_TILESET = [[Tile((i+1.5)*TILE_SIZE, (j+1.5)*TILE_SIZE, EVEN_CELL_COLOR if ((i+j) % 2) == 0 else ODD_CELL_COLOR) 
#             for i in range(8)] for j in range(8)]

PIECE_SCALE = 0.8
PIECE_SIZE = TILE_SIZE * PIECE_SCALE
P1_COLOR = (255, 255, 255)
P2_COLOR = (0,0,0)

# GFX_PIECES = []

# mozgáshoz szükséges globális változók
# IN_MOTION = False

class CheckersGraphics():
    def __init__(self):
        # global TILE_SIZE, GAME_WINDOW_SIZE, PIECE_SCALE, PIECE_SIZE
        # global EVEN_CELL_COLOR, ODD_CELL_COLOR, P1_COLOR, P2_COLOR

        self.tileset = [[TileGFX((i+1.5)*TILE_SIZE, (j+1.5)*TILE_SIZE, EVEN_CELL_COLOR if ((i+j) % 2) == 0 else ODD_CELL_COLOR) 
                        for i in range(8)] for j in range(8)]
        self.pieces = []

        self.in_motion = False
        self.motion_cue: Deque[GFXMotion] = deque()
        self.current_motion: GFXMotion = None
        self.destroy_cue: Deque[PieceGFX] = deque()

        self.clicked_pos: tuple[int,int] = (-1,-1)
        self.active_piece: PieceGFX = None
        self.phantom_pieces: list[tuple[int, int]] = list() 

class TileGFX:
    def __init__(self, x,y, color = (255,255,255)):
        self.x = x
        self.y = y 
        self.color = color
    
class PieceGFX:
    def __init__(self, 
                 pos: tuple[int, int], 
                 P1: bool, 
                 crowned: bool, 
                 GFX: CheckersGraphics):
        self.x = (pos[1]+1.5)*TILE_SIZE
        self.y = (pos[0]+1.5)*TILE_SIZE
        self.p1 = P1
        self.crowned = crowned
        self.GFX = GFX
        GFX.pieces.append(self)

    def destroy(self):
        self.GFX.pieces.remove(self)

    def draw(self) -> None:
        # kell a kinézetváltás, ha dáma
        if self.p1: color = P1_COLOR
        else: color = P2_COLOR
        py5.fill(*color)
        py5.circle(self.x, self.y, PIECE_SIZE)
        if self.crowned:
            py5.fill(255,0,0)
            py5.circle(self.x, self.y, PIECE_SIZE*0.2)

class GFXMotion:
    def __init__(self, 
                 piece: PieceGFX, 
                 source: Tuple[int, int], 
                 target: Tuple[int, int], 
                 crowned = False):
        self.piece: PieceGFX = piece
        self.source = ((source[1]+1.5)*TILE_SIZE,
                       (source[0]+1.5)*TILE_SIZE)
        self.target = ((target[1]+1.5)*TILE_SIZE,
                       (target[0]+1.5)*TILE_SIZE)
        self.angle = 0
        self.creates_crown = crowned
    
    def update(self):
        if self.angle == 180: 
            self.piece.x = self.target[0]
            self.piece.y = self.target[1]
            return True

        scale = (1 - py5.cos(py5.PI*self.angle/180)) / 2 
        self.piece.x = scale*self.target[0] + (1-scale)*self.source[0]
        self.piece.y = scale*self.target[1] + (1-scale)*self.source[1]
        self.angle += 4
        return False
    
    def __del__(self):
        if self.creates_crown: 
            self.piece.crowned = True

# if __name__ == "__main__":
#     GFX = CheckersGraphics()
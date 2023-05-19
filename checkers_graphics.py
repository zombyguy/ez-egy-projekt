import py5
import py5_tools
from collections import deque 
from typing import Tuple, Deque
from time import sleep, time

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
    """
    Creates and manages the py5 graphics necessary for rendering
    a game of checkers.
    """
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
        self.possible_choices: list[tuple[int,int]] = list()

        self.pause_box = (GAME_WINDOW_SIZE-40, 15, 80, 30)

class TileGFX:
    def __init__(self, x,y, color = (255,255,255)):
        self.x = x
        self.y = y 
        self.color = color
    
class PieceGFX:
    """
    Object to manage the graphical representation of a chekers piece. 
    """
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
        """
        Renders the piece on the py5 canvas.
        """
        # kell a kinézetváltás, ha dáma
        if self.p1: color = P1_COLOR
        else: color = P2_COLOR
        py5.fill(*color)
        py5.circle(self.x, self.y, PIECE_SIZE)
        if self.crowned:
            py5.fill(255,0,0)
            py5.circle(self.x, self.y, PIECE_SIZE*0.2)

class GFXMotion:
    """
    Object to manage the movement of a piece.

    Input:
        - piece_gfx: The piece to be moved.
        - source: the starting position of the movement
        - target: the ending position of the movement
        - crowned: whether the piece ends with a crown created
    """
    def __init__(self, 
                 piece_gfx: PieceGFX, 
                 source: Tuple[int, int], 
                 target: Tuple[int, int], 
                 crowned: bool = False):
        self.piece_gfx: PieceGFX = piece_gfx
        self.source = ((source[1]+1.5)*TILE_SIZE,
                       (source[0]+1.5)*TILE_SIZE)
        self.target = ((target[1]+1.5)*TILE_SIZE,
                       (target[0]+1.5)*TILE_SIZE)
        self.angle = 0
        self.creates_crown = crowned
    
    def update(self):
        """
        Update the position of the corresponding piece. 
        """
        if self.angle == 180: 
            self.piece_gfx.x = self.target[0]
            self.piece_gfx.y = self.target[1]
            if self.creates_crown:
                self.piece_gfx.crowned = True
            return True

        scale = (1 - py5.cos(py5.PI*self.angle/180)) / 2 
        self.piece_gfx.x = scale*self.target[0] + (1-scale)*self.source[0]
        self.piece_gfx.y = scale*self.target[1] + (1-scale)*self.source[1]
        self.angle += 4
        return False

    def __del__(self):
        if self.creates_crown: 
            self.piece_gfx.crowned = True

def draw_box(box: tuple[int, int, int, int], 
            color: tuple,  
            **kwargs):
    """
    Draws a box with a specified color.

    Input:
        - box: the coordinates of the box
        - color: the color of the box
        
    Optional kwargs:
        - hover_color: color to use if the mouse pointer is hovering over the box
        - text: text to display in box
        - text_size: text size to use for text 
    """
    py5.fill(*color)
    if "hover_color" in kwargs.keys():
        if cursor_in_box(*box): py5.fill(*kwargs["hover_color"])
    py5.rect(*box)

    if "text_size" in kwargs.keys():
        py5.text_size(kwargs["text_size"])

    if "text" in kwargs.keys():
        py5.text_align(py5.CENTER)
        py5.fill(0)
        py5.text(kwargs["text"], *box)

def cursor_in_box(x:int,y:int,w:int,h:int):
    """
    Checks whether the cursor is in the box with center (x,y), 
    width w and height h.
    """
    return (((x - w//2) <= py5.mouse_x <= (x + w//2)) and 
            ((y - h//2) <= py5.mouse_y <= (y + h//2)))

def take_screenshot():
    py5.save(f"C:\\Users\\zsomb\\Pictures\\py5checkers\\checkers_{time()}.jpg")


# if __name__ == "__main__":
#     GFX = CheckersGraphics()
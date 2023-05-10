from game_pvp import *
from checkers_graphics import *

# TILE_SIZE = 40
# GAME_WINDOW_SIZE = TILE_SIZE * 10
# EVEN_CELL_COLOR = (248,231,179)
# ODD_CELL_COLOR = (170,76,35)

# PIECE_SCALE = 0.8
# PIECE_SIZE = TILE_SIZE * PIECE_SCALE
# P1_COLOR = (255, 255, 255)
# P2_COLOR = (0,0,0)

CAN_PROCEED = True

def setup():
    py5.size(GAME_WINDOW_SIZE, GAME_WINDOW_SIZE)
    py5.rect_mode(py5.CENTER)
    py5.background(128)

def draw():
    global GAME_STATE, CAN_PROCEED

    for row in GFX.tileset:
        for tile in row:
            py5.fill(*tile.color)
            py5.square(tile.x, tile.y, TILE_SIZE)

    for piece in GFX.pieces:
        piece.draw()

    if GFX.in_motion:
        if (86 <= GFX.current_motion.angle < 90) and len(GFX.destroy_cue) > 0:
            print("--- PIECE REMOVED ---")
            piece_gfx = GFX.destroy_cue.popleft()
            piece_gfx.destroy()
            del piece_gfx
        # print(GFX.current_motion.angle)
        if GFX.current_motion.update():
            GFX.current_motion = None
            GFX.in_motion = False
        
    if not GFX.in_motion:
        if len(GFX.motion_cue) > 0:
            GFX.current_motion = GFX.motion_cue.popleft()
            piece_gfx = GFX.current_motion.piece
            i = GFX.pieces.index(piece_gfx)
            GFX.pieces[-1], GFX.pieces[i] = GFX.pieces[i], GFX.pieces[-1]
            GFX.in_motion = True

    if not GFX.in_motion:
        if CAN_PROCEED and GAME_STATE != 0:
            print(f"Current player: {GAME.turn}")
            CAN_PROCEED = False
            GAME_STATE = GAME.bot_turn()

def key_pressed(e):
    global CAN_PROCEED
    pressed_key = e.get_key()
    if pressed_key == py5.ENTER:
        CAN_PROCEED = True


if __name__ == "__main__":
    GAME = game()
    GFX = GAME.GFX
    GAME_STATE = 1
    GAME.update_all()
    py5.run_sketch()

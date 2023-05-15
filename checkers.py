from game_pvp import *
from checkers_graphics import *
from menu import *

# TILE_SIZE = 40
# GAME_WINDOW_SIZE = TILE_SIZE * 10
# EVEN_CELL_COLOR = (248,231,179)
# ODD_CELL_COLOR = (170,76,35)

# PIECE_SCALE = 0.8
# PIECE_SIZE = TILE_SIZE * PIECE_SCALE
# P1_COLOR = (255, 255, 255)
# P2_COLOR = (0,0,0)

CAN_PROCEED = True
GFX: CheckersGraphics = None
GAME: game = None

def setup():
    py5.size(MENU.width, MENU.height)
    py5.rect_mode(py5.CENTER)

    # py5.size(GAME_WINDOW_SIZE, GAME_WINDOW_SIZE)
    # py5.rect_mode(py5.CENTER)
    # py5.background(128)

def draw():
    global CAN_PROCEED

    if MENU.state == "menu":
        MENU.draw()
        return
    elif MENU.state == "end":
        print("end")
        py5.stroke_weight(2)
        py5.fill(128)
        py5.rect(GAME_WINDOW_SIZE//2, GAME_WINDOW_SIZE//2,
                 200, 50)
        py5.text_align(py5.CENTER)
        py5.fill(0)
        py5.text(f"{'Fehér' if GAME.turn == -1 else 'Fekete'} győz", 
                 GAME_WINDOW_SIZE//2, GAME_WINDOW_SIZE//2,
                 200, 50)
        if py5.has_thread("wait"): pass
        else:
            surface = py5.get_surface()
            surface.set_resizable(True)
            surface.set_size(MENU.width, MENU.height)
            surface.set_resizable(False)
            MENU.state = "menu"
            # MENU.state = "game"
        return


    py5.stroke_weight(1)
    py5.stroke(0)
    for row in GFX.tileset:
        for tile in row:
            py5.fill(*tile.color)
            py5.square(tile.x, tile.y, TILE_SIZE)
    
    if GAME.turn == 1: py5.fill(255)
    else: py5.fill(0)
    py5.square(10, 10, 20)

    for piece in GFX.pieces:
        piece.draw()

    py5.fill(255,0,0,128)
    for pos in GFX.phantom_pieces:
        py5.circle((pos[1]+1.5)*TILE_SIZE, 
                   (pos[0]+1.5)*TILE_SIZE, 
                   PIECE_SIZE)

    if GFX.active_piece != None: 
        py5.circle(GFX.active_piece.x, GFX.active_piece.y, PIECE_SIZE//2)

    py5.fill(0,0,0,0)
    py5.stroke(255,0,0,128) 
    py5.stroke_weight(3)
    for pos in GFX.possible_choices:
        py5.circle((pos[1]+1.5)*TILE_SIZE, 
                   (pos[0]+1.5)*TILE_SIZE, 
                   PIECE_SIZE*0.5)
    py5.stroke(0)
    py5.stroke_weight(1)

    # GAME.turn *= -1
    # GAME.game_state = 0


    if py5.has_thread('move'): return
    # if py5.has_thread('gfx_motion'): return
    # py5.launch_thread(GAME.move, name='move')

    # if len(GFX.motion_cue) > 0:
    #     motion = GFX.motion_cue.popleft()
    #     py5.launch_thread(motion.animate, name='gfx_motion')

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
        print(GAME.game_state)
        if len(GFX.motion_cue) > 0:
            GFX.current_motion = GFX.motion_cue.popleft()
            piece_gfx = GFX.current_motion.piece_gfx
            i = GFX.pieces.index(piece_gfx)
            GFX.pieces[-1], GFX.pieces[i] = GFX.pieces[i], GFX.pieces[-1]
            GFX.in_motion = True
        
        elif GAME.game_state != 0:
    # if not GFX.in_motion:
        # if CAN_PROCEED and GAME_STATE != 0:
        # if GAME.game_state != 0:
            # print(f"Current player: {GAME.turn}")
            # CAN_PROCEED = False
            py5.launch_thread(GAME.move, name='move')
        else:
            MENU.state = "end"
            py5.launch_thread(waiting, name="wait")

def key_pressed(e):
    global CAN_PROCEED
    pressed_key = e.get_key()
    if py5.has_thread('move'): return 
    if pressed_key == py5.ENTER:
        CAN_PROCEED = True

def mouse_clicked(e):
    if MENU.state == "menu":
        for name, box in MENU.boxes.items():
            if cursor_in_box(*box):
                MENU.selected_mode = name
                return
        if cursor_in_box(*MENU.start_box):
            global GAME, GFX
            MENU.state = "game"

            GAME = game(MENU.selected_mode)
            GFX = GAME.GFX

            surface = py5.get_surface()
            surface.set_resizable(True)
            surface.set_size(GAME_WINDOW_SIZE, GAME_WINDOW_SIZE)
            surface.set_resizable(False)

            GAME.update_all()

    elif MENU.state == "game": # ingame
        i = py5.mouse_y // TILE_SIZE - 1
        j = py5.mouse_x // TILE_SIZE - 1
        print(f"[{i}, {j}]")
        GFX.clicked_pos = (i,j)

def waiting():
    for i in range(30):
        sleep(0.1)


if __name__ == "__main__":
    MENU = Menu()
    # GAME = game('pvp')
    # GFX = GAME.GFX
    # GAME_STATE = 1
    # GAME.update_all()
    py5.run_sketch()

import py5
from checkers_graphics import *
class Menu:
    """
    Object to manage manage UI outside the game itself. 
    """
    def __init__(self):
        self.state = "menu"

        self.width = 300
        self.height = 300
        self.boxes = {
            "pvp": (50,125,20,20),
            "pvb": (50,155,20,20),
            "bvb": (50,185,20,20)
        }
        self.base_color = (160,)
        self.hover_color = (200,)
        self.selected_mode = "pvp"

        self.start_box = (self.width//2, 250, 100, 50)
        self.start_base_color = (200, 180, 70)
        self.start_hover_color = (240, 220, 110)

        self.pause_boxes = {
            "Szünet":    (200,130,150,50),
            "Folytatás": (200,190,150,50),
            "Kilépés":   (200,250,150,50)
        }
        

    def draw(self):
        """
        Draws the main menu.
        """
        py5.background(121,171,135)
        
        # py5.rect_mode(py5.CENTER)
        py5.text_size(60)
        py5.fill(0)
        py5.text_align(py5.CENTER)
        py5.text("Menü", self.width//2, 50, 150, 100)
        
        # py5.rect_mode(py5.CORNER)
        py5.text_size(20)
        py5.text_align(py5.LEFT)
        py5.text("Válaszd ki a játék módját!", 30, 100)
        py5.text("játékos vs játékos", 70, 130)
        py5.text("játékos vs bot", 70, 160)
        py5.text("bot vs bot (néző)", 70, 190)

        for name, box in self.boxes.items():
            py5.stroke_weight(2)
            if cursor_in_box(*box): py5.fill(*self.hover_color)
            else: py5.fill(*self.base_color)
            py5.rect(*box)
            if name == self.selected_mode:
                py5.stroke(181, 24, 24)
                py5.line(box[0]-box[2]/4, box[1]-box[3]/4,
                         box[0]+box[2]/4, box[1]+box[3]/4)
                py5.line(box[0]-box[2]/4, box[1]+box[3]/4,
                         box[0]+box[2]/4, box[1]-box[3]/4)
                py5.stroke(0)

        draw_box(self.start_box, self.start_base_color, 
                 hover_color = self.start_hover_color,
                 text="Start", text_size = 35)
        # if cursor_in_box(*self.start_box): py5.fill(*self.start_hover_color)
        # else: py5.fill(*self.start_base_color)
        # py5.rect(*self.start_box)
        # py5.text_size(35)
        # py5.fill(0)
        # py5.text_align(py5.CENTER)
        # py5.text("Start", *self.start_box)
        
    def draw_pause(self):
        """
        Draws the pause menu. 
        """
        py5.stroke_weight(2)
        py5.fill(128)
        py5.rect(200, 200,
                 200, 200)
        py5.text_align(py5.CENTER)
        py5.fill(0)

        for name, box in self.pause_boxes.items():
            if name == "Szünet":
                py5.stroke_weight(4)
                py5.text(name, *box)
                py5.stroke_weight(2)
                continue
            
            draw_box(box, self.base_color, 
                     hover_color = self.hover_color, 
                     text=name, text_size=35)
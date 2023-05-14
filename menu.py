import py5

class Menu:
    def __init__(self):
        self.in_menu = True

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
        

    def draw(self):
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

        if cursor_in_box(*self.start_box): py5.fill(*self.start_hover_color)
        else: py5.fill(*self.start_base_color)
        py5.rect(*self.start_box)
        py5.text_size(35)
        py5.fill(0)
        py5.text_align(py5.CENTER)
        py5.text("Start", *self.start_box)
        


def cursor_in_box(x,y,w,h):
    return (((x - w//2) <= py5.mouse_x <= (x + w//2)) and 
            ((y - h//2) <= py5.mouse_y <= (y + h//2)))

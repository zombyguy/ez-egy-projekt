from typing import List, Dict, Type

class Pos:
    def __init__(self, i:int, j:int) -> None:
        self.ind: tuple[int, int] = (i,j)

    def __getitem__(self, c) -> int:
        return self.ind[c]

    def __add__(self, other: 'Pos') -> None:
        self.ind = (self[0] + other[0], self[1] + other[1])

    def __mul__(self, scalar: int) -> None:
        self.ind = (scalar*self[0], scalar*self[1])

    def is_valid(self) -> bool:
        return (0 <= self[0] < 8) and (0 <= self[1] < 8) 
    

FL = Pos( 1,  1)
FR = Pos( 1, -1)
BL = Pos(-1,  1)
BR = Pos(-1, -1)

class CheckersPiece(object):
    def __init__(self,
                 game: 'CheckersGame',
                 pos: Pos,
                 color: int):
        
        self.game: CheckersGame = game
        self.pos: Pos = pos
        self.color: int = color
        self.crowned: bool = False

        self.move_options: list[Pos] = []
        self.detailed_options: dict[Pos, MoveDetails] = dict()
        self.forced_capture: bool = True

    def __str__(self):
        if not self.crowned:
            return " 1" if self.color == 1 else "-1"
        else:
            return " Q" if self.color == 1 else "-Q"

    def update_options(self):
        move_options: List[Pos] = []
        detailed_options: Dict[Pos, MoveDetails] = dict()
        forced_capture: bool  = False

        if self.crowned: dirs = [FR, FL, BR, BL]
        elif self.color == 1: dirs = [FR, FL]
        else: dirs = [BR, BL]
        
        for direction in dirs:
            if self.is_possible_capture(direction):
                pass

        if not self.forced_capture:
            for direction in dirs:
                # self.no_take(direction)
                pass

        for move in self.detailed_options.keys():
            move_options.append(move)

        self.move_options = move_options
        self.detailed_options = detailed_options

    def is_possible_capture(self, direction: Pos):
        pos_to_capture = self.pos + direction
        pass
        # TODO:
        #   szerintem ez egy stack-kel egész hatékonyan megoldható
        #   anélkül, hogy kéne még a can_take_more-is. Tehát gyakorlatilag
        #   DFS-sé lehet alakítani, és akkor a visszalépésnél a taken
        #   dolgot visszaállítjuk a piece objektumra

    # def no_take(self, direction):
    #     pass
        
class PlayerCharacterBase(object):
    """
    Base class for all player characters, a.k.a RealPlayer and 
    the bots
    """
    def __init__(self, 
                 game: 'CheckersGame', 
                 color: int):
        self.color = color
    
    def make_move(self) -> None:
        pass

class CheckersGame:
    def __init__(self,
                 TypeP1: Type[PlayerCharacterBase],
                 TypeP2: Type[PlayerCharacterBase]):
        
        P1 = TypeP1(self,  1)
        P2 = TypeP2(self, -1)
        self.current_player = 1

        self.board: dict[tuple[int, int], CheckersPiece] = {
            (i, j): CheckersPiece(self, Pos(i, j),  1)
            for i in range(0, 3) for j in range(8)
            if (i+j)%2 == 1 
        } | {
            (i, j): CheckersPiece(self, Pos(i, j), -1)
            for i in range(5, 8) for j in range(8)
            if (i+j)%2 == 1 
        }

    def duplicate(self):
        newgame = CheckersGame()

class MoveDetails:
    def __init__(self, 
                 piece: CheckersPiece):
        self.piece = piece
        self.final_pos: Pos = None
        self.taking: list[CheckersPiece] = []
        self.creates_crown: bool = False


class RealPlayer(PlayerCharacterBase):
    def __init__(self, game):
        pass

    def make_move(self):
        pass
    # TODO: játékos lépési lehetőségei és megfelelő animációk
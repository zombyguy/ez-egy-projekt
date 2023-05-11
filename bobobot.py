from game_class import *
from collections import deque
from typing import Union

MAX_DEPTH = 4

class BoboBot(PlayerCharacterBase):
    def __init__(self, game):
        pass
    
    def make_move(self):
        pass
    # TODO: simulate_step és társai

class PieceSimulator(CheckersPiece):
    def __init__(self, 
                 simulator: 'CheckersGameSimulator',
                 piece: CheckersPiece):
        
        self.game = simulator
        self.pos = piece.pos
        self.color = piece.color
        self.crowned = piece.crowned

        self.move_options = piece.move_options
        self.detailed_options = piece.detailed_options
        self.forced_capture = piece.forced_capture

        self.pos_stack: deque[Pos | None] = deque()
        self.opt_stack: deque[Pos | None] = deque()
        self.dopt_stack: deque[MoveDetails | None] = deque()
            
class CheckersGameSimulator(CheckersGame):
    def __init__(self, 
                 game: CheckersGame):
        
        self.pieces: list[PieceSimulator] = [
            PieceSimulator(self, game.board[pos])
            for pos in game.board.keys()
        ]
        self.board: dict[tuple[int, int], PieceSimulator] = dict()
        self.refresh_board()

        self.player = game.current_player # a játékos, akinek a szemszögéből vizsgálunk
        # self.current_player = self.player # a szimuláció során éppen tevékenykedő játékos

    def refresh_board(self) -> None:
        self.board = {piece.pos.ind: piece for piece in self.pieces}

    def simulate_step(self, motion: MoveDetails):
        moving_piece: PieceSimulator = self.board[motion.positions[0]]
        taken_pieces: list[PieceSimulator] = [self.board[tpos] for tpos in motion.taking]
        final_neighbours: list[PieceSimulator] = []
        
        for dir in [FL, FR, BL, BR]:
            pos: Pos = motion.positions[-1] + dir
            if pos.ind in self.board.keys():
                final_neighbours.append(self.board[pos.ind])


        for piece in self.pieces:
            # minden szimulált bábu állapotát frissíti dfs-nek megfelelően
            piece.pos_stack.append(piece.pos_stack[-1])
            piece.opt_stack.append(piece.opt_stack[-1])
            piece.dopt_stack.append(piece.dopt_stack[-1])
            
            if piece == moving_piece:
                piece.pos = motion.positions[-1]
                piece.move_options = None # update options
                piece.detailed_options = None # update options
            
            elif piece in final_neighbours:
                piece.move_options = None # update options
                piece.detailed_options = None # update options

            elif piece in taken_pieces:
                piece.pos = None
                piece.move_options = None
                piece.move_options = None

    def find_best_step(self):
        score_stack: deque[int] = deque([-1000])
        best_list: list[MoveDetails] = []
        
        num_pieces = [0,0]
        for piece in self.pieces:
            num_pieces[piece.color] += 1
        num_pieces_stack: deque[tuple[int, int]] = deque([num_pieces])

        self.smotion_stack: deque[SimulatedMotion] = deque()
        
        current_color = self.player
        self.add_smotions(1, current_color) # első szintű lépések hozzáadása
                
        depth = 1
        while len(self.smotion_stack) != 0:
            """
            addig csinálunk dfs-t a lehetséges mozgásokon, amíg
            tudunk, vagy el nem érjük a kívánt mélységet

            """
            
            smotion = self.smotion_stack.pop()

            while smotion.simulation_depth < depth:
                """
                A DFS-ben ekkor visszaléptünk, ezért vissza kell
                állítani az elemek állapotát a megfelelő szintre
                """
                for piece in self.pieces:
                    piece.pos = piece.pos_stack.pop()
                    piece.move_options = piece.opt_stack.pop()
                    piece.detailed_options = piece.dopt_stack.pop()
                num_pieces = num_pieces_stack.pop()
                # calculate new score from score stack

                depth -= 1 
                self.current_player *= -1
            
            self.simulate_step(smotion.dopt)
            num_pieces[current_color * -1] = len(smotion.dopt.taking)
            num_pieces_stack.append(num_pieces)

            # evaluate step and modify score stack
            if num_pieces[self.player] == 0: 
                # a vizsgált játékos vesztett
                continue
            elif num_pieces[self.player * -1] == 0:
                # a vizsgált játékos nyert 
                continue
            elif smotion.simulation_depth == MAX_DEPTH:
                # elértük a szimulációs mélységet, pontot kell számolni
                continue
            else:
                depth += 1 
                current_color *= -1
                self.add_smotions(depth)

    def add_smotions(self, depth: int, current_color):
        for piece in self.board.values():
            if piece.color == current_color:
                for motion in piece.detailed_options.values():
                    self.smotion_stack.append(SimulatedMotion(motion, depth))
        


class SimulatedMotion():
    def __init__(self, 
                 dopt: MoveDetails, 
                 depth: int):
        self.dopt = dopt
        self.simulation_depth = depth
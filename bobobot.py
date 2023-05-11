from game_class import *
from collections import deque
from typing import Union

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

        self.current_player = game.current_player

    def refresh_board(self) -> None:
        self.board = {piece.pos.ind: piece for piece in self.pieces}

    def simulate_step(self, motion: MoveDetails):
        moving_piece: PieceSimulator = self.board[motion.piece.pos]
        taken_pieces: list[PieceSimulator] = [self.board[piece.pos] for piece in motion.taking]
        final_neighbours: list[PieceSimulator] = []
        
        for dir in [FL, FR, BL, BR]:
            pos: Pos = motion.final_pos + dir
            if pos.ind in self.board.keys():
                final_neighbours.append(self.board[pos.ind])


        for piece in self.pieces:
            # minden szimulált bábu állapotát frissíti dfs-nek megfelelően
            piece.pos_stack.append(piece.pos_stack[-1])
            piece.opt_stack.append(piece.opt_stack[-1])
            piece.dopt_stack.append(piece.dopt_stack[-1])
            
            if piece == moving_piece:
                piece.pos = motion.final_pos
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
        best_score = -1000
        best_list: list[SimulatedMotion] = []
        
        depth = 0
        score_stack: deque[int] = deque()

        motion_stack: deque[SimulatedMotion] = deque()

        for piece in self.board.values():
            if piece.color == self.current_player:
                motion_stack += deque(piece.detailed_options)

        while len(motion_stack) != 0:
            """
            addig csinálunk dfs-t a lehetséges mozgásokon, amíg
            tudunk, vagy el nem érjük a kívánt mélységet

            """
            
            pass 


class SimulatedMotion(MoveDetails):
    def __init__(self, piece, depth):
        self.piece = piece
        self.final_pos: Pos = None
        self.taking: list[CheckersPiece] = []
        self.creates_crown: bool = False

        self.simulation_depth = depth
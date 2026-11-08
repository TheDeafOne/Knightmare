"""Depth-limited minimax with alpha-beta pruning."""
import math
from game_logic.board_utils import BoardConstants as constants, BoardUtils as utils


class MiniMax:
    MATE_SCORE = 100000

    def __init__(self, depth=2):
        # One ply is one move by one player; depth means exactly this many plies.
        self.MAX_DEPTH = max(1, int(depth))
        self.next_move = None
        self.use_eval_functions = True
        self.nodes = 0

    @staticmethod
    def moves(board, player):
        result = []
        for origin in range(64):
            if board.check_piece(origin, player):
                for target in utils.board_to_indexes(board.get_moves(origin)):
                    result.append((utils.index_to_square(origin), utils.index_to_square(target)))
        # Stable capture-first ordering makes the search reproducible.
        return sorted(result, key=lambda move: board.get_piece(move[1]) == constants.EMPTY)

    def get_next_move(self, board, player):
        self.next_move = None
        self.nodes = 0
        if board.outcome(player):
            return None
        best, alpha = -math.inf, -math.inf
        for move in self.moves(board, player):
            board.move_piece(*move, evaluate_outcome=False)
            try:
                score = self._search(board, 1 - player, player, self.MAX_DEPTH - 1,
                                     alpha, math.inf, 1)
            finally:
                board.undo_last()
            if score > best:
                best, self.next_move = score, move
            alpha = max(alpha, best)
        return self.next_move

    def _search(self, board, player, root, remaining, alpha, beta, ply):
        self.nodes += 1
        outcome = board.outcome(player)
        if outcome == 1:
            return -self.MATE_SCORE + ply if player == root else self.MATE_SCORE - ply
        if outcome == 2:
            return 0
        if remaining == 0:
            return board.get_score(root, 0) if self.use_eval_functions else 0
        maximizing = player == root
        best = -math.inf if maximizing else math.inf
        for move in self.moves(board, player):
            board.move_piece(*move, evaluate_outcome=False)
            try:
                score = self._search(board, 1 - player, root, remaining - 1,
                                     alpha, beta, ply + 1)
            finally:
                board.undo_last()
            best = max(best, score) if maximizing else min(best, score)
            if maximizing:
                alpha = max(alpha, best)
            else:
                beta = min(beta, best)
            if beta <= alpha:
                break
        return best

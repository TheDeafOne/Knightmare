"""Regression tests, with python-chess as an independent rules oracle."""
import copy
import random
import unittest
import chess
from algorithms.minimax import MiniMax
from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils


def from_fen(fen):
    oracle = chess.Board(fen)
    board = Board()
    for square in range(64):
        board.set_piece('-', square)
    for square, piece in oracle.piece_map().items():
        board.set_piece(piece.symbol(), square)
    board.side_to_move = 0 if oracle.turn else 1
    board.castling_rights = oracle.castling_xfen()
    board.en_passant_board = 1 << oracle.ep_square if oracle.ep_square is not None else 0
    board.halfmove_clock = oracle.halfmove_clock
    board.last_move = [1, 1, 1]
    board.last_last_move = [0, 0, 0]
    board._positions = [board._position_key()]
    board.get_king_shelter(0)
    board.get_king_shelter(1)
    return board


def move_set(board, color):
    return {a + b for a, b in MiniMax.moves(board, color)}


class EngineTests(unittest.TestCase):
    def assert_oracle(self, board, oracle):
        expected = {m.uci()[:4] for m in oracle.legal_moves}
        self.assertEqual(move_set(board, 0 if oracle.turn else 1), expected, oracle.fen())
        self.assertEqual([board.get_piece(i) for i in range(64)],
                         [oracle.piece_at(i).symbol() if oracle.piece_at(i) else '-' for i in range(64)])

    def test_opening_perft(self):
        board = Board()
        def perft(color, depth):
            if not depth:
                return 1
            count = 0
            for move in MiniMax.moves(board, color):
                board.move_piece(*move, evaluate_outcome=False)
                count += perft(1 - color, depth - 1)
                board.undo_last()
            return count
        self.assertEqual(perft(0, 1), 20)
        self.assertEqual(perft(0, 2), 400)
        self.assertEqual(perft(0, 3), 8902)

    def test_random_games_match_independent_rules(self):
        for seed in (0, 7, 42):
            rng, board, oracle = random.Random(seed), Board(), chess.Board()
            for _ in range(120):
                self.assert_oracle(board, oracle)
                moves = [m for m in oracle.legal_moves if not m.promotion or m.promotion == chess.QUEEN]
                if not moves:
                    break
                move = rng.choice(moves)
                state = copy.deepcopy(board._snapshot())
                board.move_piece(move.uci()[:2], move.uci()[2:4])
                after = copy.deepcopy(board._snapshot())
                board.undo_last()
                self.assertEqual(board._snapshot(), state)
                board.move_piece(move.uci()[:2], move.uci()[2:4])
                self.assertEqual(board._snapshot(), after)
                oracle.push(move)

    def test_special_moves_and_undo(self):
        cases = (
            ('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1', 'e1g1'),
            ('r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1', 'e8c8'),
            ('4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1', 'e5d6'),
            ('4k3/P7/8/8/8/8/8/4K3 w - - 0 1', 'a7a8q'),
            ('4k3/8/8/8/8/8/p7/4K3 b - - 0 1', 'a2a1n'),
            ('4k3/8/8/8/8/8/4q3/4R1K1 w - - 0 1', 'e1e2'),
        )
        for fen, uci in cases:
            board, oracle = from_fen(fen), chess.Board(fen)
            self.assert_oracle(board, oracle)
            before = copy.deepcopy(board._snapshot())
            board.move_piece(uci[:2], uci[2:4], uci[4:] or 'Q')
            oracle.push_uci(uci)
            self.assert_oracle(board, oracle)
            board.undo_last()
            self.assertEqual(board._snapshot(), before)

    def test_pins_double_check_and_castling_through_check(self):
        for fen in (
            '4r1k1/8/8/8/8/8/4R3/4K3 w - - 0 1',
            '4r1k1/8/8/8/1b6/8/8/4K3 w - - 0 1',
            '4kr2/8/8/8/8/8/8/R3K2R w KQ - 0 1',
            '4k3/8/8/r4pPK/8/8/8/8 w - f6 0 1',
        ):
            self.assert_oracle(from_fen(fen), chess.Board(fen))

    def test_checkmate_stalemate_and_search_state(self):
        mate = from_fen('7k/6Q1/5K2/8/8/8/8/8 b - - 0 1')
        stale = from_fen('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')
        self.assertEqual(mate.outcome(), 1)
        self.assertEqual(stale.outcome(), 2)
        self.assertIsNone(MiniMax(2).get_next_move(mate, 1))
        board = from_fen('7k/8/5KQ1/8/8/8/8/8 w - - 0 1')
        before = copy.deepcopy(board._snapshot())
        move = MiniMax(1).get_next_move(board, 0)
        self.assertEqual(board._snapshot(), before)
        board.move_piece(*move)
        self.assertEqual(board.outcome(), 1)

    def test_search_prefers_undefended_queen_and_preserves_captures(self):
        for fen, expected in (
            ('6k1/8/8/8/8/4q3/4R3/6K1 w - - 0 1', ('e2', 'e3')),
            ('6k1/4r3/4Q3/8/8/8/8/6K1 b - - 0 1', ('e7', 'e6')),
        ):
            board = from_fen(fen)
            before = copy.deepcopy(board._snapshot())
            self.assertEqual(MiniMax(1).get_next_move(board, board.side_to_move), expected)
            self.assertEqual(board._snapshot(), before)

    def test_draw_and_illegal_input(self):
        board = Board()
        for _ in range(2):
            for a, b in [('g1','f3'),('g8','f6'),('f3','g1'),('f6','g8')]:
                board.move_piece(a, b)
        self.assertEqual(board.outcome(), 2)
        with self.assertRaises(ValueError):
            Board().move_piece('e2', 'e5')
        self.assertFalse(utils.is_valid_square(''))
        self.assertFalse(utils.is_valid_square('a10'))


if __name__ == '__main__':
    unittest.main()

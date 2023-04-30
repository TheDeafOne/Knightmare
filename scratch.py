from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import datetime
from algorithms.minimax import MiniMax


def test_minimax():
    board = Board()

    minimax = MiniMax()

    for i in range(100):
        print('move', i)
        start = datetime.datetime.now()
        if (i % 2 == 0):
            next_move = minimax.get_next_move(board, constants.WHITE)
        else:
            next_move = minimax.get_next_move(board, constants.BLACK)
        print(next_move[0] + " to " + next_move[1] + '\n')
        board.move_piece(next_move[0], next_move[1])
        print(board.get_board_string())
        end = datetime.datetime.now()
        delta = end - start
        print(delta.total_seconds())

        if board.check_piece(utils.square_to_index('a2'), constants.WHITE):
            print('success')
        if board.check_piece(utils.square_to_index('d8'), constants.BLACK):
            print('success')
    print(board.get_board_string())


def test_misc():
    board = Board()
    # place king in vulnerable position
    board.move_piece('e8', 'e4')

    # place rook where it coud get the king
    board.set_piece('R', 'a4')
    board.set_piece('p', 'g5')
    # board.set_piece(constants.EMPTY,'d2')
    # board.set_piece(constants.EMPTY,'f2')
    # board.set_piece(constants.EMPTY,'c1')
    board.move_piece('f8', 'f7')
    board.move_piece('h2', 'h3')
    board.set_piece('q', 'c4')
    board.set_piece('Q', 'b4')
    start = datetime.datetime.now()
    # print(utils.bin_to_string(board.get_moves('c4')))
    print(board.get_board_string())
    print(str(board.get_score(constants.BLACK, False)))

    end = datetime.datetime.now()
    print('\nt:', (end-start).seconds)

    # board.highlight_moves(board.get_moves('e4'))
    print(board.get_board_string())


def print_initial_board():
    board = Board()
    print(board.get_board_string())


def focal_control_tests():
    board = Board()
    board.set_piece('q', 'd5')
    board.set_piece('p', 'e4')
    board.set_piece('r', 'd4')
    # board.set_piece('p','e5')
    print(board.get_board_string())
    print(board.get_focal_points(constants.BLACK))


def pawn_to_queen_test():
    board = Board()
    # board.set_piece(constants.EMPTY, 'h8')
    # board.set_piece(constants.EMPTY, 'h7')
    board.move_piece('h7', 'h1')
    print(board.get_board_string())


def development_order_evaluation_test():
    board = Board()
    board.move_piece('d8', 'h3')
    board.move_piece('b8', 'a6')
    board.move_piece('g8', 'c6')
    print(board.get_board_string())
    print(board.get_development_order_points(constants.BLACK, [1, 0, 0]))


def get_focal_point():
    board = Board()
    board.move_piece('a1', 'c4')
    print(board.get_score(None, None))


def duplicate_king_glitch():
    board = Board()
    board.move_piece('g8', 'f2')
    board.move_piece('e1', 'f2')
    board.undo_last()
    print(board.get_board_string())


def testing_enable_moves():
    board = Board()
    board.move_piece('b8', 'd3')
    # board.move_piece('d1','c2')
    moves = board.get_moves('d1')
    board.highlight_moves(moves)

    print(board.get_board_string())


def get_endgame_king_eval():
    board = Board()
    board.move_piece('e8', 'e4')
    print(board.get_endgame_points(constants.BLACK))
    print(board.get_board_string())


def minor_piece_dev_test():
    board = Board()
    board.move_piece('b1','c3')
    print(board.get_score(constants.WHITE,None))
    print(board.get_board_string())


def king_check_bug_tests():
    board = Board()
    board.set_piece(constants.EMPTY, 'e7')
    print(board.move_piece('d2', 'd7'))
    print(board.get_board_string())
    moves = board.get_moves('b8')
    print(utils.bin_to_string(moves))

def king_block_bug_tests():
    board = Board()
    board.move_piece('f2','f4')
    board.move_piece('e7','e6')
    board.move_piece('a2','a4')
    board.move_piece('d8','h4')
    print(board.get_board_string())
    print(utils.bin_to_string(board.get_moves('g2')))

def king_block_bug_tests2():
    board = Board()
    board.set_piece(constants.EMPTY, 'g1')
    board.set_piece(constants.EMPTY, 'e2')
    board.set_piece(constants.EMPTY, 'g2')
    board.set_piece(constants.EMPTY, 'f1')
    board.move_piece('d8','f2')
    print(board.get_board_string())
    print(utils.bin_to_string(board.get_moves('e1')))

if __name__ == "__main__":
    # test_minimax()

    # duplicate_king_glitch()
    # print_initial_board()
    # focal_control_tests()
    # development_order_evaluation_test()
    # get_focal_point()
    # testing_enable_moves()
    # get_endgame_king_eval()
    # # minor_piece_dev_test()
    
    king_check_bug_tests()
    king_block_bug_tests()
    king_block_bug_tests2()

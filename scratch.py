from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import datetime
from algorithms.minimax import MiniMax

def test_minimax():
    board = Board()

    minimax = MiniMax()

    for i in range(40):
        start = datetime.datetime.now()
        if (i % 2 == 0): 
            next_move = minimax.get_next_move(board,constants.WHITE)
        else:
            next_move = minimax.get_next_move(board,constants.BLACK)
        print(next_move[0] + " to " + next_move[1] + '\n')
        board.move_piece(next_move[0],next_move[1])
        print(board.get_board_string())
        end = datetime.datetime.now()
        delta = end - start
        print(delta.total_seconds())

        if board.check_piece(utils.square_to_index('a2'),constants.WHITE):
            print('success')
        if board.check_piece(utils.square_to_index('d8'),constants.BLACK):
            print('success')


def test_misc():
    board = Board()
    # place king in vulnerable position
    board.move_piece('e8','e4')

    # place rook where it coud get the king
    board.set_piece('R','a4')
    board.set_piece('p','g5')
    # board.set_piece(constants.EMPTY,'d2')
    # board.set_piece(constants.EMPTY,'f2')
    # board.set_piece(constants.EMPTY,'c1')
    board.move_piece('f8','f7')
    board.move_piece('h2','h3')
    board.set_piece('q','c4')
    start = datetime.datetime.now()
    print(utils.bin_to_string(board.get_moves('c4')))


    end = datetime.datetime.now()
    print('\nt:',(end-start).seconds)

    # board.highlight_moves(board.get_moves('e4'))
    print(board.get_board_string())

def print_initial_board():
    board = Board()
    print(board.get_board_string())

def focal_control_tests():
    board = Board()
    board.set_piece('q','d5')
    board.set_piece('p','e4')
    board.set_piece('r','d4')
    # board.set_piece('p','e5')
    print(board.get_board_string())
    print(board.get_focal_points(constants.BLACK))
    

def pawn_to_queen_test():
    board = Board()
    # board.set_piece(constants.EMPTY, 'h8')
    # board.set_piece(constants.EMPTY, 'h7')
    board.move_piece('h7','h1')
    print(board.get_board_string())

def development_order_evaluation_test():
    board = Board()
    board.move_piece('d8','h3')
    board.move_piece('b8','a6')
    board.move_piece('g8','c6')
    print(board.get_board_string())
    print(board.get_development_order_points(constants.BLACK, [1,0,0]))

def get_focal_point():
    b = 1 << utils.square_to_index('e4')
    b |= 1 << utils.square_to_index('e5')
    b |= 1 << utils.square_to_index('d4')
    b |= 1 << utils.square_to_index('d5')
    print(utils.bin_to_string(b))
    print(b)
    print(0x1818 << 8 * 2)

if __name__ == "__main__":
    # test_minimax()
    
    # test_misc()
    # print_initial_board()
    # focal_control_tests()
    # development_order_evaluation_test()
    get_focal_point()

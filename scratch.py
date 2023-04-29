from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import datetime
from algorithms.minimax import MiniMax

# time initialize board


def test_minimax():
    board = Board()


    board.set_piece('k','d5')
    board.set_piece(constants.EMPTY, 'e2')
    board.set_piece(constants.EMPTY, 'c2')
    board.move_piece('d5','e5')
    index = utils.square_to_index('e5')

    print(board.get_board_string())
    board.move_piece('g2','g4')
    print(board.get_board_string())
    board.undo_last()
    print(board.get_board_string())

    if board.check_piece(utils.square_to_index('a2'),constants.WHITE):
        print('success')
    if board.check_piece(utils.square_to_index('d8'),constants.BLACK):
        print('success')

    minimax = MiniMax()
    next_move = minimax.get_next_move(board,constants.WHITE)
    print(next_move[0] + " to " + next_move[1] + '\n')
    print(board.get_board_string())


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

if __name__ == "__main__":
    # test_minimax()
    
    test_misc()

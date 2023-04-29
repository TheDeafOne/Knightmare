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

if __name__ == "__main__":
    test_minimax()
    
    # test_misc()

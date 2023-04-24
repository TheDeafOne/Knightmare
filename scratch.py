from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import datetime
from algorithms.minimax import MiniMax

# time initialize board
start = datetime.datetime.now()
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

# moves = board.get_moves('b5')
# print(utils.bin_to_string(moves))
# board.highlight_moves(moves)

# end = datetime.datetime.now()
# delta = end - start
# print(delta.total_seconds())
# print(board.get_board_string())
# possible_moves = []
# moves = board.get_moves('a2')
# index_moves = board.board_to_piece_list(board.white_pieces, True)
# print(index_moves)


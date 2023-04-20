from board_logic.board import Board
from board_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import datetime

# time initialize board
start = datetime.datetime.now()
board = Board()


board.set_piece('k','d5')
board.set_piece(constants.EMPTY, 'e2')
board.set_piece(constants.EMPTY, 'c2')
board.move_piece('d5','b5')

moves = board.get_moves('b5')

# print(utils.bin_to_string(moves))
board.highlight_moves(moves)
end = datetime.datetime.now()
delta = end - start
print(delta.total_seconds())
print(board.get_board_string())
# print(utils.bin_to_string(board.get_moves('h1')))


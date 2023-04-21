from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import datetime

# time initialize board
start = datetime.datetime.now()
board = Board()


board.set_piece('k','d5')
board.set_piece(constants.EMPTY, 'e2')
board.set_piece(constants.EMPTY, 'c2')
board.move_piece('d5','e5')
board.move_piece('g2','g4')
index = utils.square_to_index('e5')

# moves = board.get_moves('b5')
# print(utils.bin_to_string(moves))
# board.highlight_moves(moves)
end = datetime.datetime.now()
delta = end - start
print(delta.total_seconds())
print(board.get_board_string())
# print(utils.bin_to_string(board.get_moves('h1')))
index_moves = board.board_to_piece_list(board.white_pieces, True)
print(index_moves)


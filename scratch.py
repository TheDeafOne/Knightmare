from board_logic.board import Board
import datetime

# time initialize board
start = datetime.datetime.now()
board = Board()
end = datetime.datetime.now()
delta = end - start
print(delta.total_seconds())

# set board values
board.set_piece('r', 'a6')

# print initial board
print(board.get_board_string())

# get moves
bishop_moves = board.get_moves('a6')
board.hilight_moves(bishop_moves)

# print changed board
print(board.get_board_string())

from board_logic.board import Board
import datetime

# time initialize board
start = datetime.datetime.now()
board = Board()
end = datetime.datetime.now()
delta = end - start
print(delta.total_seconds())

print(board.get_board_string())

# move pieces
board.move_piece('a2','a3')
board.move_piece('f2','d7')
print()
print(board.get_board_string())

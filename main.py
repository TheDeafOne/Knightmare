from game_logic.game import Chess
from game_logic.board import Board
from game_logic.board_utils import BoardConstants as constants, BoardUtils as utils
from algorithms.minimax import MiniMax


def play_console():
    ply_depth = 3
    game_type = 1
    while True:
        game_type = input("AI vs AI (1) or human vs AI (2)?")
        if not game_type.isdigit():
            print('input 1 for AI vs AI or 2 for human vs AI')
            continue
        elif int(game_type) not in range(1,3):
            print('input 1 for AI vs AI or 2 for human vs AI')
            continue
        ply_depth = input("input a ply depth > 0 (default is 3):")

        if ply_depth.isdigit() and int(ply_depth) > 0:
            ply_depth = int(ply_depth)
            break
        print("input a digit > 0")

    board = Board()
    minimax = MiniMax(ply_depth)
    
    if game_type == '1':
        print('starting...')
        print(board.get_board_string())
        color = constants.WHITE
        for i in range(250):
            if (i % 2 == 0):
                color = constants.WHITE
                next_move = minimax.get_next_move(board, constants.WHITE)
            else:
                color = constants.BLACK
                next_move = minimax.get_next_move(board, constants.BLACK)
            print(next_move[0] + " to " + next_move[1] + '\n')
            if (board.move_piece(next_move[0], next_move[1])):
                color_string = "white" if color else "black"
                print(color_string + "won")
                break
            print(board.get_board_string())
    elif game_type == '2':
        print('starting...')
        print(board.get_board_string())
        color = constants.WHITE
        color_set = board.white_pieces
        while True:
            if color == constants.WHITE:
                print('input the square from which you will be moving from and the square from with you will be moving to')
                print('e.g. a2, a3')
                move_pair = input('give your move pair:')
                if ',' not in move_pair:
                    print()
                    print("not a valid pair")
                    continue
                move_pair = move_pair.strip().split(',')[:2]
                from_square, to_square = move_pair
                if not (utils.is_valid_square(from_square) and utils.is_valid_square(to_square)):
                    print()
                    print('one of your squares was invalid, please try again')
                    continue
                from_index, to_index = utils.square_to_index(from_square), utils.square_to_index(to_square)
                if not color_set & 1 << from_index:
                    print()
                    print('this from_square you selected is not your color')
                    continue
                from_moves = board.get_moves(from_index)
                if not from_moves & 1 << to_index:
                    print('this move is outside of the moves of the piece you selected')
                    continue

            else:
                print("AI now making a move:")
                print("loading...")
                from_square, to_square = minimax.get_next_move(board,constants.BLACK)

            in_check = board.move_piece(from_square, to_square)
            if in_check:
                color_string = "black" if color else "white"
                print(color_string + " won")
                break
            print(board.get_board_string())

            print()
            if color == constants.WHITE:
                color = constants.BLACK
                color_set = board.black_pieces
            else:
                color = constants.WHITE
                color_set = board.white_pieces
        



def run():
    print('Welcome to Knightmare')
    while True:
        play_type = input(
            'Do you want to play in console or with a gui (beta)? "c" for console, "g" for gui:')
        if play_type == 'g':
            print('loading...')
            Chess().play()
            break
        elif play_type == 'c':
            play_console()
            play_again = input('play again? (y/n)')
            if play_again == "y":
                continue
            break
        else:
            print('input must be either "c" for console for "g" for gui')


if __name__ == "__main__":
    run()

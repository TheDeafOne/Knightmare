class BoardUtils:
    '''
        A method to convert a given square into an index

        PARAMS
        square: string identifying the cell on the board to return

        RETURNS
        index value of the square on the board
    '''
    def square_to_index(square):
        # get index equivalent of characters
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        # return bitwise index of given square
        return rank * BoardConstants.BOARD_LENGTH + file

    def index_to_square(index):
        row = index // BoardConstants.BOARD_LENGTH + 1
        col = index % BoardConstants.BOARD_LENGTH
        return chr(ord('a') + col) + str(row)

    def bin_to_string(integer_board):
        board = []
        board_string = format(integer_board, '064b')
        for i in range(7, -1, -1):
            for j in range(7, -1, -1):
                board.append(board_string[(i*8)+(7-j)] + ' ')
            board.append('\n')
        return ''.join(board[::-1][1:])

    def board_to_squares(integer_board, index=False):
        return [BoardUtils.index_to_square(i) if index else i
                for i, cell in enumerate(format(integer_board, '064b')) if cell == '1']


class BoardConstants:
    # numeric constants
    BOARD_LENGTH = 8
    ACROSS_BOARD = BOARD_LENGTH ** 2 - BOARD_LENGTH

    # piece constants
    # empty and highlight pieces
    EMPTY = '-'
    HIGHLIGHT = '#'

    # white pieces
    WHITE_PAWN = 'P'
    WHITE_ROOK = 'R'
    WHITE_KNIGHT = 'N'
    WHITE_BISHOP = 'B'
    WHITE_QUEEN = 'Q'
    WHITE_KING = 'K'

    # black pieces
    BLACK_PAWN = 'p'
    BLACK_ROOK = 'r'
    BLACK_KNIGHT = 'n'
    BLACK_BISHOP = 'b'
    BLACK_QUEEN = 'q'
    BLACK_KING = 'k'

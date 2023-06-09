import math


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
        row, col = BoardUtils.square_to_row_col(square)
        # return bitwise index of given square
        return row * BoardConstants.BOARD_LENGTH + col

    def square_to_row_col(square):
        row = int(square[1]) - 1
        col = ord(square[0]) - ord('a')
        return row, col

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

    def singleton_board_to_index(integer_board):
        # verify the board is a power of two (i.e. a singleton board)
        if (integer_board & (integer_board - 1)) > 0 or integer_board == 0:
            return -1
        # gets the index of the piece
        return int(round(math.log(integer_board, 2)))

    def board_to_indexes(integer_board):
        return [i for i, cell in enumerate(format(integer_board, '064b')[::-1]) if cell == '1']
    
    def is_valid_square(square):
        return square[0] in 'abcdefgh' and square[1] in '12345678'

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

    WHITE_PAWN_INDEXES = [8,9,10,11,12,13,14,15]
    WHITE_ROOK_INDEXES = [0,7]
    WHITE_KNIGHT_INDEXES = [1,6]
    WHITE_BISHOP_INDEXES = [2,5]
    WHITE_QUEEN_INDEX = 3
    WHITE_KING_INDEX = 4

    # black pieces
    BLACK_PAWN = 'p'
    BLACK_ROOK = 'r'
    BLACK_KNIGHT = 'n'
    BLACK_BISHOP = 'b'
    BLACK_QUEEN = 'q'
    BLACK_KING = 'k'

    BLACK_PAWN_INDEXES = [63-x for x in WHITE_PAWN_INDEXES]
    BLACK_ROOK_INDEXES = [63-x for x in WHITE_ROOK_INDEXES]
    BLACK_KNIGHT_INDEXES = [63-x for x in WHITE_KNIGHT_INDEXES]
    BLACK_BISHOP_INDEXES = [63-x for x in WHITE_BISHOP_INDEXES]
    BLACK_QUEEN_INDEX = 59
    BLACK_KING_INDEX = 60


    WHITE_PIECES = set([WHITE_PAWN, WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN])
    BLACK_PIECES = set([WHITE_KING, BLACK_PAWN, BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING])
    ALL_PIECE_TYPES = WHITE_PIECES.union(BLACK_PIECES)
                          
    # players
    WHITE = 0
    BLACK = 1

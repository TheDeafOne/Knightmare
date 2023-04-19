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
        row = []
        for i, cell in enumerate(format(integer_board,'064b')):
            print(i)
            if i % BoardConstants.BOARD_LENGTH == 0:
                row.append('\n')
                board.extend(row[::-1])
                row = []
            row.append(cell + ' ')
        return ''.join(board)

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
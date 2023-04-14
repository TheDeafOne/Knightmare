import datetime


class Board:
    '''
        A class used to manage a chess board using the piece-centric bitboard representation
        Each unique chess piece type (e.g. black queen, white rooks, etc.) have their own 64 bit integer representing the 
        location of those pieces. This integer is called a sub-board since it is a subset of all the piece locations.

        As an example, the locations of the black pawns for the initial board would be reprsented by the integer 65280, 
        which has a binary value of 0b1111111100000000, and can be viewed as the following:
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0
        1 1 1 1 1 1 1 1
        0 0 0 0 0 0 0 0

        ATTRIBUTES
        BOARD_LENGTH: an integer indicating the length of a standard chess board
        ACROSS_BOARD: an integer representing the number of cells from one side of the board to other
        board: a 64 bit integer whose bits represent the location of pieces (1 if a piece is on that cell, 0 otherwise)
        white_pawns: a 64 bit integer whose bits represent the location of the white pawns
        white_rooks: a 64 bit integer whose bits represent the location of the white rooks
        white_knights: a 64 bit integer whos bits represent the location of the white knights
        white_bishops: a 64 bit integer whose bits represent the location of the white bishops
        white_queens: a 64 bit integer whose bits represent the location of the white queens
        white_king: a 64 bit integer whose bits represent the location of the white king

        black_pawns: a 64 bit integer whose bits represent the location of the black pawns
        black_rooks: a 64 bit integer whose bits represent the location of the black rooks
        black_knights: a 64 bit integer whose bits represent the location of the black knights
        black_bishops: a 64 bit integer whose bits represent the location of the black bishops
        black_queens: a 64 bit integer whose bits represent the location of the black queens
        black_king: a 64 bit integer whose bits represent the location of the black king
    '''

    def __init__(self):
        # globals
        self.BOARD_LENGTH = 8
        self.ACROSS_BOARD = self.BOARD_LENGTH ** 2 - self.BOARD_LENGTH

        # total board
        self.board = 0xffff << self.BOARD_LENGTH * (self.BOARD_LENGTH - 2)
        self.board |= 0xffff

        # sub-boards
        # white pieces
        self.white_pawns = 0xff << self.BOARD_LENGTH
        self.white_rooks = 0x81
        self.white_knights = 0x42
        self.white_bishops = 0x24
        self.white_king = 0x10
        self.white_queens = 0x8

        # black pieces
        self.black_pawns = 0xff << self.ACROSS_BOARD >> self.BOARD_LENGTH
        self.black_rooks = 0x81 << self.ACROSS_BOARD
        self.black_knights = 0x42 << self.ACROSS_BOARD
        self.black_bishops = 0x24 << self.ACROSS_BOARD
        self.black_king = 0x10 << self.ACROSS_BOARD
        self.black_queens = 0x8 << self.ACROSS_BOARD

    '''
        sets a given piece to a given square

        PARAMS
        piece: a character identifying the type of chess piece (e.g. 'K' for white King, 'Q' for white Queen, etc.)
        square: string or integer index identifying the cell on the board needing to be set
    '''

    def set_piece(self, piece, square):
        if type(square) == str:
            index = self._square_to_index(square)
        else:
            index = square

        # set piece location in temporary mask
        mask = 1 << index

        # check if piece location corresponds with any of the sub-boards
        if piece.isupper():
            if piece == 'K':
                self.white_king |= mask
            elif piece == 'Q':
                self.white_queens |= mask
            elif piece == 'R':
                self.white_rooks |= mask
            elif piece == 'B':
                self.white_bishops |= mask
            elif piece == 'N':
                self.white_knights |= mask
            elif piece == 'P':
                self.white_pawns |= mask
        else:
            if piece == 'k':
                self.black_king |= mask
            elif piece == 'q':
                self.black_queens |= mask
            elif piece == 'r':
                self.black_rooks |= mask
            elif piece == 'b':
                self.black_bishops |= mask
            elif piece == 'n':
                self.black_knights |= mask
            elif piece == 'p':
                self.black_pawns |= mask

    '''
        gets the piece in the given square or index

        PARAMS
        square: string or integer index identifying the cell on the board to return

        RETURNS
        a character in the set of pieces if that piece is in the cell, the empty character otherwise
    '''

    def get_piece(self, square):
        if type(square) == str:
            index = self._square_to_index(square)
        else:
            index = square
        mask = 1 << index
        if self.white_king & mask:
            return 'K'
        elif self.white_queens & mask:
            return 'Q'
        elif self.white_rooks & mask:
            return 'R'
        elif self.white_bishops & mask:
            return 'B'
        elif self.white_knights & mask:
            return 'N'
        elif self.white_pawns & mask:
            return 'P'
        elif self.black_king & mask:
            return 'k'
        elif self.black_queens & mask:
            return 'q'
        elif self.black_rooks & mask:
            return 'r'
        elif self.black_bishops & mask:
            return 'b'
        elif self.black_knights & mask:
            return 'n'
        elif self.black_pawns & mask:
            return 'p'
        return ' '

    '''
        moves the piece from cell 'from_square' to the cell 'to_square'

    '''
    def move_piece(self, from_square, to_square):
        # convert squares to indexes
        # check to_square
        # update boards
        pass

    '''
        A method to convert a given square into an index

        PARAMS
        square: string identifying the cell on the board to return

        RETURNS
        index value of the square on the board
    '''

    def _square_to_index(self, square):
        # get index equivalent of characters
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1

        # validate index
        if file < 0 or file > self.board - 1 or rank < 0 or rank > self.board - 1:
            raise ValueError("Invalid square notation")

        # return bitwise index of given square
        return rank * self.BOARD_LENGTH + file

    '''
        returns the board as a string
        
        RETURNS
        string representing the board
    '''

    def get_board_string(self):
        board_str = []

        # cycle through board cells and append what the cell contains
        for row in range(self.BOARD_LENGTH):
            for col in range(self.BOARD_LENGTH-1, -1, -1):
                board_str.append(self.get_piece(
                    row * self.BOARD_LENGTH + col) + ' ')
            board_str.append('\n')
        board_str = board_str[:-1]  # remove trailing new line

        return ''.join(board_str[::-1])


if __name__ == "__main__":
    start = datetime.datetime.now()
    board = Board()
    end = datetime.datetime.now()
    delta = end - start
    print(delta.total_seconds())
    print(board.get_board_string())

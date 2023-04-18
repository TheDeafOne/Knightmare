from .board_utils import BoardUtils as utils, BoardConstants as constants
from .move_generator import MoveGenerator

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
        # total board
        self.black_pieces = 0xffff << constants.BOARD_LENGTH * \
            (constants.BOARD_LENGTH - 2)
        self.white_pieces = 0xffff
        self.board = self.black_pieces | self.white_pieces
        self.en_passant_board = 0
        self.hilight_board = 0

        # sub-boards
        self.white_pawns = 0xff << constants.BOARD_LENGTH
        self.white_rooks = 0x81
        self.white_knights = 0x42
        self.white_bishops = 0x24
        self.white_king = 0x10
        self.white_queens = 0x8

        self.black_pawns = 0xff << constants.ACROSS_BOARD >> constants.BOARD_LENGTH
        self.black_rooks = 0x81 << constants.ACROSS_BOARD
        self.black_knights = 0x42 << constants.ACROSS_BOARD
        self.black_bishops = 0x24 << constants.ACROSS_BOARD
        self.black_king = 0x10 << constants.ACROSS_BOARD
        self.black_queens = 0x8 << constants.ACROSS_BOARD

        self.move_generator = MoveGenerator(self)

    '''
        sets a given piece to a given square

        PARAMS
        piece: a character identifying the type of chess piece (e.g. constants.WHITE_KING for white King, constants.WHITE_QUEEN for white Queen, etc.)
        square: string or integer index identifying the cell on the board needing to be set
    '''

    def set_piece(self, piece, square):
        if type(square) == str:
            index = utils.square_to_index(square)
        else:
            index = square

        # set piece location in temporary mask
        mask = 1 << index

        self.board |= mask
        # check if piece location corresponds with any of the sub-boards
        if piece == constants.EMPTY:
            # update main board
            self.board ^= mask

            # update white pieces
            self.white_pieces ^= mask
            self.white_pawns ^= mask
            self.white_rooks ^= mask
            self.white_knights ^= mask
            self.white_bishops ^= mask
            self.white_king ^= mask
            self.white_queens ^= mask

            # update black pieces
            self.black_pieces ^= mask
            self.black_pawns ^= mask
            self.black_rooks ^= mask
            self.black_knights ^= mask
            self.black_bishops ^= mask
            self.black_king ^= mask
            self.black_queens ^= mask
        elif piece == constants.HIGHLIGHT:
            self.hilight_board |= mask
        elif piece.isupper():
            self.white_pieces |= mask
            if piece == constants.WHITE_KING:
                self.white_king |= mask
            elif piece == constants.WHITE_QUEEN:
                self.white_queens |= mask
            elif piece == constants.WHITE_ROOK:
                self.white_rooks |= mask
            elif piece == constants.WHITE_BISHOP:
                self.white_bishops |= mask
            elif piece == constants.WHITE_KNIGHT:
                self.white_knights |= mask
            elif piece == constants.WHITE_PAWN:
                self.white_pawns |= mask
        else:
            self.black_pieces |= mask
            if piece == constants.BLACK_KING:
                self.black_king |= mask
            elif piece == constants.BLACK_QUEEN:
                self.black_queens |= mask
            elif piece == constants.BLACK_ROOK:
                self.black_rooks |= mask
            elif piece == constants.BLACK_BISHOP:
                self.black_bishops |= mask
            elif piece == constants.BLACK_KNIGHT:
                self.black_knights |= mask
            elif piece == constants.BLACK_PAWN:
                self.black_pawns |= mask

    '''
        gets the piece in the given square or index

        PARAMS
        square: string or integer index identifying the cell on the board to return

        RETURNS
        a character in the set of pieces if that piece is in the cell, the empty character otherwise
    '''

    def get_piece(self, square):
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)

        mask = 1 << index
        if self.hilight_board & mask:
            return constants.HIGHLIGHT
        elif self.white_pieces & mask:
            if self.white_king & mask:
                return constants.WHITE_KING
            elif self.white_queens & mask:
                return constants.WHITE_QUEEN
            elif self.white_rooks & mask:
                return constants.WHITE_ROOK
            elif self.white_bishops & mask:
                return constants.WHITE_BISHOP
            elif self.white_knights & mask:
                return constants.WHITE_KNIGHT
            elif self.white_pawns & mask:
                return constants.WHITE_PAWN
        else:
            if self.black_king & mask:
                return constants.BLACK_KING
            elif self.black_queens & mask:
                return constants.BLACK_QUEEN
            elif self.black_rooks & mask:
                return constants.BLACK_ROOK
            elif self.black_bishops & mask:
                return constants.BLACK_BISHOP
            elif self.black_knights & mask:
                return constants.BLACK_KNIGHT
            elif self.black_pawns & mask:
                return constants.BLACK_PAWN
        return constants.EMPTY

    '''
        moves the piece from cell 'from_square' to the cell 'to_square'

    '''

    def move_piece(self, from_square, to_square):
        # convert squares to indexes
        from_index = utils.square_to_index(from_square)
        to_index = utils.square_to_index(to_square)
        # check to_square
        to_mask = 1 << to_index
        to_remove = self.get_piece(to_square)

        if (self.white_pieces & to_mask):
            self.white_pieces ^= to_mask
            if (to_remove == constants.WHITE_KING):
                self.white_king &= ~to_mask; 
            elif (to_remove == constants.WHITE_QUEEN):
                self.white_queens &= ~to_mask
            elif (to_remove == constants.WHITE_ROOK):
                self.white_rooks &= ~to_mask
            elif (to_remove == constants.WHITE_BISHOP):
                self.white_bishops &= ~to_mask
            elif (to_remove == constants.WHITE_KNIGHT):
                self.white_knights &= ~to_mask
            elif (to_remove == constants.WHITE_PAWN):
                self.white_pawns &= ~to_mask
        elif (self.black_pieces & to_mask):
            self.black_pieces &= ~to_mask
            if (to_remove == constants.BLACK_KING):
                self.black_king &= ~to_mask
            elif (to_remove == constants.BLACK_QUEEN):
                self.black_queens &= ~to_mask
            elif (to_remove == constants.BLACK_ROOK):
                self.black_rooks &= ~to_mask
            elif (to_remove == constants.BLACK_BISHOP):
                self.black_bishops &= ~to_mask
            elif (to_remove == constants.BLACK_KNIGHT):
                self.black_knights &= ~to_mask
            elif (to_remove == constants.BLACK_PAWN):
                self.black_pawns &= ~to_mask

        # update boards
        from_mask = 1 << from_index
        self.board |= to_mask
        self.board &= ~from_mask
        if (self.white_pieces & from_index):
            self.white_pieces |= to_mask
            self.white_pieces &= ~from_mask
            if (self.white_king & from_mask):
                self.white_king |= to_mask
                self.white_king &= ~from_mask
            elif (self.white_queens & from_mask):
                self.white_queens |= to_mask
                self.white_queens &= ~from_mask
            elif (self.white_rooks & from_mask):
                self.white_rooks |= to_mask
                self.white_rooks &= ~from_mask
            elif (self.white_bishops & from_mask):
                self.white_bishops |= to_mask
                self.white_bishops &= ~from_mask
            elif (self.white_pawns & from_mask):
                self.white_pawns |= to_mask
                self.white_pawns &= ~from_mask
        else:
            self.black_pieces |= to_mask
            self.black_pieces &= ~ from_mask
            if (self.black_king & ~from_mask):
                self.black_king |= to_mask
                self.black_king &= ~from_mask
            elif (self.black_queens & from_mask):
                self.black_queens |= to_mask
                self.black_queens &= ~from_mask
            elif (self.black_rook & from_mask):
                self.black_rooks |= to_mask
                self.black_rooks &= ~from_mask
            elif (self.black_bishops & from_mask):
                self.black_bishops |= to_mask
                self.black_bishops &= ~to_mask
            elif (self.black_pawns & from_mask):
                self.black_pawns |= to_mask
                self.black_pawns &= ~from_mask

    def get_moves(self, square):
        return self.move_generator.generate_moves(square)

    def hilight_moves(self, moves):
        for move in moves:
            move_to = move[1]
            self.set_piece(constants.HIGHLIGHT, move_to)

    '''
        returns the board as a string
        
        RETURNS
        string representing the board
    '''

    def get_board_string(self):
        board_str = []

        # cycle through board cells and append what the cell
        for row in range(constants.BOARD_LENGTH):
            for col in range(constants.BOARD_LENGTH-1, -1, -1):
                board_str.append(self.get_piece(
                    row * constants.BOARD_LENGTH + col) + ' ')
            board_str.append(str(row+1) + '| ')
            board_str.append('\n')
        board_str = board_str[:-1]  # remove trailing new line
        board_str.append('   ' + '\033[4m' + 'a b c d e f g h' + '\033[0m \n')

        return ''.join(board_str[::-1])

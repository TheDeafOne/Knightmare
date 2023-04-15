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
        self.EMPTY = ' '

        # total board
        self.black_pieces = 0xffff << self.BOARD_LENGTH * \
            (self.BOARD_LENGTH - 2)
        self.white_pieces = 0xffff
        self.board = self.black_pieces | self.white_pieces
        self.en_passant_board = 0

        # sub-boards
        # white pieces
        self.WHITE_PAWN_LABEL = 'P'
        self.WHITE_ROOK_LABEL = 'R'
        self.WHITE_KNIGHT_LABEL = 'N'
        self.WHITE_BISHOP_LABEL = 'B'
        self.WHITE_QUEEN_LABEL = 'Q'
        self.WHITE_KING_LABEL = 'K'

        self.white_pawns = 0xff << self.BOARD_LENGTH
        self.white_rooks = 0x81
        self.white_knights = 0x42
        self.white_bishops = 0x24
        self.white_king = 0x10
        self.white_queens = 0x8

        # black pieces
        self.BLACK_PAWN_LABEL = 'p'
        self.BLACK_ROOK_LABEL = 'r'
        self.BLACK_KNIGHT_LABEL = 'n'
        self.BLACK_BISHOP_LABEL = 'b'
        self.BLACK_QUEEN_LABEL = 'q'
        self.BLACK_KING_LABEL = 'k'

        self.black_pawns = 0xff << self.ACROSS_BOARD >> self.BOARD_LENGTH
        self.black_rooks = 0x81 << self.ACROSS_BOARD
        self.black_knights = 0x42 << self.ACROSS_BOARD
        self.black_bishops = 0x24 << self.ACROSS_BOARD
        self.black_king = 0x10 << self.ACROSS_BOARD
        self.black_queens = 0x8 << self.ACROSS_BOARD

    '''
        sets a given piece to a given square

        PARAMS
        piece: a character identifying the type of chess piece (e.g. self.WHITE_KING_LABEL for white King, self.WHITE_QUEEN_LABEL for white Queen, etc.)
        square: string or integer index identifying the cell on the board needing to be set
    '''

    def set_piece(self, piece, square):
        if type(square) == str:
            index = self._square_to_index(square)
        else:
            index = square

        # set piece location in temporary mask
        mask = 1 << index

        self.board |= mask
        # check if piece location corresponds with any of the sub-boards
        if piece == self.EMPTY:
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
        elif piece.isupper():
            self.white_pieces |= mask
            if piece == self.WHITE_KING_LABEL:
                self.white_king |= mask
            elif piece == self.WHITE_QUEEN_LABEL:
                self.white_queens |= mask
            elif piece == self.WHITE_ROOK_LABEL:
                self.white_rooks |= mask
            elif piece == self.WHITE_BISHOP_LABEL:
                self.white_bishops |= mask
            elif piece == self.WHITE_KNIGHT_LABEL:
                self.white_knights |= mask
            elif piece == self.WHITE_PAWN_LABEL:
                self.white_pawns |= mask
        else:
            self.black_pieces |= mask
            if piece == self.BLACK_KING_LABEL:
                self.black_king |= mask
            elif piece == self.BLACK_QUEEN_LABEL:
                self.black_queens |= mask
            elif piece == self.BLACK_ROOK_LABEL:
                self.black_rooks |= mask
            elif piece == self.BLACK_BISHOP_LABEL:
                self.black_bishops |= mask
            elif piece == self.BLACK_KNIGHT_LABEL:
                self.black_knights |= mask
            elif piece == self.BLACK_PAWN_LABEL:
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
        if self.white_pieces & mask:
            if self.white_king & mask:
                return self.WHITE_KING_LABEL
            elif self.white_queens & mask:
                return self.WHITE_QUEEN_LABEL
            elif self.white_rooks & mask:
                return self.WHITE_ROOK_LABEL
            elif self.white_bishops & mask:
                return self.WHITE_BISHOP_LABEL
            elif self.white_knights & mask:
                return self.WHITE_KNIGHT_LABEL
            elif self.white_pawns & mask:
                return self.WHITE_PAWN_LABEL
        else:
            if self.black_king & mask:
                return self.BLACK_KING_LABEL
            elif self.black_queens & mask:
                return self.BLACK_QUEEN_LABEL
            elif self.black_rooks & mask:
                return self.BLACK_ROOK_LABEL
            elif self.black_bishops & mask:
                return self.BLACK_BISHOP_LABEL
            elif self.black_knights & mask:
                return self.BLACK_KNIGHT_LABEL
            elif self.black_pawns & mask:
                return self.BLACK_PAWN_LABEL
        return self.EMPTY

    '''
        moves the piece from cell 'from_square' to the cell 'to_square'

    '''

    def move_piece(self, from_square, to_square):
        # convert squares to indexes
        # check to_square
        # update boards
        pass

    def get_moves(self, square):
        moves = []
        index = self._square_to_index(square)
        piece = self.get_piece(index)

        if piece == self.EMPTY:
            return moves

        # Generate moves based on piece type
        if piece == self.WHITE_PAWN_LABEL or piece == self.BLACK_PAWN_LABEL:
            moves.extend(map(lambda x: (square, x),
                         self.get_pawn_moves(index)))
        elif piece == self.WHITE_KNIGHT_LABEL or piece == self.BLACK_KNIGHT_LABEL:
            moves.extend(map(lambda x: (square, x),
                         self.get_knight_moves(index)))
        # elif piece in (self.WHITE_BISHOP_LABEL, 'b'):
        #     moves = self._get_bishop_moves(index)
        # elif piece in (self.WHITE_ROOK_LABEL, 'r'):
        #     moves = self._get_rook_moves(index)
        # elif piece in (self.WHITE_QUEEN_LABEL, self.BLACK_QUEEN_LABEL):
        #     moves = self._get_queen_moves(index)
        # elif piece in (self.WHITE_KING_LABEL, self.BLACK_KING_LABEL):
        #     moves = self._get_king_moves(index)

        return moves

    def get_pawn_moves(self, index):
        moves = []
        mask = 1 << index

    

        # check if piece is white
        if mask & self.white_pieces:
            # Check one square forward
            if not self.board & (mask << 8):
                moves.append(self._index_to_square(index + 8))

                # Check two squares forward on first move
                if index < 16 and not self.board & (mask << 16):
                    moves.append(self._index_to_square(index + 16))

            # Check diagonal captures
            if index % 8 < 7 and self.black_pieces & (mask << 9):
                moves.append(self._index_to_square(index + 9))
            if index % 8 > 0 and self.black_pieces & (mask << 7):
                moves.append(self._index_to_square(index + 7))

            # Check en passant capture
            if self.en_passant_board & mask:
                if index % 8 < 7 and self.black_pieces & (mask << 1):
                    moves.append(self._index_to_square(index + 9))
                if index % 8 > 0 and self.black_pieces & (mask >> 1):
                    moves.append(self._index_to_square(index + 7))

        else:
            # Check one square forward
            if not self.black_pieces & (mask >> 8):
                moves.append(self._index_to_square(index - 8))

                # Check two squares forward on first move
                if index > 47 and not self.black_pieces & (mask >> 16):
                    moves.append(self._index_to_square(index - 16))

            # Check diagonal captures
            if index % 8 < 7 and self.white_pieces & (mask >> 7):
                moves.append(self._index_to_square(index - 7))
            if index % 8 > 0 and self.white_pieces & (mask >> 9):
                moves.append(self._index_to_square(index - 9))

            # Check en passant capture
            if self.en_passant_board & mask:
                if index % 8 < 7 and self.white_pieces & (mask << 1):
                    moves.append(self._index_to_square(index - 7))
                if index % 8 > 0 and self.white_pieces & (mask >> 1):
                    moves.append(self._index_to_square(index - 9))

        return moves

    '''
        Generates all the possible moves for a knight in a given square

        Note the difference knight move types are referenced to as follows:
        * right down: two squares right, one square down
        * right up: two squares right, one square up
        * left down: two squares left, one square down
        * left up: two squares left, one square up
        * down left: two squares down, one square left
        * down right: two squares down, one square right
        * up left: two squares up, one square left
        * up right: two squares up, one square right

        PARAMS
        index: an integer representing the square that the piece is located in

        RETURNS
        all the possible knight moves for the piece in the given square, given as a list of square indexes
    '''

    def get_knight_moves(self, index):
        moves = []
        mask = 1 << index

        piece_color = self._get_piece_color(self.get_piece(index))

        # right L shape moves
        # validate column moveable position
        if index % 8 < 6:
            # validate row moveable position 
            if index // 8 > 0 and not mask >> 6 & piece_color:
                # right down
                moves.append(self._index_to_square(index - 6))
            if index // 8 < 7 and not mask << 10 & piece_color:
                # right up
                moves.append(self._index_to_square(index + 10))

        # left L shape moves
        if index % 8 > 1:
            if index // 8 > 0 and not mask >> 10 & piece_color:
                # left down
                moves.append(self._index_to_square(index - 10))
            if index // 8 < 7 and not mask << 6 & piece_color:
                # left up
                moves.append(self._index_to_square(index + 6))

        # up L shape moves
        if index // 8 > 1:
            if index % 8 > 0 and not mask >> 17 & piece_color:
                # down left
                moves.append(self._index_to_square(index - 17))
            if index % 8 < 7 and not mask >> 15 & piece_color:
                # down right
                moves.append(self._index_to_square(index - 15))

        # down L shape moves
        if index // 8 < 6:
            if index % 8 > 0 and not mask << 15 & piece_color:
                # up left
                moves.append(self._index_to_square(index + 15))
            if index % 8 < 7 and not mask << 17 & piece_color:
                # up right
                moves.append(self._index_to_square(index + 17))

        return moves

    def _get_piece_color(self, piece):
        return self.white_pieces if piece in ('KQRNBP') else self.black_pieces

    def _get_other_piece_color(self, piece):
        return self.black_pieces if piece in ('KQRNBP') else self.white_pieces

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

    def _index_to_square(self, index):
        row = index // self.BOARD_LENGTH + 1
        col = index % self.BOARD_LENGTH
        return chr(ord('a') + col) + str(row)

    '''
        returns the board as a string
        
        RETURNS
        string representing the board
    '''

    def get_board_string(self):
        board_str = []

        # cycle through board cells and append what the cell
        for row in range(self.BOARD_LENGTH):
            for col in range(self.BOARD_LENGTH-1, -1, -1):
                board_str.append(self.get_piece(
                    row * self.BOARD_LENGTH + col) + ' ')
            board_str.append(str(row+1) + '| ')
            board_str.append('\n')
        board_str = board_str[:-1]  # remove trailing new line
        board_str.append('   ' + '\033[4m' + 'a b c d e f g h' + '\033[0m \n')

        return ''.join(board_str[::-1])


if __name__ == "__main__":
    start = datetime.datetime.now()
    board = Board()
    end = datetime.datetime.now()
    delta = end - start

    print(delta.total_seconds())

    board.set_piece('n', 'h3')

    print(board.get_board_string())
    print(board.get_moves('h3'))

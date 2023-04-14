import datetime


class Board:
    BOARD_LENGTH = 8
    ACROSS_BOARD = BOARD_LENGTH ** 2 - BOARD_LENGTH

    def __init__(self):

        # total board
        self.board = 0xffff << self.BOARD_LENGTH * (self.BOARD_LENGTH - 2)
        self.board |= 0xffff

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

    def set_piece(self, piece, square):
        if type(square) == str:
            index = self._square_to_index(square)
        else:
            index = square
        mask = 1 << index
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

    def move_piece(self, from_square, to_square):
        pass

    def _square_to_index(self, square):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1

        if file < 0 or file > self.board - 1 or rank < 0 or rank > self.board - 1:
            raise ValueError("Invalid square notation")

        return rank * self.BOARD_LENGTH + file

    def get_board_string(self):
        board_str = []

        for row in range(self.BOARD_LENGTH):
            for col in range(self.BOARD_LENGTH-1, -1, -1):
                board_str.append(self.get_piece(
                    row * self.BOARD_LENGTH + col) + ' ')
            board_str.append('\n')
        return ''.join(board_str[::-1])


if __name__ == "__main__":
    start = datetime.datetime.now()
    board = Board()
    end = datetime.datetime.now()
    delta = end - start
    print(delta.total_seconds())
    print(board.get_board_string())

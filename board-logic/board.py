import datetime

class Board:
    BOARD_LENGTH = 8
    def __init__(self):
        # black pieces
        # pawns
        self.black_pawns = 255 << self.BOARD_LENGTH * (self.BOARD_LENGTH - 2)
        # rooks
        self.black_rooks = 1 << self.BOARD_LENGTH * (self.BOARD_LENGTH - 1)
        self.black_rooks |= 1 << self.BOARD_LENGTH * self.BOARD_LENGTH - 1
        # knights
        self.black_knights = 1 << self.BOARD_LENGTH * (self.BOARD_LENGTH - 1) + 1
        self.black_knights |= 1 << self.BOARD_LENGTH * self.BOARD_LENGTH - 2
        # bishops
        self.black_bishops = 1 << self.BOARD_LENGTH * (self.BOARD_LENGTH - 1) + 2
        self.black_bishops |= 1 << self.BOARD_LENGTH * self.BOARD_LENGTH - 3
        # royalty
        self.black_king = 1 << self.BOARD_LENGTH * (self.BOARD_LENGTH - 1) + 4
        self.black_queens = 1 << self.BOARD_LENGTH * self.BOARD_LENGTH - 5

        # white pieces
        # pawns
        self.white_pawns = 255 << self.BOARD_LENGTH
        # rooks
        self.white_rooks = 1
        self.white_rooks |= 1 << self.BOARD_LENGTH - 1
        # knights
        self.white_knights = 1 << 1
        self.white_knights |= 1 << self.BOARD_LENGTH - 2
        # bishops
        self.white_bishops = 1 << 2
        self.white_bishops |= 1 << self.BOARD_LENGTH - 3
        # royalty
        self.white_queens = 1 << 3
        self.white_king = 1 << 4

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

        if file < 0 or file > 7 or rank < 0 or rank > 7:
            raise ValueError("Invalid square notation")
        
        return rank * self.BOARD_LENGTH + file

    def get_board_string(self):
        board_str = ''

        for row in range(8):
            for col in range(8):
                board_str += self.get_piece(row * 8 + col) + ' '
            board_str += '\n'
        return board_str


if __name__ == "__main__":
    start = datetime.datetime.now()
    board = Board()
    end = datetime.datetime.now()
    delta = end - start
    print(delta.total_seconds())
    print(board.get_board_string())

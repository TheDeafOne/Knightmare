class Board:
    def __init__(self):
        self.white_pieces = 0
        self.black_pieces = 0
        self.white_king = 0
        self.black_king = 0
        self.white_queen = 0
        self.black_queen = 0
        self.white_rook = 0
        self.black_rook = 0
        self.white_bishop = 0
        self.black_bishop = 0
        self.white_knight = 0
        self.black_knight = 0
        self.white_pawn = 0
        self.black_pawn = 0

    def set_piece(self, piece, square):
        mask = 1 << square
        if piece.isupper():
            self.white_pieces |= mask
            if piece == 'K':
                self.white_king |= mask
            elif piece == 'Q':
                self.white_queen |= mask
            elif piece == 'R':
                self.white_rook |= mask
            elif piece == 'B':
                self.white_bishop |= mask
            elif piece == 'N':
                self.white_knight |= mask
            elif piece == 'P':
                self.white_pawn |= mask
        else:
            self.black_pieces |= mask
            if piece == 'k':
                self.black_king |= mask
            elif piece == 'q':
                self.black_queen |= mask
            elif piece == 'r':
                self.black_rook |= mask
            elif piece == 'b':
                self.black_bishop |= mask
            elif piece == 'n':
                self.black_knight |= mask
            elif piece == 'p':
                self.black_pawn |= mask

    def get_piece(self, square):
        mask = 1 << square
        if self.white_pieces & mask:
            if self.white_king & mask:
                return 'K'
            elif self.white_queen & mask:
                return 'Q'
            elif self.white_rook & mask:
                return 'R'
            elif self.white_bishop & mask:
                return 'B'
            elif self.white_knight & mask:
                return 'N'
            elif self.white_pawn & mask:
                return 'P'
        elif self.black_pieces & mask:
            if self.black_king & mask:
                return 'k'
            elif self.black_queen & mask:
                return 'q'
            elif self.black_rook & mask:
                return 'r'
            elif self.black_bishop & mask:
                return 'b'
            elif self.black_knight & mask:
                return 'n'
            elif self.black_pawn & mask:
                return 'p'
        return ' '
    
    def _square_to_index(square):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        if file < 0 or file > 7 or rank < 0 or rank > 7:
            raise ValueError("Invalid square notation")
        return rank * 8 + file
    
    def get_board_string(self):
        board_str = ''
        for row in range(8):
            for col in range(8):
                board_str += self.get_piece(row * 8 + col)
            board_str += '\n'
        return board_str
    
if __name__ == "__main__":
    board = Board()
    board_string = board.get_board_string()

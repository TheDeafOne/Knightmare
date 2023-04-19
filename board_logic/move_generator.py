from .board_utils import BoardUtils as utils, BoardConstants as constants
# from .board import Board


class MoveGenerator:
    def __init__(self, board):
        self.board = board
        self.opponent = 0
        self.player = 0

    def generate_moves(self, square):
        index = utils.square_to_index(square)
        piece = self.board.get_piece(index)
        self.opponent = self._get_opponent_piece_color(piece)
        self.player = self._get_piece_color(piece)

        # Generate moves based on piece type
        if piece == constants.WHITE_PAWN or piece == constants.BLACK_PAWN:
            return self._get_pawn_moves(index)
        elif piece == constants.WHITE_KNIGHT or piece == constants.BLACK_KNIGHT:
            return self._get_knight_moves(index)
        elif piece == constants.WHITE_BISHOP or piece == constants.BLACK_BISHOP:
            return self._get_bishop_moves(index)
        elif piece == constants.WHITE_ROOK or piece == constants.BLACK_ROOK:
            return self._get_rook_moves(index)
        elif piece == constants.WHITE_QUEEN or piece == constants.BLACK_QUEEN:
            return self._get_queen_moves(index)
        elif piece == constants.WHITE_KING or piece == constants.BLACK_KING:
            return self._get_king_moves(index)

        return 0  # square given was empty

    def _get_pawn_moves(self, index):
        # moves = []
        moves = 0
        mask = 1 << index
        col = index % 8
        # check if piece is white
        if self.opponent == self.board.black_pieces:
            # Check one square forward
            if not self.board.board & (mask << 8):
                # moves.append(utils.index_to_square(index + 8))
                moves |= mask << 8

                # Check two squares forward on first move
                if index < 16 and not self.board.board & (mask << 16):
                    # moves.append(utils.index_to_square(index + 16))
                    moves |= mask << 16

            # Check diagonal captures
            if col < 7 and self.board.black_pieces & (mask << 9):
                # moves.append(utils.index_to_square(index + 9))
                moves |= mask << 9
            if col > 0 and self.board.black_pieces & (mask << 7):
                # moves.append(utils.index_to_square(index + 7))
                moves |= mask << 7

            # Check en passant capture
            if self.board.en_passant_board & mask:
                if col < 7 and self.board.black_pieces & (mask << 1):
                    # moves.append(utils.index_to_square(index + 9))
                    moves |= mask << 1
                if col > 0 and self.board.black_pieces & (mask >> 1):
                    # moves.append(utils.index_to_square(index + 7))
                    moves |= mask >> 1
        else:
            # Check one square forward
            if not self.board.board & (mask >> 8):
                # moves.append(utils.index_to_square(index - 8))
                moves |= mask >> 8

                # Check two squares forward on first move
                if index > 47 and not self.board.board & (mask >> 16):
                    # moves.append(utils.index_to_square(index - 16))
                    moves |= mask >> 8

            # Check diagonal captures
            if col < 7 and self.board.white_pieces & (mask >> 7):
                # moves.append(utils.index_to_square(index - 7))
                moves |= mask >> 7
            if col > 0 and self.board.white_pieces & (mask >> 9):
                # moves.append(utils.index_to_square(index - 9))
                moves |= mask >> 9

            # Check en passant capture
            if self.board.en_passant_board & mask:
                if col < 7 and self.board.white_pieces & (mask << 1):
                    # moves.append(utils.index_to_square(index - 7))
                    moves |= mask << 1
                if col > 0 and self.board.white_pieces & (mask >> 1):
                    # moves.append(utils.index_to_square(index - 9))
                    moves |= mask >> 1

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

    def _get_knight_moves(self, index):
        moves = 0
        mask = 1 << index
        col, row = index % 8, index // 8

        # right L shape moves
        # validate column moveable position
        if col < 6:
            # validate row moveable position
            if row > 0 and not mask >> 6 & self.player:
                # right down
                moves |= mask >> 6
            if row < 7 and not mask << 10 & self.player:
                # right up
                moves |= mask << 10

        # left L shape moves
        if col > 1:
            if row > 0 and not mask >> 10 & self.player:
                # left down
                moves |= mask >> 10
            if row < 7 and not mask << 6 & self.player:
                # left up
                moves |= mask << 6

        # up L shape moves
        if row > 1:
            if col > 0 and not mask >> 17 & self.player:
                # down left
                moves |= mask >> 17
            if col < 7 and not mask >> 15 & self.player:
                # down right
                moves |= mask >> 15

        # down L shape moves
        if row < 6:
            if col > 0 and not mask << 15 & self.player:
                # up left
                moves |= mask << 15
            if col < 7 and not mask << 17 & self.player:
                # up right
                moves |= mask << 17

        return moves

    def _get_bishop_moves(self, index):
        col, row = index % 8, index // 8
        moves = 0
        
        # Check northeast moves
        for i in range(1, min(8 - row, 8 - col)):
            new_index = index + i * 9
            if self._is_empty(new_index):
                moves |= 1 << new_index
            elif self._is_opponent(new_index):
                moves |= 1 << new_index
                break
            else:
                break

        # Check northwest moves
        for i in range(1, min(8 - row, col + 1)):
            new_index = index + i * 7
            if self._is_empty(new_index):
                moves |= 1 << new_index
            elif self._is_opponent(new_index):
                moves |= 1 << new_index
                break
            else:
                break

        # Check southeast moves
        for i in range(1, min(row + 1, 8 - col)):
            new_index = index - i * 7
            if self._is_empty(new_index):
                moves |= 1 << new_index
            elif self._is_opponent(new_index):
                moves |= 1 << new_index
                break
            else:
                break

        # Check southwest moves
        for i in range(1, min(row + 1, col + 1)):
            new_index = index - i * 9
            if self._is_empty(new_index):
                moves |= 1 << new_index
            elif self._is_opponent(new_index):
                moves |= 1 << new_index
                break
            else:
                break
        return moves

    def _get_rook_moves(self, index):
        moves = 0

        # Get all possible moves to the right
        for i in range(index + 1, index // 8 * 8 + 8):
            if self._is_empty(i):
                moves |= 1 << i
            elif self._is_opponent(i):
                moves |= 1 << i
                break
            else:
                break

        # Get all possible moves to the left
        for i in range(index - 1, index // 8 * 8 - 1, -1):
            if self._is_empty(i):
                moves |= 1 << i
            elif self._is_opponent(i):
                moves |= 1 << i
                break
            else:
                break

        # Get all possible moves going up
        for i in range(index + 8, 64, 8):
            if self._is_empty(i):
                moves |= 1 << i
            elif self._is_opponent(i):
                moves |= 1 << i
                break
            else:
                break

        # Get all possible moves going down
        for i in range(index - 8, -1, -8):
            if self._is_empty(i):
                moves |= 1 << i
            elif self._is_opponent(i):
                moves |= 1 << i
                break
            else:
                break

        return moves

    def _get_queen_moves(self, index):
        moves = self._get_bishop_moves(index)
        moves |= self._get_rook_moves(index)
        return moves

    def _get_king_moves(self, index):
        moves = 0
        for i in [1, 7, 8, 9]:
            top_index = index + i
            bottom_index = index - i
            top_mask = 1 << top_index
            bottom_mask = 1 << bottom_index
            if top_index >= 0 and not top_mask & self.player and not self._in_check(top_index, index):
                moves |= 1 << top_index
            if bottom_index >= 0 and not bottom_mask & self.player and not self._in_check(bottom_index, index):
                moves |= 1 << bottom_index

        return moves

    def _in_check(self, index, relative_to):
        if not self._is_next_to(index, relative_to):
            return True
        
        if self.opponent == self.board.black_pieces:
            pawns = self.board.black_pawns
            bishops = self.board.black_bishops
            knights = self.board.black_knights
            rooks = self.board.black_rooks
            queens = self.board.black_queens
            king = self.board.black_king
            self.opponent = self.board.black_pieces
            self.player = self.board.white_pieces
        else:
            pawns = self.board.white_pawns
            bishops = self.board.white_bishops
            knights = self.board.white_knights
            rooks = self.board.white_rooks
            queens = self.board.white_queens
            king = self.board.white_king
            self.opponent = self.board.white_pieces
            self.player = self.board.black_pieces
       
        
        if pawns & self._get_pawn_moves(index):
            print('in check from pawns')
            return True
        if bishops & self._get_bishop_moves(index):
            return True
        if knights & self._get_knight_moves(index):
            return True
        if rooks & self._get_rook_moves(index):
            return True
        if queens & self._get_queen_moves(index):
            return True

        tentative_king_positions = 0
        for i in [1, 7, 8, 9]:
            top_index = index + i
            bottom_index = index - i
            if self._is_next_to(index, top_index):
                tentative_king_positions |= 1 << top_index
                
            if bottom_index >= 0 and self._is_next_to(index, bottom_index):
                tentative_king_positions |= 1 << bottom_index
                
        if tentative_king_positions & king:
            return True
        # check for other king moves
        return False
    
    def _is_next_to(self, from_index, to_index):
        from_col, from_row = from_index % 8, from_index // 8
        to_col, to_row = to_index % 8, to_index // 8
        if abs(from_col - to_col) > 1 or abs(from_row - to_row) > 1:
            return False
        return True
        
    def _is_empty(self, square):
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)
        return not self.board.board & 1 << index

    def _is_opponent(self, square):
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)
        return bool(self.opponent & 1 << index)

    def _get_piece_color(self, piece):
        return self.board.white_pieces if piece in ('KQRNBP') else self.board.black_pieces

    def _get_opponent_piece_color(self, piece):
        return self.board.black_pieces if piece in ('KQRNBP') else self.board.white_pieces

    def _get_move_paths(self, from_square, moves):
        return [(from_square, to_square) for to_square in moves]

from .board_utils import BoardUtils as utils, BoardConstants as constants


class MoveGenerator:
    '''
        A helper class used to generate moves and manage the various processes around move generation, including
        managing the moves for a king based on whether those moves will put the king in check or not



        ATTRIBUTES

        board: the integer representation of the current board
        opponent: the integer representation of the opponent pieces
        player: the integer representation of the player pieces



        METHODS

        generate_moves(square)
            generates the moves the piece in the given square could take
            returns an integer mask representation of the possible moves the piece could take

        _get_pawn_moves(index)
            gets the possible pawn moves at the given index
            return those moves as an integer mask

        _get_rook_moves(index)
           gets the possible rook moves at the given index
           returns those moves as an integer mask

        _get_knight_moves(index)
            gets the possible knight moves at the given index
            returns those moves as an integer mask

        _get_bishop_moves(index)
            gets the possible bishop moves at the given index
            returns those moves as an integer mask

        _get_queen_moves(index)
            gets the possible queen moves at the given index
            returns those moves as an integer mask

        _get_king_moves(index)
            gets the possible king moves at the given index
            returns those moves as an integer mask

        _is_next_to(from_index, to_index)
            identifies if the piece in from_index is next to the piece in the to_index (board-wise)
            returns True if the from_index is next to to_index, False otherwise

        _is_empty(square)
            determines if there is a piece in the given square
            return True if the square is empty, False otherwise

        _is_opponent(square)
            determines if the piece in the given square is an opponent to the current player
            returns True if the piece is an opponent piece, False otherwise

        _get_piece_color(piece)
            determines the color of the given piece
            returns the piece's color set

        _get_opponent_piece_color(piece)
            determines the color the given piece's opponent
            returns the piece's opponent color

        _get_moves_paths(from_square, moves)
            parses the moves of a given square into a list of of tuples 
            returns a list such that each element is a tuple (a, b) 
            where a is the square from which the piece will move from and b is a square that the piece could move to
    '''

    def __init__(self, board):
        self.board = board
        self.opponent = board.black_pieces
        self.player = board.white_pieces
        self.piece_move_map = {
            constants.WHITE_BISHOP: self._get_bishop_moves,
            constants.WHITE_PAWN: self._get_pawn_moves,
            constants.WHITE_KNIGHT: self._get_knight_moves,
            constants.WHITE_ROOK: self._get_rook_moves,
            constants.WHITE_QUEEN: self._get_queen_moves,
            constants.WHITE_KING: self._get_king_moves
        }

    '''
        gets all the possible moves the piece in the given square could possibly make, if any
        
        PARAMS
        square: an alphanumeric representation of the cell location on the board

        RETURNS
        an integer map of the possible moves the piece at the given square could make
    '''

    def generate_moves(self, square, is_swapped=False):
        # convert square to index and get piece
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)
        piece = self.board.get_piece(index)

        # initialize player and opponent piece sets
        if (is_swapped):
            self.opponent = self.board.get_piece_color(piece)
            self.player = self.board.get_opponent_piece_color(piece)
        else:
            self.opponent = self.board.get_opponent_piece_color(piece)
            self.player = self.board.get_piece_color(piece)

        move_board = 0
        # Generate moves based on piece type and update move_board accordingly
        if piece == constants.WHITE_PAWN or piece == constants.BLACK_PAWN:
            move_board = self._get_pawn_moves(index)
        elif piece == constants.WHITE_KNIGHT or piece == constants.BLACK_KNIGHT:
            move_board = self._get_knight_moves(index)
        elif piece == constants.WHITE_BISHOP or piece == constants.BLACK_BISHOP:
            move_board = self._get_bishop_moves(index)
        elif piece == constants.WHITE_ROOK or piece == constants.BLACK_ROOK:
            move_board = self._get_rook_moves(index)
        elif piece == constants.WHITE_QUEEN or piece == constants.BLACK_QUEEN:
            move_board = self._get_queen_moves(index)
        elif piece == constants.WHITE_KING or piece == constants.BLACK_KING:
            move_board = self._get_king_moves(index)
        king_board = self.board.white_king if self.player == self.board.white_pieces else self.board.black_king
        if king_board == 0:
            return 0
        king_index = utils.singleton_board_to_index(king_board)

        if (is_swapped):
            return move_board

        # check if the king is in check
        # 0 is attacking piece, 1 is line of attack
        is_king_in_check = self._in_check(king_index, king_index)

        if is_king_in_check[0]:
            # get attacking index/piece
            attacking_index = utils.singleton_board_to_index(
                is_king_in_check[0])
            attacking_piece = self.board.get_piece(attacking_index)

            # multiple attacking pieces, double check is impossible to get out of
            if attacking_index < 0:
                return 0

            # get line of attack
            attacking_moves = self.piece_move_map[attacking_piece.upper()](
                attacking_index)
            blocking_moves = is_king_in_check[1] & (
                is_king_in_check[0] | attacking_moves)
            actual_moves = move_board

            # only allow moves that blocks the check
            move_board &= blocking_moves

            # king can still move and attack as long as it doesn't cause a check
            if piece == constants.BLACK_KING or piece == constants.WHITE_KING:
                move_board |= actual_moves
        else:
            # verify that the piece is not pinned, and handle accordingly if it is
            is_piece_pinned = self._is_pinned(index)
            if is_piece_pinned[1]:
                # only moves available are within the line of attack or the attacking piece
                move_board &= is_piece_pinned[1]
                move_board |= is_piece_pinned[0]

        return move_board

    '''
        gets all the possible moves a pawn at the given index could make
        Note that this includes en passant
        
        PARAMS
        index: an integer representing the location of the pawn on the board

        RETURNS
        an integer map of the possible moves the pawn at the given index could make
    '''

    def _get_pawn_moves(self, index):
        moves = 0
        mask = 1 << index
        col = index % 8
        # check if piece is white
        if self.opponent == self.board.black_pieces:
            # Check one square forward
            if not self.board.board & (mask << 8):
                moves |= mask << 8

                # Check two squares forward on first move
                if index < 16 and not self.board.board & (mask << 16):
                    moves |= mask << 16

            # Check diagonal captures
            if col < 7 and self.board.black_pieces & (mask << 9):
                moves |= mask << 9
            if col > 0 and self.board.black_pieces & (mask << 7):
                moves |= mask << 7

            # Check en passant capture
            if self.board.en_passant_board & mask:
                if col < 7 and self.board.black_pieces & (mask << 1):
                    moves |= mask << 1
                if col > 0 and self.board.black_pieces & (mask >> 1):
                    moves |= mask >> 1
        else:
            # Check one square forward
            if not self.board.board & (mask >> 8):
                moves |= mask >> 8

                # Check two squares forward on first move
                if index > 47 and not self.board.board & (mask >> 16):
                    moves |= mask >> 16

            # Check diagonal captures
            if col < 7 and self.board.white_pieces & (mask >> 7):
                moves |= mask >> 7
            if col > 0 and self.board.white_pieces & (mask >> 9):
                moves |= mask >> 9

            # Check en passant capture
            if self.board.en_passant_board & mask:
                if col < 7 and self.board.white_pieces & (mask << 1):
                    moves |= mask << 1
                if col > 0 and self.board.white_pieces & (mask >> 1):
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

    '''
        gets all the possible moves a bishop at the given index could make
        
        PARAMS
        index: an integer representing the location of the bishop on the board

        RETURNS
        an integer map of the possible moves the bishop at the given index could make
    '''

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
                # stopped by an opponent
                break
            else:
                # stopped by a player piece
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

    '''
        gets all the possible moves a rook at the given index could make
        
        PARAMS
        index: an integer representing the location of the rook on the board

        RETURNS
        an integer map of the possible moves the rook at the given index could make
    '''

    def _get_rook_moves(self, index):
        moves = 0
        # Get all possible moves to the right
        for i in range(index + 1, index // 8 * 8 + 8):
            if self._is_empty(i):
                moves |= 1 << i
            elif self._is_opponent(i):
                moves |= 1 << i
                # stopped by opponent
                break
            else:
                # stopped by player piece
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

    '''
        gets all the possible moves a queen at the given index could make
        
        PARAMS
        index: an integer representing the location of the queen on the board

        RETURNS
        an integer map of the possible moves the queen at the given index could make
    '''

    def _get_queen_moves(self, index):
        # queen moves is equivalent to rook moves | bishop moves of given index
        moves = self._get_bishop_moves(index)
        moves |= self._get_rook_moves(index)
        return moves

    '''
        gets all the possible moves a king at the given index could make
        
        PARAMS
        index: an integer representing the location of the king on the board

        RETURNS
        an integer map of the possible moves the king at the given index could make
    '''

    def _get_king_moves(self, index):
        # set up a temporary king piece to get the king color and further management when swapping/replaced
        tmp_king = self.board.get_piece(index)
        self.board.set_piece(constants.EMPTY, index)

        # ongoing movement collection for king
        moves = 0

        # get all positions around king and determine if the king can move into each position
        for i in [1, 7, 8, 9]:
            top_index = index + i
            bottom_index = index - i
            top_mask = 1 << top_index
            if bottom_index >= 0:
                bottom_mask = 1 << bottom_index
            if top_index >= 0 and not top_mask & self.player and not self._in_check(top_index, index)[0]:
                moves |= 1 << top_index
            if bottom_index >= 0 and not bottom_mask & self.player and not self._in_check(bottom_index, index)[0]:
                moves |= 1 << bottom_index

        # reassign king to given index now that all feasible positions were found
        self.board.set_piece(tmp_king, index)

        return moves

    '''
        Determines whether moving the king to a given index will put the king in check or not.
        This is done by having the index imitate all the possible piece moves (e.g. pawn moves, bishops moves, etc.)
        and comparing those move sets to the opponents actual pieces. 
        If the two overlap (i.e. if the imitated pawn moves overlaps with the opponent pawn moves), the king would be in check.
        This is done for evey piece.

        Note that this is essentially an is_attacked function that determines whether a given piece is being attacked,
        but because of its initial setup and use for king checks, we call it in_check

        PARAMS 
        index: an integer identifying the cell the king may tentatively be able to move to
        relative_to: an integer identifying the cell from with the king originates 
    '''

    def _in_check(self, index, relative_to):
        # verify that the move_to square is next to (board-wise) the move_from square (i.e. index must be next to relative_to)
        if not self._is_next_to(index, relative_to) or index < 0:
            return (-1, -1)  # i.e. True

        # determine which piece color to compare to when sensing
        if self.opponent == self.board.black_pieces:
            # set opponent piece set
            pawns = self.board.black_pawns
            bishops = self.board.black_bishops
            knights = self.board.black_knights
            rooks = self.board.black_rooks
            queens = self.board.black_queens
            king = self.board.black_king

        else:
            # set opponent piece set
            pawns = self.board.white_pawns
            bishops = self.board.white_bishops
            knights = self.board.white_knights
            rooks = self.board.white_rooks
            queens = self.board.white_queens
            king = self.board.white_king

        # ongoing board of pieces checking the king
        checking_pieces = 0
        test_checked_piece = 0

        # board of squares the king has searched for enemies
        search_field = 0

        # determine what moves would cause a check, if any, add to check_board accordingly
        # simulate pawn moves
        pawn_moves = self._get_pawn_moves(index)
        test_checked_piece = pawns & pawn_moves
        if test_checked_piece:
            search_field |= pawn_moves
            checking_pieces |= test_checked_piece

        # simulate knight moves
        knight_moves = self._get_knight_moves(index)
        test_checked_piece = knights & knight_moves
        if test_checked_piece:
            search_field |= knight_moves
            checking_pieces |= test_checked_piece

        # simulate bishop moves
        bishop_moves = self._get_bishop_moves(index)
        test_checked_piece = bishops & bishop_moves
        if test_checked_piece:
            search_field |= bishop_moves
            checking_pieces |= test_checked_piece

        # simulate rook moves
        rook_moves = self._get_rook_moves(index)
        test_checked_piece = rooks & rook_moves
        if test_checked_piece:
            search_field |= rook_moves
            checking_pieces |= test_checked_piece

        # simulate queen moves (needed even though rook/bishop already called)
        queen_moves = self._get_queen_moves(index)
        test_checked_piece = queens & queen_moves
        if test_checked_piece:
            search_field |= queen_moves
            checking_pieces |= test_checked_piece

        # a call to get_king_moves cannot be made to avoid an infinite recursion, so the positions must be found manually
        tentative_king_positions = 0

        # cycle through each position in a 1 cell radius of the given index
        for i in [1, 7, 8, 9]:
            top_index = index + i
            bottom_index = index - i

            # verify that the new cell is next to the index (board-wise)
            if self._is_next_to(index, top_index):
                tentative_king_positions |= 1 << top_index

            # verify non-negativity and board-wise closeness
            if bottom_index >= 0 and self._is_next_to(index, bottom_index):
                tentative_king_positions |= 1 << bottom_index

        # validate simulated king moves and adjust search field/check board accordingly
        test_checked_piece = tentative_king_positions & king
        if test_checked_piece:
            search_field |= tentative_king_positions
            checking_pieces |= test_checked_piece

        # i.e. (attacking pieces, places the king looked at for attacking pieces)
        return checking_pieces, search_field

    '''
        This determines whether the given king is in check.
        Note that this function assumes no moves are available to the given king, the caller must handle that logic

        PARAMS
        king_board: bitboard of an arbitrary king

        RETURNS
        True if the given king is in mate, false otherwise
    '''

    def _in_mate(self, king_board):
        # get player/opponent color
        self.player = self.board.white_pieces
        self.opponent = self.board.black_pieces

        if king_board == self.board.black_king:
            self.player = self.board.black_pieces
            self.opponent = self.board.white_pieces

        # get king information of received color
        king_index = utils.singleton_board_to_index(king_board)
        king_check = self._in_check(king_index, king_index)
        attacking = king_check[0]

        # nobody is attacking
        if attacking == 0:
            return False

        # king has been taking (this is for minimax compatibility and will not be used in a human v human game)
        if king_board == 0:
            return True

        # verify double check (no moves means automatic checkmate)
        if attacking and (attacking & (attacking - 1)) > 0:
            return True

        # swap players to get attacking piece moves
        tmp = self.player
        self.player = self.opponent
        self.opponent = tmp

        # get attacking piece info
        attacking_index = utils.singleton_board_to_index(attacking)
        attacker_check = self._in_check(attacking_index, attacking_index)
        attacker_moves = self.piece_move_map[self.board.get_piece(
            attacking_index).upper()](attacking_index)

        # get lines between attacking piece and attacked piece as a bitboard
        line_of_attack = attacker_moves & king_check[1]

        # get pieces blocking the line of attack
        blocking_pieces = utils.board_to_indexes(self.opponent)
        blocking_pieces.remove(king_index)
        for piece in blocking_pieces:
            blocking_moves = self.generate_moves(piece)
            if blocking_moves & line_of_attack:
                return False

        # attacking piece cannot be taken and no piece can block it, king is in mate
        if not attacker_check[0]:
            return True

        # king not in mate
        return False

    '''
        Determines if the piece in the given square is pinned

        PARAMS
        square: an index identifying the location of the piece to be analyzed for pinning

        RETURNS
        a pair of values: attacking (bitboard of the attacking pieces) 
        and line_of_attack (a bitboard of the line between the attacking pieces and the pinned piece)
    '''

    def _is_pinned(self, square):
        # convert square to index
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)

        # square contains no piece
        if index < 0:
            return (0, 0)  # no attackers or line of attack

        piece = self.board.get_piece(index)

        # determine piece color
        king_board = self.board.white_king
        self.player = self.board.white_pieces
        self.opponent = self.board.black_pieces
        if self.board.get_piece_color(piece) == self.board.black_pieces:
            king_board = self.board.black_king
            self.player = self.board.black_pieces
            self.opponent = self.board.white_pieces

        # get information of king with same color as given piece
        king_index = utils.singleton_board_to_index(king_board)

        # temporarily remove given piece from board
        self.board.set_piece(constants.EMPTY, index)

        # if king in check, piece was protecting it, meaning the piece is pinned
        king_in_check = self._in_check(king_index, king_index)

        # determine the attacking piece and its line of attack
        attacking, line_of_attack = 0, 0
        if king_in_check[0]:
            attacking = king_in_check[0]

            attacking_index = utils.singleton_board_to_index(attacking)

            attacker_moves = self.piece_move_map[self.board.get_piece(
                attacking_index).upper()](attacking_index)
            line_of_attack = attacker_moves & king_in_check[1]

        # replace piece now that its pin was determined
        self.board.set_piece(piece, index)

        return attacking, line_of_attack

    '''
        determines whether a given cell a is next to a given cell b. This is to manage out of board errors when doing bitshifts

        PARAMS
        from_index: an arbitrary index representing a location on the board
        to_index: an arbitrary index reprsenting a second location on the board

        RETURNS
        True if from_index is within one cell of to_index, false otherwise
    '''

    def _is_next_to(self, from_index, to_index):
        # get row and column values for each index
        from_col, from_row = from_index % 8, from_index // 8
        to_col, to_row = to_index % 8, to_index // 8

        # check if radius of size 1 for to_index contains from_index
        if abs(from_col - to_col) > 1 or abs(from_row - to_row) > 1:
            return False
        return True

    '''
        determines if there is a piece in the given square

        PARAMS
        square: an alphanumeric index or integer identifying the location of the square within the board

        RETURNS
        true if the square is empty, false otherwise
    '''

    def _is_empty(self, square):
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)
        return not self.board.board & 1 << index

    '''
        determines if the piece in a given square is an opponent to the current player

        PARAMS
        square: an alphanumeric index or integer identifying the location of the piece to manage

        RETURNS
        true if the piece in the given square is an opponent, false otherwise
    '''

    def _is_opponent(self, square):
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)
        return bool(self.opponent & 1 << index)

    '''
        parses the moves of a given square into a list of tuples

        PARAMS
        from_square: the square from which the piece will originate
        moves: the squares to which the piece in the from_square can move

        RETURNS
        a list such that each element is a tuple (a,b) where a is the square from which the piece will move from
        and b is a square that the piece could move to
    '''

    def _get_move_paths(self, from_square, moves):
        return [(from_square, to_square) for to_square in moves]

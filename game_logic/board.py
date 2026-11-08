from .board_utils import BoardUtils as utils, BoardConstants as constants
from .move_generator import MoveGenerator
from algorithms.evaluations import Evaluations
from . import rules


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

        METHODS
        
        check_piece(square,color)
            checks whether there is a piece of the given color in a specific square
            returns boolean

        set_pieces(piece, square)
            sets the given square to the given piece
            returns None

        get_piece(square)
            returns the character value of the piece in the given square (e.g. K if the piece in the given square is the white king)

        move_piece(from_square, to_square)
            moves the piece in the cell identified by 'from_square' to the cell identified by 'to_square'
            returns None

        get_moves(square)
            returns an integer mask representing the moves that the piece in the given square can take

        highlight_moves(moves)
            clears the highlighted board and sets it to whatever the given integer mask of moves is
            note that to clear highlighted moves, a 0 must be passed to this function
            returns None

        get_board_string()
            returns the current state of the board as a string. Any highlighted moves on the highlighted moves board will be represented
            
        get_score(color,is_winning_board)
            gets the score of the current board from the perspective of the given color
            returns floating point number representing the score
            
        get_king_shelter(color)
            Updates integer representations of a color's king shelter regions
            returns None
    '''

    def __init__(self):
        # total board
        self.black_pieces = 0xffff << constants.BOARD_LENGTH * \
            (constants.BOARD_LENGTH - 2)
        self.white_pieces = 0xffff
        self.board = self.black_pieces | self.white_pieces
        self.board_development = self.board

        # track en_passant for pawns
        self.en_passant_board = 0

        # track move highlights for the board string
        self.highlight_board = 0

        # sub-boards
        # note the sub-boards have the following bit patterns for each piece:
        # pawn: 0b1111111100000000
        # rook: 0b10000001
        # knight: 0b01000010
        # bishop: 0b00100100
        # king: 0b00010000
        # queen: 0b00001000

        # set the initial white pieces
        self.white_pawns = 0xff << constants.BOARD_LENGTH
        self.white_rooks = 0x81
        self.white_knights = 0x42
        self.white_bishops = 0x24
        self.white_king = 0x10
        self.white_queens = 0x8

        # set the initial black pieces and move them accross the board
        self.black_pawns = 0xff << constants.ACROSS_BOARD >> constants.BOARD_LENGTH
        self.black_rooks = 0x81 << constants.ACROSS_BOARD
        self.black_knights = 0x42 << constants.ACROSS_BOARD
        self.black_bishops = 0x24 << constants.ACROSS_BOARD
        self.black_king = 0x10 << constants.ACROSS_BOARD
        self.black_queens = 0x8 << constants.ACROSS_BOARD

        self.last_move = [1,1,1]
        self.last_last_move = [0,0,0]
        self.last_moves = []
        self.move_generator = MoveGenerator(self)  
        self.evaluations = Evaluations(self) 
        
        # setup king shelter positions
        self.white_immediate_shelter = 0x0000
        self.white_diag_wide_shelter = 0x0000
        self.white_cross_wide_shelter = 0x0000
        self.white_sinu_wide_shelter = 0x0000    
        self.black_immediate_shelter = 0x0000
        self.black_diag_wide_shelter = 0x0000
        self.black_cross_wide_shelter = 0x0000
        self.black_sinu_wide_shelter = 0x0000   
        
        self.get_king_shelter(constants.WHITE)
        self.get_king_shelter(constants.BLACK)

        self.num_moves = 0
        self.side_to_move = constants.WHITE
        self.castling_rights = 'KQkq'
        self.halfmove_clock = 0
        self._history = []
        self._positions = [self._position_key()]
         
    
    '''
        Checks whether there is a piece in the given square with the given color

        PARAMS
        index: index of the square to check
        color: color to check for

        RETURNS
        boolean indicating whether there is a piece in the given square with the given color
    '''
    def check_piece(self, index, color):
        if (color == constants.WHITE):
            return self.white_pieces & (1 << index)
        else:
            return self.black_pieces & (1 << index)
        
    '''
        sets a given piece to a given square

        PARAMS
        piece: a character identifying the type of chess piece (e.g. 'K' for white King, 'Q' for white Queen, etc.)
        square: string or integer index identifying the cell on the board needing to be set
    '''

    def set_piece(self, piece, square):
        index = utils.square_to_index(square) if isinstance(square, str) else square
        mask = 1 << index
        self.board &= ~mask
        self.white_pieces &= ~mask
        self.black_pieces &= ~mask
        for name in self._piece_fields.values():
            setattr(self, name, getattr(self, name) & ~mask)
        if piece != constants.EMPTY:
            name = self._piece_fields[piece]
            setattr(self, name, getattr(self, name) | mask)
            self.board |= mask
            if piece.isupper():
                self.white_pieces |= mask
            else:
                self.black_pieces |= mask
        self.board_development &= ~mask

    '''
        gets the piece in the given square or index

        PARAMS
        square: an alphanumeric index or integer index identifying the cell on the board to return

        RETURNS
        a character in the set of pieces if that piece is in the cell, the empty character otherwise
    '''

    def get_piece(self, square):
        # convert given square to index
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)
        if index < 0:
            return constants.EMPTY
        # make mask representation of index
        mask = 1 << index

        # prioritize highlights for board string
        if self.highlight_board & mask:
            return constants.HIGHLIGHT
        # manage white pieces
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
        # manage black pieces
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

        PARAMS
        from_square: an alphnumeric square index (e.g. a1, h4, etc.) identifying the square from which the moving piece originated
        to_square: an alphanumeric square index indentifying the square to which the moving piece will land
    '''

    _piece_fields = dict(zip('PNBRQKpnbrqk', (
        'white_pawns', 'white_knights', 'white_bishops', 'white_rooks', 'white_queens', 'white_king',
        'black_pawns', 'black_knights', 'black_bishops', 'black_rooks', 'black_queens', 'black_king')))

    def _snapshot(self):
        # Copy value state only. Helpers retain their reference to this board.
        return {key: value[:] if isinstance(value, list) else value
                for key, value in vars(self).items()
                if key not in ('move_generator', 'evaluations', '_history')}

    def _restore(self, state):
        for key, value in state.items():
            setattr(self, key, value)

    def _position_key(self):
        ep = self.en_passant_board
        if ep:
            pawns = self.white_pawns if self.side_to_move == 0 else self.black_pawns
            if not any(self.get_moves(i) & ep for i in utils.board_to_indexes(pawns)):
                ep = 0
        return (tuple(getattr(self, field) for field in self._piece_fields.values()),
                self.side_to_move, self.castling_rights, ep)

    def _apply_move(self, origin, target, promotion='Q'):
        piece, captured = self.get_piece(origin), self.get_piece(target)
        color = 0 if piece.isupper() else 1
        en_passant = (piece.upper() == 'P' and captured == '-'
                      and bool(self.en_passant_board & (1 << target)))
        if en_passant:
            self.set_piece('-', target - (8 if color == 0 else -8))
        self.set_piece('-', origin)
        self.set_piece(piece, target)
        if piece.upper() == 'P' and target // 8 in (0, 7):
            self.set_piece(promotion.upper() if color == 0 else promotion.lower(), target)
        if piece.upper() == 'K' and abs(target - origin) == 2:
            rook_origin = origin + 3 if target > origin else origin - 4
            rook_target = origin + 1 if target > origin else origin - 1
            self.set_piece('-', rook_origin)
            self.set_piece('R' if color == 0 else 'r', rook_target)
        remove = ''
        if piece == 'K':
            remove += 'KQ'
        if piece == 'k':
            remove += 'kq'
        for square, right in ((0, 'Q'), (7, 'K'), (56, 'q'), (63, 'k')):
            if origin == square or target == square:
                remove += right
        self.castling_rights = ''.join(r for r in self.castling_rights if r not in remove)
        self.en_passant_board = (1 << ((origin + target) // 2)
                                 if piece.upper() == 'P' and abs(target - origin) == 16 else 0)
        self.halfmove_clock = 0 if piece.upper() == 'P' or captured != '-' or en_passant else self.halfmove_clock + 1
        self.side_to_move = 1 - color
        self.num_moves += 1
        self.get_king_shelter(constants.WHITE)
        self.get_king_shelter(constants.BLACK)

    def move_piece(self, from_square, to_square, promotion='Q', evaluate_outcome=True):
        if promotion.upper() not in 'QRBN':
            raise ValueError('Promotion must be Q, R, B, or N')
        origin, target = utils.square_to_index(from_square), utils.square_to_index(to_square)
        piece = self.get_piece(origin)
        if piece == '-' or (0 if piece.isupper() else 1) != self.side_to_move:
            raise ValueError('Move must belong to the side to move')
        if not self.get_moves(origin) & (1 << target):
            raise ValueError(f'Illegal move: {from_square}{to_square}')
        self._history.append(self._snapshot())
        self.last_last_move = self.last_move
        self.last_moves.append(self.last_move)
        self.last_move = (self.get_piece(origin), from_square, self.get_piece(target), to_square)
        self._apply_move(origin, target, promotion)
        self._positions.append(self._position_key())
        return self.outcome(self.side_to_move) if evaluate_outcome else 0

    def outcome(self, color=None):
        """0: ongoing, 1: side to move is checkmated, 2: draw."""
        color = self.side_to_move if color is None else color
        has_move = any(self.get_moves(i) for i in range(64) if self.check_piece(i, color))
        if not has_move:
            return 1 if rules.in_check(self, color) else 2
        if self.halfmove_clock >= 100 or self._positions.count(self._position_key()) >= 3:
            return 2
        # Basic dead-material cases; broader dead positions are outside this engine.
        if not (self.white_pawns | self.black_pawns | self.white_rooks | self.black_rooks
                | self.white_queens | self.black_queens):
            if (self.white_knights | self.black_knights | self.white_bishops | self.black_bishops).bit_count() <= 1:
                return 2
        return 0

    '''
        undo the last move made

    '''
    def undo_last(self):
        if self._history:
            self._restore(self._history.pop())

    '''
        gets the moves the piece in the given square can take

        RETURNS
        an integer mask representing the moves the piece in the given square can take
    '''

    def get_moves(self, square, is_swapped = False):
        index = utils.square_to_index(square) if isinstance(square, str) else square
        return rules.attacks(self, index) if is_swapped else rules.legal_moves(self, index)
    
    '''
        determines the given piece's color

        PARAMS
        piece: a character representing the piece in an arbitrary cell

        RETURNS
        the given piece's color
    '''

    def get_piece_color(self, piece):
        return self.white_pieces if piece in ('KQRNBP') else self.black_pieces

    '''
        determines the opponent piece color based on the given piece

        PARAMS
        piece: a character representing the piece in an arbitrary cell

        RETURNS
        the opposing color of the the given piece's color (e.g. black if the piece is white)
    '''

    def get_opponent_piece_color(self, piece):
        return self.black_pieces if piece in ('KQRNBP') else self.white_pieces

    def board_to_piece_list(self, integer_board, index=False):
        return [utils.index_to_square(i) if not index else i
                for i, cell in enumerate(format(integer_board, '064b')[::-1]) if cell == '1']

    '''
        sets the highlight board

        PARAMS
        moves: an integer mask representing the moves a piece can take
    '''

    def highlight_moves(self, moves):
        # clear any previously highlighted moves
        self.highlight_board = 0

        # set highlight_board to the given moves
        self.highlight_board |= moves

    '''
        returns the current board as a string
        
        RETURNS
        string representing the board with an origin of a1 on the lower left corner
    '''

    def get_board_string(self):
        board_str = []

        # cycle through board cells and append what the cell
        for row in range(constants.BOARD_LENGTH):
            # reflect board so origin is in lower left corner
            for col in range(constants.BOARD_LENGTH-1, -1, -1):
                board_str.append(self.get_piece(
                    row * constants.BOARD_LENGTH + col) + ' ')
            board_str.append(str(row+1) + '| ')  # left board index and border
            board_str.append('\n')
        board_str = board_str[:-1]  # remove trailing new line
        # top index and border
        board_str.append('   ' + '\033[4m' + 'a b c d e f g h' + '\033[0m \n')

        # reverse board to have origin on lower left corner
        return ''.join(board_str[::-1])


    '''
        Gets the score of the current board from a given color's perspective based on evaluation functions from the Evaluations helper
        
        PARAMS
        color: the color from whose perspective we are scoring the board
        winning_board: integer, where 1 indicates this board is a winning board (checkmate), and 2 indicates a stalemate (>max allowable moves)
        
    '''
    
    def get_score(self, color, winning_board):
        return self.evaluations.get_score(color, winning_board)
        
    '''
        Updates the integer representation of the king's shelter regions for a given color, given the king's position and the king's distance to board edges. 
        The king's shelter is divided into four regions:
            The immediate shelter consists of the squares adjacent to the king.
            The diagonal wide shelter consists of diagonals two squares apart from the king.
            The cross wide shelter consists of the verticals and horizontals two squares apart from the king.
            The sinuous board wide shelter consists of the curved spaces two squares from the king.
            
        PARAMS
        color: the color whose king this method finds the shelter of
    '''
    
    def get_king_shelter(self, color):        
        if (color == constants.WHITE):
            self.white_immediate_shelter = 0x0000 # clear integer representations for each shelter region
            self.white_diag_wide_shelter = 0x0000
            self.white_cross_wide_shelter = 0x0000
            self.white_sinu_wide_shelter = 0x0000
            
            if (self.white_king.bit_count() != 1): # if there is no king, do not attempt to evaluate
                return
            
            index = utils.singleton_board_to_index(self.white_king) # get the index of the given color's king
            if ((index-1)%8<7): # if there is a square left of king
                self.white_immediate_shelter |= 1 << (index-1) # add left square to immediate shelter mask
                if ((index-2)%8<7): self.white_cross_wide_shelter |= 1 << (index-2) # add left left
            if ((index+1)%8>0): # if the right square right of king
                self.white_immediate_shelter |= 1 << (index+1) # add right
                if ((index+2)%8>0): self.white_cross_wide_shelter |= 1 << (index+2) # add right right
            if ((index-8)>-1): # check the level below the king
                self.white_immediate_shelter |= 1 << (index-8) # below
                if ((index-8-1)%8<7):
                    self.white_immediate_shelter |= 1 << (index-8-1) # bottom left corner
                    if ((index-8-2)%8<7):
                        self.white_sinu_wide_shelter |= 1 << (index-8-2) # bottom left left
                if ((index-8+1)%8>0):
                    self.white_immediate_shelter |= 1 << (index-8+1) # bottom right
                    if ((index-8+2)%8>0):
                        self.white_sinu_wide_shelter |= 1 << (index-8+2) # bottom right right
            if ((index-16)>-1): # check two levels below the king
                self.white_cross_wide_shelter |= 1 << (index-16) 
                if ((index-16-1)%8<7): # bottom bottom left
                    self.white_sinu_wide_shelter |= 1 << (index-16-1)
                    if ((index-16-2)%8<7): # bottom bottom left left
                        self.white_diag_wide_shelter |= 1 << (index-16-2)
                if ((index-16+1)%8>0): # bottom bottom right
                    self.white_sinu_wide_shelter |= 1 << (index-16+1)
                    if ((index-16+2)%8>0): # bottom bottom right right
                        self.white_diag_wide_shelter |= 1 << (index-16+2)
            if ((index+8)<56): # level above king
                self.white_immediate_shelter |= 1 << (index+8)
                if ((index+8-1)%8<7):
                    self.white_immediate_shelter |= 1 << (index+8-1) # top left corner
                    if ((index+8-2)%8<7):
                        self.white_sinu_wide_shelter |= 1 << (index+8-2) # top left left
                if ((index+8+1)%8>0):
                    self.white_immediate_shelter |= 1 << (index+8+1) # top right
                    if ((index+8+2)%8>0):
                        self.white_sinu_wide_shelter |= 1 << (index+8+2) # top right right
            if ((index+16)<56): # two levels above king
                self.white_cross_wide_shelter |= 1 << (index+16) 
                if ((index+16-1)%8<7): # top top left
                    self.white_sinu_wide_shelter |= 1 << (index+16-1)
                    if ((index+16-2)%8<7): # top top left left
                        self.white_diag_wide_shelter |= 1 << (index+16-2)
                if ((index+16+1)%8>0): # top top right
                    self.white_sinu_wide_shelter |= 1 << (index+16+1)
                    if ((index+16+2)%8>0): # top top right right
                        self.white_diag_wide_shelter |= 1 << (index+16+2)
        else:
            self.black_immediate_shelter = 0x0000 # clear integer representations of the shelter
            self.black_diag_wide_shelter = 0x0000
            self.black_cross_wide_shelter = 0x0000
            self.black_sinu_wide_shelter = 0x0000
            if (self.black_king.bit_count() != 1): # if there is no king, do not attempt to eval
                return
            
            index = utils.singleton_board_to_index(self.black_king) # get index of the king
            if ((index-1)%8<7): # check left of king
                self.black_immediate_shelter |= 1 << (index-1) # left 
                if ((index-2)%8<7): self.black_cross_wide_shelter |= 1 << (index-2) # left left
            if ((index+1)%8>0): # check right of king
                self.black_immediate_shelter |= 1 << (index+1) # right
                if ((index+2)%8>0): self.black_cross_wide_shelter |= 1 << (index+2) # right right
            if ((index-8)>-1): # level below king
                self.black_immediate_shelter |= 1 << (index-8)
                if ((index-8-1)%8<7):
                    self.black_immediate_shelter |= 1 << (index-8-1) # bottom left corner
                    if ((index-8-2)%8<7):
                        self.black_sinu_wide_shelter |= 1 << (index-8-2) # bottom left left
                if ((index-8+1)%8>0):
                    self.black_immediate_shelter |= 1 << (index-8+1) # bottom right
                    if ((index-8+2)%8>0):
                        self.black_sinu_wide_shelter |= 1 << (index-8+2) # bottom right right
            if ((index-16)>-1): # two levels below king
                self.black_cross_wide_shelter |= 1 << (index-16) 
                if ((index-16-1)%8<7): # bottom bottom left
                    self.black_sinu_wide_shelter |= 1 << (index-16-1)
                    if ((index-16-2)%8<7): # bottom bottom left left
                        self.black_diag_wide_shelter |= 1 << (index-16-2)
                if ((index-16+1)%8>0): # bottom bottom right
                    self.black_sinu_wide_shelter |= 1 << (index-16+1)
                    if ((index-16+2)%8>0): # bottom bottom right right
                        self.black_diag_wide_shelter |= 1 << (index-16+2)
            if ((index+8)<56): # level above king
                self.black_immediate_shelter |= 1 << (index+8)
                if ((index+8-1)%8<7):
                    self.black_immediate_shelter |= 1 << (index+8-1) # top left corner
                    if ((index+8-2)%8<7):
                        self.black_sinu_wide_shelter |= 1 << (index+8-2) # top left left
                if ((index+8+1)%8>0):
                    self.black_immediate_shelter |= 1 << (index+8+1) # top right
                    if ((index+8+2)%8>0):
                        self.black_sinu_wide_shelter |= 1 << (index+8+2) # top right right
            if ((index+16)<56): # two levels above king
                self.black_cross_wide_shelter |= 1 << (index+16) 
                if ((index+16-1)%8<7): # top top left
                    self.black_sinu_wide_shelter |= 1 << (index+16-1)
                    if ((index+16-2)%8<7): # top top left left
                        self.black_diag_wide_shelter |= 1 << (index+16-2)
                if ((index+16+1)%8>0): # top top right
                    self.black_sinu_wide_shelter |= 1 << (index+16+1)
                    if ((index+16+2)%8>0): # top top right right
                        self.black_diag_wide_shelter |= 1 << (index+16+2)

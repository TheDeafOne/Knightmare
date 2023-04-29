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



        METHODS

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
         
    
    '''
        checks whether there is a piece in the given square with the given color

        PARAMS
        index: index of the square to check
        color: color to check for

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
        # conver given square to index
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)

        # set piece location in temporary mask
        mask = 1 << index

        self.board |= mask
        self.board_development &= ~mask
        # check if piece location corresponds with any of the sub-boards
        # set the cell to be empty
        if piece == constants.EMPTY:
            # update main board
            self.board &= ~mask

            # update white pieces
            self.white_pieces &= ~mask
            self.white_pawns &= ~mask
            self.white_rooks &= ~mask
            self.white_knights &= ~mask
            self.white_bishops &= ~mask
            self.white_king &= ~mask
            self.white_queens &= ~mask

            # update black pieces
            self.black_pieces &= ~mask
            self.black_pawns &= ~mask
            self.black_rooks &= ~mask
            self.black_knights &= ~mask
            self.black_bishops &= ~mask
            self.black_king &= ~mask
            self.black_queens &= ~mask
        # set the cell to be a white piece
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
        # set the cell to be a black piece
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
        square: an alphanumeric index or integer index identifying the cell on the board to return

        RETURNS
        a character in the set of pieces if that piece is in the cell, the empty character otherwise
    '''

    def get_piece(self, square):
        # convert given square to index
        index = square
        if type(square) == str:
            index = utils.square_to_index(square)

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

    def move_piece(self, from_square, to_square):
        # get pieces
        to_piece = self.get_piece(to_square)
        from_piece = self.get_piece(from_square)

        # clear to cell
        self.set_piece(constants.EMPTY, to_square)

        # set to cell to piece in from cell
        self.set_piece(from_piece, to_square)

        # clear from cell
        self.set_piece(constants.EMPTY, from_square)
        
        self.last_last_moves = self.last_move
        # save latest move
        # if self.last_moves[:10] == [(), ('P', 'h2', '-', 'h4'), ('n', 'g8', '-', 'h6'), ('P', 'h4', '-', 'h5'), ('n', 'h6', '-', 'g4'), (), (), (), ('N', 'g1', '-', 'h3'), ('n', 'g4', 'P', 'f2')]:
        #     print(self.get_board_string())
        #     print(self.last_moves)
        #     print()
        # self.last_moves.append(self.last_move)
        self.last_moves.append(self.last_move)
        self.last_move = (from_piece,from_square,to_piece,to_square)
        

        # pawn check
        to_index = utils.square_to_index(to_square)
        from_color = self.get_piece_color(from_piece)
        if from_piece == constants.WHITE_PAWN or from_piece == constants.BLACK_PAWN:
            if from_color == self.white_pieces and to_index > 55:
                self.set_piece(constants.WHITE_QUEEN, to_square)
            elif to_index < 8:
                self.set_piece(constants.BLACK_QUEEN, to_square)

        if (from_piece == constants.BLACK_KING):
            self.get_king_shelter(constants.BLACK)
        elif (from_piece == constants.WHITE_KING):
            self.get_king_shelter(constants.WHITE)
            
        king = self.white_king
        if self.get_piece_color(from_piece) == self.white_pieces:
            king = self.black_king
        return self.move_generator._in_mate(king)

    '''
        undo the last move made

    '''
    def undo_last(self):
        if len(self.last_move) != 0:
            self.move_piece(self.last_move[3],self.last_move[1])
            self.last_move = tuple()


    '''
        gets the moves the piece in the given square can take

        RETURNS
        an integer mask representing the moves the piece in the given square can take
    '''

    def get_moves(self, square, is_swapped = False):
        return self.move_generator.generate_moves(square, is_swapped)
    
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
        gets the board's evaluation score
    '''
    def get_score(self, color, winning_board):
        if (color == constants.WHITE):
            enemy_color = constants.BLACK
        else:
            enemy_color = constants.WHITE
            
        # get all moves, for use in evaluation functions
        all_moves = {piece_type:[] for piece_type in constants.ALL_PIECE_TYPES}
        for i in range (0,64):
            if (self.board & (1<<i)):
                square = utils.index_to_square(i)
                moves = self.get_moves(square)
                piece = self.get_piece(i)
                all_moves[piece].append((square,moves))     
        
        # 1) Get initial piece scores
        opening = False
        middle = False
        endgame = False
        
        queen = 9.0
        rook = 4.5
        knight = 3.0
        bishop = 3.0
        pawn = 1.0
        king = 100.0 
        
        if (color == constants.WHITE):
            pawn_count = self.white_pawns.bit_count()
        else:
            pawn_count = self.black_pawns.bit_count()

        overall_piece_strength = bishop*self.white_bishops.bit_count() +  \
            rook*self.white_rooks.bit_count() + \
            knight*self.white_knights.bit_count() + \
            queen*self.white_queens.bit_count() + \
            king*self.white_king.bit_count() + \
            bishop*self.black_bishops.bit_count() +  \
            rook*self.black_rooks.bit_count() + \
            knight*self.black_knights.bit_count() + \
            queen*self.black_queens.bit_count() + \
            king*self.black_king.bit_count()
        
        if (overall_piece_strength >= 45): # opening
            middle = True
            opening = True
        elif (overall_piece_strength >= 30): # middle game
            middle = True
            pawn = pawn * 0.05
        elif (overall_piece_strength >= 15): # Early endgame
            endgame = True
            pawn = pawn * 1.10
        else:  # late endgame
            endgame = True
            pawn = pawn * 1.15
        
        if (pawn_count >= 13): # closed positions
            queen = 0.95*queen
            rook = 0.85*rook
            bishop = bishop*1.05
            knight = knight*1.15
        elif (pawn_count >= 9): # semi-closed positions
            queen = 0.95*queen
            rook = 0.90*rook
            bishop = bishop*1.05
            knight = knight*1.10
        elif (pawn_count >= 5): # semi-open positions
            queen = 1.20*queen
            rook = 1.10*rook
            bishop = bishop*1.15
            knight = knight*0.9
        else: # open positions
            queen = 1.30*queen
            rook = 1.10*rook
            bishop = bishop*1.20
            knight = knight*0.85
            
        # TODO: add extra conditions for openning/middlegame/endgame (see doc), and put result in score_mod
        score_mod = 0.0 # add to the returned score based on various conditions
        
        if (winning_board): score_mod += 200.0   
        if opening:
            score_mod += self.get_focal_points(color, all_moves)
            score_mod += self.get_development_order_points(color)
        score_mod += self.get_mobility_score(all_moves,color)
        score_mod += self.get_position_score(color)
        score_mod += self.get_attacking_potential(all_moves, color, queen, rook, bishop, knight, pawn)
        score_mod += self.get_king_security(color)
        
        white_count = bishop*self.white_bishops.bit_count() +  \
            pawn*self.white_pawns.bit_count() + \
            rook*self.white_rooks.bit_count() + \
            knight*self.white_knights.bit_count() + \
            queen*self.white_queens.bit_count() + \
            king*self.white_king.bit_count()
            
        black_count = bishop*self.black_bishops.bit_count() +  \
            pawn*self.black_pawns.bit_count() + \
            rook*self.black_rooks.bit_count() + \
            knight*self.black_knights.bit_count() + \
            queen*self.black_queens.bit_count() + \
            king*self.black_king.bit_count()
        
        # Return score
        if (color == constants.WHITE):
            return white_count - black_count + score_mod
        else:
            return black_count - white_count + score_mod

    '''
        Get the mobility score for a board (applicible in any stage)
    '''
    def get_mobility_score(self, all_moves, color):
        mobility = 0
        if (color == constants.WHITE):
            for piece in constants.WHITE_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    mobility += each_piece_move[1].bit_count()
        else:
            for piece in constants.BLACK_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    mobility += each_piece_move[1].bit_count()
        return mobility * 0.10
    
    '''
        Get the position score for a board (applicable at any stage)
    '''
    def get_position_score(self,color):
        score = 0
        if (color == constants.WHITE):
            score -= 0.015*((self.white_pieces & 0xff).bit_count()) # first rank
            score += 0.015*((self.white_pieces & (0xff << 8)).bit_count()) # second rank
            score += 0.030*((self.white_pieces & (0xff << 8*2)).bit_count()) # third rank
            score += 0.45*((self.white_pieces & (0xff << 8*3)).bit_count()) # fourth rank
            score += 0.60*((self.white_pieces & (0xff << 8*4)).bit_count()) # fifth rank
            score += 0.75*((self.white_pieces & (0xff << 8*5)).bit_count()) # sixth rank
            score += 0.60*((self.white_pieces & (0xff << 8*6)).bit_count()) # seventh rank
            score += 0.030*((self.white_pieces & (0xff << 8*7)).bit_count()) # eigth rank           
        else:
            score -= 0.015*((self.black_pieces & 0xff << 8*7).bit_count()) # first rank (reverse orientation)
            score += 0.015*((self.black_pieces & (0xff << 8*6)).bit_count()) # second rank
            score += 0.030*((self.black_pieces & (0xff << 8*5)).bit_count()) # third rank
            score += 0.45*((self.black_pieces & (0xff << 8*4)).bit_count()) # fourth rank
            score += 0.60*((self.black_pieces & (0xff << 8*3)).bit_count()) # fifth rank
            score += 0.75*((self.black_pieces & (0xff << 8*2)).bit_count()) # sixth rank
            score += 0.60*((self.black_pieces & (0xff << 8*1)).bit_count()) # seventh rank
            score += 0.030*((self.black_pieces & 0xff).bit_count()) # eigth rank
        return score
    
    '''
        Get the attacking potential of a board (applicable in all stages)
        
        + 1/10 of all attacked pieces strength
    '''
    def get_attacking_potential(self, all_moves, color, queen, rook, bishop, knight, pawn):
        attack_potential = 0
        if (color == constants.WHITE):
            for piece in constants.WHITE_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    attack_potential += queen/10*(each_piece_move[1] & self.black_queens).bit_count()
                    attack_potential += rook/10*(each_piece_move[1] & self.black_rooks).bit_count()
                    attack_potential += bishop/10*(each_piece_move[1] & self.black_bishops).bit_count()
                    attack_potential += knight/10*(each_piece_move[1] & self.black_knights).bit_count()
                    attack_potential += pawn/10*(each_piece_move[1] & self.black_pawns).bit_count()
        else:
            for piece in constants.BLACK_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    attack_potential += queen/10*(each_piece_move[1] & self.white_queens).bit_count()
                    attack_potential += rook/10*(each_piece_move[1] & self.white_rooks).bit_count()
                    attack_potential += bishop/10*(each_piece_move[1] & self.white_bishops).bit_count()
                    attack_potential += knight/10*(each_piece_move[1] & self.white_knights).bit_count()
                    attack_potential += pawn/10*(each_piece_move[1] & self.white_pawns).bit_count()
        return attack_potential
    
                        # if (piece == constants.WHITE_PAWN): # special case: pawns defend diagonals
                        # index = utils.square_to_index(each_piece_move[0])
                        # if (index % 8 == 0):
                        #     defended = 1 << (index + 7)
                        # elif (index % 8 == 7):
                        #     defended = 1 << (index + 9)
                        # else:
                        #     defended = 1 << (index + 7) | 1 << (index + 9)
                        # defensive_potential += queen/20*(defended & self.black_queens).bit_count()
                        # defensive_potential += rook/20*(defended & self.black_rooks).bit_count()
                        # defensive_potential += bishop/20*(defended & self.black_bishops).bit_count()
                        # defensive_potential += knight/20*(defended & self.black_knights).bit_count()
                        # defensive_potential += pawn/20*(defended & self.black_pawns).bit_count()
    
    '''
        Get defensive potential (applicable at all stages) TODO: finish
        
        + 1/20 of all defended pieces strength
    '''
    def get_defensive_potential(self, all_moves, color, queen, rook, bishop, knight, pawn):
        defensive_potential = 0
        if (color == constants.WHITE):
            for piece in constants.WHITE_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    defended_mask = self.get_moves(each_piece_move[0],True)
                    print(each_piece_move[0] + "\n" + utils.bin_to_string(defended_mask))
                    defensive_potential += queen/20*(defended_mask & self.white_queens).bit_count()
                    defensive_potential += rook/20*(defended_mask & self.white_rooks).bit_count()
                    defensive_potential += bishop/20*(defended_mask & self.white_bishops).bit_count()
                    defensive_potential += knight/20*(defended_mask & self.white_knights).bit_count()
                    defensive_potential += pawn/20*(defended_mask & self.white_pawns).bit_count()
        else:
            for piece in constants.BLACK_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    defended_mask = self.get_moves(each_piece_move[0],True)
                    defensive_potential += queen/20*(defended_mask & self.black_queens).bit_count()
                    defensive_potential += rook/20*(defended_mask & self.black_rooks).bit_count()
                    defensive_potential += bishop/20*(defended_mask & self.black_bishops).bit_count()
                    defensive_potential += knight/20*(defended_mask & self.black_knights).bit_count()
                    defensive_potential += pawn/20*(defended_mask & self.black_pawns).bit_count()
        return defensive_potential
    
    '''
        Measure king security
    '''
    def get_king_security(self,color):
        king_security = 0.0
        if (color == constants.WHITE):
            king_security += .50*(self.white_pawns & self.white_immediate_shelter).bit_count() \
                + .50/2*(self.white_pawns & (self.white_cross_wide_shelter | self.white_diag_wide_shelter)).bit_count() \
                + .50/3*(self.white_pawns & self.white_sinu_wide_shelter).bit_count()
            full_shelter = self.white_cross_wide_shelter | self.white_diag_wide_shelter | self.white_immediate_shelter | self.white_sinu_wide_shelter
            king_security += 0.1*(full_shelter & self.white_queens).bit_count() \
                + 0.15*(full_shelter & self.white_rooks).bit_count() \
                + 0.25*(full_shelter & self.white_knights).bit_count() \
                + 0.30*(full_shelter & self.white_bishops).bit_count()
        else:
            king_security += .50*(self.black_pawns & self.black_immediate_shelter).bit_count() \
                + .50/2*(self.black_pawns & (self.black_cross_wide_shelter | self.black_diag_wide_shelter)).bit_count() \
                + .50/3*(self.black_pawns & self.black_sinu_wide_shelter).bit_count()
            full_shelter = self.black_cross_wide_shelter | self.black_diag_wide_shelter | self.black_immediate_shelter | self.black_sinu_wide_shelter
            king_security += 0.1*(full_shelter & self.black_queens).bit_count() \
                + 0.15*(full_shelter & self.black_rooks).bit_count() \
                + 0.25*(full_shelter & self.black_knights).bit_count() \
                + 0.30*(full_shelter & self.black_bishops).bit_count()
        return king_security
    
    '''
        Re-gets king shelter positions after the king has been moved
    '''
    def get_king_shelter(self, color):        
        if (color == constants.WHITE):
            self.white_immediate_shelter = 0x0000
            self.white_diag_wide_shelter = 0x0000
            self.white_cross_wide_shelter = 0x0000
            self.white_sinu_wide_shelter = 0x0000
            if (self.white_king.bit_count() != 1):
                return
            
            index = utils.singleton_board_to_index(self.white_king)
            if ((index-1)%8<7): 
                self.white_immediate_shelter |= 1 << (index-1) # left 
                if ((index-2)%8<7): self.white_cross_wide_shelter |= 1 << (index-2) # two left
            if ((index+1)%8>0):
                self.white_immediate_shelter |= 1 << (index+1) # right
                if ((index+2)%8>0): self.white_cross_wide_shelter |= 1 << (index+2) # two right
            if ((index-8)>-1): # level below king
                self.white_immediate_shelter |= 1 << (index-8) # below
                if ((index-8-1)%8<7):
                    self.white_immediate_shelter |= 1 << (index-8-1) # bottom left corner
                    if ((index-8-2)%8<7):
                        self.white_sinu_wide_shelter |= 1 << (index-8-2) # bottom left left
                if ((index-8+1)%8>0):
                    self.white_immediate_shelter |= 1 << (index-8+1) # bottom right
                    if ((index-8+2)%8>0):
                        self.white_sinu_wide_shelter |= 1 << (index-8+2) # bottom right right
            if ((index-16)>-1): # two levels below king
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
            self.black_immediate_shelter = 0x0000
            self.black_diag_wide_shelter = 0x0000
            self.black_cross_wide_shelter = 0x0000
            self.black_sinu_wide_shelter = 0x0000
            if (self.black_king.bit_count() != 1):
                return
            
            index = utils.singleton_board_to_index(self.black_king)
            if ((index-1)%8<7): 
                self.black_immediate_shelter |= 1 << (index-1) # left 
                if ((index-2)%8<7): self.black_cross_wide_shelter |= 1 << (index-2) # two left
            if ((index+1)%8>0):
                self.black_immediate_shelter |= 1 << (index+1) # right
                if ((index+2)%8>0): self.black_cross_wide_shelter |= 1 << (index+2) # two right
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

            
        


    def get_focal_points(self, color, piece_moves):
        pawn_check = constants.WHITE_PAWN
        piece_color_check = constants.WHITE_PIECES
        queen_check = constants.WHITE_QUEEN
        player = self.white_pieces
        if color == constants.BLACK:
            pawn_check = constants.BLACK_PAWN
            piece_color_check = constants.BLACK_PIECES
            queen_check = constants.BLACK_QUEEN
            player = self.black_pieces

        evaluate_value = 0
        focal_square = ('e4','d4','e5','d5')
        for square in focal_square:
            piece = self.get_piece(square)
            if piece == pawn_check:
                evaluate_value += 0.4
            elif piece == queen_check:
                evaluate_value += 0.3
            elif piece in piece_color_check:
                evaluate_value += 0.2

        focal_square_mask = 0x1818 << 8 * 3
        wider_focal_square_mask = 0x3c24243c00 << 8
        inner_moves = 0
        for piece_type in piece_color_check:
            for move_board in [move_board[1] for move_board in piece_moves[piece_type]]:
                inner_moves |= move_board
        inner_moves &= focal_square_mask
        evaluate_value += inner_moves.bit_count() * 0.1
        wider_focal_square_mask &= player
        evaluate_value += wider_focal_square_mask.bit_count() * 0.1

        return evaluate_value


    
    def get_development_order_points(self, color):
        evaluate_value = 0.0
        if self.last_move[0] == self.last_last_move[0]:
            evaluate_value -= 0.35
        
        knight_indexes = constants.WHITE_KNIGHT_INDEXES
        bishop_indexes = constants.WHITE_BISHOP_INDEXES
        knight = constants.WHITE_KNIGHT
        queen = constants.WHITE_QUEEN
        rook = constants.WHITE_ROOK

        if color == constants.BLACK:
            knight_indexes = constants.BLACK_KNIGHT_INDEXES
            bishop_indexes = constants.BLACK_BISHOP_INDEXES
            knight = constants.BLACK_KNIGHT
            queen = constants.BLACK_QUEEN
            rook = constants.BLACK_ROOK

        minor_pieces_developed = 0
        for index in knight_indexes:
            if not self.board_development & 1 << index:
                minor_pieces_developed += 1
        
        for index in bishop_indexes:
            if not self.board_development & 1 << index:
                minor_pieces_developed += 1

        if self.last_move[0] == queen and minor_pieces_developed < 2:
            evaluate_value -= 0.3
        elif self.last_move[0] == rook and minor_pieces_developed < 2:
            evaluate_value -= 0.5
        if self.last_move[0] == knight:
            left_bishop, right_bishop = bishop_indexes
            if self.board_development & 1 << left_bishop or self.board_development & 1 << right_bishop:
                evaluate_value += 0.2

        return evaluate_value
            


    

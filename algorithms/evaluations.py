from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import math

class Evaluations():
    '''
        A helper used to evaluate a board and generate utility scores based on various strategic parameters
        
        ATTRIBUTES
        board: the integer representation of the current board
        
        METHODS
        get_focal_points(color,pieces_move)

        get_development_order_points(color)

        get_mobility_score(all_moves, color)
            Gets board score based on the free spaces accessible by a color's pieces
            
        get_position_score(color)
            Gets board score based on the position of a color's pieces
            
        get_attacking_potential(all_moves, color, queen, rook, bishop, knight, pawn)
            Gets board score based on a color's pieces ability to attack enemy pieces
            
        get_defensive_potential(color, queen, rook, bishop, knight, pawn)
            Gets board score based on a color's pieces ability to defend each other
            
        get_king_security(color)
            Gets board score based on quantity and type of pieces occupying the king's shelter region
            
        get_king_shelter(color)
            Gets integer representations of a color's king shelter regions
            
        get_endgame_points(color)

    '''
    
    def __init__(self, board):
        self.board = board
        
    '''
        
        
    '''
    
    def get_focal_points(self, color, piece_moves):
        pawn_check = constants.WHITE_PAWN
        piece_color_check = constants.WHITE_PIECES
        queen_check = constants.WHITE_QUEEN
        player = self.board.white_pieces
        if color == constants.BLACK:
            pawn_check = constants.BLACK_PAWN
            piece_color_check = constants.BLACK_PIECES
            queen_check = constants.BLACK_QUEEN
            player = self.board.black_pieces

        evaluate_value = 0
        focal_square = ('e4','d4','e5','d5')
        for square in focal_square:
            piece = self.board.get_piece(square)
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


    '''
        TODO: comment
        
    '''
    
    def get_development_order_points(self, color):
        evaluate_value = 0.0
        if self.board.last_move[0] == self.board.last_last_move[0]:
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
            if not self.board.board_development & 1 << index:
                minor_pieces_developed += 1

        for index in bishop_indexes:
            if not self.board.board_development & 1 << index:
                minor_pieces_developed += 1
        if self.board.last_move[0] == queen and minor_pieces_developed < 2:
            evaluate_value -= 0.5
        elif self.board.last_move[0] == rook and minor_pieces_developed < 2:
            evaluate_value -= 0.5
        if self.board.last_move[0] == knight:
            left_bishop, right_bishop = bishop_indexes
            if self.board.board_development & 1 << left_bishop or self.board.board_development & 1 << right_bishop:
                evaluate_value += 0.2

        return evaluate_value
    
    '''
        Evaluates the utility of the current board for a given color based on the mobility of that color's pieces. 
        This method adds .1 for each free space a piece has access to.
             
        PARAMS
        all_moves: a dictionary containing integer representations of all possible moves for all pieces on the board
        color: the color whose perspective we are evaluating from
        
        RETURNS
        a number equal to the mobility utility score of the given color for the current board      
        
    '''
    
    def get_mobility_score(self, all_moves, color):
        mobility = 0
        if (color == constants.WHITE): 
            for piece in constants.WHITE_PIECES: # for each white piece type
                piece_moves = all_moves[piece] # get possible moves for all instances of the piece type
                for each_piece_move in piece_moves:
                    mobility += each_piece_move[1].bit_count() # sum all free spaces pieces have access to
        else:
            for piece in constants.BLACK_PIECES: # for each black piece type
                piece_moves = all_moves[piece] # get possible moves for all instances of the piece type
                for each_piece_move in piece_moves:
                    mobility += each_piece_move[1].bit_count() # sum all free spaces pieces have access to
        return mobility * 0.10
    
    '''
        Evaluates the utility of a the current board for a given color based on the positioning of that color's pieces.
        Uses the following point scheme for different ranks (relative to the color):
            -.015 for pieces in the first rank
            +.015 for pieces in the second rank
            +.03 for pieces in the third rank
            +.45 for pieces in the fourth rank
            +.6 for pieces in the fifth rank
            +.75 for pieces in the sixth rank
            +.6 for pieces in the seventh rank
            +.03 for pieces in the eigth rank
            
        PARAMS
        color: the color whose perspective we are evaluating from
        
        RETURNS
        a number equal to the position utility score of the given color for the current board
                
    '''
    
    def get_position_score(self,color):
        position_score = 0
        if (color == constants.WHITE):
            position_score -= 0.015*((self.board.white_pieces & 0xff).bit_count()) # use a mask to isolate and sum scores from the first rank
            position_score += 0.015*((self.board.white_pieces & (0xff << 8)).bit_count()) # second rank
            position_score += 0.030*((self.board.white_pieces & (0xff << 8*2)).bit_count()) # third rank
            position_score += 0.45*((self.board.white_pieces & (0xff << 8*3)).bit_count()) # fourth rank
            position_score += 0.60*((self.board.white_pieces & (0xff << 8*4)).bit_count()) # fifth rank
            position_score += 0.75*((self.board.white_pieces & (0xff << 8*5)).bit_count()) # sixth rank
            position_score += 0.60*((self.board.white_pieces & (0xff << 8*6)).bit_count()) # seventh rank
            position_score += 0.030*((self.board.white_pieces & (0xff << 8*7)).bit_count()) # eigth rank           
        else:
            position_score -= 0.015*((self.board.black_pieces & 0xff << 8*7).bit_count()) # sum scores from the first rank, reverse orientation
            position_score += 0.015*((self.board.black_pieces & (0xff << 8*6)).bit_count()) # second rank
            position_score += 0.030*((self.board.black_pieces & (0xff << 8*5)).bit_count()) # third rank
            position_score += 0.45*((self.board.black_pieces & (0xff << 8*4)).bit_count()) # fourth rank
            position_score += 0.60*((self.board.black_pieces & (0xff << 8*3)).bit_count()) # fifth rank
            position_score += 0.75*((self.board.black_pieces & (0xff << 8*2)).bit_count()) # sixth rank
            position_score += 0.60*((self.board.black_pieces & (0xff << 8*1)).bit_count()) # seventh rank
            position_score += 0.030*((self.board.black_pieces & 0xff).bit_count()) # eigth rank
        return position_score
    
    '''
        Evaluates the utility of the current board for a given color based on that color's pieces potential to attack enemy pieces.
              
        Uses the following point scheme based on the types of enemy pieces the given color can attack, with extra weight on pieces
        which are attacking the king:
            + 1/10 of all attacked pieces strength
            + 1/10 of the attacking piece's strength if it attacks the enemy king
            + 1/20 of the attacking piece's strength if it attacks pieces in the enemy king's immediate shelter
            + 1/20 * 2/3 of the attacking piece's strength if it attacks pieces in the enemy king's wide shelter
            
        PARAMS
        all_moves: a dictionary containing integer representations of all possible moves for all pieces on the board
        color: the color whose perspective we are evaluating from
        queen: the piece strength of a queen
        rook: the piece strength of a rook
        bishop: the piece strength of a bishop
        knight: the piece strength of a knight
        pawn: the piece strength of a pawn
        
        RETURNS
        a number equalt to the attacking potential utility score of the given color for the current board
    '''
    
    def get_attacking_potential(self, all_moves, color, queen, rook, bishop, knight, pawn):
        attack_potential = 0
        
        if (color == constants.WHITE):
            wide_shelter = self.board.black_cross_wide_shelter | self.board.black_diag_wide_shelter | self.board.black_sinu_wide_shelter # gets a mask of the enemy king's wide shelter
            for piece in constants.WHITE_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves: # for each set of moves by white's pieces
                    attack_potential += queen/10*(each_piece_move[1] & self.board.black_queens).bit_count() # sum general attacking potential, weighting points by attacked piece strength
                    attack_potential += rook/10*(each_piece_move[1] & self.board.black_rooks).bit_count()
                    attack_potential += bishop/10*(each_piece_move[1] & self.board.black_bishops).bit_count()
                    attack_potential += knight/10*(each_piece_move[1] & self.board.black_knights).bit_count()
                    attack_potential += pawn/10*(each_piece_move[1] & self.board.black_pawns).bit_count()
                    
                    # king and king's shelter attack potentials
                    if (piece == constants.WHITE_QUEEN):
                        attack_potential += queen/10*(each_piece_move[1] & self.board.black_king).bit_count() # check whether the queen is attacking the enemy king
                        attack_potential += queen/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count() # check whether the queen attacks king's immediate shelter pieces
                        attack_potential += queen/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count() # check whether the queen attacks the king's wide shelter pieces
                    elif (piece == constants.WHITE_ROOK):
                        attack_potential += rook/10*(each_piece_move[1] & self.board.black_king).bit_count() # rook king attack potential
                        attack_potential += rook/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += rook/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    elif (piece == constants.WHITE_BISHOP):
                        attack_potential += bishop/10*(each_piece_move[1] & self.board.black_king).bit_count() # bishop king attack potential
                        attack_potential += bishop/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += bishop/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    if (piece == constants.WHITE_KNIGHT):
                        attack_potential += knight/10*(each_piece_move[1] & self.board.black_king).bit_count() # knight king attack potential
                        attack_potential += knight/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += knight/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    if (piece == constants.WHITE_PAWN):
                        attack_potential += pawn/10*(each_piece_move[1] & self.board.black_king).bit_count() # pawn king attack potential
                        attack_potential += pawn/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += pawn/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
        else:
            for piece in constants.BLACK_PIECES:
                wide_shelter = self.board.white_cross_wide_shelter | self.board.white_diag_wide_shelter | self.board.white_sinu_wide_shelter
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves: # for each set of moves by black's pieces
                    attack_potential += queen/10*(each_piece_move[1] & self.board.white_queens).bit_count() # sum of general attacking potentials
                    attack_potential += rook/10*(each_piece_move[1] & self.board.white_rooks).bit_count()
                    attack_potential += bishop/10*(each_piece_move[1] & self.board.white_bishops).bit_count()
                    attack_potential += knight/10*(each_piece_move[1] & self.board.white_knights).bit_count()
                    attack_potential += pawn/10*(each_piece_move[1] & self.board.white_pawns).bit_count()
                    
                    # king and king's shelter attack potentials
                    if (piece == constants.BLACK_QUEEN):
                        attack_potential += queen/10*(each_piece_move[1] & self.board.white_king).bit_count() # check whether the queen is attacking the enemy king
                        attack_potential += queen/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count() # check whether the queen attacks king's immediate shelter pieces
                        attack_potential += queen/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count() # check whether the queen attacks the king's wide shelter piece
                    elif (piece == constants.BLACK_ROOK):
                        attack_potential += rook/10*(each_piece_move[1] & self.board.white_king).bit_count() # rook king attack potential
                        attack_potential += rook/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += rook/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    elif (piece == constants.BLACK_BISHOP):
                        attack_potential += bishop/10*(each_piece_move[1] & self.board.white_king).bit_count() # bishop king attack potential
                        attack_potential += bishop/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += bishop/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    if (piece == constants.BLACK_KNIGHT):
                        attack_potential += knight/10*(each_piece_move[1] & self.board.white_king).bit_count() # knight king attack potential
                        attack_potential += knight/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += knight/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    if (piece == constants.BLACK_PAWN):
                        attack_potential += pawn/10*(each_piece_move[1] & self.board.white_king).bit_count() # pawn king attack potential
                        attack_potential += pawn/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += pawn/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
        return attack_potential
    
    '''
        Evaluates the utility of the current board for a given color based on that its pieces are defended by other pieces.
        For each defended piece, 1/20 of that piece's strength is added to the score.
        
             
        PARAMS
        color: the color whose perspective we are evaluating from
        queen: the piece strength of a queen
        rook: the piece strength of a rook
        bishop: the piece strength of a bishop
        knight: the piece strength of a knight
        pawn: the piece strength of a pawn
        
        RETURNS
        a number equal to the defensive potential utility score of the given color for the current board
        
    '''
    def get_defensive_potential(self, color, queen, rook, bishop, knight, pawn):
        defensive_potential = 0 # initialize
        defended_mask = 0x0000 # this will be a cumulative defensive mask
        if (color == constants.WHITE):
            # get an integer mask of the defended pieces
            for i in range(64):
                if self.board.white_pieces & (1 << i): # for each white piece
                    piece = self.board.get_piece(utils.index_to_square(i))
                    if (piece == constants.WHITE_KING): 
                        defended_mask |= self.board.white_immediate_shelter # the king can defend any piece in its immediate shelter
                    elif (piece == constants.WHITE_PAWN):
                        index = i
                        if (index%8>0 and index < 56): defended_mask |= 1 << (index+7) # the pawn can defend the diagonals in its direction of advance
                        if (index%8<7 and index < 56): defended_mask |= 1 << (index+9)
                    else: # use get_moves with is_swapped set to True, so it gets the squares a piece defends rather than attacks
                        defended_mask |= self.board.get_moves(utils.index_to_square(i),True) 
            # sum defended piece points, weighted according to piece strength
            defensive_potential += queen/20*(defended_mask & self.board.white_queens).bit_count() 
            defensive_potential += rook/20*(defended_mask & self.board.white_rooks).bit_count()
            defensive_potential += bishop/20*(defended_mask & self.board.white_bishops).bit_count()
            defensive_potential += knight/20*(defended_mask & self.board.white_knights).bit_count()
            defensive_potential += pawn/20*(defended_mask & self.board.white_pawns).bit_count()
        else:
            # get an integer mask of the defended pieces
            for i in range(64):
                if self.board.black_pieces & (1 << i): # for each black piece
                    piece = self.board.get_piece(utils.index_to_square(i))
                    if (piece == constants.BLACK_KING):
                        defended_mask |= self.board.black_immediate_shelter # the king can defend any piece in its immediate shelter
                    elif (piece == constants.BLACK_PAWN):
                        index = i
                        defended_mask = 0x0000
                        if (index%8>0 and index < 56): defended_mask |= 1 << (index-9) # the pawn can defend the diagonals in its direction of advance
                        if (index%8<7 and index < 56): defended_mask |= 1 << (index-7)
                    else: # use get_moves with is_swapped set to True, so it gets the squares a piece defends rather than attacks
                        defended_mask |= self.board.get_moves(utils.index_to_square(i),True)
            # sum defended piece points, weighted according to piece strength
            defensive_potential += queen/20*(defended_mask & self.board.black_queens).bit_count()
            defensive_potential += rook/20*(defended_mask & self.board.black_rooks).bit_count()
            defensive_potential += bishop/20*(defended_mask & self.board.black_bishops).bit_count()
            defensive_potential += knight/20*(defended_mask & self.board.black_knights).bit_count()
            defensive_potential += pawn/20*(defended_mask & self.board.black_pawns).bit_count()
        return defensive_potential
    
    '''
        Evaluates the utility of the current board for a given color based on the security of that color's king. This method adds points 
        when pieces occupy the sheltering region around the king using the following point scheme:
            +.5 for pawns in the immediate king shelter
            +.5/2 for pawns in the cross or diagonal wide shelter
            +.5/3 for pawns in the sinuous wide shelter
            +.1 for queens in any part of the king's shelter region (wide or immediate)
            +.15 for rooks in any part of the king's shelter region
            +.25 for knights in any part of the king's shelter region
            +.3 for bishops in any part of the king's shelter region
            
        PARAMS
        color: the color whose perspective we are evaluating from
        
        RETURNS
        the sum of all points assigned based on pieces sheltering the given color's king
        
    '''
    
    def get_king_security(self,color):
        king_security = 0.0
        if (color == constants.WHITE):
            # count and weight pawns in the shelter regions
            king_security += .50*(self.board.white_pawns & self.board.white_immediate_shelter).bit_count() \
                + .50/2*(self.board.white_pawns & (self.board.white_cross_wide_shelter | self.board.white_diag_wide_shelter)).bit_count() \
                + .50/3*(self.board.white_pawns & self.board.white_sinu_wide_shelter).bit_count()
            # get a mask of the full king shelter region
            full_shelter = self.board.white_cross_wide_shelter | self.board.white_diag_wide_shelter | self.board.white_immediate_shelter | self.board.white_sinu_wide_shelter
            # count and weight pieces in the king shelter region 
            king_security += 0.1*(full_shelter & self.board.white_queens).bit_count() \
                + 0.15*(full_shelter & self.board.white_rooks).bit_count() \
                + 0.25*(full_shelter & self.board.white_knights).bit_count() \
                + 0.30*(full_shelter & self.board.white_bishops).bit_count()
        else:
            # count and weight pawns in the shelter eregion
            king_security += .50*(self.board.black_pawns & self.board.black_immediate_shelter).bit_count() \
                + .50/2*(self.board.black_pawns & (self.board.black_cross_wide_shelter | self.board.black_diag_wide_shelter)).bit_count() \
                + .50/3*(self.board.black_pawns & self.board.black_sinu_wide_shelter).bit_count()
            # get a mask of the full king shelter region
            full_shelter = self.board.black_cross_wide_shelter | self.board.black_diag_wide_shelter | self.board.black_immediate_shelter | self.board.black_sinu_wide_shelter
            # count and weight pieces in teh king shelter region
            king_security += 0.1*(full_shelter & self.board.black_queens).bit_count() \
                + 0.15*(full_shelter & self.board.black_rooks).bit_count() \
                + 0.25*(full_shelter & self.board.black_knights).bit_count() \
                + 0.30*(full_shelter & self.board.black_bishops).bit_count()
        return king_security
    
    '''
        Gets an integer representation of the king's shelter regions for a given color, given the king's position and the king's distance to board edges. 
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
            self.board.white_immediate_shelter = 0x0000 # clear integer representations for each shelter region
            self.board.white_diag_wide_shelter = 0x0000
            self.board.white_cross_wide_shelter = 0x0000
            self.board.white_sinu_wide_shelter = 0x0000
            
            if (self.board.white_king.bit_count() != 1): # if there is no king, do not attempt to evaluate
                return
            
            index = utils.singleton_board_to_index(self.board.white_king) # get the index of the given color's king
            if ((index-1)%8<7): # if there is a square left of king
                self.board.white_immediate_shelter |= 1 << (index-1) # add left square to immediate shelter mask
                if ((index-2)%8<7): self.board.white_cross_wide_shelter |= 1 << (index-2) # add left left
            if ((index+1)%8>0): # if the right square right of king
                self.board.white_immediate_shelter |= 1 << (index+1) # add right
                if ((index+2)%8>0): self.board.white_cross_wide_shelter |= 1 << (index+2) # add right right
            if ((index-8)>-1): # check the level below the king
                self.board.white_immediate_shelter |= 1 << (index-8) # below
                if ((index-8-1)%8<7):
                    self.board.white_immediate_shelter |= 1 << (index-8-1) # bottom left corner
                    if ((index-8-2)%8<7):
                        self.board.white_sinu_wide_shelter |= 1 << (index-8-2) # bottom left left
                if ((index-8+1)%8>0):
                    self.board.white_immediate_shelter |= 1 << (index-8+1) # bottom right
                    if ((index-8+2)%8>0):
                        self.board.white_sinu_wide_shelter |= 1 << (index-8+2) # bottom right right
            if ((index-16)>-1): # check two levels below the king
                self.board.white_cross_wide_shelter |= 1 << (index-16) 
                if ((index-16-1)%8<7): # bottom bottom left
                    self.board.white_sinu_wide_shelter |= 1 << (index-16-1)
                    if ((index-16-2)%8<7): # bottom bottom left left
                        self.board.white_diag_wide_shelter |= 1 << (index-16-2)
                if ((index-16+1)%8>0): # bottom bottom right
                    self.board.white_sinu_wide_shelter |= 1 << (index-16+1)
                    if ((index-16+2)%8>0): # bottom bottom right right
                        self.board.white_diag_wide_shelter |= 1 << (index-16+2)
            if ((index+8)<56): # level above king
                self.board.white_immediate_shelter |= 1 << (index+8)
                if ((index+8-1)%8<7):
                    self.board.white_immediate_shelter |= 1 << (index+8-1) # top left corner
                    if ((index+8-2)%8<7):
                        self.board.white_sinu_wide_shelter |= 1 << (index+8-2) # top left left
                if ((index+8+1)%8>0):
                    self.board.white_immediate_shelter |= 1 << (index+8+1) # top right
                    if ((index+8+2)%8>0):
                        self.board.white_sinu_wide_shelter |= 1 << (index+8+2) # top right right
            if ((index+16)<56): # two levels above king
                self.board.white_cross_wide_shelter |= 1 << (index+16) 
                if ((index+16-1)%8<7): # top top left
                    self.board.white_sinu_wide_shelter |= 1 << (index+16-1)
                    if ((index+16-2)%8<7): # top top left left
                        self.board.white_diag_wide_shelter |= 1 << (index+16-2)
                if ((index+16+1)%8>0): # top top right
                    self.board.white_sinu_wide_shelter |= 1 << (index+16+1)
                    if ((index+16+2)%8>0): # top top right right
                        self.board.white_diag_wide_shelter |= 1 << (index+16+2)
        else:
            self.board.black_immediate_shelter = 0x0000 # clear integer representations of the shelter
            self.board.black_diag_wide_shelter = 0x0000
            self.board.black_cross_wide_shelter = 0x0000
            self.board.black_sinu_wide_shelter = 0x0000
            if (self.board.black_king.bit_count() != 1): # if there is no king, do not attempt to eval
                return
            
            index = utils.singleton_board_to_index(self.board.black_king) # get index of the king
            if ((index-1)%8<7): # check left of king
                self.board.black_immediate_shelter |= 1 << (index-1) # left 
                if ((index-2)%8<7): self.board.black_cross_wide_shelter |= 1 << (index-2) # left left
            if ((index+1)%8>0): # check right of king
                self.board.black_immediate_shelter |= 1 << (index+1) # right
                if ((index+2)%8>0): self.board.black_cross_wide_shelter |= 1 << (index+2) # right right
            if ((index-8)>-1): # level below king
                self.board.black_immediate_shelter |= 1 << (index-8)
                if ((index-8-1)%8<7):
                    self.board.black_immediate_shelter |= 1 << (index-8-1) # bottom left corner
                    if ((index-8-2)%8<7):
                        self.board.black_sinu_wide_shelter |= 1 << (index-8-2) # bottom left left
                if ((index-8+1)%8>0):
                    self.board.black_immediate_shelter |= 1 << (index-8+1) # bottom right
                    if ((index-8+2)%8>0):
                        self.board.black_sinu_wide_shelter |= 1 << (index-8+2) # bottom right right
            if ((index-16)>-1): # two levels below king
                self.board.black_cross_wide_shelter |= 1 << (index-16) 
                if ((index-16-1)%8<7): # bottom bottom left
                    self.board.black_sinu_wide_shelter |= 1 << (index-16-1)
                    if ((index-16-2)%8<7): # bottom bottom left left
                        self.board.black_diag_wide_shelter |= 1 << (index-16-2)
                if ((index-16+1)%8>0): # bottom bottom right
                    self.board.black_sinu_wide_shelter |= 1 << (index-16+1)
                    if ((index-16+2)%8>0): # bottom bottom right right
                        self.board.black_diag_wide_shelter |= 1 << (index-16+2)
            if ((index+8)<56): # level above king
                self.board.black_immediate_shelter |= 1 << (index+8)
                if ((index+8-1)%8<7):
                    self.board.black_immediate_shelter |= 1 << (index+8-1) # top left corner
                    if ((index+8-2)%8<7):
                        self.board.black_sinu_wide_shelter |= 1 << (index+8-2) # top left left
                if ((index+8+1)%8>0):
                    self.board.black_immediate_shelter |= 1 << (index+8+1) # top right
                    if ((index+8+2)%8>0):
                        self.board.black_sinu_wide_shelter |= 1 << (index+8+2) # top right right
            if ((index+16)<56): # two levels above king
                self.board.black_cross_wide_shelter |= 1 << (index+16) 
                if ((index+16-1)%8<7): # top top left
                    self.board.black_sinu_wide_shelter |= 1 << (index+16-1)
                    if ((index+16-2)%8<7): # top top left left
                        self.board.black_diag_wide_shelter |= 1 << (index+16-2)
                if ((index+16+1)%8>0): # top top right
                    self.board.black_sinu_wide_shelter |= 1 << (index+16+1)
                    if ((index+16+2)%8>0): # top top right right
                        self.board.black_diag_wide_shelter |= 1 << (index+16+2)
    
    '''
        Evaluates board utility for a certain color in the endgame by checking the mobility of that colors king and the king's position.
        
        PARAMS
        color: the color whose king this method finds the shelter of

        RETURNS
        evaluate_value: score of the current board for a given color based on endgame king mobility and position
    '''
    
    def get_endgame_points(self, color):
        evaluate_value = 0
        point_rank_per_row = [0.75, 0.5, 0.35, 0.25]
        if color == constants.BLACK:
            king = self.board.black_king
        else:
            point_rank_per_row = point_rank_per_row[::-1]
            king = self.board.white_king

        # king mobility
        king_index = utils.singleton_board_to_index(king)
        king_moves = self.board.get_moves(king_index)
        
        evaluate_value += king_moves.bit_count() * 0.15

        for i, row_rank_val in enumerate(point_rank_per_row):
            row_mask = 60 << 8 * (i + 2)
            if king & row_mask:
                evaluate_value += row_rank_val
            
        return evaluate_value

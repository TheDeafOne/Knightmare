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
            
        get_position_score(color)
        get_attacking_potential(all_moves, color, queen, rook, bishop, knight, pawn)
        get_king_security(color)
        get_king_shelter(color)
        get_endgame_points(color)
    '''
    
    def __init__(self, board):
        self.board = board
        
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
        Evaluates the utility of the current board for a certain color based on the mobility of various pieces. 
        This method adds 1/10 for each free space a piece has access to.
             
        PARAMS
        all_moves: a dictionary containing integer representations of all possible moves for all pieces on the board
        color: the color pieces being evaluated
        
        RETURNS
        mobility: the mobility score of the given color for the current board      
        
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
            score -= 0.015*((self.board.white_pieces & 0xff).bit_count()) # first rank
            score += 0.015*((self.board.white_pieces & (0xff << 8)).bit_count()) # second rank
            score += 0.030*((self.board.white_pieces & (0xff << 8*2)).bit_count()) # third rank
            score += 0.45*((self.board.white_pieces & (0xff << 8*3)).bit_count()) # fourth rank
            score += 0.60*((self.board.white_pieces & (0xff << 8*4)).bit_count()) # fifth rank
            score += 0.75*((self.board.white_pieces & (0xff << 8*5)).bit_count()) # sixth rank
            score += 0.60*((self.board.white_pieces & (0xff << 8*6)).bit_count()) # seventh rank
            score += 0.030*((self.board.white_pieces & (0xff << 8*7)).bit_count()) # eigth rank           
        else:
            score -= 0.015*((self.board.black_pieces & 0xff << 8*7).bit_count()) # first rank (reverse orientation)
            score += 0.015*((self.board.black_pieces & (0xff << 8*6)).bit_count()) # second rank
            score += 0.030*((self.board.black_pieces & (0xff << 8*5)).bit_count()) # third rank
            score += 0.45*((self.board.black_pieces & (0xff << 8*4)).bit_count()) # fourth rank
            score += 0.60*((self.board.black_pieces & (0xff << 8*3)).bit_count()) # fifth rank
            score += 0.75*((self.board.black_pieces & (0xff << 8*2)).bit_count()) # sixth rank
            score += 0.60*((self.board.black_pieces & (0xff << 8*1)).bit_count()) # seventh rank
            score += 0.030*((self.board.black_pieces & 0xff).bit_count()) # eigth rank
        return score
    
    '''
        Get the attacking potential of a board (applicable in all stages)
        
        + 1/10 of all attacked pieces strength
        + 1/10 for attacking the king
        + 1/20 for attacking the king's immediate shelter
        + 1/20 * 2/3 for attacking the king's wide shelter
    '''
    def get_attacking_potential(self, all_moves, color, queen, rook, bishop, knight, pawn):
        attack_potential = 0
        
        if (color == constants.WHITE):
            wide_shelter = self.board.black_cross_wide_shelter | self.board.black_diag_wide_shelter | self.board.black_sinu_wide_shelter
            for piece in constants.WHITE_PIECES:
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    attack_potential += queen/10*(each_piece_move[1] & self.board.black_queens).bit_count()
                    attack_potential += rook/10*(each_piece_move[1] & self.board.black_rooks).bit_count()
                    attack_potential += bishop/10*(each_piece_move[1] & self.board.black_bishops).bit_count()
                    attack_potential += knight/10*(each_piece_move[1] & self.board.black_knights).bit_count()
                    attack_potential += pawn/10*(each_piece_move[1] & self.board.black_pawns).bit_count()
                    
                    if (piece == constants.WHITE_QUEEN):
                        attack_potential += queen/10*(each_piece_move[1] & self.board.black_king).bit_count()
                        attack_potential += queen/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += queen/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    elif (piece == constants.WHITE_ROOK):
                        attack_potential += rook/10*(each_piece_move[1] & self.board.black_king).bit_count()
                        attack_potential += rook/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += rook/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    elif (piece == constants.WHITE_BISHOP):
                        attack_potential += bishop/10*(each_piece_move[1] & self.board.black_king).bit_count()
                        attack_potential += bishop/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += bishop/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    if (piece == constants.WHITE_KNIGHT):
                        attack_potential += knight/10*(each_piece_move[1] & self.board.black_king).bit_count()
                        attack_potential += knight/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += knight/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
                    if (piece == constants.WHITE_PAWN):
                        attack_potential += pawn/10*(each_piece_move[1] & self.board.black_king).bit_count()
                        attack_potential += pawn/20*(each_piece_move[1] & self.board.black_pieces & self.board.black_immediate_shelter).bit_count()
                        attack_potential += pawn/20 * 2/3 * (each_piece_move[1] & self.board.black_pieces & wide_shelter).bit_count()
        else:
            for piece in constants.BLACK_PIECES:
                wide_shelter = self.board.white_cross_wide_shelter | self.board.white_diag_wide_shelter | self.board.white_sinu_wide_shelter
                piece_moves = all_moves[piece]
                for each_piece_move in piece_moves:
                    attack_potential += queen/10*(each_piece_move[1] & self.board.white_queens).bit_count()
                    attack_potential += rook/10*(each_piece_move[1] & self.board.white_rooks).bit_count()
                    attack_potential += bishop/10*(each_piece_move[1] & self.board.white_bishops).bit_count()
                    attack_potential += knight/10*(each_piece_move[1] & self.board.white_knights).bit_count()
                    attack_potential += pawn/10*(each_piece_move[1] & self.board.white_pawns).bit_count()
                    
                    if (piece == constants.BLACK_QUEEN):
                        attack_potential += queen/10*(each_piece_move[1] & self.board.white_king).bit_count()
                        attack_potential += queen/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += queen/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    elif (piece == constants.BLACK_ROOK):
                        attack_potential += rook/10*(each_piece_move[1] & self.board.white_king).bit_count()
                        attack_potential += rook/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += rook/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    elif (piece == constants.BLACK_BISHOP):
                        attack_potential += bishop/10*(each_piece_move[1] & self.board.white_king).bit_count()
                        attack_potential += bishop/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += bishop/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    if (piece == constants.BLACK_KNIGHT):
                        attack_potential += knight/10*(each_piece_move[1] & self.board.white_king).bit_count()
                        attack_potential += knight/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += knight/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
                    if (piece == constants.BLACK_PAWN):
                        attack_potential += pawn/10*(each_piece_move[1] & self.board.white_king).bit_count()
                        attack_potential += pawn/20*(each_piece_move[1] & self.board.white_pieces & self.board.white_immediate_shelter).bit_count()
                        attack_potential += pawn/20 * 2/3 * (each_piece_move[1] & self.board.white_pieces & wide_shelter).bit_count()
        return attack_potential
    
    '''
        Measure king security
    '''
    def get_king_security(self,color):
        king_security = 0.0
        if (color == constants.WHITE):
            king_security += .50*(self.board.white_pawns & self.board.white_immediate_shelter).bit_count() \
                + .50/2*(self.board.white_pawns & (self.board.white_cross_wide_shelter | self.board.white_diag_wide_shelter)).bit_count() \
                + .50/3*(self.board.white_pawns & self.board.white_sinu_wide_shelter).bit_count()
            full_shelter = self.board.white_cross_wide_shelter | self.board.white_diag_wide_shelter | self.board.white_immediate_shelter | self.board.white_sinu_wide_shelter
            king_security += 0.1*(full_shelter & self.board.white_queens).bit_count() \
                + 0.15*(full_shelter & self.board.white_rooks).bit_count() \
                + 0.25*(full_shelter & self.board.white_knights).bit_count() \
                + 0.30*(full_shelter & self.board.white_bishops).bit_count()
        else:
            king_security += .50*(self.board.black_pawns & self.board.black_immediate_shelter).bit_count() \
                + .50/2*(self.board.black_pawns & (self.board.black_cross_wide_shelter | self.board.black_diag_wide_shelter)).bit_count() \
                + .50/3*(self.board.black_pawns & self.board.black_sinu_wide_shelter).bit_count()
            full_shelter = self.board.black_cross_wide_shelter | self.board.black_diag_wide_shelter | self.board.black_immediate_shelter | self.board.black_sinu_wide_shelter
            king_security += 0.1*(full_shelter & self.board.black_queens).bit_count() \
                + 0.15*(full_shelter & self.board.black_rooks).bit_count() \
                + 0.25*(full_shelter & self.board.black_knights).bit_count() \
                + 0.30*(full_shelter & self.board.black_bishops).bit_count()
        return king_security
    
    '''
        Re-gets king shelter positions after the king has been moved
    '''
    def get_king_shelter(self, color):        
        if (color == constants.WHITE):
            self.board.white_immediate_shelter = 0x0000
            self.board.white_diag_wide_shelter = 0x0000
            self.board.white_cross_wide_shelter = 0x0000
            self.board.white_sinu_wide_shelter = 0x0000
            if (self.board.white_king.bit_count() != 1):
                return
            
            index = utils.singleton_board_to_index(self.board.white_king)
            if ((index-1)%8<7): 
                self.board.white_immediate_shelter |= 1 << (index-1) # left 
                if ((index-2)%8<7): self.board.white_cross_wide_shelter |= 1 << (index-2) # two left
            if ((index+1)%8>0):
                self.board.white_immediate_shelter |= 1 << (index+1) # right
                if ((index+2)%8>0): self.board.white_cross_wide_shelter |= 1 << (index+2) # two right
            if ((index-8)>-1): # level below king
                self.board.white_immediate_shelter |= 1 << (index-8) # below
                if ((index-8-1)%8<7):
                    self.board.white_immediate_shelter |= 1 << (index-8-1) # bottom left corner
                    if ((index-8-2)%8<7):
                        self.board.white_sinu_wide_shelter |= 1 << (index-8-2) # bottom left left
                if ((index-8+1)%8>0):
                    self.board.white_immediate_shelter |= 1 << (index-8+1) # bottom right
                    if ((index-8+2)%8>0):
                        self.board.white_sinu_wide_shelter |= 1 << (index-8+2) # bottom right right
            if ((index-16)>-1): # two levels below king
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
            self.board.black_immediate_shelter = 0x0000
            self.board.black_diag_wide_shelter = 0x0000
            self.board.black_cross_wide_shelter = 0x0000
            self.board.black_sinu_wide_shelter = 0x0000
            if (self.board.black_king.bit_count() != 1):
                return
            
            index = utils.singleton_board_to_index(self.board.black_king)
            if ((index-1)%8<7): 
                self.board.black_immediate_shelter |= 1 << (index-1) # left 
                if ((index-2)%8<7): self.board.black_cross_wide_shelter |= 1 << (index-2) # two left
            if ((index+1)%8>0):
                self.board.black_immediate_shelter |= 1 << (index+1) # right
                if ((index+2)%8>0): self.board.black_cross_wide_shelter |= 1 << (index+2) # two right
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

from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import math
import copy
import datetime

class MiniMax():
    '''
        Class to run the minimax algorithm with alpha-beta pruning for chess
        
        ATTRIBUTES
        MAX_DEPTH: the depth at which we call minimax recursively (ply depth is MAX_DEPTH + 1)
        next_move: a tuple of squares to hold the next move to make
        
        METHODS
        get_next_move(board,player)
            initiates minimax for the given player (black or white) for the given board, and deposits the recommended move
            into next_move
            returns the best move represented as a tuple
            
        minimax(maximizing, board, player, depth, alpha, beta)
            recursive function for searching the minimax tree
            returns the score of the given board state
            
        get_max(board,color,is_terminal_board)
            returns the score of the given board for a maximizing player, using the board's get_score function
        
        get_min(board,color,is_terminal_board)
            returns the score of the given board for a minimizing player, which will equal -get_max with the same parameters
    '''
    def __init__(self, depth=2):
        self.MAX_DEPTH = depth # ply depth is MAX_DEPTH + 1
        self.next_move = tuple()
        self.use_eval_functions = True

    '''
        Gets the minimax optimized next move for the given player on a given board
        
        PARAMS
        board: the current board for the chess game
        player: the player (black or white) asking for a move
        
        RETURNS
        the recommended move for the player in the form (from_square, to_square)
    '''
    def get_next_move(self,board,player):
        self.minimax(True,board,player,0,-math.inf,math.inf)
        return self.next_move

    '''
        Implements the minimax algorith with alpha-beta pruning
        
        PARAMS
        board: the current board state
        maximizing: boolean indicating whether we are maximizing
        player: the current player (black or white) making the next move in the minimax tree
        depth: the current search tree depth
        alpha: the highest value choice we have found so far at any point along the path of the maximizer
        beta: the lower value choice we have found so far at any point along the path of the minimizer
        
        RETURNS
        the best score (maximized or minimized) of the current search tree depth, 
    '''
    def minimax(self, maximizing, board, player, depth, alpha, beta):
        possible_moves = []
        break_cond = False # flag to help break out of nested for loops

        board_cpy = copy.deepcopy(board)
        # get bit board possible moves for each of the current player's pieces
        for i in range (0,64):
            if (board_cpy.check_piece(i,player)):
                moves = board_cpy.get_moves(utils.index_to_square(i))
                possible_moves.append((i,moves))

        if (maximizing):
            best_val = -math.inf
            if (depth < self.MAX_DEPTH):
                for moves in possible_moves:     # for each piece of player's color
                    if (break_cond): break       # break if alpha-beta break was signaled in the nested loop
                    for i in range (0,64):           # for each square in the board
                        if moves[1] & (1<<i):        # if the piece can move to that square
                            is_terminal_board = board_cpy.move_piece(utils.index_to_square(moves[0]),utils.index_to_square(i)) # make move
                            if (not is_terminal_board and player == constants.WHITE): # if not a terminal board call minimax to continue the search tree
                                score = (self.minimax(not maximizing, board_cpy, constants.BLACK, depth+1, alpha, beta))
                            elif (not is_terminal_board): # same except for the other color 
                                score = (self.minimax(not maximizing, board_cpy, constants.WHITE, depth+1, alpha, beta))
                            else: # if terminal state, use the get_max function to return a score
                                score = self.get_max(board,player,is_terminal_board)
                            board_cpy.undo_last() # undo move

                            if (score >= best_val): # keeping a running max
                                if (depth == 0): # if we are at, depth 0, these are the moves the starting player would make
                                    self.next_move = (utils.index_to_square(moves[0]),utils.index_to_square(i)) # track the next move
                                best_val = score

                            alpha = max(alpha,best_val) # prune states with alpha-beta
                            if (beta <= alpha):
                                break_cond = True
                                break
            else: # if we've reached max depth
                for moves in possible_moves:    # for each piece of player's color
                    if (break_cond): break      # break if alpha-beta break was signaled in the nested loop
                    for i in range (0,64):          # for each square in the board
                        if moves[1] & (1<<i):       # if the piece can move to that square
                            is_terminal_board = board_cpy.move_piece(utils.index_to_square(moves[0]),utils.index_to_square(i))
                            score = self.get_max(board,player,is_terminal_board) # use get max to get the score
                            board_cpy.undo_last()
                            best_val = max(score,best_val) # track running max

                            alpha = max(alpha,best_val) # prune with alpha-beta
                            if (beta <= alpha):
                                break_cond = True
                                break
            return best_val
        else:
            best_val = math.inf
            if (depth < self.MAX_DEPTH):
                for moves in possible_moves:    # for each piece of player's color
                    if (break_cond): break      # break if alpha-beta break was signaled in the nested loop
                    for i in range (0,64):          # for each square in the board
                        if moves[1] & (1<<i):       # if the piece can move to that square
                            is_terminal_board = board_cpy.move_piece(utils.index_to_square(moves[0]),utils.index_to_square(i))
                            if (not is_terminal_board and player == constants.WHITE): # if not a terminal board call minimax to continue the search tree
                                score = (self.minimax(not maximizing, board_cpy, constants.BLACK, depth+1, alpha, beta))
                            elif (not is_terminal_board): # recursive call for the other color
                                score = (self.minimax(not maximizing, board_cpy, constants.WHITE, depth+1, alpha, beta))
                            else:
                                score = self.get_min(board,player,is_terminal_board) # if reached a terminal state, use get_min to get a score
                            board_cpy.undo_last()

                            best_val = min(score, best_val) # track running min
                            beta = min(best_val, beta) # prune with alpha-beta
                            if (beta <= alpha):
                                break_cond = True
                                break
            else:
                for moves in possible_moves:    # for each piece of player's color
                    if (break_cond): break      # break if alpha-beta break was signaled in the nested loop
                    for i in range (0,64):          # for each square in the board
                        if moves[1] & (1<<i):       # if the piece can move to that square
                            is_terminal_board = board_cpy.move_piece(utils.index_to_square(moves[0]),utils.index_to_square(i))
                            score = self.get_min(board,player,is_terminal_board)  
                            board_cpy.undo_last()
                            best_val = min(score,best_val,player)

                            beta = min(best_val, beta) # track running min
                            if (beta <= alpha): # prune with alpha-beta
                                break_cond = True
                                break
            return best_val

    '''
        Gets the score of the current board for the current color for minimax, from the perspective of a maximizer
        
        PARAMS
        board: current board state
        color: color currently making a move
        is_terminal_board: an integer, where 1 indicates a winning board state (checkmate), and 2 indicates a stalemate (exceeded max moves)
        
        RETURNS
        score of the given board
    '''
    def get_max(self,board,color,is_terminal_board):
        # start = datetime.datetime.now()
        score = board.get_score(color, is_terminal_board) if self.use_eval_functions else 0 # get score using a function of the board
        # end = datetime.datetime.now()
        # print((end-start).total_seconds())
        return score

    '''
        Gets the score of the current board for the current color for minimax, from the perspective of a minimizer
        
        PARAMS
        board: current board state
        color: color currently making a move
        is_terminal_board: an integer, where 1 indicates a winning board state (checkmate), and 2 indicates a stalemate (exceeded max moves)
        
        RETURNS
        score of the given board
    '''
    def get_min(self,board,color,is_terminal_board):
        return -self.get_max(board,color,is_terminal_board)

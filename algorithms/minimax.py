from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import math
import copy

class MiniMax():
    def __init__(self):
        self.MAX_DEPTH = 4 # ply depth is MAX_DEPTH + 1
        self.next_move = tuple()

    '''
        gets the minimax optimized next move for the given player on a given board
    '''
    def get_next_move(self,board,player):
        self.minimax(True,board,player,0,-math.inf,math.inf)
        return self.next_move

    '''
        Implements the minimax algorith with alpha-beta pruning
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
                            board_cpy.move_piece(utils.index_to_square(moves[0]),utils.index_to_square(i))
                            if (player == constants.WHITE):
                                score = (self.minimax(not maximizing, board_cpy, constants.BLACK, depth+1, alpha, beta))
                            else:
                                score = (self.minimax(not maximizing, board_cpy, constants.WHITE, depth+1, alpha, beta))
                            board_cpy.undo_last()

                            if (score >= best_val): # could make >= to keep latest best move rather than first
                                if (depth == 0):
                                    self.next_move = (utils.index_to_square(moves[0]),utils.index_to_square(i)) # track next move
                                best_val = score

                            alpha = max(alpha,best_val)
                            if (beta <= alpha):
                                break_cond = True
                                break
            else:
                for moves in possible_moves:    # for each piece of player's color
                    if (break_cond): break      # break if alpha-beta break was signaled in the nested loop
                    for i in range (0,64):          # for each square in the board
                        if moves[1] & (1<<i):       # if the piece can move to that square
                            score = self.get_max(board,(utils.index_to_square(moves[0]),utils.index_to_square(i)),player)
                            best_val = max(score,best_val)

                            alpha = max(alpha,best_val)
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
                            board_cpy.move_piece(utils.index_to_square(moves[0]),utils.index_to_square(i))
                            if (player == constants.WHITE):
                                score = (self.minimax(not maximizing, board_cpy, constants.BLACK, depth+1, alpha, beta))
                            else:
                                score = (self.minimax(not maximizing, board_cpy, constants.WHITE, depth+1, alpha, beta))
                            board_cpy.undo_last()

                            best_val = min(score, best_val)
                            beta = min(best_val, beta)
                            if (beta <= alpha):
                                break_cond = True
                                break
            else:
                for moves in possible_moves:    # for each piece of player's color
                    if (break_cond): break      # break if alpha-beta break was signaled in the nested loop
                    for i in range (0,64):          # for each square in the board
                        if moves[1] & (1<<i):       # if the piece can move to that square
                            score = self.get_min(board,(utils.index_to_square(moves[0]),utils.index_to_square(i)),player)  
                            best_val = min(score,best_val,player)

                            beta = min(best_val, beta)
                            if (beta <= alpha):
                                break_cond = True
                                break
            return best_val

    def get_max(self,board,move,color):
        is_winning_board = board.move_piece(move[0],move[1])
        score = board.get_score(color, is_winning_board)
        board.undo_last()
        return score

    def get_min(self,board,move,color):
        return -self.get_max(board,move,color)

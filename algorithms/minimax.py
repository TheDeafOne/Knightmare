from game_logic.board import Board
from game_logic.board_utils import BoardUtils as utils, BoardConstants as constants
import math
import copy

class MiniMax():
    def __init__(self):
        self.MAX_DEPTH = 4
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

        board_cpy = copy.deepcopy(board)
        # get possible moves for the current player
        for i in range (0,64):
            if (board_cpy.check_piece(i,player)):
                moves = board_cpy.get_moves(utils.index_to_square(i))
                for j in range (0,64):
                    if moves & (1 << j):
                        possible_moves.append((utils.index_to_square(i),utils.index_to_square(j)))
                        #print(utils.index_to_square(i) + " to " + utils.index_to_square(j))

        if (maximizing):
            best_val = -math.inf
            if (depth < self.MAX_DEPTH):
                for move in possible_moves:
                    board_cpy.move_piece(move[0],move[1])
                    if (player == constants.WHITE):
                        score = (self.minimax(not maximizing, board_cpy, constants.BLACK, depth+1, alpha, beta))
                    else:
                        score = (self.minimax(not maximizing, board_cpy, constants.WHITE, depth+1, alpha, beta))
                    board_cpy.undo_last()

                    if (score >= best_val): # could make >= to keep latest best move rather than first
                        if (depth == 0):
                            self.next_move = move # track next move
                        best_val = score

                    alpha = max(alpha,best_val)
                    if (beta <= alpha):
                        break
            else:
                for move in possible_moves:
                    score = self.get_max(board,move)
                    best_val = max(score,best_val)

                    alpha = max(alpha,best_val)
                    if (beta <= alpha):
                        break
            return best_val
        else:
            best_val = math.inf
            if (depth < self.MAX_DEPTH):
                for move in possible_moves:
                    board_cpy.move_piece(move[0],move[1])
                    if (player == constants.WHITE):
                        score = (self.minimax(not maximizing, board_cpy, constants.BLACK, depth+1, alpha, beta))
                    else:
                        score = (self.minimax(not maximizing, board_cpy, constants.WHITE, depth+1, alpha, beta))
                    board_cpy.undo_last()

                    best_val = min(score, best_val)
                    beta = min(best_val, beta)
                    if (beta <= alpha):
                        break
            else:
                for move in possible_moves:
                    score = self.get_min(board,move)  
                    best_val = min(score, best_val)

                    beta = min(best_val, beta)
                    if (beta <= alpha):
                        break
            return best_val

    def get_max(self,board,move):
        return 0

    def get_min(self,board,move):
        return -self.get_max(move,board)

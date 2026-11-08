"""Legal moves for the bitboard model, including king-safety filtering.

Geometric attacks are separate: pinned pieces still attack king destinations.
"""
from .board_utils import BoardUtils as utils

KNIGHT = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
DIAGONAL = ((1, 1), (1, -1), (-1, 1), (-1, -1))
STRAIGHT = ((1, 0), (-1, 0), (0, 1), (0, -1))


def attacks(board, origin):
    piece = board.get_piece(origin)
    if piece == '-':
        return 0
    row, col = divmod(origin, 8)
    kind = piece.upper()
    if kind == 'P':
        offsets = ((1 if piece.isupper() else -1, -1), (1 if piece.isupper() else -1, 1))
    elif kind == 'N':
        offsets = KNIGHT
    elif kind == 'K':
        offsets = DIAGONAL + STRAIGHT
    else:
        offsets = DIAGONAL if kind == 'B' else STRAIGHT if kind == 'R' else DIAGONAL + STRAIGHT
    result = 0
    for dr, dc in offsets:
        for step in range(1, 8) if kind in 'BRQ' else (1,):
            r, c = row + dr * step, col + dc * step
            if not (0 <= r < 8 and 0 <= c < 8):
                break
            target = r * 8 + c
            result |= 1 << target
            if board.board & (1 << target):
                break
    return result


def attacked(board, square, by_color):
    pieces = board.white_pieces if by_color == 0 else board.black_pieces
    return any(attacks(board, origin) & (1 << square)
               for origin in utils.board_to_indexes(pieces))


def in_check(board, color):
    king = board.white_king if color == 0 else board.black_king
    return king == 0 or attacked(board, utils.singleton_board_to_index(king), 1 - color)


def legal_moves(board, origin):
    piece = board.get_piece(origin)
    if piece == '-':
        return 0
    color = 0 if piece.isupper() else 1
    own = board.white_pieces if color == 0 else board.black_pieces
    enemy = board.black_pieces if color == 0 else board.white_pieces
    enemy_king = board.black_king if color == 0 else board.white_king
    candidates = attacks(board, origin) & ~own & ~enemy_king
    if piece.upper() == 'P':
        candidates &= enemy | board.en_passant_board
        direction = 8 if color == 0 else -8
        target = origin + direction
        if 0 <= target < 64 and board.get_piece(target) == '-':
            candidates |= 1 << target
            if origin // 8 == (1 if color == 0 else 6) and board.get_piece(target + direction) == '-':
                candidates |= 1 << (target + direction)
    if piece.upper() == 'K' and origin == (4 if color == 0 else 60) and not in_check(board, color):
        for right, rook, empty, transit in (
            ('K' if color == 0 else 'k', origin + 3, (1, 2), (1, 2)),
            ('Q' if color == 0 else 'q', origin - 4, (-1, -2, -3), (-1, -2)),
        ):
            if (right in board.castling_rights and board.get_piece(rook) == ('R' if color == 0 else 'r')
                    and all(board.get_piece(origin + d) == '-' for d in empty)
                    and all(not attacked(board, origin + d, 1 - color) for d in transit)):
                candidates |= 1 << (origin + transit[-1])
    result = 0
    for target in utils.board_to_indexes(candidates):
        state = board._snapshot()
        try:
            board._apply_move(origin, target)
            if not in_check(board, color):
                result |= 1 << target
        finally:
            board._restore(state)
    return result

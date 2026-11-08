"""Play and record a real Knightmare-vs-random game; validate every move independently."""
import argparse
import json
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import chess
import chess.pgn
from PIL import Image, ImageDraw, ImageFont
from algorithms.minimax import MiniMax
from game_logic.board import Board

ROOT = Path(__file__).resolve().parents[1]


def render(oracle, ply, label, last_move=None, outcome=None):
    image = Image.new('RGB', (640, 748), '#17212d')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype('Arial.ttf', 23)
    except OSError:
        font = ImageFont.load_default(size=23)
    small = ImageFont.load_default(size=17)
    draw.text((32, 17), 'Knightmare vs random', fill='#f3e9d7', font=font)
    draw.text((32, 51), 'Black: Knightmare / White: seeded random', fill='#c0c9d1', font=small)
    size, left, top = 70, 40, 92
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            x, y = left + col * size, top + row * size
            color = '#e5dac5' if (row + col) % 2 == 0 else '#6f877b'
            if last_move and square in (last_move.from_square, last_move.to_square):
                color = '#d8b45a'
            draw.rectangle((x, y, x + size, y + size), fill=color)
            piece = oracle.piece_at(square)
            if piece:
                side = 'white' if piece.color else 'black'
                names = {'p':'pawn','n':'knight','b':'bishop','r':'rook','q':'queen','k':'king'}
                asset = Image.open(ROOT / 'game_logic' / 'assets' / f'{side}_{names[piece.symbol().lower()]}.bmp').convert('RGB').resize((54, 54))
                # Existing sprites have a white background. Preserve the pieces, remove only near-white background.
                alpha = asset.convert('RGBA')
                pixels = asset.get_flattened_data() if hasattr(asset, 'get_flattened_data') else asset.getdata()
                alpha.putdata([(r,g,b,0 if min(r,g,b)>245 else 255) for r,g,b in pixels])
                image.paste(alpha, (x + 8, y + 8), alpha)
    for i in range(8):
        draw.text((left + i*size + 29, top + 564), 'abcdefgh'[i], fill='#d6dddf', font=small)
        draw.text((15, top + i*size + 25), str(8-i), fill='#d6dddf', font=small)
    draw.text((40, 692), f'Ply {ply}: {label}', fill='#f3e9d7', font=font)
    if outcome:
        draw.rectangle((0, 0, 640, 47), fill='#17212d')
        draw.text((32, 17), outcome, fill='#f3e9d7', font=font)
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--depth', type=int, default=2)
    parser.add_argument('--max-plies', type=int, default=300)
    args = parser.parse_args()
    rng, board, oracle, engine = random.Random(args.seed), Board(), chess.Board(), MiniMax(args.depth)
    game = chess.pgn.Game()
    game.headers.update(Event='Knightmare demonstration', White='Seeded random', Black=f'Knightmare depth {args.depth}', Date='2026.11.08')
    node, records, frames = game, [], [render(oracle, 0, 'Starting position')]
    for ply in range(1, args.max_plies + 1):
        player = 0 if oracle.turn else 1
        if board.outcome(player) or oracle.is_game_over(claim_draw=True):
            break
        moves = engine.moves(board, player)
        pair = rng.choice(moves) if player == 0 else engine.get_next_move(board, player)
        move = chess.Move.from_uci(''.join(pair))
        if oracle.piece_at(move.from_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in (0,7):
            move.promotion = chess.QUEEN
        if move not in oracle.legal_moves:
            raise AssertionError(f'Illegal move at ply {ply}: {move}')
        san = oracle.san(move)
        board.move_piece(*pair)
        oracle.push(move)
        node = node.add_variation(move)
        if [board.get_piece(i) for i in range(64)] != [oracle.piece_at(i).symbol() if oracle.piece_at(i) else '-' for i in range(64)]:
            raise AssertionError('Board mismatch')
        records.append({'ply':ply,'uci':move.uci(),'san':san,'fen':oracle.fen(),'nodes':engine.nodes if player else None})
        frames.append(render(oracle, ply, san, move))
        print(f'{ply}: {san}', flush=True)
    result = oracle.result(claim_draw=True)
    game.headers['Result'] = result
    if result != '0-1' or not oracle.is_checkmate():
        raise RuntimeError(f'No checkmate win in this run: {result}. No winning artifact written.')
    ending = render(oracle, len(records), records[-1]['san'], move, 'Knightmare wins by checkmate')
    frames[-1] = ending
    output = ROOT / 'docs'
    output.mkdir(exist_ok=True)
    (output/'winning-game.pgn').write_text(str(game)+'\n')
    (output/'winning-game.json').write_text(json.dumps({'seed':args.seed,'depth':args.depth,'opponent':'uniform random legal moves','result':result,'plies':len(records),'moves':records},indent=2)+'\n')
    frames[0].save(output/'winning-game.gif',save_all=True,append_images=frames[1:],duration=[1200]+[500]*(len(frames)-2)+[4000],loop=0,optimize=True)
    ending.save(output/'winning-position.png')
    print(f'Wrote full {len(records)}-ply game, seed {args.seed}, result {result}',flush=True)


if __name__ == '__main__':
    main()

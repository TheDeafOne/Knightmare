# Knightmare

Knightmare is a chess engine built to explore minimax, alpha-beta pruning, and the heuristics that help a computer choose a move. It includes a console interface and a Pygame board where you can play against the AI or watch two AIs play.

![A complete Knightmare game against a seeded random opponent](docs/winning-game.gif)

*A complete game with Knightmare playing Black at a search depth of two plies against a seeded random opponent. Knightmare wins with **24...Nd4#**.*

[Download the game as PGN](docs/winning-game.pgn) · [Move-by-move record](docs/winning-game.json)

## Our motive

Chess gives us a familiar setting for studying adversarial search. The rules define which moves are possible, but deciding which move is useful requires looking ahead and comparing positions.

Our goal was to build a small engine where those choices could be examined directly. We explored how board representation, search depth, and different evaluation functions affect the moves it makes.

## Playing the AI

Use Python 3.10 or newer. Run these commands from a terminal:

```sh
git clone https://github.com/TheDeafOne/Knightmare.git
cd Knightmare
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` on Windows. Then run:

```sh
python -m pip install -r requirements.txt
python main.py
```

Choose `c` for the console or `g` for the graphical interface. In the GUI, open **Options** to choose human vs. human, human vs. AI, or AI vs. AI, and set the search depth. Select a piece, then a highlighted destination. Press **Escape** to return to the menu.

A ply is one move by one player. Start at depth two: deeper searches take longer, and the GUI waits while the engine thinks. Interactive pawn promotions become queens; the board API also accepts rook, bishop, and knight promotions.

![Knightmare's Pygame board](docs/gui.png)

## How it works

### Board representation

The board uses twelve 64-bit integers, one for each piece type and color. A set bit marks a square occupied by that type of piece. This **bitboard** representation keeps board states compact during search.

[board.py](game_logic/board.py) manages piece placement and reversible moves. Each search move saves the complete state, including captured pieces, castling rights, en passant, and move history, so exploring one branch does not change another.

[rules.py](game_logic/rules.py) separates geometric attacks from legal moves. Candidate moves are filtered for king safety. It handles castling, en passant, promotion, checkmate, and stalemate. Threefold repetition and the fifty-move rule are claimed automatically; basic insufficient-material draws are recognized.

### Search and evaluation

[minimax.py](algorithms/minimax.py) searches legal moves to the selected depth. Alpha-beta pruning skips branches that cannot improve the current choice. Positions are evaluated from the starting player's perspective, and checkmate takes priority over heuristic scores.

[evaluations.py](algorithms/evaluations.py) contains the project's hand-written heuristics, including material, central control, development, mobility, attacks, defended pieces, and king safety. These heuristics give each position a score for the search to compare.

The AI plays at **roughly 600 Elo**.

## Paper

Our [research paper](using_minimax_in_chess.pdf) explores how different evaluation functions affect the moves the engine chooses.

## Reproducing the recording

The game recorder plays the engine against a seeded random opponent, checks every move and board position against the independent `chess` library, and writes the complete GIF, PGN, and JSON record. It reuses the project's existing piece images.

```sh
python -m pip install -r requirements-demo.txt
python tools/record_game.py --seed 7 --depth 2
```

The recording is saved in `docs/`. Use `--seed` and `--depth` to try different games and search settings.

## Tests

With the demonstration dependencies installed:

```sh
python -m unittest discover -s tests -v
```

The regression checks cover opening move counts through three plies (20, 400, and 8,902), independent legal-move comparisons over seeded games, special moves, pins, double check, captures and undo, tactical choices, mate, stalemate, and repetition.

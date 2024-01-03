# Knightmare
## Our Motive
[Chess](https://en.wikipedia.org/wiki/Chess), one of the most well-known turn-based games in the world, has been around for the last few centuries. It has gained multiple variants alongside its followers and has only increased in popularity with time. Our goal is a provide a simple implementation of minimax to act as a player in chess.
## Rules
Chess has a fairly extensive set of rules, which can be found [here](https://en.wikipedia.org/wiki/Rules_of_chess)
## Setup
It's important that the game setup is not only easy to work with throughout the program but also uses the least amount of memory possible. This is because we need to quickly represent tens of thousands of board states, which can take a toll on any CPU.
### Board
To maintain the ideal of having a minimalist representation, we set up a given chess board with a piece-centric approach: [Zobrist hashing](https://en.wikipedia.org/wiki/Zobrist_hashing). Also called the bitboard representation, this method of board representation uses 12 64-bit integers to represent the locations of each unique chess piece (6 for the white pieces, and another 6 for the black pieces). While we use other utility and flag-type variables for other rules, this concept is the core of our board representation. \
This board representation can be found in [board.py](game_logic/board.py). [board.py](game_logic/board.py) contains methods like move_piece and get_piece which allow for efficient manipulation of the board.

### Moves
We identify feasible moves of a given piece through a co-dependent class [move_generator.py](game_logic/move_generator.py) (with its sibling being board.py). We split these classes up because despite their interconnectedness, because the functions they provide are distinct in their use. [move_generator.py](game_logic/move_generator.py) provides the program with every method necessary for efficient movement generation, including utility-esc functions for verifying a check, a mate, and identifying specific piece attack fields.
## Algorithms
### Minimax
[Minimax](https://en.wikipedia.org/wiki/Minimax) is a well-documented recursive adversarial search algorithm. It is one of the more popular algorithms used when developing chess engines, largely due to the benefits it provides when also implementing [alpha-beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning). 
### Evaluation Functions
While Minimax is the foundation of how most chess AI works, it is useless without heuristic evaluation functions for given boards. Each board has a "goodness" value that helps Minimax determine whether to keep that given board state, prune it, or continue down the search tree. This value is found by using common, intuitive heuristics for a board, such as how many pieces are in the center, where the king is, the order in which pieces are developed, and many more. While there are hundreds of such heuristics, we implement a handful that we consider the most valuable. These are documented in [evaluations.py](algorithms/evaluations.py).
## Playing the AI
### Installation and running
clone the project with ```git clone https://github.com/TheDeafOne/Knightmare.git```
install pygames ```python -m pip install pygames```
run main with ```python .\main.py```
### Navigating Playthrough
The AI has an Elo of roughly 600, due to the simplistic implementation and small number of heuristic evaluation functions. To play it, run [main.py](main.py). This will prompt you to either play on the console or the GUI version. Note that the GUI version of the game has some issues with lag due to PyGames threading limitations. More information is provided in the instructions portion of the GUI version.

## Paper
Despite the simple implementation, we found that certain heuristics produced more valuable board evaluations. These our explored in our [research paper](using_minimax_in_chess.pdf).

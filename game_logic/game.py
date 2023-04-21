import pygame
from .board import Board
from .board_utils import BoardConstants as constants

class Chess:
    def __init__(self):
        # initialize game logic
        self.board = Board()
        self.player = self.board.white_pieces
        self.opponent = self.board.black_pieces
        
        # column letters
        self.letters = "abcdefgh"
        
        
        # initialize visualization variables
        # start menu
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)

        self.WINDOW_SIZE = (400, 400)
        self.PIECE_IMAGE_SIZE = (45,45)

        # game
        self.BOARD_SIZE = 8
        self.SQUARE_SIZE = 50
        self.BORDER_SIZE = 25

        self.pieces = [
            pygame.image.load("./game_logic/assets/black_knight.bmp"),
            pygame.image.load("./game_logic/assets/black_pawn.bmp"),
            pygame.image.load("./game_logic/assets/black_bishop.bmp"),
            pygame.image.load("./game_logic/assets/black_rook.bmp"),
            pygame.image.load("./game_logic/assets/black_queen.bmp"),
            pygame.image.load("./game_logic/assets/black_king.bmp"),
            pygame.image.load("./game_logic/assets/white_pawn.bmp"),
            pygame.image.load("./game_logic/assets/white_knight.bmp"),
            pygame.image.load("./game_logic/assets/white_bishop.bmp"),
            pygame.image.load("./game_logic/assets/white_rook.bmp"),
            pygame.image.load("./game_logic/assets/white_queen.bmp"),
            pygame.image.load("./game_logic/assets/white_king.bmp")
        ]
        self.pieces = [pygame.transform.scale(piece_image, self.PIECE_IMAGE_SIZE) for piece_image in self.pieces]
        self.piece_map = dict(zip(["n","p","b","r","q","k","P","N","B","R","Q","K"],self.pieces))
        

        # Create the chess board
        self.draw_board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

        # game states
        self.game_state = "start_menu"
        self.player_state = "selection"

        # Create the window
        pygame.init()
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Knightmare")



    def play(self):
        # Start the game loop
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                elif self.game_state == "start_menu":
                    start_button, options_button, quit_button = self.draw_start_menu()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()
                        if start_button.collidepoint(mouse_position):
                            self.game_state = "game"
                            self.window.fill(0) # clear window
                        if quit_button.collidepoint(mouse_position):
                            pygame.quit()
                            quit()
                elif self.game_state == "options_menu":
                    self.draw_options_menu()
                elif self.game_state == "game":
                    self.draw_game()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()
                        if self.player_state == "selection":
                            position = self.get_square_clicked(mouse_position)
                            print(position)

                            if position != None and self.board.get_piece(position) != constants.EMPTY:
                                self.game_state = "move"
                                moves = self.board.get_moves(position)

                                print(moves)
                        

            # Update the display
            pygame.display.update()

    def draw_start_menu(self):
        # Create the font object
        title_font = pygame.font.SysFont(None, 50)
        option_font = pygame.font.SysFont(None, 40)

        # Create the text objects
        title_text = title_font.render("Choose an Option", True, self.BLACK)
        start_text = option_font.render("Start", True, self.BLACK)
        options_text = option_font.render("Options", True, self.BLACK)
        quit_text = option_font.render("Quit", True, self.BLACK)

        # Get the dimensions of the text objects
        title_text_rect = title_text.get_rect()
        start_text_rect = start_text.get_rect()
        options_text_rect = options_text.get_rect()
        quit_text_rect = quit_text.get_rect()

        # Set the positions of the text objects
        title_text_rect.center = (self.WINDOW_SIZE[0] // 2, 50)
        start_text_rect.center = (self.WINDOW_SIZE[0] // 2, 150)
        options_text_rect.center = (self.WINDOW_SIZE[0] // 2, 250)
        quit_text_rect.center = (self.WINDOW_SIZE[0] // 2, 350)

        self.window.fill(self.WHITE)

        # Draw the text objects
        self.window.blit(title_text, title_text_rect)
        self.window.blit(start_text, start_text_rect)
        self.window.blit(options_text, options_text_rect)
        self.window.blit(quit_text, quit_text_rect)

        return start_text_rect, options_text_rect, quit_text_rect

    def draw_options_menu(self):
        pass

    def draw_game(self):
        # Draw the chess board
        for row in range(8):
            for col in range(8):
                x = col * self.SQUARE_SIZE
                y = row * self.SQUARE_SIZE
                if (row + col) % 2 == 0:
                    color = self.WHITE
                else:
                    color = self.GRAY
                pygame.draw.rect(self.window, color, [x, y, self.SQUARE_SIZE, self.SQUARE_SIZE])

                # draw pieces
                piece = self.draw_board[row][col]
                if piece != "":
                    image = self.piece_map[piece]
                    self.window.blit(image, (x,y))

    
    def get_square_clicked(self, position):
        x, y = position
        x += self.SQUARE_SIZE//2
        y += self.SQUARE_SIZE//2

        
        # if the click was outside the board, ignore it
        if x < self.BORDER_SIZE or x > self.BORDER_SIZE + (self.SQUARE_SIZE * self.BOARD_SIZE) or \
        y < self.BORDER_SIZE or y > self.BORDER_SIZE + (self.SQUARE_SIZE * self.BOARD_SIZE):
            return None
        
        row = (y - self.BORDER_SIZE) // self.SQUARE_SIZE
        col = (x - self.BORDER_SIZE) // self.SQUARE_SIZE

        return self.letters[col] + str(self.BOARD_SIZE - row)
        

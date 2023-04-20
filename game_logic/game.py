import pygame
from .board import Board

class Chess:
    def __init__(self):
        # initialize game logic
        self.board = Board()
        self.player = self.board.white_pieces
        self.opponent = self.board.black_pieces

        # initialize visualization variables
        # start menu
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)

        pygame.init()
        self.WINDOW_SIZE = (400, 400)

        # game
        self.BOARD_SIZE = 8
        self.SQUARE_SIZE = 50
        self.BORDER_SIZE = 25

        
        # Create the window
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Knightmare")

        self.game_state = "start_menu"


    def play(self):
        # Start the game loop
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            if self.game_state == "start_menu":
                start_button, options_button, quit_button = self.draw_start_menu()
                if pygame.mouse.get_pressed()[0]:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button.collidepoint(mouse_pos):
                        self.game_state = "game"
                

            elif self.game_state == "options_menu":
                self.draw_options_menu()
            elif self.game_state == "game":
                self.draw_game()

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


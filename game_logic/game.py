import pygame
from .board import Board
from .board_utils import BoardUtils as utils, BoardConstants as constants


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

        self.WINDOW_SIZE = (425, 425)
        self.PIECE_IMAGE_SIZE = (45, 45)

        # game
        self.BOARD_SIZE = 8
        self.SQUARE_SIZE = 50

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
        self.pieces = [pygame.transform.scale(
            piece_image, self.PIECE_IMAGE_SIZE) for piece_image in self.pieces]
        self.piece_map = dict(
            zip(["n", "p", "b", "r", "q", "k", "P", "N", "B", "R", "Q", "K"], self.pieces))

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
                            self.window.fill(self.WHITE)  # clear window
                        if quit_button.collidepoint(mouse_position):
                            pygame.quit()
                            quit()
                elif self.game_state == "options_menu":
                    self.draw_options_menu()
                elif self.game_state == "game":
                    self.draw_game()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()
                        tentative_moves = []
                        position = self.get_square_clicked(mouse_position)
                        print(position)
                        if position != None:
                            piece = self.board.get_piece(position)
                        if self.player_state == "selection":
                            if position != None and self.board.get_piece_color(piece) == self.player:
                                self.game_state = "move"
                                moves = self.board.board_to_piece_list(
                                    self.board.get_moves(position))
                                tentative_moves = moves
                                for move in moves:
                                    row, col = utils.square_to_row_col(move)
                                    self.highlight_square(row, col)
                        # if self.player_state == "move"
                                

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
                x = col * self.SQUARE_SIZE + self.SQUARE_SIZE//2
                y = row * self.SQUARE_SIZE
                if (row + col) % 2 == 0:
                    color = self.WHITE
                else:
                    color = self.GRAY
                pygame.draw.rect(self.window, color, [
                                 x, y, self.SQUARE_SIZE, self.SQUARE_SIZE])

                # draw pieces
                piece = self.draw_board[row][col]
                if piece != "":
                    image = self.piece_map[piece]
                    self.window.blit(image, (x, y))

        index_font = pygame.font.SysFont("Arial", int(self.SQUARE_SIZE/2.5))
        for i in range(8):
            row_label = index_font.render(str(8-i), True, self.BLACK)
            self.window.blit(row_label, (
                self.SQUARE_SIZE/8,
                i*self.SQUARE_SIZE+self.SQUARE_SIZE/4
            ))

            col_label = index_font.render(self.letters[i], True, self.BLACK)
            self.window.blit(col_label, (
                (i + 1) * self.SQUARE_SIZE - self.SQUARE_SIZE/8,
                self.SQUARE_SIZE*8))
        
        current_player = 'W'
        current_color = self.WHITE
        contrast_color = self.BLACK
        if self.player == self.board.black_pieces:
            current_player = 'B'
            current_color = self.BLACK
            contrast_color = self.WHITE
        player_indication_position = (self.SQUARE_SIZE/8,self.WINDOW_SIZE[0]-self.SQUARE_SIZE/2)
        pygame.draw.circle(self.window, contrast_color, (self.SQUARE_SIZE/3.5,self.WINDOW_SIZE[0]-self.SQUARE_SIZE/4), self.SQUARE_SIZE/4)
        player_label = index_font.render(current_player, True, current_color)
        self.window.blit(player_label, player_indication_position)




    def get_square_clicked(self, position):
        x, y = position
        x -= self.SQUARE_SIZE//2
        # if the click was outside the board, ignore it
        if x < 0 or x > self.WINDOW_SIZE[0] or \
                y < 0 or y > (self.WINDOW_SIZE[0] - self.SQUARE_SIZE/2):
            return None

        row = y // self.SQUARE_SIZE
        col = x // self.SQUARE_SIZE

        return self.letters[col] + str(self.BOARD_SIZE - row)

    # https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame
    def highlight_square(self, x, y):
        left = (x * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2 + self.SQUARE_SIZE)
        top = (y * self.SQUARE_SIZE) - self.SQUARE_SIZE // 2

        # square_surface = pygame.Surface((top, left), pygame.SRCALPHA)
        # pygame.draw.rect(self.window, (0, 0, 255, 125), rect)

        highlight_surface = pygame.Surface(
            (self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)  # the size of your rect
        # this fills the entire surface
        highlight_surface.fill((173, 216, 230, 150))
        self.window.blit(highlight_surface, (top, left))

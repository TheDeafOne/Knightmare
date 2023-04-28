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
        self.EGGSHELL = (245, 245, 245)

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


        # game states
        self.game_state = "start_menu"
        self.player_state = "selection"
        self.current_player_color = "W"
        self.player_moves = []
        self.player_focus = None
        self.winner = ''

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
                        if options_button.collidepoint(mouse_position):
                            print('go to options page')

                elif self.game_state == "options_menu":
                    self.draw_options_menu()
                elif self.game_state == "game":
                    self.draw_game()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()
                        position = self.get_square_clicked(mouse_position)
      
                        if position != None:
                            piece = self.board.get_piece(position)
                            if self.player_state == "selection":
                                if self.board.get_piece_color(piece) == self.player:
                                    self.player_state = "move"
                                    self.player_focus = position
                                    self.player_moves = self.board.board_to_piece_list(
                                        self.board.get_moves(position))
                                    
                            if self.player_state == "move":
                                if position not in self.player_moves:
                                    if self.board.get_piece_color(piece) == self.player:
                                        self.player_focus = position
                                        self.player_moves = self.board.board_to_piece_list(
                                            self.board.get_moves(position))
                                else:
                                    # move piece
                                    is_mate = self.board.move_piece(self.player_focus, position)
                                    print(is_mate)
                                    # verify checkmate and switch state if true
                                    if is_mate:
                                        self.game_state = "over"
                                        self.winner = self.current_player_color

                                    print('move: ', (self.current_player_color, self.player_focus, position))
                                    # switch players
                                    if self.current_player_color == "W":
                                        self.current_player_color = "B"
                                        updated_player = self.board.black_pieces
                                        updated_opponent = self.board.white_pieces
                                    else:
                                        self.current_player_color = "W"
                                        updated_player = self.board.white_pieces
                                        updated_opponent = self.board.black_pieces

                                    self.player = updated_player
                                    self.opponent = updated_opponent

                                    # switch player state
                                    self.player_moves = []
                                    self.player_focus = None
                                    self.player_state = "selection"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.player_state = "selection"
                            self.current_player_color = "W"
                            self.player_moves = []
                            self.player_focus = None
                            self.winner = ''
                            self.window.fill(self.WHITE)

                            self.board = Board()
                            self.player = self.board.white_pieces
                            self.opponent = self.board.black_pieces

                            self.game_state = "start_menu"

                elif self.game_state == "over":
                    self.draw_game()
                    self.draw_winner()


            # Update the display
            pygame.display.update()

    def draw_start_menu(self):
        # Create the font object
        title_font = pygame.font.SysFont(None, 50)
        option_font = pygame.font.SysFont(None, 40)
        notif_font = pygame.font.SysFont(None, 20)

        # Create the text objects
        title_text = title_font.render("Choose an Option", True, self.BLACK)
        notif_text = notif_font.render("Press escape any time to return to this menu", True, self.BLACK)
        start_text = option_font.render("Start", True, self.BLACK)
        options_text = option_font.render("Options", True, self.BLACK)
        quit_text = option_font.render("Quit", True, self.BLACK)

        # Get the dimensions of the text objects
        title_text_rect = title_text.get_rect()
        notif_text_rect = notif_text.get_rect()
        start_text_rect = start_text.get_rect()
        options_text_rect = options_text.get_rect()
        quit_text_rect = quit_text.get_rect()

        # Set the positions of the text objects
        title_text_rect.center = (self.WINDOW_SIZE[0] // 2, 50)
        notif_text_rect.center = (self.WINDOW_SIZE[0] // 2, 55 + title_text.get_height())
        start_text_rect.center = (self.WINDOW_SIZE[0] // 2, 150)
        options_text_rect.center = (self.WINDOW_SIZE[0] // 2, 250)
        quit_text_rect.center = (self.WINDOW_SIZE[0] // 2, 350)

        self.window.fill(self.WHITE)

        # Draw the text objects
        self.window.blit(title_text, title_text_rect)
        self.window.blit(notif_text, notif_text_rect)
        self.window.blit(start_text, start_text_rect)
        self.window.blit(options_text, options_text_rect)
        self.window.blit(quit_text, quit_text_rect)

        return start_text_rect, options_text_rect, quit_text_rect

    def draw_options_menu(self):
        pass

    def draw_game(self):
        # Draw the chess board
        index = 0
        for row in range(7,-1,-1):
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
                piece = self.board.get_piece(index)
                if piece != constants.EMPTY:
                    image = self.piece_map[piece]
                    self.window.blit(image, (x, y))
                index += 1

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
        contrast = 0
        letter_pos = 8
        if self.player == self.board.black_pieces:
            current_player = 'B'
            current_color = self.BLACK
            contrast = 2
            letter_pos = 6

        player_indication_position = (self.SQUARE_SIZE/letter_pos,self.WINDOW_SIZE[0]-self.SQUARE_SIZE/2)
        pygame.draw.circle(self.window, self.WHITE, (self.SQUARE_SIZE/3.5,self.WINDOW_SIZE[0]-self.SQUARE_SIZE/4), self.SQUARE_SIZE/4)
        pygame.draw.circle(self.window, self.BLACK, (self.SQUARE_SIZE/3.5,self.WINDOW_SIZE[0]-self.SQUARE_SIZE/4), self.SQUARE_SIZE/4, contrast)
        player_label = index_font.render(current_player, True, current_color)
        self.window.blit(player_label, player_indication_position)

        if self.player_moves:
            for move in self.player_moves:
                row, col = utils.square_to_row_col(move)
                self.highlight_square(col, row)

    def draw_winner(self):
        winner_font = pygame.font.SysFont("Arial", 50, bold=True)
        winner = "black" if self.winner == 'B' else "white"
        text_color = (0,0,0) if winner == "black" else (255, 255, 255)

        winner_label = winner_font.render(winner + " won", True, text_color)
        text_width, text_height = winner_label.get_width(), winner_label.get_height()
        outline_surface = pygame.Surface((text_width + 2, text_height*1.5))
        outline_surface.fill(pygame.Color("white" if winner == "black" else "black"))

        escape_font = pygame.font.SysFont("Arial", 25, bold=True)
        escape_label = escape_font.render("Press escape", True, text_color)
        
        
        notif_position = (self.WINDOW_SIZE[0]//2-text_width//2,self.WINDOW_SIZE[0]//2-text_height)
        self.window.blit(outline_surface, notif_position)
        self.window.blit(winner_label, notif_position)
        self.window.blit(escape_label, (notif_position[0]+text_width//2-escape_label.get_width()//2, notif_position[1] + text_height))




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
        y = self.BOARD_SIZE - y - 1
        left = (x * self.SQUARE_SIZE) + self.SQUARE_SIZE/2
        top = (y * self.SQUARE_SIZE)
        highlight_surface = pygame.Surface(
            (self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)  # the size of your rect
        # this fills the entire surface
        highlight_surface.fill((173, 216, 230, 150))
        self.window.blit(highlight_surface, (left, top))

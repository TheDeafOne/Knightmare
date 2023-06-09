from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from .board import Board
from .board_utils import BoardUtils as utils, BoardConstants as constants
from algorithms.minimax import MiniMax


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
        self.current_player_color = constants.WHITE
        self.player_moves = []
        self.player_focus = None
        self.winner = ''

        self.focused_on_ply_textbox = False
        self.ply_text = "3"
        self.ply_input_range = range(1, 10)  # Only allow integers from 1 to 10
        self.ply_value = 3

        # Create the window
        pygame.init()
        self.window = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Knightmare")

        self.checkbox1_checked = False
        self.checkbox2_checked = True
        self.checkbox3_checked = False
        self.checkbox4_checked = True  # use evaluation functions

        self.minimax = MiniMax()

    def play(self):
        # Start the game loop
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.player_state = "selection"
                        self.current_player_color = constants.WHITE
                        self.player_moves = []
                        self.player_focus = None
                        self.winner = ''
                        self.window.fill(self.WHITE)

                        self.board = Board()
                        self.player = self.board.white_pieces
                        self.opponent = self.board.black_pieces

                        self.game_state = "start_menu"

                if self.game_state == "start_menu":
                    start_button, options_button, instructions_button, quit_button = self.draw_start_menu()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()
                        if start_button.collidepoint(mouse_position):
                            self.game_state = "game"
                            self.window.fill(self.WHITE)  # clear window
                        if quit_button.collidepoint(mouse_position):
                            pygame.quit()
                            quit()
                        if options_button.collidepoint(mouse_position):
                            self.game_state = "options_menu"
                            self.window.fill(self.WHITE)
                        if instructions_button.collidepoint(mouse_position):
                            self.window.fill(self.WHITE)
                            self.game_state = "instructions"

                elif self.game_state == "options_menu":
                    check1_rect, check2_rect, check3_rect, check4_rect, textbox = self.draw_options_menu()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()

                        if check1_rect.collidepoint(mouse_position):
                            self.checkbox1_checked = True
                            self.checkbox2_checked = False
                            self.checkbox3_checked = False
                        if check2_rect.collidepoint(mouse_position):
                            self.checkbox1_checked = False
                            self.checkbox2_checked = True
                            self.checkbox3_checked = False
                        if check3_rect.collidepoint(mouse_position):
                            self.checkbox1_checked = False
                            self.checkbox2_checked = False
                            self.checkbox3_checked = True
                        if check4_rect.collidepoint(mouse_position):
                            self.checkbox4_checked = not self.checkbox4_checked
                            self.minimax.use_eval_functions = self.checkbox4_checked
                        elif textbox.collidepoint(mouse_position):
                            self.focused_on_ply_textbox = True

                    if event.type == pygame.KEYDOWN and self.focused_on_ply_textbox:
                        if event.key == pygame.K_BACKSPACE:
                            self.ply_text = self.ply_text[:-1]

                        elif event.unicode.isdigit() and len(self.ply_text) < 1:
                            value = int(event.unicode)
                            if 0 < value < 10:
                                self.ply_text += event.unicode
                                self.ply_value = value
                elif self.game_state == "instructions":
                    self.draw_instructions()

                elif self.game_state == "game":
                    # https://github.com/pygame/pygame/issues/2011
                    if not pygame.display.get_active():
                        continue
                    self.draw_game()
                    move = []
                    if self.checkbox2_checked and self.current_player_color == constants.BLACK:
                        move = self.minimax.get_next_move(
                            self.board, constants.BLACK)
                    elif self.checkbox3_checked:
                        move = self.minimax.get_next_move(
                            self.board, self.current_player_color)
                    else:
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
                                        move = self.player_focus, position
                                        # verify checkmate and switch state if true
                    if move:

                        is_mate = self.board.move_piece(move[0], move[1])
                        print(self.board.get_piece(move[1]), move[0], move[1])
                        if is_mate:
                            self.game_state = "over"
                            self.winner = self.current_player_color
                        # switch players
                        if self.current_player_color == constants.WHITE:
                            self.current_player_color = constants.BLACK
                            updated_player = self.board.black_pieces
                            updated_opponent = self.board.white_pieces
                        else:
                            self.current_player_color = constants.WHITE
                            updated_player = self.board.white_pieces
                            updated_opponent = self.board.black_pieces

                        self.player = updated_player
                        self.opponent = updated_opponent

                        # switch player state
                        self.player_moves = []
                        self.player_focus = None
                        self.player_state = "selection"
                    # https://stackoverflow.com/questions/18839039/how-to-wait-some-time-in-pygame
                    # pygame.display.update()
                    # pygame.event.pump()
                    # pygame.time.delay(1000)
                    self.draw_game()

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
        notif_text = notif_font.render(
            "Press escape any time to return to this menu", True, self.BLACK)
        start_text = option_font.render("Start", True, self.BLACK)
        options_text = option_font.render("Options", True, self.BLACK)
        instructions_text = option_font.render(
            "Instructions", True, self.BLACK)
        quit_text = option_font.render("Quit", True, self.BLACK)

        # Get the dimensions of the text objects
        title_text_rect = title_text.get_rect()
        notif_text_rect = notif_text.get_rect()
        start_text_rect = start_text.get_rect()
        options_text_rect = options_text.get_rect()
        instructions_text_rect = instructions_text.get_rect()
        quit_text_rect = quit_text.get_rect()

        # Set the positions of the text objects
        title_text_rect.center = (self.WINDOW_SIZE[0] // 2, 50)
        notif_text_rect.center = (
            self.WINDOW_SIZE[0] // 2, 55 + title_text.get_height())
        start_text_rect.center = (self.WINDOW_SIZE[0] // 2, 150)
        options_text_rect.center = (self.WINDOW_SIZE[0] // 2, 225)
        instructions_text_rect.center = (self.WINDOW_SIZE[0] // 2, 300)
        quit_text_rect.center = (self.WINDOW_SIZE[0] // 2, 375)

        self.window.fill(self.WHITE)

        # Draw the text objects
        self.window.blit(title_text, title_text_rect)
        self.window.blit(notif_text, notif_text_rect)
        self.window.blit(start_text, start_text_rect)
        self.window.blit(options_text, options_text_rect)
        self.window.blit(instructions_text, instructions_text_rect)
        self.window.blit(quit_text, quit_text_rect)

        return start_text_rect, options_text_rect, instructions_text_rect, quit_text_rect

    def draw_instructions(self):
        title_font = pygame.font.SysFont(None, 40)
        notif_font = pygame.font.SysFont(None, 20)

        title_text = title_font.render("Instructions", True, self.BLACK)
        notif_text = notif_font.render(
            "Press escape any time to return to the main menu", True, self.BLACK)

        self.window.blit(
            title_text, (self.WINDOW_SIZE[0] // 2 - title_text.get_width()//2, 25))
        self.window.blit(
            notif_text, (self.WINDOW_SIZE[0] // 2 - notif_text.get_width()//2, 50))

        instructions_string = "Use options to toggle between the following game types: \n1) Human vs Human - this allows two humans to play against each other\n2) Human vs AI - this pits white (human) vs black (the AI)\n3) AI vs AI - this pits two AIs against each other (buggy)\n\n\nThis chess engine is in beta, so there are some known bugs:\n1) depending on the OS running the game, AI vs AI may be rendered very slowly\n2) minimizing the screen will freeze rendering despite game continuation\nsee: https://github.com/pygame/pygame/issues/2011\n3) when playing human vs AI, the game will momentarily freeze before the AI makes a move. This is the AI loading.\n4) AI vs AI will occasionally freeze while the game continues in the background. This is a pygames threading issue that we have not figured out how to resolve yet. Instead, use the console version of the game, which is automatically AI vs AI."
        instructions_rect = pygame.Rect((20, 100, 400, 350))
        rendered_text = render_textrect(
            instructions_string, notif_font, instructions_rect, self.BLACK, self.WHITE)
        if rendered_text:
            self.window.blit(rendered_text, instructions_rect.topleft)

    def draw_options_menu(self):
        title_font = pygame.font.SysFont(None, 25)
        notif_font = pygame.font.SysFont(None, 20)
        font = pygame.font.SysFont(None, 24)
        CHECKBOX_SIZE = 24
        checkbox1_rect = pygame.Rect(50, 100, CHECKBOX_SIZE, CHECKBOX_SIZE)
        checkbox2_rect = pygame.Rect(50, 150, CHECKBOX_SIZE, CHECKBOX_SIZE)
        checkbox3_rect = pygame.Rect(50, 200, CHECKBOX_SIZE, CHECKBOX_SIZE)
        checkbox4_rect = pygame.Rect(50, 300, CHECKBOX_SIZE, CHECKBOX_SIZE)
        pygame.draw.rect(self.window, (0, 0, 0), checkbox1_rect, 2)
        pygame.draw.rect(self.window, (0, 0, 0), checkbox2_rect, 2)
        pygame.draw.rect(self.window, (0, 0, 0), checkbox3_rect, 2)
        pygame.draw.rect(self.window, (0, 0, 0), checkbox4_rect, 2)
        if self.checkbox1_checked:
            pygame.draw.line(self.window, (0, 0, 0), (checkbox1_rect.x + 2, checkbox1_rect.centery),
                             (checkbox1_rect.centerx, checkbox1_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (0, 0, 0), (checkbox1_rect.centerx,
                             checkbox1_rect.bottom - 2), (checkbox1_rect.right - 2, checkbox1_rect.top + 2), 2)

            pygame.draw.line(self.window, (255, 255, 255), (checkbox2_rect.x + 2,
                             checkbox2_rect.centery), (checkbox2_rect.centerx, checkbox2_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox2_rect.centerx,
                             checkbox2_rect.bottom - 2), (checkbox2_rect.right - 2, checkbox2_rect.top + 2), 2)

            pygame.draw.line(self.window, (255, 255, 255), (checkbox3_rect.x + 2,
                             checkbox3_rect.centery), (checkbox3_rect.centerx, checkbox3_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox3_rect.centerx,
                             checkbox3_rect.bottom - 2), (checkbox3_rect.right - 2, checkbox3_rect.top + 2), 2)

        elif self.checkbox2_checked:
            pygame.draw.line(self.window, (0, 0, 0), (checkbox2_rect.x + 2, checkbox2_rect.centery),
                             (checkbox2_rect.centerx, checkbox2_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (0, 0, 0), (checkbox2_rect.centerx,
                             checkbox2_rect.bottom - 2), (checkbox2_rect.right - 2, checkbox2_rect.top + 2), 2)

            pygame.draw.line(self.window, (255, 255, 255), (checkbox1_rect.x + 2,
                             checkbox1_rect.centery), (checkbox1_rect.centerx, checkbox1_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox1_rect.centerx,
                             checkbox1_rect.bottom - 2), (checkbox1_rect.right - 2, checkbox1_rect.top + 2), 2)

            pygame.draw.line(self.window, (255, 255, 255), (checkbox3_rect.x + 2,
                             checkbox3_rect.centery), (checkbox3_rect.centerx, checkbox3_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox3_rect.centerx,
                             checkbox3_rect.bottom - 2), (checkbox3_rect.right - 2, checkbox3_rect.top + 2), 2)
        elif self.checkbox3_checked:
            pygame.draw.line(self.window, (0, 0, 0), (checkbox3_rect.centerx,
                             checkbox3_rect.bottom - 2), (checkbox3_rect.right - 2, checkbox3_rect.top + 2), 2)
            pygame.draw.line(self.window, (0, 0, 0), (checkbox3_rect.x + 2, checkbox3_rect.centery),
                             (checkbox3_rect.centerx, checkbox3_rect.bottom - 2), 2)

            pygame.draw.line(self.window, (255, 255, 255), (checkbox2_rect.x + 2,
                             checkbox2_rect.centery), (checkbox2_rect.centerx, checkbox2_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox2_rect.centerx,
                             checkbox2_rect.bottom - 2), (checkbox2_rect.right - 2, checkbox2_rect.top + 2), 2)

            pygame.draw.line(self.window, (255, 255, 255), (checkbox1_rect.x + 2,
                             checkbox1_rect.centery), (checkbox1_rect.centerx, checkbox1_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox1_rect.centerx,
                             checkbox1_rect.bottom - 2), (checkbox1_rect.right - 2, checkbox1_rect.top + 2), 2)

        if self.checkbox4_checked:
            pygame.draw.line(self.window, (0, 0, 0), (checkbox4_rect.x + 2, checkbox4_rect.centery),
                             (checkbox4_rect.centerx, checkbox4_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (0, 0, 0), (checkbox4_rect.centerx,
                             checkbox4_rect.bottom - 2), (checkbox4_rect.right - 2, checkbox4_rect.top + 2), 2)
        else:
            pygame.draw.line(self.window, (255, 255, 255), (checkbox4_rect.x + 2,
                             checkbox4_rect.centery), (checkbox4_rect.centerx, checkbox4_rect.bottom - 2), 2)
            pygame.draw.line(self.window, (255, 255, 255), (checkbox4_rect.centerx,
                             checkbox4_rect.bottom - 2), (checkbox4_rect.right - 2, checkbox4_rect.top + 2), 2)
        checkbox_title = title_font.render(
            "check the type of game you want to play", True, (0, 0, 0))
        notif_text = notif_font.render(
            "Press escape any time to return to the main menu", True, self.BLACK)
        label1 = font.render("Human vs Human", True, (0, 0, 0))
        label2 = font.render("AI vs Human", True, (0, 0, 0))
        label3 = font.render("AI vs AI", True, (0, 0, 0))
        self.window.blit(checkbox_title, (50, 50))
        self.window.blit(notif_text, (50, 55 + checkbox_title.get_height()))
        self.window.blit(label1, (checkbox1_rect.right + 10,
                         checkbox1_rect.centery - label1.get_height() // 2))
        self.window.blit(label2, (checkbox2_rect.right + 10,
                         checkbox2_rect.centery - label2.get_height() // 2))
        self.window.blit(label3, (checkbox3_rect.right + 10,
                         checkbox3_rect.centery - label2.get_height() // 2))

        textbox = pygame.Rect(50, 250, 50, 26)
        pygame.draw.rect(self.window, (225, 225, 225), textbox)
        pygame.draw.rect(self.window, (0, 0, 0), textbox, 2)

        text_surface = font.render(self.ply_text, True, (0, 0, 0))
        ply_label = font.render("Number of Ply", True, (0, 0, 0))
        evaluate_label = font.render(
            "Use Evaluation Heuristics", True, (0, 0, 0))

        self.window.blit(text_surface, (textbox.x + 5, textbox.y + 5))
        self.window.blit(ply_label, (textbox.right + 10,
                         textbox.centery - ply_label.get_height()//2))
        self.window.blit(evaluate_label, (checkbox4_rect.right + 10,
                         checkbox4_rect.centery - evaluate_label.get_height()//2))

        return checkbox1_rect, checkbox2_rect, checkbox3_rect, checkbox4_rect, textbox

    def draw_game(self):
        # Draw the chess board
        index = 0
        for row in range(7, -1, -1):
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

        current_player = constants.WHITE
        current_color = self.WHITE
        current_player_char = "W"
        contrast = 0
        letter_pos = 8
        if self.player == self.board.black_pieces:
            current_player = constants.BLACK
            current_color = self.BLACK
            current_player_char = "B"
            contrast = 2
            letter_pos = 6

        player_indication_position = (
            self.SQUARE_SIZE/letter_pos, self.WINDOW_SIZE[0]-self.SQUARE_SIZE/2)
        pygame.draw.circle(self.window, self.WHITE, (self.SQUARE_SIZE/3.5,
                           self.WINDOW_SIZE[0]-self.SQUARE_SIZE/4), self.SQUARE_SIZE/4)
        pygame.draw.circle(self.window, self.BLACK, (self.SQUARE_SIZE/3.5,
                           self.WINDOW_SIZE[0]-self.SQUARE_SIZE/4), self.SQUARE_SIZE/4, contrast)
        player_label = index_font.render(
            current_player_char, True, current_color)
        self.window.blit(player_label, player_indication_position)

        if self.player_moves:
            for move in self.player_moves:
                row, col = utils.square_to_row_col(move)
                self.highlight_square(col, row)

    def draw_winner(self):
        winner_font = pygame.font.SysFont("Arial", 50, bold=True)
        winner = "black" if self.winner == constants.BLACK else "white"
        text_color = (0, 0, 0) if winner == "black" else (255, 255, 255)

        winner_label = winner_font.render(winner + " won", True, text_color)
        text_width, text_height = winner_label.get_width(), winner_label.get_height()
        outline_surface = pygame.Surface((text_width + 2, text_height*1.5))
        outline_surface.fill(pygame.Color(
            "white" if winner == "black" else "black"))

        escape_font = pygame.font.SysFont("Arial", 25, bold=True)
        escape_label = escape_font.render("Press escape", True, text_color)

        notif_position = (
            self.WINDOW_SIZE[0]//2-text_width//2, self.WINDOW_SIZE[0]//2-text_height)
        self.window.blit(outline_surface, notif_position)
        self.window.blit(winner_label, notif_position)
        self.window.blit(
            escape_label, (notif_position[0]+text_width//2-escape_label.get_width()//2, notif_position[1] + text_height))

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


# taken from https://www.pygame.org/pcr/text_rect/index.php
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """


def render_textrect(string, font, rect, text_color, background_color, justification=0):
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException(
                        "The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException(
                "Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(
                    tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width -
                             tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException(
                    "Invalid justification argument: " + str(justification))
        accumulated_height += font.size(line)[1]

    return surface


class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message

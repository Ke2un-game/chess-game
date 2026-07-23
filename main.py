import pygame
import chess
import random

# Pygame स्टार्ट करें
pygame.init()

# --- 1. वर्टिकल / पोर्ट्रेट स्क्रीन सेटिंग्स ---
info = pygame.display.Info()
SCREEN_WIDTH = min(info.current_w, info.current_h)
SCREEN_HEIGHT = max(info.current_w, info.current_h)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Career")

# --- 2. लेआउट और साइज़ ---
MAX_BOARD_SIZE = SCREEN_WIDTH - 20
SQ_SIZE = MAX_BOARD_SIZE // 8
BOARD_SIZE = SQ_SIZE * 8

BOARD_X = (SCREEN_WIDTH - BOARD_SIZE) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_SIZE) // 2 - 30

# --- 3. कलर थीम्स ---
COLOR_LIGHT = (238, 238, 210)
COLOR_DARK = (118, 150, 86)
COLOR_SELECTED = (246, 246, 105)
COLOR_LAST_MOVE = (205, 210, 106)
COLOR_CHECK = (235, 75, 75)
COLOR_BG = (20, 23, 26)
COLOR_CARD = (35, 40, 48)
COLOR_LOCKED = (25, 28, 33)
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_DIM = (120, 125, 135)
COLOR_ACCENT = (76, 175, 80)
COLOR_GOLD = (255, 215, 0)
COLOR_OVERLAY = (0, 0, 0, 190)

PIECE_NAMES = {'P': 'P', 'N': 'N', 'B': 'B', 'R': 'R', 'Q': 'Q', 'K': 'K'}

BTN_HEIGHT = int(SCREEN_HEIGHT * 0.085)
font_title = pygame.font.SysFont("arial", int(SCREEN_WIDTH * 0.065), bold=True)
font_piece = pygame.font.SysFont("arial", int(SQ_SIZE * 0.45), bold=True)
font_ui = pygame.font.SysFont("arial", int(SCREEN_WIDTH * 0.045), bold=True)

font_btn_main = pygame.font.SysFont("arial", int(BTN_HEIGHT * 0.30), bold=True)
font_btn_sub = pygame.font.SysFont("arial", int(BTN_HEIGHT * 0.20), bold=True)
font_game_btn = pygame.font.SysFont("arial", int(SCREEN_WIDTH * 0.038), bold=True)

STATE_MENU = 0
STATE_GAME = 1

unlocked_stage = 1

# --- 4. AI ENGINE ---
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

PST_PAWN = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0
]

PST_KNIGHT = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

def evaluate_board(board):
    if board.is_checkmate():
        return 99999 if board.turn == chess.WHITE else -99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = PIECE_VALUES[piece.piece_type]
            pst = 0
            sq_idx = sq if piece.color == chess.WHITE else chess.square_mirror(sq)

            if piece.piece_type == chess.PAWN:
                pst = PST_PAWN[sq_idx]
            elif piece.piece_type == chess.KNIGHT:
                pst = PST_KNIGHT[sq_idx]

            total = val + pst
            if piece.color == chess.BLACK:
                score += total
            else:
                score -= total
    return score

def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    legal_moves = list(board.legal_moves)
    
    def move_score(m):
        if board.is_capture(m):
            cap = board.piece_at(m.to_square)
            return PIECE_VALUES.get(cap.piece_type, 0) if cap else 100
        return 0
    
    legal_moves.sort(key=move_score, reverse=True)
    best_move = legal_moves[0] if legal_moves else None

    if is_maximizing:
        max_eval = -999999
        for move in legal_moves:
            board.push(move)
            eval_val, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = 999999
        for move in legal_moves:
            board.push(move)
            eval_val, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = move
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move

def get_bot_move(board, stage):
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    for m in legal_moves:
        board.push(m)
        if board.is_checkmate():
            board.pop()
            return m
        board.pop()

    depth = 1 if stage <= 2 else 2
    _, best = minimax(board, depth, -999999, 999999, True)
    return best if best else random.choice(legal_moves)

# --- 5. DRAWING FUNCTIONS ---
def draw_home_screen(screen):
    screen.fill(COLOR_BG)
    
    title_surf = font_title.render("ROAD TO GRANDMASTER", True, COLOR_GOLD)
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.10)))

    stages_info = [
        ("Candidate Master", 1, (100, 180, 100)),
        ("FIDE Master", 2, (220, 180, 50)),
        ("International Master", 3, (220, 120, 50)),
        ("Grandmaster", 4, (235, 75, 75))
    ]

    btn_w = SCREEN_WIDTH * 0.86
    btn_h = BTN_HEIGHT
    start_y = SCREEN_HEIGHT * 0.18
    gap = btn_h + 16

    stage_rects = []

    for name, lvl, color in stages_info:
        y_pos = start_y + (gap * (lvl - 1))
        rect = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, y_pos, btn_w, btn_h)
        stage_rects.append((rect, lvl))

        is_unlocked = lvl <= unlocked_stage
        card_color = COLOR_CARD if is_unlocked else COLOR_LOCKED
        border_color = color if is_unlocked else (45, 50, 58)
        text_color = COLOR_TEXT if is_unlocked else COLOR_TEXT_DIM

        pygame.draw.rect(screen, card_color, rect, border_radius=14)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=14)

        if lvl < unlocked_stage:
            status_str = "[ BEATEN ]"
            status_color = (100, 220, 100)
        elif lvl == unlocked_stage:
            status_str = "[ UNLOCKED ]"
            status_color = COLOR_ACCENT
        else:
            status_str = "[ LOCKED ]"
            status_color = (130, 135, 145)

        sub_surf = font_btn_sub.render(status_str, True, status_color)
        screen.blit(sub_surf, sub_surf.get_rect(center=(rect.centerx, rect.top + int(btn_h * 0.28))))

        main_surf = font_btn_main.render(name, True, text_color)
        screen.blit(main_surf, main_surf.get_rect(center=(rect.centerx, rect.top + int(btn_h * 0.68))))

    btn_2p_y = start_y + (gap * 4) + 6
    btn_2p = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, btn_2p_y, btn_w, btn_h)
    pygame.draw.rect(screen, COLOR_CARD, btn_2p, border_radius=14)
    pygame.draw.rect(screen, COLOR_ACCENT, btn_2p, width=2, border_radius=14)

    sub_2p = font_btn_sub.render("[ PASS & PLAY ]", True, COLOR_ACCENT)
    screen.blit(sub_2p, sub_2p.get_rect(center=(btn_2p.centerx, btn_2p.top + int(btn_h * 0.28))))

    main_2p = font_btn_main.render("2 Player Mode", True, COLOR_TEXT)
    screen.blit(main_2p, main_2p.get_rect(center=(btn_2p.centerx, btn_2p.top + int(btn_h * 0.68))))

    return stage_rects, btn_2p

def draw_piece_badge(screen, piece, center_x, center_y):
    radius = SQ_SIZE // 2 - 6
    if piece.color == chess.WHITE:
        bg_color, border_color, text_color = (255, 255, 255), (40, 40, 40), (20, 20, 20)
    else:
        bg_color, border_color, text_color = (45, 45, 45), (220, 220, 220), (255, 255, 255)

    pygame.draw.circle(screen, border_color, (center_x, center_y), radius)
    pygame.draw.circle(screen, bg_color, (center_x, center_y), radius - 3)

    symbol = PIECE_NAMES.get(piece.symbol().upper(), piece.symbol().upper())
    text_surf = font_piece.render(symbol, True, text_color)
    screen.blit(text_surf, text_surf.get_rect(center=(center_x, center_y)))

def draw_game_screen(board, selected_square, valid_moves, current_stage, vs_bot, bot_thinking=False):
    screen.fill(COLOR_BG)

    titles_map = {1: "Candidate Master", 2: "FIDE Master", 3: "International Master", 4: "Grandmaster"}
    mode_text = titles_map.get(current_stage, "Vs Bot") if vs_bot else "2 Player Mode"

    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        status_text = f"CHECKMATE! {winner} Wins!"
    elif board.is_check():
        status_text = "CHECK!"
    elif bot_thinking:
        status_text = f"[{mode_text}] Bot is Thinking..."
    else:
        turn_name = "White" if board.turn == chess.WHITE else "Black"
        status_text = f"[{mode_text}] {turn_name}'s Turn"

    text_surf = font_ui.render(status_text, True, COLOR_GOLD if bot_thinking else (COLOR_CHECK if board.is_check() else COLOR_TEXT))
    screen.blit(text_surf, text_surf.get_rect(center=(SCREEN_WIDTH // 2, BOARD_Y // 2)))

    last_move = board.peek() if board.move_stack else None
    king_sq = board.king(board.turn) if board.is_check() else None

    # Chess Board
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            x = BOARD_X + (col * SQ_SIZE)
            y = BOARD_Y + (row * SQ_SIZE)

            if square == selected_square:
                color = COLOR_SELECTED
            elif square == king_sq:
                color = COLOR_CHECK
            elif last_move and (square == last_move.from_square or square == last_move.to_square):
                color = COLOR_LAST_MOVE
            else:
                color = COLOR_LIGHT if (row + col) % 2 == 0 else COLOR_DARK

            pygame.draw.rect(screen, color, (x, y, SQ_SIZE, SQ_SIZE))

            if square in valid_moves:
                pygame.draw.circle(screen, (50, 205, 50), (x + SQ_SIZE // 2, y + SQ_SIZE // 2), SQ_SIZE // 7)

            piece = board.piece_at(square)
            if piece:
                draw_piece_badge(screen, piece, x + SQ_SIZE // 2, y + SQ_SIZE // 2)

    # Clean Buttons Layout: Home | Undo | Restart
    btn_y = BOARD_Y + BOARD_SIZE + 35
    gap = 8
    btn_w = (BOARD_SIZE - (gap * 2)) // 3
    btn_h = 50

    btn_home_rect = pygame.Rect(BOARD_X, btn_y, btn_w, btn_h)
    pygame.draw.rect(screen, COLOR_CARD, btn_home_rect, border_radius=12)
    pygame.draw.rect(screen, (60, 70, 85), btn_home_rect, width=2, border_radius=12)
    screen.blit(font_game_btn.render("Home", True, COLOR_TEXT), font_game_btn.render("Home", True, COLOR_TEXT).get_rect(center=btn_home_rect.center))

    btn_undo_rect = pygame.Rect(BOARD_X + btn_w + gap, btn_y, btn_w, btn_h)
    pygame.draw.rect(screen, COLOR_CARD, btn_undo_rect, border_radius=12)
    pygame.draw.rect(screen, (220, 180, 50), btn_undo_rect, width=2, border_radius=12)
    screen.blit(font_game_btn.render("Undo", True, COLOR_TEXT), font_game_btn.render("Undo", True, COLOR_TEXT).get_rect(center=btn_undo_rect.center))

    btn_restart_rect = pygame.Rect(BOARD_X + (btn_w + gap) * 2, btn_y, btn_w, btn_h)
    pygame.draw.rect(screen, COLOR_CARD, btn_restart_rect, border_radius=12)
    pygame.draw.rect(screen, COLOR_ACCENT, btn_restart_rect, width=2, border_radius=12)
    screen.blit(font_game_btn.render("Restart", True, COLOR_TEXT), font_game_btn.render("Restart", True, COLOR_TEXT).get_rect(center=btn_restart_rect.center))

    return btn_home_rect, btn_undo_rect, btn_restart_rect

def draw_game_over_popup(screen, board, vs_bot, current_stage):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(COLOR_OVERLAY)
    screen.blit(overlay, (0, 0))

    box_w, box_h = int(SCREEN_WIDTH * 0.88), 220
    box_x = (SCREEN_WIDTH - box_w) // 2
    box_y = (SCREEN_HEIGHT - box_h) // 2
    box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
    
    pygame.draw.rect(screen, COLOR_CARD, box_rect, border_radius=16)
    pygame.draw.rect(screen, COLOR_GOLD, box_rect, width=3, border_radius=16)

    player_won = False
    if board.is_checkmate():
        if vs_bot:
            if board.turn == chess.BLACK:
                player_won = True
                msg = "STAGE CLEARED!" if current_stage < 4 else "GRANDMASTER BEATEN!"
            else:
                msg = "YOU LOST!"
        else:
            msg = "WHITE WINS!" if board.turn == chess.BLACK else "BLACK WINS!"
    else:
        msg = "DRAW / STALEMATE!"

    res_surf = font_title.render(msg, True, COLOR_GOLD if player_won else COLOR_TEXT)
    screen.blit(res_surf, res_surf.get_rect(center=(SCREEN_WIDTH // 2, box_y + 55)))

    btn_w = (box_w - 50) // 2
    
    btn_left = pygame.Rect(box_x + 18, box_y + 135, btn_w, 50)
    pygame.draw.rect(screen, COLOR_ACCENT, btn_left, border_radius=10)
    left_label = "Next Title" if (player_won and current_stage < 4) else "Play Again"
    screen.blit(font_game_btn.render(left_label, True, (255, 255, 255)), font_game_btn.render(left_label, True, (255, 255, 255)).get_rect(center=btn_left.center))

    btn_right = pygame.Rect(box_x + 32 + btn_w, box_y + 135, btn_w, 50)
    pygame.draw.rect(screen, (70, 80, 95), btn_right, border_radius=10)
    screen.blit(font_game_btn.render("Menu", True, COLOR_TEXT), font_game_btn.render("Menu", True, COLOR_TEXT).get_rect(center=btn_right.center))

    return btn_left, btn_right, player_won

# --- 6. MAIN LOOP ---
def main():
    global unlocked_stage
    board = chess.Board()
    current_state = STATE_MENU
    selected_square = None
    valid_moves = []
    vs_bot = True
    current_stage = 1
    running = True

    while running:
        if current_state == STATE_MENU:
            stage_rects, btn_2p = draw_home_screen(screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, lvl in stage_rects:
                        if rect.collidepoint(event.pos) and lvl <= unlocked_stage:
                            vs_bot = True
                            current_stage = lvl
                            board.reset()
                            current_state = STATE_GAME
                            break

                    if btn_2p.collidepoint(event.pos):
                        vs_bot = False
                        board.reset()
                        current_state = STATE_GAME

        elif current_state == STATE_GAME:
            btn_home_rect, btn_undo_rect, btn_restart_rect = draw_game_screen(board, selected_square, valid_moves, current_stage, vs_bot)

            if board.is_game_over():
                btn_left, btn_right, player_won = draw_game_over_popup(screen, board, vs_bot, current_stage)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if btn_left.collidepoint(event.pos):
                            if player_won and vs_bot:
                                if current_stage == unlocked_stage and unlocked_stage < 4:
                                    unlocked_stage += 1
                                if current_stage < 4:
                                    current_stage += 1
                            board.reset()
                            selected_square = None
                            valid_moves = []
                        elif btn_right.collidepoint(event.pos):
                            if player_won and vs_bot and current_stage == unlocked_stage and unlocked_stage < 4:
                                unlocked_stage += 1
                            current_state = STATE_MENU
                continue

            pygame.display.flip()

            # Bot Turn logic with visual delay & thinking indicator
            if vs_bot and board.turn == chess.BLACK:
                draw_game_screen(board, selected_square, valid_moves, current_stage, vs_bot, bot_thinking=True)
                pygame.display.flip()
                pygame.time.wait(400)

                bot_move = get_bot_move(board, current_stage)
                if bot_move:
                    board.push(bot_move)
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if btn_home_rect.collidepoint(event.pos):
                        current_state = STATE_MENU
                        continue

                    if btn_undo_rect.collidepoint(event.pos):
                        if vs_bot:
                            if len(board.move_stack) >= 2:
                                board.pop()
                                board.pop()
                            elif len(board.move_stack) == 1:
                                board.pop()
                        else:
                            if len(board.move_stack) >= 1:
                                board.pop()
                        selected_square = None
                        valid_moves = []
                        continue

                    if btn_restart_rect.collidepoint(event.pos):
                        board.reset()
                        selected_square = None
                        valid_moves = []
                        continue

                    if BOARD_X <= mx < BOARD_X + BOARD_SIZE and BOARD_Y <= my < BOARD_Y + BOARD_SIZE:
                        col = (mx - BOARD_X) // SQ_SIZE
                        row = (my - BOARD_Y) // SQ_SIZE
                        clicked_square = chess.square(col, 7 - row)

                        if selected_square is None:
                            piece = board.piece_at(clicked_square)
                            if piece and piece.color == board.turn:
                                selected_square = clicked_square
                                valid_moves = [m.to_square for m in board.legal_moves if m.from_square == selected_square]
                        else:
                            move = chess.Move(selected_square, clicked_square)
                            promo_move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)

                            if move in board.legal_moves:
                                board.push(move)
                            elif promo_move in board.legal_moves:
                                board.push(promo_move)

                            selected_square = None
                            valid_moves = []

    pygame.quit()

if __name__ == "__main__":
    main()


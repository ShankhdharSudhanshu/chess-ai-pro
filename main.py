import pygame
import chess
import chess.engine

pygame.init()

WIDTH, HEIGHT = 520, 520
SQ_SIZE = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI Pro")

# Colors (Modern UI)
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (106, 246, 105)
MOVE_DOT = (0, 0, 0)

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(r"C:\stockfish\stockfish-windows-x86-64-avx2.exe")

# Load images
pieces = {}
def load_images():
    names = ["wp","wr","wn","wb","wq","wk",
             "bp","br","bn","bb","bq","bk"]
    for n in names:
        img = pygame.image.load(f"assets/{n}.png")
        pieces[n] = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))

load_images()

def get_piece(piece):
    if piece is None:
        return None
    color = 'w' if piece.color else 'b'
    return pieces[color + piece.symbol().lower()]

def draw_board(selected=None):
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r+c)%2==0 else DARK
            pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    # Highlight selected square
    if selected is not None:
        col = chess.square_file(selected)
        row = 7 - chess.square_rank(selected)
        pygame.draw.rect(screen, HIGHLIGHT,
                         (col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE), 5)

def draw_pieces(dragging_piece=None, mouse_pos=None):
    for r in range(8):
        for c in range(8):
            sq = chess.square(c, 7-r)
            piece = board.piece_at(sq)

            if piece:
                img = get_piece(piece)

                if dragging_piece and sq == dragging_piece[0]:
                    continue  # skip original square while dragging

                screen.blit(img, (c*SQ_SIZE, r*SQ_SIZE))

    # Draw dragged piece on cursor
    if dragging_piece:
        img = dragging_piece[1]
        x, y = mouse_pos
        screen.blit(img, (x - SQ_SIZE//2, y - SQ_SIZE//2))

def highlight_moves(square):
    for move in board.legal_moves:
        if move.from_square == square:
            col = chess.square_file(move.to_square)
            row = 7 - chess.square_rank(move.to_square)
            pygame.draw.circle(screen, MOVE_DOT,
                               (col*SQ_SIZE + SQ_SIZE//2,
                                row*SQ_SIZE + SQ_SIZE//2), 8)

def get_square(pos):
    x, y = pos
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    return chess.square(col, 7-row)

dragging = None
selected_square = None
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    draw_board(selected_square)

    if selected_square:
        highlight_moves(selected_square)

    draw_pieces(dragging, mouse_pos)
    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            engine.quit()

        # START DRAG
        elif event.type == pygame.MOUSEBUTTONDOWN:
            sq = get_square(mouse_pos)
            piece = board.piece_at(sq)

            if piece and piece.color == board.turn:
                selected_square = sq
                dragging = (sq, get_piece(piece))

        # DROP PIECE
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
             from_sq = dragging[0]
             to_sq = get_square(mouse_pos)

            move = chess.Move(from_sq, to_sq)

            if move in board.legal_moves:
               board.push(move)

               # Check after player move
               if board.is_checkmate():
                  print("Checkmate! You win")
            
               elif board.is_stalemate():
                print("Draw!")

               else:
                # AI Move
                result = engine.play(board, chess.engine.Limit(time=0.4))
                board.push(result.move)

                # Check after AI move
                if board.is_checkmate():
                    print("Checkmate! AI wins")

                elif board.is_stalemate():
                    print("Draw!")

                dragging = None
                selected_square = None

        # undo move with right click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right click
                if len(board.move_stack) >= 2:
                   board.pop()
                   board.pop()        

pygame.quit()
import pygame as p
from ChessEngine import ChessEngine, Move, Piece


class ChessWnd:
    # Constant
    BORDER = 30
    WIDTH = HEIGHT = 512

    CELL_SIZE = WIDTH // ChessEngine.DIMENSION # 64
    GRAY = (196, 196, 196)
    WHITE = (238, 238, 210)
    GREEN = (118, 150, 86)

# Constructor
    def __init__(self):
        p.init()
        p.display.set_caption("Chess")
        self.screen = p.display.set_mode((self.WIDTH + self.BORDER * 2,
                                          self.HEIGHT + self.BORDER * 2))
        self.clock = p.time.Clock()
        self.engine = ChessEngine()



        self.images = {}
        self.__load_images()


    def main(self):
        running = True
        while running:

            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                elif event.type == p.MOUSEBUTTONDOWN:
                    self.on_mouse_down()
                elif event.type == p.MOUSEMOTION:
                    self.on_mouse_move()
                elif event.type == p.MOUSEBUTTONUP:
                    self.on_mouse_up()

            self.__draw_chessboard()
            p.display.flip()

    def on_mouse_down(self):
        pos = p.mouse.get_pos()
        row = (pos[1] - self.BORDER) // self.CELL_SIZE
        col = (pos[0] - self.BORDER) // self.CELL_SIZE
        if row < 0 or row > ChessEngine.DIMENSION - 1 \
            or col < 0 or col > ChessEngine.DIMENSION - 1:
            return

        self.engine.on_mouse_down(row, col)


    def on_mouse_move(self):
        if not self.engine.cell_selected:
            return
        self.engine.mouse_pos = p.mouse.get_pos()

    def on_mouse_up(self):
        pos = p.mouse.get_pos()
        row = (pos[1] - self.BORDER) // self.CELL_SIZE
        col = (pos[0] - self.BORDER) // self.CELL_SIZE
        if row < 0 or row > ChessEngine.DIMENSION - 1 \
                or col < 0 or col > ChessEngine.DIMENSION - 1:
            return

        if not self.engine.cell_selected or self.engine.cell_selected == (row, col):
            self.engine.reset_move()
        else:
            # make the move now
            move = Move(self.engine.cell_selected, (row, col), self.engine.board)

            # if this move i a valid move
            for valid_move in self.engine.all_moves:
                if move == valid_move:
                    self.engine.move_made = True
                    self.engine.make_move(valid_move)

    def __load_images(self):
        for row in self.engine.board:
            for piece in row:

                if piece == 0 or piece.curr_piece in self.images.keys():
                    continue
                self.images[piece.curr_piece] = p.image.load(f'res/{piece.curr_piece}.png')


    def __draw_chessboard(self):
        self.screen.fill(self.GRAY)
        self.__draw_squares()
        self.__draw_pieces()
        self.__draw_words()

    def __draw_words(self):
        font = p.font.SysFont('Courier New', 18, True)
        for i in range(8):
            num = font.render(str(i+1), True, (0, 128, 0))
            let = font.render(chr(65+i), True, (0, 128, 0))
            self.screen.blit(num, (15, 64*(i+1) - 10))
            self.screen.blit(let, (64*(i+1) - 10, 550))

    def __draw_squares(self):
        arr_pos = []
        sel = self.engine.cell_selected
        if sel and self.engine.mouse_pos:
            piece = self.engine.board[sel[0]][sel[1]]
            for move in piece.moves:
                arr_pos.append((move.end_row, move.end_col))

        x = y = self.BORDER
        w = h = self.CELL_SIZE
        colors = [self.WHITE, self.GREEN]
        for row in range(8):
            for col in range(8):
                color = colors[(row +col) % 2]
                rect = p.Rect(x + w * col, y + h * row, w, h)
                p.draw.rect(self.screen, color, rect)

                if (row, col) in arr_pos:
                    center = (self.BORDER + col * self.CELL_SIZE + self.CELL_SIZE//2,
                              self.BORDER + row * self.CELL_SIZE + self.CELL_SIZE//2)
                    radius = 15
                    p.draw.circle(self.screen, self.GRAY, center, radius)

                # draw dot to indicate possible moves


    def __draw_pieces(self):
        for row in range(ChessEngine.DIMENSION):
            for col in range(ChessEngine.DIMENSION):
                piece = self.engine.board[row][col]
                if piece != self.engine.EMPTY:
                    if self.engine.cell_selected == (row, col) and self.engine.mouse_pos:
                        rect = p.Rect(self.engine.mouse_pos[0] - self.CELL_SIZE/2,
                                      self.engine.mouse_pos[1] - self.CELL_SIZE/2,
                                      self.CELL_SIZE, self.CELL_SIZE)
                    else:
                        rect = p.Rect(self.BORDER + self.CELL_SIZE*col,
                                      self.BORDER + self.CELL_SIZE*row,
                                      self.CELL_SIZE, self.CELL_SIZE)

                    self.screen.blit(self.images[piece.curr_piece], rect)



# Driver Code
if __name__ == '__main__':
    wnd = ChessWnd()
    wnd.main()
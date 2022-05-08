class ChessEngine:
    EMPTY = 0
    BLACK = 1 << 0  # 1
    WHITE = 1 << 1  # 2
    PAWN = 1 << 2
    KNIGHT = 1 << 4
    BISHOP = 1 << 5
    ROOK = 1 << 6
    QUEEN = 1 << 11
    KING = 1 << 12
    DIMENSION = 8

    def __init__(self):
        E = self.EMPTY
        w, b = self.WHITE, self.BLACK
        R, N, B = self.ROOK, self.KNIGHT, self.BISHOP
        Q, K, P = self.QUEEN, self.KING, self.PAWN
        self.board = [
            [b | R, b | N, b | B, b | Q, b | K, b | B, b | N, b | R],
            [b | P, b | P, b | P, b | P, b | P, b | P, b | P, b | P],
            [E, E, E, E, E, E, E, E],
            [E, E, E, E, E, E, E, E],
            [E, E, E, E, E, E, E, E],
            [E, E, E, E, E, E, E, E],
            [w | P, w | P, w | P, w | P, w | P, w | P, w | P, w | P],
            [w | R, w | N, w | B, w | Q, w | K, w | B, w | N, w | R]
        ]

        self.init_board()
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.move_log = []
        self.curr_player = self.WHITE
        self.cell_selected = None
        self.mouse_pos = None
        self.en_passant_loc = ()
        self.castling_rights = CastlingRights()
        self.castling_rights_log = [self.castling_rights]

        self.all_moves = self.get_all_valid_moves()
        self.move_made = False

    def init_board(self):
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                if self.board[row][col] != self.EMPTY:
                    self.board[row][col] = Piece((row, col), self.board[row][col])

    def get_all_valid_moves(self, test=False):
        moves = []
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                if self.board[row][col] != self.EMPTY:
                    self.get_valid_moves(self.board[row][col], moves, test)

        return moves

    # 0b 1 0 1 0
    #        1 0
    # ---------------
    # 0b     1 0
    def on_mouse_down(self, row, col):
        piece = self.board[row][col]
        if piece == self.EMPTY:
            return
        elif (piece.curr_piece & self.curr_player) != self.curr_player:
            return

        self.cell_selected = (row, col)

    def reset_move(self):
        self.cell_selected = None
        self.mouse_pos = None

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = self.EMPTY
        self.board[move.end_row][move.end_col] = move.piece_moved
        # update piece cell info
        if move.piece_moved != self.EMPTY:
            move.piece_moved.cell = (move.end_row, move.end_col)

        self.move_log.append(move)

        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = self.EMPTY

        # update en_passant_loc
        if move.piece_moved.chess_type == self.PAWN and \
                abs(move.end_row - move.start_row) == 2:
            self.en_passant_loc = ((move.start_row + move.end_row) // 2,
                                   move.start_col)
        else:
            self.en_passant_loc = ()

        # pawn to queen
        if move.piece_moved.chess_type == self.PAWN and \
                (move.end_row == 0 or move.end_row == 7):
            self.board[move.end_row][move.end_col] = Piece((move.end_row, move.end_col), self.board[move.end_row][
                move.end_col].chess_color | self.QUEEN)

        if (move.piece_moved == self.ROOK or move.piece_moved == self.KING) and \
                move.is_castling_move:
            if move.end_col - move.start_col == 2:  # ks
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # shift rook and king
                self.board[move.end_row][move.end_col + 1] == self.EMPTY  # remove rook
            else:  # qs
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = self.EMPTY

        self.update_castling_rights(move)

        self.__switch_player()
        self.reset_move()

        self.all_moves = self.get_all_valid_moves()

    def under_attack(self, r, c):
        self.curr_player = self.curr_player % 2 + 1  # switch current player to opposite color
        opposite_move = self.get_all_valid_moves(True)
        self.curr_player = self.curr_player % 2 + 1  # switch back
        for move in opposite_move:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def in_check(self):
        if self.curr_player == self.WHITE:
            return self.under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def update_castling_rights(self, move):
        # if king or rook been moved
        if move.piece_moved.chess_type == (self.KING | self.WHITE):
            self.castling_rights.wks, self.castling_rights.wqs = False, False
        if move.piece_moved.chess_type == (self.KING | self.BLACK):
            self.castling_rights.bks, self.castling_rights.bqs = False, False
        if move.piece_moved.chess_type == (self.ROOK | self.WHITE) and move.start_col == 7:
            self.castling_rights.wks = False
        if move.piece_moved.chess_type == (self.ROOK | self.WHITE) and move.start_col == 0:
            self.castling_rights.wqs = False
        if move.piece_moved.chess_type == (self.ROOK | self.BLACK) and move.start_col == 7:
            self.castling_rights.bks = False
        if move.piece_moved.chess_type == (self.ROOK | self.BLACK) and move.start_col == 0:
            self.castling_rights.bqs = False

        # if rook being captured...
        if move.piece_captured != self.EMPTY:
            if move.piece_captured.chess_type == self.ROOK and move.piece_moved.chess_type != self.EMPTY:
                if move.end_row == 7 and move.end_col == 7:
                    self.castling_rights.wks = False
                elif move.end_row == 7 and move.end_col == 0:
                    self.castling_rights.wqs = False
                elif move.end_row == 0 and move.end_col == 7:
                    self.castling_rights.bks = False
                elif move.end_row == 0 and move.end_col == 0:
                    self.castling_rights.bqs = False

    def __switch_player(self):
        self.curr_player = self.BLACK if self.curr_player == self.WHITE else self.WHITE

    def get_move(self, piece, r, c, val_list):

        if r >= self.DIMENSION or r < 0 or \
                c >= self.DIMENSION or c < 0:
            return False

        if self.board[r][c] == self.EMPTY or \
                self.board[r][c].curr_piece & self.curr_player != self.curr_player:
            val_list.append(Move(piece.cell, (r, c), self.board))
            return self.board[r][c] == self.EMPTY

        # update the val_list
        return False

    def get_valid_moves(self, piece, val_list, test=False):
        moves = []
        for cur_dir in piece.directions:
            if piece.multi_moves:
                for i in range(ChessEngine.DIMENSION):
                    r = piece.cell[0] + cur_dir[0] * (i + 1)
                    c = piece.cell[1] + cur_dir[1] * (i + 1)
                    if not self.get_move(piece, r, c, moves):
                        break
            else:
                r = piece.cell[0] + cur_dir[0]
                c = piece.cell[1] + cur_dir[1]
                self.get_move(piece, r, c, moves)
        if piece.chess_type == ChessEngine.PAWN:
            self.get_pawn_moves(piece, moves)
        if piece.chess_type == ChessEngine.KING and not test:
            self.get_castling_move(piece, moves)
        piece.moves = moves
        val_list.extend(moves)

    def valid_cell(self, row, col):
        if row < 0 or row >= self.DIMENSION or \
                col < 0 or col >= self.DIMENSION:
            return False
        return True

    def get_castling_move(self, piece, moves):
        if self.under_attack(piece.cell[0], piece.cell[1]):
            return  # can't castle
        if (piece.chess_color == self.WHITE and self.castling_rights.wks) or (
                piece.chess_color == self.BLACK and self.castling_rights.bks):
            self.get_ks_castling_moves(piece, moves)
        if (piece.chess_color == self.WHITE and self.castling_rights.wqs) or (
                piece.chess_color == self.BLACK and self.castling_rights.bqs):
            self.get_qs_castling_moves(piece, moves)

    def get_ks_castling_moves(self, piece, moves):
        r = piece.cell[0]
        c = piece.cell[1]

        if self.board[r][c + 1] == self.board[r][c] == self.EMPTY:
            if not self.under_attack(r, c + 1) and not self.under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castling_move=True))

    def get_qs_castling_moves(self, piece, moves):
        r = piece.cell[0]
        c = piece.cell[1]

        if self.board[r][c - 1] == self.board[r][c - 2] == self.board[r][c - 3] == self.EMPTY:
            if not self.under_attack(r, c - 1) and not self.under_attack(r, c - 2) and not self.under_attack(r, c - 3):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castling_move=True))

    def get_pawn_moves(self, piece, moves):
        r = piece.cell[0]
        c = piece.cell[1]
        if piece.curr_piece == self.WHITE | self.PAWN and r == 6:
            moves.append(Move(piece.cell, (r - 2, c), self.board))
        elif piece.curr_piece == self.BLACK | self.PAWN and r == 1:
            moves.append(Move(piece.cell, (r + 2, c), self.board))

        # check for diagonal direction to attack enemy
        if piece.curr_piece == self.WHITE | self.PAWN:
            arr_pos = [(-1, -1), (-1, 1)]
        elif piece.curr_piece == self.BLACK | self.PAWN:
            arr_pos = [(1, -1), (1, 1)]
        if not arr_pos:
            return

        for pos in arr_pos:
            row = r + pos[0]
            col = c + pos[1]
            if self.valid_cell(row, col):

                piece2 = self.board[row][col]
                if piece2 != self.EMPTY and piece2.chess_color != piece.chess_color:
                    moves.append(Move(piece.cell, (row, col), self.board))

                if piece2 == self.EMPTY and (row, col) == self.en_passant_loc and \
                        self.curr_player == piece.chess_color:
                    moves.append(Move(piece.cell, (self.en_passant_loc), self.board, True))

                # check en passant

    def update_king_loc(self, piece):
        if piece.chess_type == self.KING:
            if piece.chess_color == self.WHITE:
                self.white_king_loc[0] = piece.cell[0]
                self.white_king_loc[1] = piece.cell[1]
            else:
                self.black_king_loc[0] = piece.cell[0]
                self.black_king_loc[1] = piece.cell[1]


class Move():
    def __init__(self, start_cell, end_cell, board,
                 is_en_passant=False, is_castling_move=False):
        self.start_row = start_cell[0]
        self.start_col = start_cell[1]
        self.end_row = end_cell[0]
        self.end_col = end_cell[1]
        self.board = board
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = f'{start_cell}_{end_cell}'
        self.is_en_passant = is_en_passant
        self.is_castling_move = False
        if is_en_passant:
            self.piece_captured = board[self.start_row][self.end_col]

        self.dict_trans = {}

    def get_chess_notation(self):
        ...

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False


class Piece():
    directions = {
        ChessEngine.PAWN: None,
        ChessEngine.ROOK: [(-1, 0), (1, 0), (0, -1), (0, 1)],
        ChessEngine.KNIGHT: [(-2, -1), (-2, 1), (2, -1), (2, 1), (1, -2), (-1, -2), (1, 2), (-1, 2)],
        ChessEngine.BISHOP: [(1, 1), (1, -1), (-1, -1), (-1, 1)],
        ChessEngine.QUEEN: [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1)],
        ChessEngine.KING: [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1)],
        ChessEngine.PAWN | ChessEngine.WHITE: [(-1, 0)],
        ChessEngine.PAWN | ChessEngine.BLACK: [(1, 0)]
    }

    multi_moves = {
        ChessEngine.PAWN: False,
        ChessEngine.ROOK: True,
        ChessEngine.KNIGHT: False,
        ChessEngine.BISHOP: True,
        ChessEngine.QUEEN: True,
        ChessEngine.KING: False
    }

    def __init__(self, cell, curr_piece):
        # self.board = board
        self.cell = cell
        self.curr_piece = curr_piece
        self.chess_color = curr_piece % (1 << 2)
        self.chess_type = (curr_piece >> 2) << 2
        self.multi_moves = Piece.multi_moves[self.chess_type]
        self.directions = Piece.directions[self.chess_type]
        self.moves = []

        if not self.directions:
            self.directions = Piece.directions[curr_piece]


class CastlingRights:
    def __init__(self, wks=True, wqs=True, bks=True, bqs=True):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

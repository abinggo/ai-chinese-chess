import numpy as np

PIECE_TYPE_MAP = {
    'K': '将', 'A': '士', 'B': '象', 'N': '马',
    'R': '车', 'C': '炮', 'P': '兵',
    'k': '帅', 'a': '仕', 'b': '相', 'n': '马',
    'r': '车', 'c': '炮', 'p': '卒'
}

class ChineseChess:
    COLORS = {'R': '红', 'B': '黑'}
    
    def __init__(self):
        self.board = self._initialize_board()
        self.current_turn = 'R'
        self.game_over = False
        self.winner = None

    def _initialize_board(self):
        board = np.full((10, 9), '   ', dtype=object)
        # 红方
        row0 = ['RR', 'RN', 'RB', 'RA', 'RK', 'RA', 'RB', 'RN', 'RR']
        for i, p in enumerate(row0): board[0][i] = p
        board[2][1] = 'RC'; board[2][7] = 'RC'
        for i in range(0, 9, 2): board[3][i] = 'RP'
        # 黑方
        row9 = ['Br', 'Bn', 'Bb', 'Ba', 'Bk', 'Ba', 'Bb', 'Bn', 'Br']
        for i, p in enumerate(row9): board[9][i] = p
        board[7][1] = 'Bc'; board[7][7] = 'Bc'
        for i in range(0, 9, 2): board[6][i] = 'Bp'
        return board

    # --- 新增：获取当前玩家所有合法走法 (喂给AI用) ---
    def get_all_legal_moves(self):
        all_moves = []
        for r in range(10):
            for c in range(9):
                piece = self.board[r][c].strip()
                if piece and piece[0] == self.current_turn:
                    # 获取该棋子的合法落点
                    moves = self.get_legal_moves((r, c))
                    for target in moves:
                        # 格式化为：((r1,c1), (r2,c2))
                        all_moves.append(((r, c), target))
        return all_moves

    def get_legal_moves(self, from_pos):
        x, y = from_pos
        piece = self.board[x][y].strip()
        if not piece: return []
        
        color = piece[0]
        # 严格校验轮次
        if color != self.current_turn: return []

        p_type = piece[1].upper()
        moves = []
        
        if p_type == 'R': moves = self._get_rook_moves(x, y, color)
        elif p_type == 'N': moves = self._get_knight_moves(x, y, color)
        elif p_type == 'B': moves = self._get_elephant_moves(x, y, color)
        elif p_type == 'A': moves = self._get_advisor_moves(x, y, color)
        elif p_type == 'K': moves = self._get_king_moves(x, y, color)
        elif p_type == 'C': moves = self._get_cannon_moves(x, y, color)
        elif p_type == 'P': moves = self._get_pawn_moves(x, y, color)
            
        return moves

    # --- 修复后的车走法 (解决吃子问题) ---
    def _get_rook_moves(self, x, y, color):
        moves = []
        # 上下左右
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny].strip()
                if target == '':
                    # 空位，可以走
                    moves.append((nx, ny))
                else:
                    # 有棋子
                    if target[0] != color:
                        # 是敌方，可以吃，加入列表
                        moves.append((nx, ny))
                    # 无论敌我，遇到棋子就必须停下（不能跳过）
                    break 
                nx += dx
                ny += dy
        return moves

    def _get_cannon_moves(self, x, y, color):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            screen_found = False 
            while 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny].strip()
                if not screen_found:
                    if target == '':
                        moves.append((nx, ny))
                    else:
                        screen_found = True
                else:
                    if target != '':
                        if target[0] != color:
                            moves.append((nx, ny))
                        break
                nx += dx
                ny += dy
        return moves

    def _get_knight_moves(self, x, y, color):
        moves = []
        knight_jumps = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for dx, dy in knight_jumps:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 9:
                leg_x, leg_y = x + (0 if abs(dx)==1 else dx//2), y + (0 if abs(dy)==1 else dy//2)
                if self.board[leg_x][leg_y].strip() == '':
                    target = self.board[nx][ny].strip()
                    if target == '' or target[0] != color: moves.append((nx, ny))
        return moves

    def _get_elephant_moves(self, x, y, color):
        moves = []
        elephant_jumps = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        for dx, dy in elephant_jumps:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 9:
                if self.board[x+dx//2][y+dy//2].strip() != '': continue
                if color == 'R' and nx > 4: continue
                if color == 'B' and nx < 5: continue
                target = self.board[nx][ny].strip()
                if target == '' or target[0] != color: moves.append((nx, ny))
        return moves

    def _get_advisor_moves(self, x, y, color):
        moves = []
        x_range = (0, 2) if color == 'R' else (7, 9)
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if x_range[0] <= nx <= x_range[1] and 3 <= ny <= 5:
                target = self.board[nx][ny].strip()
                if target == '' or target[0] != color: moves.append((nx, ny))
        return moves

    def _get_king_moves(self, x, y, color):
        moves = []
        x_range = (0, 2) if color == 'R' else (7, 9)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, -1)]: # 这里修正了一个小笔误，应该是横竖
             pass # King moves logic below is better
        
        # 将帅只能横竖走
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if x_range[0] <= nx <= x_range[1] and 3 <= ny <= 5:
                target = self.board[nx][ny].strip()
                if target == '' or target[0] != color: moves.append((nx, ny))
        return moves

    def _get_pawn_moves(self, x, y, color):
        moves = []
        forward = 1 if color == 'R' else -1
        crossed = (x > 4) if color == 'R' else (x < 5)
        if 0 <= x + forward < 10:
            target = self.board[x + forward][y].strip()
            if target == '' or target[0] != color: moves.append((x + forward, y))
        if crossed:
            for dy in [-1, 1]:
                if 0 <= y + dy < 9:
                    target = self.board[x][y + dy].strip()
                    if target == '' or target[0] != color: moves.append((x, y + dy))
        return moves

    def make_move(self, from_pos, to_pos):
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        # 调试：打印详细信息，帮你找Bug
        print(f"\n⚡ [Action] 尝试移动: ({x1},{y1}) -> ({x2},{y2})")
        piece = self.board[x1][y1].strip()
        target = self.board[x2][y2].strip()
        print(f"   棋子: {piece} (Color: {piece[0] if piece else 'None'})")
        print(f"   目标: {target} (Color: {target[0] if target else 'None'})")
        print(f"   当前轮次: {self.current_turn}")
        
        legal_moves = self.get_legal_moves(from_pos)
        if (x2, y2) not in legal_moves:
            print(f"❌ 移动非法！合法列表: {legal_moves}")
            return False, "违反规则", False
        
        is_capture = (target != '')
        self.board[x2][y2] = piece
        self.board[x1][y1] = '   '
        
        if 'K' in target or 'k' in target:
            self.game_over = True
            self.winner = self.current_turn
        
        self.current_turn = 'B' if self.current_turn == 'R' else 'R'
        return True, "ok", is_capture
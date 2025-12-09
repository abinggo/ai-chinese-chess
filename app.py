from flask import Flask, render_template, request, jsonify
from chinese_chess import ChineseChess
import requests
import random
import json

app = Flask(__name__)

# --- AI 配置 (保持不变) ---
AI_CONFIG = {
    "Deepseek": {
        "model": "deepseek-chat",
        "api_key": os.environ.get("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com/v1"
    },
    "Qwen": {
        "model": "qwen3-max",
        "api_key": os.environ.get("QWEN_API_KEY"),
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    "Kimi": {
        "model": "kimi-k2-0905-preview",
        "api_key": os.environ.get("KIMI_API_KEY"),
        "base_url": "https://api.moonshot.cn/v1"
    }
}

game = ChineseChess()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_game():
    global game
    game = ChineseChess()
    return jsonify({"status": "success", "board": game.board.tolist()})

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    x1, y1 = data['from']
    x2, y2 = data['to']
    success, msg, is_capture = game.make_move((x1, y1), (x2, y2))
    return jsonify({
        "success": success, "message": msg, "capture": is_capture,
        "current_turn": game.current_turn, "game_over": game.game_over, "winner": game.winner
    })

# --- 核心升级：给AI生成合法走法列表 ---
def get_ai_prompt_data(game_instance):
    """
    生成：
    1. 棋盘视觉图
    2. 合法走法列表 (Menu)
    """
    board_str = "   0 1 2 3 4 5 6 7 8 (列)\n"
    board_str += "  -------------------\n"
    for r in range(10):
        row_str = f"{r}| "
        for c in range(9):
            p = game_instance.board[r][c].strip()
            row_str += (p if p else ". ") + " "
        board_str += row_str + "\n"
    
    # 获取所有合法移动
    all_legal_moves = game_instance.get_all_legal_moves()
    # 格式化为字符串列表: "1: (7,1)->(0,1) [吃]"
    move_options = []
    
    for start, end in all_legal_moves:
        p = game_instance.board[start[0]][start[1]].strip()
        t = game_instance.board[end[0]][end[1]].strip()
        action = f"吃{t}" if t else "移动"
        # 记录格式: 坐标串
        move_options.append(f"{start[0]},{start[1]},{end[0]},{end[1]}  ({p} {action})")
    
    return board_str, move_options

@app.route('/ai_move', methods=['POST'])
def ai_move():
    data = request.json
    model_name = data.get('model', 'Deepseek')
    config = AI_CONFIG.get(model_name)
    if not config: return jsonify({"error": "Model not found"})

    # 1. 获取数据
    board_visual, move_list = get_ai_prompt_data(game)
    
    if not move_list:
        return jsonify({"success": False, "message": "无棋可走，AI认输"})

    current_color_name = "红" if game.current_turn == 'R' else "黑"
    
    # 2. 构造 Prompt
    # 截取前80个走法
    moves_str = "\n".join(move_list[:80]) 
    
    system_prompt = f"""
    你是一个中国象棋高手。当前轮到：【{current_color_name}方】。
    
    这是当前的棋盘：
    {board_visual}
    
    【重要】为了保证符合规则，请直接从下方的【合法走法列表】中选择最佳的一步。
    不要自己创造坐标，必须在列表中选择。
    """
    
    user_prompt = f"""
    请从以下合法走法中选择最佳一步：
    
    {moves_str}
    
    请直接输出那一行开头的 4个数字坐标 (x1,y1,x2,y2)。不要解释。
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # ★★★【核心修改】直接在 Python 控制台打印 Prompt ★★★
    print("\n" + "="*20 + " 🛠️ 发送给 AI 的提示词 " + "="*20)
    print(json.dumps(messages, ensure_ascii=False, indent=2))
    print("="*60 + "\n")

    try:
        # 3. 请求 AI
        headers = {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}
        payload = {
            "model": config['model'], 
            "messages": messages, 
            "temperature": 0.1 
        }

        response = requests.post(f"{config['base_url']}/chat/completions", headers=headers, json=payload)
        res_json = response.json()
        
        if 'choices' not in res_json:
             print("API Error:", res_json)
             return jsonify({"success": False, "message": "API报错"})

        content = res_json['choices'][0]['message']['content']
        print(f"🤖 AI 回复内容: {content}") # 这里也打印一下 AI 的原始回复

        # 4. 解析
        coords = [int(n) for n in content.replace(',', ' ').split() if n.isdigit()]
        if len(coords) >= 4:
            x1, y1, x2, y2 = coords[:4]
            success, msg, is_capture = game.make_move((x1, y1), (x2, y2))
            if success:
                return jsonify({"success": True, "move": [x1, y1, x2, y2], "capture": is_capture, "message": msg})
            else:
                print("AI 选择非法，随机兜底")
                
        # 兜底：随机走
        import random
        chosen_move_str = random.choice(move_list)
        parts = [int(n) for n in chosen_move_str.split('(')[0].split(',')]
        x1, y1, x2, y2 = parts
        success, msg, is_capture = game.make_move((x1, y1), (x2, y2))
        return jsonify({"success": True, "move": [x1, y1, x2, y2], "capture": is_capture, "message": f"AI随机: {msg}"})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
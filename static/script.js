let gameState = {
    mode: '', 
    turn: 'R', 
    selected: null, // {row, col, el}
    board: [], 
    gameOver: false,
    redAI: 'Deepseek',
    blackAI: 'Qwen'
};

const PIECE_MAP = {
    'R': { text: '车', class: 'red' }, 'N': { text: '马', class: 'red' },
    'B': { text: '相', class: 'red' }, 'A': { text: '仕', class: 'red' },
    'K': { text: '帅', class: 'red' }, 'C': { text: '炮', class: 'red' },
    'P': { text: '兵', class: 'red' },
    'r': { text: '车', class: 'black' }, 'n': { text: '马', class: 'black' },
    'b': { text: '象', class: 'black' }, 'a': { text: '士', class: 'black' },
    'k': { text: '将', class: 'black' }, 'c': { text: '炮', class: 'black' },
    'p': { text: '卒', class: 'black' }
};

// 1. 开始游戏
function startGame(mode) {
    gameState.mode = mode;
    gameState.redAI = document.getElementById('red-ai').value;
    gameState.blackAI = document.getElementById('black-ai').value;
    
    document.getElementById('start-screen').style.display = 'none';
    document.getElementById('game-container').classList.remove('hidden');

    fetch('/reset', {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            renderBoard(data.board);
            addLog("游戏开始！");
            checkAI();
        });
}

// 2. 渲染棋盘
function renderBoard(boardData) {
    const boardEl = document.getElementById('board');
    // 清空现有元素，但保留网格线和河界
    document.querySelectorAll('.piece, .empty-cell').forEach(el => el.remove());

    gameState.board = boardData;

    // 遍历90个格子
    for(let r=0; r<10; r++) {
        for(let c=0; c<9; c++) {
            const code = boardData[r][c].trim();
            
            if (code) {
                // --- 有棋子 ---
                const colorCode = code[0]; 
                const typeCode = code[1];
                const key = (colorCode === 'R') ? typeCode.toUpperCase() : typeCode.toLowerCase();
                const info = PIECE_MAP[key];

                if(info) {
                    createPiece(r, c, info.text, info.class, code);
                }
            } else {
                // --- 没有棋子，创建透明点击层 ---
                createEmptyCell(r, c);
            }
        }
    }
}

// 【修复版】创建棋子
function createPiece(row, col, text, colorClass, rawCode) {
    const el = document.createElement('div');
    el.className = `piece ${colorClass}`;
    el.innerText = text;
    // 存储坐标到 dataset
    el.dataset.row = row;
    el.dataset.col = col;
    el.dataset.code = rawCode;
    
    // 计算位置
    el.style.left = (col * 50 + 3) + 'px';
    el.style.top = (row * 50 + 3) + 'px';

    // 绑定点击事件
    el.onclick = (e) => {
        e.stopPropagation(); 
        
        // ★★★ 核心修复：读取实时的 dataset 坐标，而不是使用闭包里的 row/col ★★★
        // 这样即使棋子被移动了，点击时获取的也是最新坐标
        const currentR = parseInt(el.dataset.row);
        const currentC = parseInt(el.dataset.col);
        const currentCode = el.dataset.code;
        
        handleClick(currentR, currentC, currentCode, el);
    };
    
    document.getElementById('board').appendChild(el);
}

// 【修复版】创建空白格
function createEmptyCell(row, col) {
    const el = document.createElement('div');
    el.className = 'empty-cell';
    el.dataset.row = row;
    el.dataset.col = col;
    
    // 位置与棋子一致
    el.style.left = (col * 50 + 3) + 'px';
    el.style.top = (row * 50 + 3) + 'px';

    // 绑定点击事件
    el.onclick = (e) => {
        e.stopPropagation();
        
        // ★★★ 核心修复：同样读取实时的 dataset 坐标 ★★★
        const currentR = parseInt(el.dataset.row);
        const currentC = parseInt(el.dataset.col);
        
        handleClick(currentR, currentC, null, null);
    };

    document.getElementById('board').appendChild(el);
}

// 3. 统一点击处理逻辑
function handleClick(row, col, code, el) {
    if(gameState.gameOver) return;
    
    // 检查是否是AI回合（不允许人类乱点）
    if(gameState.mode === 'a_vs_a') return;
    if(gameState.mode === 'h_vs_a' && gameState.turn === 'B') return;

    // 逻辑分流
    if (!gameState.selected) {
        // --- 还没选中棋子 ---
        // 只能选中己方棋子
        if (code && code[0] === gameState.turn) {
            selectPiece(row, col, el);
        }
    } else {
        // --- 已经选中了棋子 ---
        // 情况A: 点击了同一个棋子 -> 取消选中
        if (row === gameState.selected.row && col === gameState.selected.col) {
            cancelSelection();
            return;
        }

        // 情况B: 点击了己方另一个棋子 -> 换选
        if (code && code[0] === gameState.turn) {
            selectPiece(row, col, el);
            return;
        }

        // 情况C: 点击了空白处 或 敌方棋子 -> 尝试移动
        tryMove(gameState.selected.row, gameState.selected.col, row, col);
    }
}

function selectPiece(row, col, el) {
    cancelSelection();
    el.classList.add('selected');
    gameState.selected = {row, col, el};
    document.getElementById('board').classList.add('selecting');
}

function cancelSelection() {
    document.querySelectorAll('.piece.selected').forEach(p => p.classList.remove('selected'));
    gameState.selected = null;
    document.getElementById('board').classList.remove('selecting');
}

// 4. 移动逻辑
function tryMove(r1, c1, r2, c2) {
    fetch('/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ from: [r1, c1], to: [r2, c2] })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            // 移动成功：执行动画
            animateMove(r1, c1, r2, c2, data.game_over, data.winner, data.capture);
            
            // 更新本地数据
            gameState.turn = data.current_turn;
            document.getElementById('turn-indicator').innerText = 
                (gameState.turn === 'R' ? "🔴 红方回合" : "⚫ 黑方回合");
            
            // 取消选中状态
            cancelSelection();
            
            // 如果没结束，让AI走
            if(!data.game_over) {
                setTimeout(checkAI, 500); 
            }
        } else {
            // 移动失败
            const p = document.querySelector(`.piece[data-row='${r1}'][data-col='${c1}']`);
            if(p) {
                p.style.transform = 'translateX(5px)';
                setTimeout(()=>p.style.transform = 'translateX(0)', 100);
            }
            addLog("🚫 " + data.message);
        }
    });
}

// 【修复版】动画函数
function animateMove(r1, c1, r2, c2, isGameOver, winner, isCapture) {
    const pieces = document.querySelectorAll('.piece');
    let targetPiece = null; // 要移动的棋子
    let eatenPiece = null;  // 被吃的棋子

    pieces.forEach(p => {
        const pr = parseInt(p.dataset.row);
        const pc = parseInt(p.dataset.col);
        if(pr === r1 && pc === c1) targetPiece = p;
        if(pr === r2 && pc === c2) eatenPiece = p;
    });

    if(targetPiece) {
        if(isCapture) showEatEffect(r2, c2);

        if(eatenPiece) {
            eatenPiece.style.zIndex = -1;
            setTimeout(() => eatenPiece.remove(), 300);
        }

        // 移动 DOM
        targetPiece.style.left = (c2 * 50 + 3) + 'px';
        targetPiece.style.top = (r2 * 50 + 3) + 'px';
        
        // ★★★ 核心修复：必须更新 dataset，否则下次点击还是旧坐标 ★★★
        targetPiece.dataset.row = r2;
        targetPiece.dataset.col = c2;
        
        // 维护 DOM 的完整性：
        // 1. 棋子从 (r1,c1) 走了，那里变成了空地，需要补一个 empty-cell
        // 2. 棋子到了 (r2,c2)，那里如果之前是空地(有empty-cell)，需要移除
        setTimeout(() => {
             // 1. 在老位置加个空白格
             createEmptyCell(r1, c1);
             
             // 2. 在新位置移除空白格(如果有)
             const oldEmpty = document.querySelector(`.empty-cell[data-row='${r2}'][data-col='${c2}']`);
             if(oldEmpty) oldEmpty.remove();
             
             addLog(`${r1},${c1} ➡ ${r2},${c2}`);
        }, 300);
    }

    if(isGameOver) {
        gameState.gameOver = true;
        setTimeout(() => alert("🎉 游戏结束！" + (winner === 'R' ? "红方" : "黑方") + "获胜！"), 500);
    }
}

// 吃子特效
function showEatEffect(row, col) {
    const board = document.getElementById('board');
    const eff = document.createElement('div');
    eff.innerText = "吃!";
    eff.style.position = 'absolute';
    eff.style.left = (col * 50 + 5) + 'px';
    eff.style.top = (row * 50 + 5) + 'px';
    eff.style.color = '#e74c3c';
    eff.style.fontSize = '30px';
    eff.style.fontWeight = 'bold';
    eff.style.zIndex = 100;
    eff.style.pointerEvents = 'none';
    eff.style.transition = 'all 0.5s ease-out';
    board.appendChild(eff);

    setTimeout(() => {
        eff.style.transform = 'scale(2) translateY(-20px)';
        eff.style.opacity = '0';
    }, 50);
    setTimeout(() => eff.remove(), 600);
}

// AI 逻辑
function checkAI() {
    if(gameState.gameOver) return;
    let needAI = false;
    let currentModel = '';

    if(gameState.mode === 'a_vs_a') {
        needAI = true;
        currentModel = (gameState.turn === 'R') ? gameState.redAI : gameState.blackAI;
    } else if (gameState.mode === 'h_vs_a') {
        if(gameState.turn === 'B') {
            needAI = true;
            currentModel = gameState.blackAI;
        }
    }

    if(needAI) {
        document.getElementById('status-msg').innerText = `🤖 ${currentModel} 思考中...`;
        
        fetch('/ai_move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                model: currentModel,
                board_str: "backend_gen" 
            })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('status-msg').innerText = "等待...";
            if(data.success) {
                const m = data.move;
                animateMove(m[0], m[1], m[2], m[3], false, null, data.capture);
                
                gameState.turn = (gameState.turn === 'R' ? 'B' : 'R');
                document.getElementById('turn-indicator').innerText = 
                    (gameState.turn === 'R' ? "🔴 红方回合" : "⚫ 黑方回合");
                
                if(gameState.mode === 'a_vs_a') {
                     setTimeout(checkAI, 1000);
                }
            } else {
                addLog("AI 认输或出错: " + data.message);
            }
        });
    }
}

function addLog(msg) {
    const logEl = document.getElementById('logs');
    const p = document.createElement('div');
    p.innerText = msg;
    logEl.prepend(p);
}
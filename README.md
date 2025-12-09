# 中国象棋AI对战

一个基于Streamlit的中国象棋AI对战应用，支持人机对战和AI对战模式。

## 功能特性

- 🎮 **人机对战**：玩家可以选择红方或黑方，与AI进行对战
- 🤖 **AI对战**：两个不同的AI模型可以自动对战
- 🎨 **友好界面**：直观的棋盘布局，支持棋子选择和移动
- 🔄 **多种AI模型**：支持Deepseek、Qwen、Kimi等主流AI模型
- 📊 **实时状态**：显示当前回合、移动结果和游戏状态

## 安装步骤

1. **克隆仓库**（或直接下载文件）
   ```bash
   git clone <repository-url>
   cd ai_chinese_chess
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   streamlit run app.py
   ```

## 使用方法

1. **游戏设置**：
   - 在侧边栏选择游戏模式（人机对战或AI对战）
   - 人机对战：选择阵营（红方或黑方）和AI模型
   - AI对战：选择红方和黑方的AI模型

2. **配置AI API**：
   - 输入所选AI模型的API密钥
   - 不同AI模型需要不同的API密钥

3. **开始游戏**：
   - 点击"开始新游戏"按钮初始化棋盘
   - 人机对战：点击棋子选择，再次点击目标位置移动
   - AI对战：AI会自动进行对战

4. **游戏规则**：
   - 遵循标准中国象棋规则
   - 红方先走，黑方后走
   - 将死对方获胜

## AI模型支持

当前支持以下AI模型：

- **Deepseek**：需要Deepseek API密钥
- **Qwen**：需要Qwen API密钥
- **Kimi**：需要Kimi API密钥

## 项目结构

```
ai_chinese_chess/
├── app.py              # Streamlit应用主文件
├── chinese_chess.py    # 中国象棋核心逻辑
├── requirements.txt    # 项目依赖
└── README.md           # 项目说明文档
```

## 技术栈

- **Python**：主要开发语言
- **Streamlit**：Web应用框架
- **NumPy**：棋盘数据结构处理
- **Requests**：AI API调用

## 注意事项

1. AI对战需要有效的API密钥
2. API调用可能产生费用，请参考各AI平台的收费标准
3. 首次运行应用可能需要下载一些依赖
4. 如果遇到问题，可以尝试刷新页面或重新启动应用

## 开发说明

### 扩展AI模型

要添加新的AI模型，需要在`app.py`中的`AI_MODELS`字典中添加新的模型配置：

```python
AI_MODELS = {
    "新模型": {
        "base_url": "API端点",
        "api_key_env": "环境变量名"
    }
}
```

### 修改棋盘样式

可以在`display_board`函数中调整棋盘的颜色和布局。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

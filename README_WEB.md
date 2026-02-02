# GUI Agent - Web界面版本 🌐

**无需tkinter！基于Web的智能GUI自动化助手**

## ✨ 特点

- ✅ **无需tkinter** - 使用Flask + 浏览器，兼容性更好
- ✅ **现代化界面** - 漂亮的渐变色设计，响应式布局
- ✅ **实时通信** - WebSocket实时推送日志和状态
- ✅ **跨平台** - Windows/Mac/Linux都可以运行
- ✅ **易于打包** - 可以打包成单个exe文件
- ✅ **体积更小** - 相比tkinter版本更轻量

## 🚀 快速开始

### 方式1：直接运行（推荐用于开发）

1. **安装依赖**
```bash
pip install flask flask-socketio python-socketio
```

2. **运行应用**
```bash
python web_app.py
```

3. **自动打开浏览器**
   - 应用会自动在浏览器中打开 `http://127.0.0.1:5000`
   - 如果没有自动打开，手动访问该地址

### 方式2：打包为exe（推荐用于分发）

1. **安装PyInstaller**
```bash
pip install pyinstaller
```

2. **打包应用**
```bash
pyinstaller build_web_exe.spec
```

3. **运行exe**
```bash
dist\GUI-Agent-Web.exe
```

4. **访问界面**
   - 运行exe后会显示访问地址
   - 在浏览器中打开 `http://127.0.0.1:5000`

## 📖 使用说明

### 首次配置

1. 启动应用后，如果是首次运行，会显示配置界面
2. 填写以下信息：
   - **API Key** (必填): 你的火山引擎API密钥
   - **Base URL** (必填): API服务地址
   - **Model Name** (可选): 模型名称，有默认值
3. 点击"保存配置"

### 执行任务

1. 在任务输入框中输入自然语言描述
2. 或从历史记录下拉框选择之前的任务
3. 点击"▶ 开始执行"按钮
4. 实时查看执行日志和截图
5. 任务完成后会自动停止

### 界面说明

#### 任务输入区
- 支持多行文本输入
- 可以从历史记录快速选择
- 历史记录自动保存（最多50条）

#### 控制按钮
- **▶ 开始执行**: 启动任务
- **⏹ 停止**: 中断当前任务
- **🗑 清空日志**: 清除执行日志
- **⚙ 设置**: 修改API配置

#### 执行日志
- 实时显示任务执行过程
- 不同颜色表示不同级别：
  - 白色：普通信息
  - 绿色：成功消息
  - 橙色：警告消息
  - 红色：错误消息

#### 截图预览
- 显示Agent拍摄的实时截图
- 自动缩放以适应显示区域
- 显示当前步骤编号

#### 状态栏
- 显示当前任务状态
- 不同颜色表示不同状态：
  - 灰色：就绪
  - 蓝色：执行中
  - 绿色：已完成
  - 橙色：已停止
  - 红色：错误

## 📝 示例任务

```
打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看
```

```
打开记事本，输入"Hello World"，然后保存文件
```

```
打开计算器，计算 123 + 456
```

## 🔧 技术架构

### 后端
- **Flask**: Web框架
- **Flask-SocketIO**: WebSocket实时通信
- **Python-SocketIO**: Socket.IO客户端

### 前端
- **原生HTML/CSS/JavaScript**: 无需额外框架
- **Socket.IO客户端**: 实时通信
- **响应式设计**: 支持移动端

### 自动化
- **PyAutoGUI**: 鼠标键盘控制
- **MSS**: 屏幕截图
- **火山引擎API**: 多模态AI

## 📂 文件结构

```
GUI-Agent/
├── web_app.py              # Web应用入口 ✅
├── templates/              # HTML模板 ✅
│   └── index.html
├── main.py                 # GUIAgent核心
├── core/                   # 核心功能
│   ├── config_manager.py
│   └── agent_controller.py
├── gui_operator/           # GUI操作
│   └── execute.py
├── utils/                  # 工具类
│   ├── model.py
│   └── prompts.py
├── config.json             # 配置文件（运行时生成）
├── steps/                  # 截图目录（运行时生成）
├── requirements.txt        # Python依赖
└── build_web_exe.spec      # PyInstaller配置 ✅
```

## 🆚 对比：Web版 vs Tkinter版

| 特性 | Web版 | Tkinter版 |
|------|-------|-----------|
| 依赖 | Flask (易安装) | Tkinter (可能缺失) |
| 界面 | 现代化、美观 | 传统桌面风格 |
| 跨平台 | ✅ 完美支持 | ⚠️ 需要tk/tcl |
| 打包体积 | ~30-40MB | ~40-50MB |
| 实时更新 | WebSocket | 线程回调 |
| 移动端 | ✅ 支持 | ❌ 不支持 |
| 部署方式 | 本地服务器 | 桌面应用 |

## 🔒 安全说明

- Web服务仅监听本地地址 `127.0.0.1`
- 不对外网开放，仅本机访问
- API密钥存储在本地配置文件
- 建议不要在公共网络环境下使用

## 🐛 故障排除

### 问题：浏览器没有自动打开

**解决方案**：
手动在浏览器中访问 `http://127.0.0.1:5000`

### 问题：端口5000被占用

**解决方案**：
修改 `web_app.py` 中的端口号：
```python
socketio.run(app, host='127.0.0.1', port=5001, debug=False)
```

### 问题：API调用失败

**解决方案**：
1. 检查网络连接
2. 验证API Key和Base URL
3. 查看控制台日志了解详细错误

### 问题：截图不显示

**解决方案**：
1. 确保 `steps/` 目录存在
2. 检查浏览器控制台是否有错误
3. 刷新页面重试

## 📦 打包优化

### 减小exe体积

1. **使用虚拟环境**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pyinstaller build_web_exe.spec
```

2. **排除不必要的模块**
在 `build_web_exe.spec` 的 `excludes` 中添加：
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'pytest',
    'tkinter',
]
```

3. **启用UPX压缩**
已在spec文件中启用：
```python
upx=True
```

## 🎯 未来改进

- [ ] 添加任务队列功能
- [ ] 支持多任务并行执行
- [ ] 添加任务模板库
- [ ] 支持定时任务
- [ ] 添加用户认证
- [ ] 支持远程访问（可选）

## 📄 许可证

本项目仅供学习和研究使用。

## 💬 支持

如有问题或建议，请提交Issue。

---

**推荐使用Web版本！** 无需担心tkinter依赖问题，界面更现代，功能更强大！

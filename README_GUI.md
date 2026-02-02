# GUI Agent - 图形界面版本

智能GUI自动化助手 - 通过自然语言控制GUI操作

## 功能特点

- 🖥️ **友好的图形界面** - 无需编写代码，通过界面操作
- 🤖 **智能AI驱动** - 基于多模态AI理解屏幕内容并执行操作
- 📸 **实时截图预览** - 查看Agent看到的界面内容
- 📝 **执行日志** - 实时查看任务执行过程
- 💾 **历史记录** - 保存和重用之前的任务
- ⚙️ **配置管理** - 灵活配置API凭证和参数

## 安装要求

### Python环境

- Python 3.10 或更高版本
- 需要包含 tk/tcl 组件的Python安装

### 检查Tkinter是否可用

```bash
python -c "import tkinter; print('Tkinter is available')"
```

如果提示 `ModuleNotFoundError: No module named 'tkinter'`，需要重新安装Python并确保选择了tk/tcl组件。

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式1：直接运行Python脚本

```bash
python gui_app.py
```

### 方式2：打包为独立exe（推荐）

1. 安装PyInstaller：
```bash
pip install pyinstaller
```

2. 打包应用：
```bash
pyinstaller build_exe.spec
```

3. 运行生成的exe：
```bash
dist\GUI-Agent.exe
```

## 首次使用

1. **启动应用** - 双击运行 `gui_app.py` 或 `GUI-Agent.exe`

2. **配置API凭证** - 首次启动会显示配置向导
   - 输入API Key（必填）
   - 输入Base URL（必填）
   - 输入Model Name（可选，有默认值）

3. **开始使用** - 配置完成后即可使用

## 界面说明

### 任务输入区域
- 输入自然语言任务描述
- 支持多行文本
- 可以从历史记录中选择

### 控制按钮
- **▶ 开始执行** - 启动任务
- **⏹ 停止** - 中断当前任务
- **🗑 清空日志** - 清除执行日志
- **⚙ 设置** - 修改配置

### 执行日志
- 实时显示任务执行过程
- 不同颜色表示不同级别的消息
  - 黑色：普通信息
  - 绿色：成功消息
  - 橙色：警告消息
  - 红色：错误消息

### 截图预览
- 显示Agent拍摄的实时截图
- 显示当前步骤编号
- 自动缩放以适应显示区域

### 状态栏
- 显示当前任务状态
  - 就绪（灰色）
  - 执行中（蓝色）
  - 已完成（绿色）
  - 已停止（橙色）
  - 错误（红色）

## 示例任务

```
打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看
```

```
打开记事本，输入"Hello World"，然后保存文件
```

```
打开计算器，计算 123 + 456
```

## 配置文件

配置保存在 `config.json` 文件中：

```json
{
  "api_key": "your-api-key",
  "base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "model_name": "ep-20260120161243-g7vwl",
  "history": [
    "任务1",
    "任务2"
  ]
}
```

## 故障排除

### 问题：提示"No module named 'tkinter'"

**解决方案**：
1. 重新安装Python，确保选择"tcl/tk and IDLE"组件
2. 或者使用Anaconda/Miniconda，它们默认包含tkinter

### 问题：API调用失败

**解决方案**：
1. 检查网络连接
2. 验证API Key和Base URL是否正确
3. 确认API服务是否可用

### 问题：截图显示失败

**解决方案**：
1. 确保Pillow库已正确安装
2. 检查截图文件是否存在
3. 查看错误日志了解详细信息

### 问题：打包后exe文件过大

**解决方案**：
1. 使用UPX压缩（已在spec文件中启用）
2. 排除不必要的模块
3. 考虑使用虚拟环境减少依赖

## 技术架构

- **GUI框架**: Tkinter
- **图片处理**: Pillow (PIL)
- **AI模型**: 火山引擎多模态API
- **自动化**: PyAutoGUI, MSS
- **打包工具**: PyInstaller

## 文件结构

```
GUI-Agent/
├── gui_app.py              # 应用程序入口
├── main.py                 # 原有的GUIAgent实现
├── core/                   # 核心功能
│   ├── config_manager.py   # 配置管理
│   └── agent_controller.py # Agent控制器
├── ui/                     # UI组件
│   ├── main_window.py      # 主窗口
│   ├── config_wizard.py    # 配置向导
│   └── settings_dialog.py  # 设置对话框
├── gui_operator/           # GUI操作
│   └── execute.py
├── utils/                  # 工具类
│   ├── model.py
│   └── prompts.py
├── config.json             # 配置文件（运行时生成）
├── requirements.txt        # Python依赖
└── build_exe.spec          # PyInstaller配置
```

## 许可证

本项目仅供学习和研究使用。

## 支持

如有问题或建议，请提交Issue。

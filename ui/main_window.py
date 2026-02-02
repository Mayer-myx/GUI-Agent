# ui/main_window.py

import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os
from typing import Callable
from core.config_manager import AppConfig
from core.agent_controller import AgentController


class MainWindow:
    """主窗口 - GUI Agent的主界面"""
    
    def __init__(self, root: tk.Tk, config: AppConfig, config_manager):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口
            config: 应用配置
            config_manager: 配置管理器
        """
        self.root = root
        self.config = config
        self.config_manager = config_manager
        
        # Agent控制器
        self.agent_controller = AgentController(
            api_key=config.api_key,
            base_url=config.base_url,
            model_name=config.model_name,
            log_callback=self.update_log,
            screenshot_callback=self.update_screenshot,
            status_callback=self.update_status
        )
        
        # UI组件引用
        self.task_input = None
        self.start_button = None
        self.stop_button = None
        self.settings_button = None
        self.clear_button = None
        self.log_text = None
        self.screenshot_label = None
        self.screenshot_step_label = None
        self.status_label = None
        self.history_combobox = None
        
        # 当前截图信息
        self.current_screenshot_path = None
        self.current_step = 0
        
        # 设置窗口
        self.root.title("GUI Agent - 智能GUI自动化助手")
        self.root.geometry("1200x800")
        
        # 设置UI
        self.setup_ui()
        
        # 初始状态
        self.update_status("就绪", "gray")
        self.enable_controls(True)
    
    def setup_ui(self):
        """设置UI布局"""
        # 主容器
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部区域：任务输入和控制面板
        self._create_top_section(main_container)
        
        # 中间区域：日志和截图
        self._create_middle_section(main_container)
        
        # 底部区域：状态栏
        self._create_bottom_section(main_container)
    
    def _create_top_section(self, parent):
        """创建顶部区域"""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 任务输入区域
        input_frame = ttk.LabelFrame(top_frame, text="任务输入", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 多行文本输入
        self.task_input = tk.Text(
            input_frame,
            height=4,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        self.task_input.pack(fill=tk.X)
        
        # Placeholder文本
        placeholder = "请输入任务描述，例如：\n打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看"
        self.task_input.insert("1.0", placeholder)
        self.task_input.config(foreground="gray")
        
        # 绑定焦点事件处理placeholder
        self.task_input.bind("<FocusIn>", self._on_input_focus_in)
        self.task_input.bind("<FocusOut>", self._on_input_focus_out)
        self.task_input.bind("<KeyRelease>", self._on_input_changed)
        
        # 历史记录
        history_frame = ttk.Frame(input_frame)
        history_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(history_frame, text="历史记录:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.history_combobox = ttk.Combobox(
            history_frame,
            values=self.config.history,
            state="readonly",
            width=50
        )
        self.history_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.history_combobox.bind("<<ComboboxSelected>>", self._on_history_selected)
        
        # 控制面板
        control_frame = ttk.Frame(top_frame)
        control_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            control_frame,
            text="▶ 开始执行",
            command=self.on_start_clicked,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ 停止",
            command=self.on_stop_clicked,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(
            control_frame,
            text="🗑 清空日志",
            command=self.on_clear_log_clicked
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.settings_button = ttk.Button(
            control_frame,
            text="⚙ 设置",
            command=self.on_settings_clicked
        )
        self.settings_button.pack(side=tk.RIGHT)
    
    def _create_middle_section(self, parent):
        """创建中间区域"""
        middle_frame = ttk.Frame(parent)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左侧：执行日志
        log_frame = ttk.LabelFrame(middle_frame, text="执行日志", padding="5")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置日志颜色标签
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("error", foreground="red")
        
        # 右侧：截图显示
        screenshot_frame = ttk.LabelFrame(middle_frame, text="截图预览", padding="5")
        screenshot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 截图显示区域
        self.screenshot_label = ttk.Label(
            screenshot_frame,
            text="暂无截图\n\n任务开始后将显示实时截图",
            anchor=tk.CENTER,
            background="lightgray"
        )
        self.screenshot_label.pack(fill=tk.BOTH, expand=True)
        
        # 步骤编号
        self.screenshot_step_label = ttk.Label(
            screenshot_frame,
            text="",
            font=("Arial", 10, "bold")
        )
        self.screenshot_step_label.pack(pady=(5, 0))
    
    def _create_bottom_section(self, parent):
        """创建底部状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            font=("Arial", 10, "bold"),
            foreground="gray"
        )
        self.status_label.pack(side=tk.LEFT)
    
    def _on_input_focus_in(self, event):
        """输入框获得焦点"""
        if self.task_input.get("1.0", tk.END).strip() == "请输入任务描述，例如：\n打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看":
            self.task_input.delete("1.0", tk.END)
            self.task_input.config(foreground="black")
    
    def _on_input_focus_out(self, event):
        """输入框失去焦点"""
        if not self.task_input.get("1.0", tk.END).strip():
            placeholder = "请输入任务描述，例如：\n打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看"
            self.task_input.insert("1.0", placeholder)
            self.task_input.config(foreground="gray")
    
    def _on_input_changed(self, event):
        """输入内容改变"""
        content = self.task_input.get("1.0", tk.END).strip()
        placeholder = "请输入任务描述，例如：\n打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看"
        
        # 更新开始按钮状态
        if content and content != placeholder:
            self.start_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.DISABLED)
    
    def _on_history_selected(self, event):
        """选择历史记录"""
        selected = self.history_combobox.get()
        if selected:
            self.task_input.delete("1.0", tk.END)
            self.task_input.insert("1.0", selected)
            self.task_input.config(foreground="black")
            self.start_button.config(state=tk.NORMAL)
    
    def on_start_clicked(self):
        """开始按钮点击"""
        # 获取任务内容
        task = self.task_input.get("1.0", tk.END).strip()
        if not task:
            return
        
        # 禁用控件
        self.enable_controls(False)
        
        # 清空之前的截图
        self.screenshot_label.config(image="", text="等待截图...")
        self.screenshot_step_label.config(text="")
        
        # 启动任务
        self.agent_controller.start_task(task)
        
        # 添加到历史记录
        self.config_manager.add_to_history(task)
        self.history_combobox.config(values=self.config_manager.get_history())
    
    def on_stop_clicked(self):
        """停止按钮点击"""
        self.agent_controller.stop_task()
        self.enable_controls(True)
    
    def on_settings_clicked(self):
        """设置按钮点击"""
        from ui.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self.root, self.config)
        new_config = dialog.show()
        
        if new_config:
            # 保存新配置
            if self.config_manager.save_config(new_config):
                self.config = new_config
                # 更新Agent控制器配置
                self.agent_controller.api_key = new_config.api_key
                self.agent_controller.base_url = new_config.base_url
                self.agent_controller.model_name = new_config.model_name
                self.update_log("配置已更新", "success")
    
    def on_clear_log_clicked(self):
        """清空日志按钮点击"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_log(self, message: str, level: str = "info"):
        """
        更新日志
        
        Args:
            message: 日志消息
            level: 日志级别 (info/success/warning/error)
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", level)
        self.log_text.see(tk.END)  # 自动滚动到底部
        self.log_text.config(state=tk.DISABLED)
    
    def update_screenshot(self, image_path: str, step: int):
        """
        更新截图显示
        
        Args:
            image_path: 截图文件路径
            step: 步骤编号
        """
        if not os.path.exists(image_path):
            return
        
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 获取显示区域大小
            label_width = self.screenshot_label.winfo_width()
            label_height = self.screenshot_label.winfo_height()
            
            # 如果窗口还没有渲染，使用默认大小
            if label_width <= 1:
                label_width = 500
            if label_height <= 1:
                label_height = 600
            
            # 计算缩放比例（保持宽高比）
            img_width, img_height = image.size
            width_ratio = label_width / img_width
            height_ratio = label_height / img_height
            scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不放大
            
            # 缩放图片
            new_width = int(img_width * scale_ratio)
            new_height = int(img_height * scale_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter可用的格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新显示
            self.screenshot_label.config(image=photo, text="")
            self.screenshot_label.image = photo  # 保持引用
            
            # 更新步骤编号
            self.screenshot_step_label.config(text=f"步骤 {step}")
            
            # 保存当前截图信息
            self.current_screenshot_path = image_path
            self.current_step = step
            
        except Exception as e:
            self.update_log(f"截图显示失败: {str(e)}", "error")
    
    def update_status(self, status: str, color: str):
        """
        更新状态指示器
        
        Args:
            status: 状态文本
            color: 状态颜色
        """
        self.status_label.config(text=status, foreground=color)
        
        # 根据状态更新按钮
        if status == "执行中":
            self.enable_controls(False)
        elif status in ["已完成", "已停止", "错误"]:
            self.enable_controls(True)
    
    def enable_controls(self, enabled: bool):
        """
        启用/禁用控件
        
        Args:
            enabled: 是否启用
        """
        if enabled:
            # 检查输入是否为空
            content = self.task_input.get("1.0", tk.END).strip()
            placeholder = "请输入任务描述，例如：\n打开浏览器搜索GUI，找到Wikipedia的介绍页面进行查看"
            
            if content and content != placeholder:
                self.start_button.config(state=tk.NORMAL)
            else:
                self.start_button.config(state=tk.DISABLED)
            
            self.stop_button.config(state=tk.DISABLED)
            self.task_input.config(state=tk.NORMAL)
            self.settings_button.config(state=tk.NORMAL)
            self.history_combobox.config(state="readonly")
        else:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.task_input.config(state=tk.DISABLED)
            self.settings_button.config(state=tk.DISABLED)
            self.history_combobox.config(state=tk.DISABLED)

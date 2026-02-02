# ui/settings_dialog.py

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from core.config_manager import AppConfig


class SettingsDialog:
    """设置对话框 - 允许用户修改配置"""
    
    def __init__(self, parent: tk.Tk, current_config: AppConfig):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
            current_config: 当前配置
        """
        self.parent = parent
        self.current_config = current_config
        self.result: Optional[AppConfig] = None
        
        # 创建模态对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置 - GUI Agent")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        
        # 设置为模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建UI
        self._create_widgets()
    
    def _center_window(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """创建UI组件"""
        # 主容器
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="应用程序设置",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key
        ttk.Label(input_frame, text="API Key *", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.api_key_entry = ttk.Entry(input_frame, width=50, show="*")
        self.api_key_entry.insert(0, self.current_config.api_key)
        self.api_key_entry.grid(row=1, column=0, pady=(0, 15))
        
        # 显示/隐藏API Key按钮
        self.show_api_key_var = tk.BooleanVar(value=False)
        show_api_key_check = ttk.Checkbutton(
            input_frame,
            text="显示API Key",
            variable=self.show_api_key_var,
            command=self._toggle_api_key_visibility
        )
        show_api_key_check.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        # Base URL
        ttk.Label(input_frame, text="Base URL *", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.base_url_entry = ttk.Entry(input_frame, width=50)
        self.base_url_entry.insert(0, self.current_config.base_url)
        self.base_url_entry.grid(row=4, column=0, pady=(0, 15))
        
        # Model Name
        ttk.Label(input_frame, text="Model Name", font=("Arial", 10)).grid(
            row=5, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.model_name_entry = ttk.Entry(input_frame, width=50)
        self.model_name_entry.insert(0, self.current_config.model_name)
        self.model_name_entry.grid(row=6, column=0, pady=(0, 15))
        
        # 提示文本
        hint_label = ttk.Label(
            main_frame,
            text="* 必填项",
            font=("Arial", 9),
            foreground="gray"
        )
        hint_label.pack(pady=(10, 20))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self._validate_and_save
        )
        save_button.pack(side=tk.RIGHT)
    
    def _toggle_api_key_visibility(self):
        """切换API Key的显示/隐藏"""
        if self.show_api_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def _on_cancel(self):
        """取消按钮处理"""
        self.result = None
        self.dialog.destroy()
    
    def _validate_and_save(self) -> bool:
        """
        验证输入并保存配置
        
        Returns:
            是否验证通过
        """
        # 获取输入值
        api_key = self.api_key_entry.get().strip()
        base_url = self.base_url_entry.get().strip()
        model_name = self.model_name_entry.get().strip()
        
        # 创建新配置对象（保留历史记录）
        config = AppConfig(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name if model_name else "ep-20260120161243-g7vwl",
            history=self.current_config.history.copy()
        )
        
        # 验证配置
        is_valid, error_msg = config.validate()
        if not is_valid:
            messagebox.showerror("验证失败", error_msg)
            return False
        
        # 保存结果
        self.result = config
        self.dialog.destroy()
        return True
    
    def show(self) -> Optional[AppConfig]:
        """
        显示对话框并等待用户操作
        
        Returns:
            新的配置对象，如果用户取消则返回None
        """
        self.dialog.wait_window()
        return self.result

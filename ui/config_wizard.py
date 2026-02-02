# ui/config_wizard.py

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from core.config_manager import AppConfig


class ConfigWizard:
    """配置向导对话框 - 首次运行时引导用户配置"""
    
    def __init__(self, parent: tk.Tk):
        """
        初始化配置向导
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.result: Optional[AppConfig] = None
        
        # 创建模态对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("首次配置 - GUI Agent")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # 设置为模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 禁止关闭窗口（必须完成配置）
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
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
            text="欢迎使用 GUI Agent",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 说明文字
        desc_label = ttk.Label(
            main_frame,
            text="首次使用需要配置API凭证。请填写以下信息：",
            wraplength=450
        )
        desc_label.pack(pady=(0, 20))
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key
        ttk.Label(input_frame, text="API Key *", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.api_key_entry = ttk.Entry(input_frame, width=50)
        self.api_key_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Base URL
        ttk.Label(input_frame, text="Base URL *", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.base_url_entry = ttk.Entry(input_frame, width=50)
        self.base_url_entry.insert(0, "https://ark.cn-beijing.volces.com/api/v3")
        self.base_url_entry.grid(row=3, column=0, pady=(0, 15))
        
        # Model Name
        ttk.Label(input_frame, text="Model Name (可选)", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.model_name_entry = ttk.Entry(input_frame, width=50)
        self.model_name_entry.insert(0, "your-model-name")
        self.model_name_entry.grid(row=5, column=0, pady=(0, 15))
        
        # 帮助文本
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(10, 20))
        
        help_text = ttk.Label(
            help_frame,
            text="* 必填项\n\n如何获取API凭证？",
            font=("Arial", 9),
            foreground="gray"
        )
        help_text.pack(side=tk.LEFT)
        
        help_button = ttk.Button(
            help_frame,
            text="查看帮助",
            command=self._on_help_clicked
        )
        help_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.save_button = ttk.Button(
            button_frame,
            text="保存并继续",
            command=self._validate_and_save
        )
        self.save_button.pack(side=tk.RIGHT)
    
    def _on_help_clicked(self):
        """显示帮助信息"""
        help_text = """
获取API凭证的步骤：

1. 访问火山引擎控制台
2. 进入"模型推理"服务
3. 创建或选择一个推理接入点
4. 获取API Key和Base URL

详细信息请参考火山引擎官方文档。
        """
        messagebox.showinfo("帮助", help_text.strip())
    
    def _on_close_attempt(self):
        """尝试关闭窗口时的处理"""
        result = messagebox.askyesno(
            "确认退出",
            "必须完成配置才能使用应用程序。\n确定要退出吗？"
        )
        if result:
            # 用户确认退出，关闭整个应用
            self.parent.quit()
    
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
        
        # 创建配置对象
        config = AppConfig(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name if model_name else "your-model-name"
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
        显示对话框并等待用户完成配置
        
        Returns:
            配置对象，如果用户取消则返回None
        """
        self.dialog.wait_window()
        return self.result

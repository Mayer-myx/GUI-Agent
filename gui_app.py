#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Agent - 图形界面应用程序
智能GUI自动化助手
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到路径
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from core.config_manager import ConfigManager
from ui.config_wizard import ConfigWizard
from ui.main_window import MainWindow


def main():
    """主程序入口"""
    try:
        # 创建根窗口
        root = tk.Tk()
        
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 检查是否首次运行
        if config_manager.is_first_run():
            # 显示配置向导
            wizard = ConfigWizard(root)
            config = wizard.show()
            
            if config is None:
                # 用户取消配置，退出应用
                root.destroy()
                return
            
            # 保存配置
            if not config_manager.save_config(config):
                messagebox.showerror(
                    "错误",
                    "保存配置失败，请检查文件权限。"
                )
                root.destroy()
                return
        else:
            # 加载现有配置
            try:
                config = config_manager.load_config()
            except Exception as e:
                messagebox.showerror(
                    "配置错误",
                    f"加载配置失败：{str(e)}\n\n将重新配置。"
                )
                # 显示配置向导
                wizard = ConfigWizard(root)
                config = wizard.show()
                
                if config is None:
                    root.destroy()
                    return
                
                config_manager.save_config(config)
        
        # 创建主窗口
        main_window = MainWindow(root, config, config_manager)
        
        # 运行主循环
        root.mainloop()
    
    except Exception as e:
        # 捕获未处理的异常
        messagebox.showerror(
            "严重错误",
            f"应用程序发生严重错误：{str(e)}\n\n应用程序将退出。"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

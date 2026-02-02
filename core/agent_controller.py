# core/agent_controller.py

import sys
import threading
from typing import Callable
from io import StringIO
from main import GUIAgent


class OutputRedirector:
    """输出重定向器 - 捕获print输出并传递给GUI"""
    
    def __init__(self, callback: Callable[[str], None]):
        """
        初始化输出重定向器
        
        Args:
            callback: 接收输出文本的回调函数
        """
        self.callback = callback
        self.buffer = StringIO()
    
    def write(self, text: str) -> None:
        """
        写入文本
        
        Args:
            text: 要写入的文本
        """
        if text and text.strip():
            self.callback(text)
    
    def flush(self) -> None:
        """刷新缓冲区"""
        pass


class AgentController:
    """Agent控制器 - 管理GUIAgent的生命周期"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        log_callback: Callable[[str, str], None],
        screenshot_callback: Callable[[str, int], None],
        status_callback: Callable[[str, str], None]
    ):
        """
        初始化Agent控制器
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
            log_callback: 日志回调函数 (message, level)
            screenshot_callback: 截图回调函数 (image_path, step)
            status_callback: 状态回调函数 (status, color)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.log_callback = log_callback
        self.screenshot_callback = screenshot_callback
        self.status_callback = status_callback
        
        self.agent_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self._running = False
    
    def is_running(self) -> bool:
        """
        检查任务是否正在运行
        
        Returns:
            是否正在运行
        """
        return self._running
    
    def start_task(self, instruction: str) -> None:
        """
        启动任务
        
        Args:
            instruction: 任务指令
        """
        if self._running:
            self.log_callback("任务已在运行中", "warning")
            return
        
        # 重置停止事件
        self.stop_event.clear()
        
        # 在新线程中运行Agent
        self.agent_thread = threading.Thread(
            target=self._run_agent_thread,
            args=(instruction,),
            daemon=True
        )
        self._running = True
        self.agent_thread.start()
    
    def stop_task(self) -> None:
        """停止当前任务"""
        if not self._running:
            return
        
        self.log_callback("正在停止任务...", "warning")
        self.stop_event.set()
        
        # 等待线程结束（最多5秒）
        if self.agent_thread:
            self.agent_thread.join(timeout=5.0)
        
        self._running = False
        self.status_callback("已停止", "orange")
        self.log_callback("任务已停止", "info")
    
    def _run_agent_thread(self, instruction: str) -> None:
        """
        在线程中运行Agent
        
        Args:
            instruction: 任务指令
        """
        # 保存原始stdout
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # 重定向输出
            sys.stdout = OutputRedirector(lambda msg: self.log_callback(msg, "info"))
            sys.stderr = OutputRedirector(lambda msg: self.log_callback(msg, "error"))
            
            # 更新状态
            self.status_callback("执行中", "blue")
            self.log_callback(f"开始执行任务: {instruction}", "info")
            
            # 创建并运行Agent
            # 注意：需要修改GUIAgent类以支持配置和停止事件
            agent = GUIAgent(
                instruction=instruction,
                model_name=self.model_name
            )
            
            # 修改Agent的配置
            agent.lvm_chat.client.api_key = self.api_key
            agent.lvm_chat.client.base_url = self.base_url
            
            # 运行Agent（这里需要修改GUIAgent以支持停止事件）
            final_state = agent.run()
            
            # 任务完成
            if not self.stop_event.is_set():
                self.status_callback("已完成", "green")
                self.log_callback(f"任务完成！共执行 {final_state['step']} 步", "success")
        
        except Exception as e:
            self.log_callback(f"执行错误: {str(e)}", "error")
            self.status_callback("错误", "red")
        
        finally:
            # 恢复原始stdout
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            self._running = False

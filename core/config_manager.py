# core/config_manager.py

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Tuple


@dataclass
class AppConfig:
    """应用程序配置数据类"""
    api_key: str
    base_url: str
    model_name: str = "ep-20260120161243-g7vwl"
    history: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """从字典创建配置对象"""
        return cls(**data)
    
    def validate(self) -> Tuple[bool, str]:
        """
        验证配置有效性
        
        Returns:
            (is_valid, error_message): 验证结果和错误消息
        """
        if not self.api_key or not self.api_key.strip():
            return False, "API Key不能为空"
        
        if not self.base_url or not self.base_url.strip():
            return False, "Base URL不能为空"
        
        if not self.base_url.startswith("http://") and not self.base_url.startswith("https://"):
            return False, "Base URL必须以http://或https://开头"
        
        return True, ""


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: AppConfig | None = None
    
    def load_config(self) -> AppConfig:
        """
        从文件加载配置
        
        Returns:
            AppConfig对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.config = AppConfig.from_dict(data)
        return self.config
    
    def save_config(self, config: AppConfig) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置对象
            
        Returns:
            是否保存成功
        """
        try:
            # 验证配置
            is_valid, error_msg = config.validate()
            if not is_valid:
                raise ValueError(error_msg)
            
            # 保存到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def is_first_run(self) -> bool:
        """
        检测是否首次运行
        
        Returns:
            如果配置文件不存在，返回True
        """
        return not os.path.exists(self.config_path)
    
    def add_to_history(self, task: str) -> None:
        """
        添加任务到历史记录
        
        Args:
            task: 任务描述
        """
        if not self.config:
            return
        
        # 避免重复
        if task in self.config.history:
            self.config.history.remove(task)
        
        # 添加到开头
        self.config.history.insert(0, task)
        
        # 限制最多50条
        if len(self.config.history) > 50:
            self.config.history = self.config.history[:50]
        
        # 保存配置
        self.save_config(self.config)
    
    def get_history(self) -> List[str]:
        """
        获取历史记录
        
        Returns:
            历史任务列表
        """
        if not self.config:
            return []
        return self.config.history.copy()

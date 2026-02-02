# utils/model.py

import os
import base64
from openai import OpenAI
from typing import List, Dict, Any

# 默认配置 - 实际使用时会从config.json加载
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "your-model-name"

class LVMChat:
    """支持会话记忆的多模态聊天类"""
    
    def __init__(self, api_key: str = None, base_url: str = DEFAULT_BASE_URL, 
                 model: str = DEFAULT_MODEL):
        if not api_key:
            raise ValueError("API Key is required. Please configure it in config.json")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        # 🔥 核心改动：添加会话历史记录
        self.conversation_history: List[Dict[str, Any]] = []
    
    def _encode_image(self, image_path: str) -> str:
        """将本地图片转为 data URL，方便直接作为 image_url 传入"""
        with open(image_path, "rb") as image_file:
            b64 = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    
    def get_multimodal_response(self, text: str, image_paths: str, 
                                res_format: str = "text", use_history: bool = False) -> tuple[str, dict]:
        """
        支持记忆的图文对话
        
        Args:
            text: 你的问题
            image_paths: 图片路径
            res_format: 响应格式 ("text" 或 "json")
            use_history: 是否使用会话历史（记住之前的对话）
            
        Returns:
            (response_text, usage_info): 响应文本和使用统计
        """
        # 1. 加载图片并转为 Ark 支持的 data URL
        image_url = self._encode_image(image_paths)
        
        # 2. 构建 input（Ark Responses API）
        current_message = {
            "role": "user",
            "content": [
                {"type": "input_image", "image_url": image_url},
                {"type": "input_text", "text": text},
            ],
        }
        
        # 3. 🔥 关键：如果启用历史，把之前的对话也带上
        if use_history and self.conversation_history:
            # 对于有历史的情况，需要特殊处理
            payload = self.conversation_history + [current_message]
            print(f"📚 使用历史上下文，共 {len(self.conversation_history)} 条")
            
            # 调用 API (使用chat.completions而不是responses)
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self._convert_to_chat_format(payload)
                )
                result = response.choices[0].message.content
                
                # 提取token使用信息
                usage_info = {
                    'input_tokens': getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') else 0,
                    'output_tokens': getattr(response.usage, 'completion_tokens', 0) if hasattr(response, 'usage') else 0,
                    'total_tokens': getattr(response.usage, 'total_tokens', 0) if hasattr(response, 'usage') else 0
                }
            except Exception as e:
                print(f"Chat API failed, falling back to responses API: {e}")
                # 回退到单次调用
                response = self.client.responses.create(
                    model=self.model,
                    input=[current_message]
                )
                result = getattr(response, "output_text", str(response))
                usage_info = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        else:
            payload = [current_message]
            # 4. 调用 API
            response = self.client.responses.create(
                model=self.model,
                input=payload
            )
            result = getattr(response, "output_text", str(response))
            
            # 尝试从响应中提取token信息（如果API提供）
            usage_info = {
                'input_tokens': getattr(response, 'input_tokens', 0) if hasattr(response, 'input_tokens') else 0,
                'output_tokens': getattr(response, 'output_tokens', 0) if hasattr(response, 'output_tokens') else 0,
                'total_tokens': 0
            }
            usage_info['total_tokens'] = usage_info['input_tokens'] + usage_info['output_tokens']
        
        # 6. 🔥 更新历史记录
        if use_history:
            self.conversation_history.append(current_message)
            self.conversation_history.append({
                "role": "assistant", 
                "content": [{"type": "output_text", "text": result}]
            })
        
        return result, usage_info
    
    def clear_history(self):
        """清空记忆"""
        self.conversation_history = []


# # 示例调用
# if __name__ == "__main__":
#     chat = LVMChat()
#     response = chat.get_multimodal_response(
#         text="这张图片里输入框坐标？",
#         image_paths=r"D:\projects\cc\GUI-Agent\utils\screenshot-20260120-160656.png"
#     )
#     print(response)


# 会话记忆示例
#  # 第一轮对话
# conversation_history = [
#     {"role": "user", "content": [图片1, "在输入框输入‘你好’"]},
#     {"role": "assistant", "content": "{'Thought'： '输入框在页面中间位置，我需要输入文案', 'Action': 'type(content=\'你好\')'}"}
# ]

# # 第二轮对话时，把历史也带上
# messages = conversation_history + [
#     {"role": "user", "content": [图片2, "在输入框输入‘你好’"]}
# ]
# # 现在AI能看到完整的对话链，知道自己做过什么决策。在第二轮返回:
# {'Thought'： '上一轮已经完成输入操作并且文案已经正确显示在输入框，任务已经完成', 'Action': 'finished'}
    
    def _convert_to_chat_format(self, payload):
        """将Ark responses格式转换为chat格式"""
        messages = []
        for item in payload:
            if item["role"] == "user":
                # 转换用户消息
                content = []
                for c in item["content"]:
                    if c["type"] == "input_image":
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": c["image_url"]}
                        })
                    elif c["type"] == "input_text":
                        content.append({
                            "type": "text", 
                            "text": c["text"]
                        })
                messages.append({
                    "role": "user",
                    "content": content
                })
            elif item["role"] == "assistant":
                # 转换助手消息
                text_content = ""
                for c in item["content"]:
                    if c["type"] == "output_text":
                        text_content = c["text"]
                        break
                messages.append({
                    "role": "assistant",
                    "content": text_content
                })
        return messages
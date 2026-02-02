#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Agent - 自动化GUI测试Agent
截图 -> 模型决策 -> 解析Action -> 执行 -> 循环，直到finished
"""

import sys, os
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

import re
import json
from datetime import datetime
from typing import TypedDict
from pathlib import Path
from langgraph.graph import StateGraph, END
from gui_operator.execute import Operation
from utils.model import LVMChat
from utils.prompts import COMPUTER_USE_UITARS


# 定义State
class AgentState(TypedDict):
    instruction: str  # 用户指令
    screenshot_path: str  # 当前截图路径
    step: int  # 当前步骤
    thought: str  # 模型思考
    action: str  # 模型输出的动作
    finished: bool  # 是否完成


class GUIAgent:
    """GUI自动化Agent"""
    
    def __init__(self, instruction: str, model_name: str = "your-model-name"):
        self.instruction = instruction
        self.operation = Operation()
        self.lvm_chat = LVMChat(model=model_name)
        self.s_dir = Path("steps")
        self.s_dir.mkdir(exist_ok=True)
        
        # 获取屏幕尺寸用于坐标映射
        import pyautogui
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"🖥️  屏幕尺寸: {self.screen_width}x{self.screen_height}")
    
    def normalize_coords(self, x: int, y: int) -> tuple[int, int]:
        """将归一化坐标(0-1000)转换为实际像素坐标"""
        actual_x = int(x / 1000.0 * self.screen_width)
        actual_y = int(y / 1000.0 * self.screen_height)
        print(f"   归一化坐标 ({x}, {y}) -> 实际坐标 ({actual_x}, {actual_y})")
        return actual_x, actual_y
        
    def take_screenshot(self, state: AgentState) -> AgentState:
        """步骤1: 截图并保存"""
        step = state.get("step", 0) + 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = str(self.s_dir / f"step_{step}_{timestamp}.png")
        
        self.operation.screenshot(screenshot_path)
        
        return {
            **state,
            "instruction": self.instruction,
            "screenshot_path": screenshot_path,
            "step": step,
            "finished": False
        }
    
    def model_decide(self, state: AgentState) -> AgentState:
        """步骤2: 模型决策（自动使用会话历史）"""
        from datetime import datetime
        
        step_start_time = datetime.now()
        prompt = COMPUTER_USE_UITARS.format(instruction=state["instruction"])
        
        # 调用多模态模型（use_history=True 自动保留上下文）
        response, usage_info = self.lvm_chat.get_multimodal_response(
            text=prompt,
            image_paths=state["screenshot_path"],
            res_format="json",
            use_history=True# 启用会话历史，模型会记住之前的所有交互
        )
        
        step_end_time = datetime.now()
        duration = (step_end_time - step_start_time).total_seconds()
        
        # 打印详细的步骤信息
        print(f"\n📸 Step {state['step']} - 模型响应:")
        print(f"⏱️  时间: {step_start_time.strftime('%H:%M:%S')} - {step_end_time.strftime('%H:%M:%S')} (耗时: {duration:.2f}秒)")
        print(f"🔢 Token使用: 输入={usage_info.get('input_tokens', 0)}, 输出={usage_info.get('output_tokens', 0)}, 总计={usage_info.get('total_tokens', 0)}")
        print(f"📝 响应内容:\n{response}\n")
        
        # 解析JSON响应
        try:
            result = json.loads(response)
            thought = result.get("Thought", "")
            action = result.get("Action", "")
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试正则提取
            thought_match = re.search(r'"?Thought"?\s*[:：]\s*"?([^"]*)"?', response, re.DOTALL)
            action_match = re.search(r'"?Action"?\s*[:：]\s*"?([^"]*)"?', response, re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else ""
            action = action_match.group(1).strip() if action_match else ""
            
            # 如果还是找不到，尝试更宽松的匹配
            if not action:
                # 查找包含动作的行
                lines = response.split('\n')
                for line in lines:
                    if any(cmd in line for cmd in ['click(', 'type(', 'hotkey(', 'scroll(', 'finished(']):
                        action = line.strip()
                        break
        
        return {
            **state,
            "thought": thought,
            "action": action
        }
    
    def execute_action(self, state: AgentState) -> AgentState:
        """步骤3: 解析并执行动作"""
        action = state["action"]
        
        if not action:
            print("⚠️ 没有可执行的动作")
            return {**state, "finished": True}
        
        # 检查是否完成
        if action.startswith("finished("):
            content_match = re.search(r"finished\(content='([^']*)'\)", action)
            content = content_match.group(1) if content_match else"任务完成"
            print(f"✅ 任务完成: {content}")
            return {**state, "finished": True}
        
        # 解析并执行动作
        try:
            self._parse_and_execute(action)
        except Exception as e:
            print(f"❌ 执行动作失败: {e}")
            print(f"   动作: {action}")
        
        return state
    
    def _parse_and_execute(self, action: str):
        """解析动作字符串并执行"""
        print(f"🔧 执行动作: {action}")
        
        # click(point='<point>x y</point>') 或 click(point='x y')
        if action.startswith("click("):
            # 尝试带标签的格式
            point_match = re.search(r"<point>(\d+)\s+(\d+)</point>", action)
            if not point_match:
                # 尝试不带标签的格式
                point_match = re.search(r"point=['\"](\d+)\s+(\d+)['\"]", action)
            
            if point_match:
                x, y = int(point_match.group(1)), int(point_match.group(2))
                actual_x, actual_y = self.normalize_coords(x, y)
                self.operation.click(actual_x, actual_y)
            else:
                print(f"⚠️ 无法解析点击坐标: {action}")
        
        # left_double(point='<point>x y</point>') 或 double_click(point='x y')
        elif action.startswith("left_double("):
            # 尝试带标签的格式
            point_match = re.search(r"<point>(\d+)\s+(\d+)</point>", action)
            if not point_match:
                # 尝试不带标签的格式
                point_match = re.search(r"point=['\"](\d+)\s+(\d+)['\"]", action)
            
            if point_match:
                x, y = int(point_match.group(1)), int(point_match.group(2))
                actual_x, actual_y = self.normalize_coords(x, y)
                self.operation.double_click(actual_x, actual_y)
            else:
                print(f"⚠️ 无法解析双击坐标: {action}")
        
        # type(content='xxx')
        elif action.startswith("type("):
            content_match = re.search(r"content=['\"]([^'\"]*)['\"]", action)
            if content_match:
                text = content_match.group(1)
                # 处理转义字符
                text = text.replace(r"\'", "'").replace(r'\"', '"').replace(r"\n", "\n")
                self.operation.input(text)
        
        # hotkey(key='ctrl c')
        elif action.startswith("hotkey("):
            key_match = re.search(r"key=['\"]([^'\"]*)['\"]", action)
            if key_match:
                keys = key_match.group(1).split()
                self.operation.hotkey(*keys)
        
        # scroll(point='<point>x y</point>', direction='down') 或 scroll(point='x y', direction='down')
        elif action.startswith("scroll("):
            # 尝试带标签的格式
            point_match = re.search(r"<point>(\d+)\s+(\d+)</point>", action)
            if not point_match:
                # 尝试不带标签的格式
                point_match = re.search(r"point=['\"](\d+)\s+(\d+)['\"]", action)
            
            direction_match = re.search(r"direction=['\"]([^'\"]*)['\"]", action)
            if point_match and direction_match:
                x, y = int(point_match.group(1)), int(point_match.group(2))
                actual_x, actual_y = self.normalize_coords(x, y)
                direction = direction_match.group(1)
                # 移动到位置并滚动
                import pyautogui
                pyautogui.moveTo(actual_x, actual_y)
                scroll_amount = 3 if direction in ["up", "left"] else -3
                pyautogui.scroll(scroll_amount)
        
        # wait()
        elif action.startswith("wait("):
            self.operation.wait(seconds=2)
        
        # drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')
        elif action.startswith("drag("):
            # 尝试带标签的格式
            start_match = re.search(r"start_point=['\"]<point>(\d+)\s+(\d+)</point>['\"]", action)
            end_match = re.search(r"end_point=['\"]<point>(\d+)\s+(\d+)</point>['\"]", action)
            
            if not start_match:
                # 尝试不带标签的格式
                start_match = re.search(r"start_point=['\"](\d+)\s+(\d+)['\"]", action)
                end_match = re.search(r"end_point=['\"](\d+)\s+(\d+)['\"]", action)
            
            if start_match and end_match:
                x1, y1 = int(start_match.group(1)), int(start_match.group(2))
                x2, y2 = int(end_match.group(1)), int(end_match.group(2))
                actual_x1, actual_y1 = self.normalize_coords(x1, y1)
                actual_x2, actual_y2 = self.normalize_coords(x2, y2)
                import pyautogui
                pyautogui.moveTo(actual_x1, actual_y1)
                pyautogui.drag(actual_x2 - actual_x1, actual_y2 - actual_y1, duration=0.5)
        
        # 等待一下让界面响应
        self.operation.wait(seconds=1)
    
    def should_continue(self, state: AgentState) -> str:
        """判断是否继续循环"""
        return"end"if state.get("finished", False) else"continue"
    
    def run(self):
        """运行Agent"""
        # 构建graph
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("screenshot", self.take_screenshot)
        workflow.add_node("decide", self.model_decide)
        workflow.add_node("execute", self.execute_action)
        
        # 添加边
        workflow.set_entry_point("screenshot")
        workflow.add_edge("screenshot", "decide")
        workflow.add_edge("decide", "execute")
        workflow.add_conditional_edges(
            "execute",
            self.should_continue,
            {
                "continue": "screenshot",
                "end": END
            }
        )
        
        # 编译并运行
        app = workflow.compile()
        
        print(f"🚀 开始执行任务: {self.instruction}\n")
        
        # 设置递归限制为100步
        config = {"recursion_limit": 100}
        final_state = app.invoke(
            {"instruction": self.instruction, "step": 0},
            config=config
        )
        
        print(f"\n🎉 任务完成! 共执行 {final_state['step']} 步")
        return final_state


if __name__ == "__main__":
    agent = GUIAgent(instruction="""打开edge浏览器查找bilibili, 搜索小米汽车，找到排序第一的视频并打开播放""")
    agent.run()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Agent - Web界面版本
使用Flask提供Web界面，无需tkinter
"""

import sys
import os
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import time

# 添加当前目录到路径
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from core.config_manager import ConfigManager, AppConfig
from main import GUIAgent
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gui-agent-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
config_manager = ConfigManager()
current_config = None
agent_thread = None
agent_running = False
current_task_id = None  # 当前任务ID
task_logs = []  # 当前任务的日志
task_screenshots = []  # 当前任务的截图


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    global current_config
    
    if config_manager.is_first_run():
        return jsonify({'first_run': True})
    
    try:
        current_config = config_manager.load_config()
        return jsonify({
            'first_run': False,
            'config': {
                'api_key': current_config.api_key[:10] + '...' if current_config.api_key else '',
                'base_url': current_config.base_url,
                'model_name': current_config.model_name,
                'history': current_config.history
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def save_config():
    """保存配置"""
    global current_config
    
    data = request.json
    config = AppConfig(
        api_key=data.get('api_key', ''),
        base_url=data.get('base_url', ''),
        model_name=data.get('model_name', 'your-model-name'),
        history=data.get('history', [])
    )
    
    # 验证配置
    is_valid, error_msg = config.validate()
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # 保存配置
    if config_manager.save_config(config):
        current_config = config
        return jsonify({'success': True})
    else:
        return jsonify({'error': '保存配置失败'}), 500


@app.route('/api/task/start', methods=['POST'])
def start_task():
    """启动任务"""
    global agent_thread, agent_running, current_config, current_task_id, task_logs, task_screenshots
    
    if agent_running:
        return jsonify({'error': '任务已在运行中'}), 400
    
    if not current_config:
        return jsonify({'error': '请先配置API凭证'}), 400
    
    data = request.json
    instruction = data.get('instruction', '')
    
    if not instruction:
        return jsonify({'error': '任务描述不能为空'}), 400
    
    # 生成任务ID
    current_task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_logs = []
    task_screenshots = []
    
    # 确保tasks目录存在
    tasks_dir = "tasks"
    if not os.path.exists(tasks_dir):
        os.makedirs(tasks_dir)
    
    # 在新线程中运行Agent
    agent_thread = threading.Thread(
        target=run_agent_task,
        args=(instruction,),
        daemon=True
    )
    agent_running = True
    agent_thread.start()
    
    # 添加到历史记录
    config_manager.add_to_history(instruction)
    
    return jsonify({'success': True, 'task_id': current_task_id})


@app.route('/api/task/stop', methods=['POST'])
def stop_task():
    """停止任务"""
    global agent_running
    
    agent_running = False
    socketio.emit('log', {'message': '正在停止任务...', 'level': 'warning'})
    
    return jsonify({'success': True})


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取历史记录"""
    history = config_manager.get_history()
    return jsonify({'history': history})


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_details(task_id):
    """获取任务详细信息"""
    try:
        task_file = f"tasks/{task_id}.json"
        if os.path.exists(task_file):
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            return jsonify(task_data)
        else:
            return jsonify({'error': '任务记录不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """获取所有任务列表"""
    try:
        tasks_dir = "tasks"
        if not os.path.exists(tasks_dir):
            return jsonify({'tasks': []})
        
        tasks = []
        for filename in os.listdir(tasks_dir):
            if filename.endswith('.json'):
                task_id = filename[:-5]  # 移除.json后缀
                try:
                    with open(os.path.join(tasks_dir, filename), 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # 只返回基本信息
                    task_summary = {
                        'id': task_id,
                        'instruction': task_data.get('instruction', ''),
                        'start_time': task_data.get('start_time', ''),
                        'end_time': task_data.get('end_time', ''),
                        'status': task_data.get('status', ''),
                        'steps': len(task_data.get('screenshots', [])),
                        'duration': task_data.get('duration', 0)
                    }
                    tasks.append(task_summary)
                except Exception as e:
                    print(f"读取任务文件失败 {filename}: {e}")
                    continue
        
        # 按时间倒序排列
        tasks.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        return jsonify({'tasks': tasks})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """提供截图文件"""
    # 确保steps目录存在
    steps_dir = os.path.join(base_dir, 'steps')
    if not os.path.exists(steps_dir):
        os.makedirs(steps_dir)
    
    return send_from_directory(steps_dir, filename)


def run_agent_task(instruction: str):
    """在后台线程运行Agent任务"""
    global agent_running, current_config, current_task_id, task_logs, task_screenshots
    
    start_time = datetime.now()
    
    try:
        socketio.emit('status', {'status': '执行中', 'color': 'blue'})
        
        start_log = f'[{start_time.strftime("%H:%M:%S")}] 🚀 开始执行任务: {instruction}'
        socketio.emit('log', {'message': start_log, 'level': 'info'})
        task_logs.append({'message': start_log, 'level': 'info', 'timestamp': start_time.isoformat()})
        
        # 创建Agent
        agent = GUIAgent(
            instruction=instruction,
            model_name=current_config.model_name
        )
        
        # 修改Agent的配置
        agent.lvm_chat.client.api_key = current_config.api_key
        agent.lvm_chat.client.base_url = current_config.base_url
        
        # 重定向输出
        import sys
        from io import StringIO
        
        class SocketIOWriter:
            def write(self, text):
                if text.strip():
                    # 添加时间戳
                    timestamp = datetime.now()
                    message = f"[{timestamp.strftime('%H:%M:%S')}] {text.strip()}"
                    socketio.emit('log', {'message': message, 'level': 'info'})
                    task_logs.append({'message': message, 'level': 'info', 'timestamp': timestamp.isoformat()})
            def flush(self):
                pass
        
        old_stdout = sys.stdout
        sys.stdout = SocketIOWriter()
        
        # 修改Agent以支持截图回调
        original_take_screenshot = agent.take_screenshot
        
        def enhanced_take_screenshot(state):
            # 调用原始截图方法
            result = original_take_screenshot(state)
            
            # 发送截图信息到前端
            if 'screenshot_path' in result:
                screenshot_path = result['screenshot_path']
                step = result.get('step', 0)
                
                # 获取文件名
                filename = os.path.basename(screenshot_path)
                
                # 记录截图信息
                screenshot_info = {
                    'filename': filename,
                    'step': step,
                    'path': screenshot_path,
                    'timestamp': datetime.now().isoformat()
                }
                task_screenshots.append(screenshot_info)
                
                # 发送截图事件
                socketio.emit('screenshot', screenshot_info)
                
                # 添加时间戳的截图日志
                timestamp = datetime.now()
                log_message = f'[{timestamp.strftime("%H:%M:%S")}] 📸 截图已保存: 步骤 {step}'
                socketio.emit('log', {'message': log_message, 'level': 'info'})
                task_logs.append({'message': log_message, 'level': 'info', 'timestamp': timestamp.isoformat()})
            
            return result
        
        # 替换截图方法
        agent.take_screenshot = enhanced_take_screenshot
        
        # 运行Agent
        final_state = agent.run()
        
        # 恢复stdout
        sys.stdout = old_stdout
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if agent_running:
            socketio.emit('status', {'status': '已完成', 'color': 'green'})
            success_log = f'[{end_time.strftime("%H:%M:%S")}] ✅ 任务完成！共执行 {final_state["step"]} 步，总耗时: {duration:.2f}秒'
            socketio.emit('log', {'message': success_log, 'level': 'success'})
            task_logs.append({'message': success_log, 'level': 'success', 'timestamp': end_time.isoformat()})
            
            # 保存任务记录
            save_task_record(instruction, start_time, end_time, '已完成', final_state.get('step', 0), duration)
    
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        error_log = f'[{end_time.strftime("%H:%M:%S")}] ❌ 执行错误: {str(e)}'
        socketio.emit('log', {'message': error_log, 'level': 'error'})
        task_logs.append({'message': error_log, 'level': 'error', 'timestamp': end_time.isoformat()})
        socketio.emit('status', {'status': '错误', 'color': 'red'})
        
        # 保存任务记录
        save_task_record(instruction, start_time, end_time, '错误', 0, duration, str(e))
    
    finally:
        agent_running = False


def save_task_record(instruction: str, start_time: datetime, end_time: datetime, 
                    status: str, steps: int, duration: float, error: str = None):
    """保存任务执行记录"""
    global current_task_id, task_logs, task_screenshots
    
    try:
        task_record = {
            'id': current_task_id,
            'instruction': instruction,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'status': status,
            'steps': steps,
            'duration': duration,
            'logs': task_logs,
            'screenshots': task_screenshots
        }
        
        if error:
            task_record['error'] = error
        
        # 保存到文件
        task_file = f"tasks/{current_task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_record, f, ensure_ascii=False, indent=2)
        
        print(f"任务记录已保存: {task_file}")
    
    except Exception as e:
        print(f"保存任务记录失败: {e}")


def open_browser():
    """延迟打开浏览器"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    print("🚀 GUI Agent Web版本启动中...")
    print("📱 浏览器将自动打开，如未打开请访问: http://127.0.0.1:5000")
    
    # 在新线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动Flask应用
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)

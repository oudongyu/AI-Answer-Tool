import pyautogui
import os
import sys
from openai import OpenAI
import datetime
from PIL import Image
import tkinter as tk
import win32con
import win32gui
import win32api
import requests
import base64
import re


# 处理打包后的资源路径
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# 配置 DeepSeek API
client = OpenAI(api_key="skce6f7", base_url="https://api.deepseek.com")


# 获取百度 OCR access token
def get_baidu_access_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    response = requests.post(url, params=params)
    if response:
        return response.json().get("access_token")
    return None


# 全局变量
start_pos = None
end_pos = None
region = None
selecting = False

# 热键 ID
HOTKEY_START = 1
HOTKEY_RECOGNIZE = 2


# 保存识别文字和 AI 回答到文件
def save_to_file(text, answer):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = "recognized_text.txt"
    file_exists = os.path.exists(filename)

    with open(filename, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(f"[{today}]\n")
        f.write(f"识别内容: {text}\n")
        f.write(f"AI 回答: {answer}\n\n")


# 判断题目类型
def detect_question_type(text):
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["是否", "对错", "true", "false", "是", "否", "判断"]):
        return "judgment"
    if any(kw in text_lower for kw in ["选择", "a.", "b.", "c.", "d.", "1.", "2.", "3.", "4."]):
        return "choice"
    if any(kw in text_lower for kw in ["填空"]) or re.search(r'_{2,}', text):
        return "fill_in"
    return "short_answer"


# 显示字幕
def show_subtitle(answer):
    subtitle = tk.Toplevel()
    subtitle.overrideredirect(True)  # 无边框
    subtitle.attributes("-alpha", 0.7)  # 透明度
    subtitle.attributes("-topmost", True)  # 置顶

    # 获取屏幕尺寸
    screen_width = subtitle.winfo_screenwidth()
    screen_height = subtitle.winfo_screenheight()

    # 设置固定大小
    subtitle_width = 800
    subtitle_height = 200
    font_size = 12

    # 计算字幕位置
    x_pos = (screen_width - subtitle_width) // 2
    y_pos = int(screen_height * 2 / 3) - (subtitle_height // 2)

    subtitle.geometry(f"{subtitle_width}x{subtitle_height}+{x_pos}+{y_pos}")

    label = tk.Label(subtitle, text=answer, font=("Segoe UI", 14, "bold"), fg="#E0E0E0", bg="#333333",
                     wraplength=subtitle_width - 20, justify="left", anchor="w", padx=10, pady=5)
    label.pack(expand=True)

    # 固定 5 秒后关闭
    subtitle.after(5000, subtitle.destroy)
    return subtitle  # 返回字幕对象以确保事件循环处理


# 开始选择区域
def start_selection():
    global start_pos, selecting
    if not selecting:
        selecting = True
        start_pos = pyautogui.position()
        print("选择开始，请拖动鼠标并再次按 Ctrl+Shift+Q 结束")


# 结束选择区域
def end_selection():
    global start_pos, end_pos, region, selecting
    if selecting and start_pos:
        end_pos = pyautogui.position()
        region = (min(start_pos[0], end_pos[0]), min(start_pos[1], end_pos[1]),
                  max(abs(end_pos[0] - start_pos[0]), 50), max(abs(end_pos[1] - start_pos[1]), 50))
        selecting = False
        print(f"区域已选择: {region}")


# 识别并回答
def recognize_and_answer():
    global region
    if region is None:
        print("请先选择区域（Ctrl+Shift+Q）")
        return

    try:
        # 截图并保存
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save("temp.png")

        # 读取图片并转换为 base64
        with open("temp.png", "rb") as f:
            img = base64.b64encode(f.read()).decode('utf-8')

        # 获取百度 OCR access token
        api_key = "G4V"
        secret_key = "P3B"
        access_token = get_baidu_access_token(api_key, secret_key)
        if not access_token:
            show_subtitle("获取百度 OCR token 失败")
            print("获取百度 OCR token 失败")
            return

        # 调用百度 OCR API
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        params = {"image": img}
        request_url = f"{request_url}?access_token={access_token}"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers, timeout=10)

        if not response or 'words_result' not in response.json():
            show_subtitle("百度 OCR 识别失败")
            print("百度 OCR 识别失败")
            return

        # 提取识别结果
        words = [item['words'] for item in response.json()['words_result']]
        text = "\n".join(words)
        if not text.strip():
            show_subtitle("未识别到文字")
            print("未识别到文字")
            return

        # 判断题目类型
        question_type = detect_question_type(text)

        # 根据题目类型调整提示词和参数
        if question_type == "judgment":
            system_content = "你是一名考试助手。请用中文回答正确答案（是 或 否），不要解释。"
            max_tokens = 10
        elif question_type == "choice":  # 单选题
            system_content = "你是一名考试助手。请用中文直接输出正确的选项文本，不要解释。"
            max_tokens = 20
        elif question_type == "multi_choice":  # 多选题
            system_content = "你是一名考试助手。请用中文直接输出所有正确的选项文本，每个选项单独占一行，不要解释。"
            max_tokens = 50
        elif question_type == "fill_in":
            system_content = "你是一名考试助手。请用中文直接提供正确的填空答案，不要解释。"
            max_tokens = 20
        else:  # 简答题
            system_content = "你是一名考试助手。请用中文直接回答最精准的答案，不要解释。"
            max_tokens = 50

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": text},
            ],
            stream=False,
            max_tokens=max_tokens
        )

        answer = response.choices[0].message.content
        save_to_file(text, answer)
        print(f"识别内容:\n{text}\n\nAI 回答:\n{answer}")

        subtitle = show_subtitle(answer)

    except requests.RequestException as e:
        show_subtitle("网络错误，请检查连接")
        print(f"网络错误: {str(e)}")
    except Exception as e:
        show_subtitle("未知错误")
        print(f"错误: {str(e)}")


# 注册热键
def register_hotkeys(hwnd):
    win32gui.RegisterHotKey(hwnd, HOTKEY_START, win32con.MOD_CONTROL | win32con.MOD_SHIFT, ord('Q'))
    win32gui.RegisterHotKey(hwnd, HOTKEY_RECOGNIZE, win32con.MOD_CONTROL | win32con.MOD_SHIFT, ord('W'))


# 热键处理
def handle_hotkeys():
    hwnd = root.winfo_id()
    register_hotkeys(hwnd)

    def wnd_proc(hwnd, msg, wparam, lparam):
        if msg == win32con.WM_HOTKEY:
            if wparam == HOTKEY_START:
                if not selecting:
                    start_selection()
                else:
                    end_selection()
            elif wparam == HOTKEY_RECOGNIZE:
                recognize_and_answer()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    win32gui.SetWindowLong(hwnd, win32con.GWL_WNDPROC, wnd_proc)


# 主程序
root = tk.Tk()
root.withdraw()  # 隐藏窗口
root.title("屏幕识别与 AI 回答工具（隐藏）")
handle_hotkeys()

print("程序已启动，按 Ctrl+Shift+Q 拖动选择区域，按 Ctrl+Shift+W 识别并回答")
root.mainloop()

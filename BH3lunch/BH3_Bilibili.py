# -*- coding: utf-8 -*-
import BH3MatchPicture as BMP
import elevate
from tkinter import ttk
import tkinter as tk
import psutil
import win32api
import os
import ctypes
import json


def load_json(config_path="./config_path.json"):
    try:
        with open(config_path, 'r') as load_f:
            path_dict = json.load(load_f)
            print("Config loaded:", path_dict)
            return path_dict
    except (FileNotFoundError, json.JSONDecodeError):
        return dump_json(config_path)


def dump_json(config_path="./config_path.json"):
    path_dict = {}
    path_dict["Logger_path"] = input("请输入B服崩坏三扫码器文件路径(右键->复制路径)：\n")
    path_dict["Game_path"] = input("请输入“BH3.exe”文件路径(右键->复制路径)：\n")
    with open(config_path, "w") as f:
        json.dump(path_dict, f)
    print("Config saved:", path_dict)
    return path_dict


def start_applications(path_dict):
    try:
        os.startfile(path_dict["Logger_path"])
        os.startfile(path_dict["Game_path"])
    except Exception as e:
        print(f"Error starting applications: {e}")
        raise


def setup_dpi_awareness():
    ctypes.windll.shcore.SetProcessDpiAwareness(1)


def capture_screen():
    win32api.keybd_event(0x2C, 0, 0, 0)  # Press Print Screen key


def kill_process(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].startswith(process_name):
            try:
                proc.kill()
                print(f"Process '{process_name}' has been killed.")
                return True
            except Exception as e:
                print(f"Error: Unable to kill process '{process_name}': {e}")
                return False
    return False


def match_and_click():
    result = BMP.find_and_click_image()
    if result:
        print(f"Clicked on image at coordinates: {result}")
        return True
    print("No matching image found on the screen.")
    return False


def detect_and_handle_qr_code():
    qr_code_data = BMP.detect_qr_code()
    if qr_code_data:
        capture_screen()
        print(f"Detected QR code with data: {qr_code_data}")
        return True
    print("No QR code detected in the screenshot.")
    return False


def create_gui(root, ruler):
    label = ttk.Label(root, justify='center', text="点击“截图扫码”，或等待程序自动扫码")
    label.pack(pady=int(3 * ruler))

    def capture_screen_callback():
        capture_screen()
        label.config(text="截图已保存至剪贴板，两秒后退出")
        root.after(2000, root.destroy)

    button = ttk.Button(root, text="截图扫码", width=int(
        0.8 * ruler), command=capture_screen_callback)
    button.pack(pady=int(1 * ruler))
    return label


def auto_scan(root, label, ruler, had_scan=0):
    if match_and_click():
        if had_scan:
            if kill_process("[仅B服]PC扫码器"):
                root.after(2000, root.destroy)
    elif detect_and_handle_qr_code():
        had_scan = 1
        label.config(text="自动截屏成功，请等待程序自动关闭")

    root.after(1500, lambda: auto_scan(root, label, ruler, had_scan))


def main():
    elevate.elevate()
    setup_dpi_awareness()
    path_dict = load_json()

    try:
        start_applications(path_dict)
    except Exception:
        path_dict = dump_json()
        start_applications(path_dict)

    root = tk.Tk()
    root.title("Screenshoter")
    screenheight = root.winfo_screenheight()
    screenwidth = root.winfo_screenwidth()
    ruler = int(((screenheight * screenwidth) ** 0.5)) // 100
    root.geometry(f"{30 * ruler}x{15 * ruler}+{5 * ruler}+{5 * ruler}")
    root.attributes("-topmost", True)

    label = create_gui(root, ruler)
    auto_scan(root, label, ruler)

    root.mainloop()


if __name__ == '__main__':
    main()

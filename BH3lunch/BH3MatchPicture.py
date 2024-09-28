import cv2
import numpy as np
import pyautogui
import os
from pyzbar import pyzbar


def get_screen_resolution():
    return pyautogui.size()

def read_images_from_folder(folder_path):
    images = []
    filenames = os.listdir(folder_path)
    for filename in filenames:
        img = cv2.imread(os.path.join(folder_path, filename))
        if img is not None:
            images.append(img)
    return images, filenames

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def match_images(screen_img, template_img):
    gray_screen = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)  # 将屏幕截图转换为灰度图像
    gray_template = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)  # 将模板图像转换为灰度图像

    res = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)  # 模板匹配
    threshold = 0.9  # 设置匹配阈值
    loc = np.where(res >= threshold)  # 获取匹配位置

    if len(loc[0]) > 0:  # 如果找到匹配位置
        pt = (loc[1][0], loc[0][0])  # 获取匹配位置的坐标
        h, w = template_img.shape[:2]  # 获取模板图像的高和宽
        center = (pt[0] + w // 2, pt[1] + h // 2)  # 计算中心位置
        return center
    return None


def resize_and_save_images(default_folder, target_folder, scale_factor, current_res_height):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    for i, filename in enumerate(os.listdir(default_folder), start=1):
        img = cv2.imread(os.path.join(default_folder, filename))
        if img is not None:
            resized_img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor)
            target_filename = os.path.join(target_folder, f"{current_res_height}p_{i}.png")
            cv2.imwrite(target_filename, resized_img)

def prepare_images():
    default_folder = os.path.join("Pictures_to_Match", "Default")
    default_images, default_filenames = read_images_from_folder(default_folder)
    if not default_images:
        print("No default images found.")
        return None

    # 从文件名中提取默认分辨率高度
    sample_filename = default_filenames[0]
    default_res_height = int(sample_filename.split('p')[0])

    current_res = get_screen_resolution()
    current_res_height = current_res.height
    scale_factor = current_res_height / default_res_height
    target_folder = os.path.join("Pictures_to_Match", f"{current_res_height}p")
    
    if not os.path.exists(target_folder) or len(os.listdir(target_folder)) != len(default_filenames):
        resize_and_save_images(default_folder, target_folder, scale_factor, current_res_height)
    
    return target_folder


def find_and_click_image():
    target_folder = prepare_images()
    if not target_folder:
        return None
    images, _ = read_images_from_folder(target_folder)
    screen_img = capture_screenshot()
    for template_img in images:
        match = match_images(screen_img, template_img)
        if match:
            x, y = match
            pyautogui.click(x, y)
            return x, y
    return None

def detect_qr_code(screen_img):
    gray_img = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    qr_codes = pyzbar.decode(gray_img)
    for qr_code in qr_codes:
        x, y, w, h = qr_code.rect
        cv2.rectangle(screen_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        qr_data = qr_code.data.decode('utf-8')
        return qr_data
    return None

if __name__ == "__main__":
    result = find_and_click_image()
    if result:
        print(f"Clicked on image at coordinates: {result}")
    else:
        print("No matching image found on the screen.")
    screen_img = capture_screenshot()
    qr_code_data = detect_qr_code(screen_img)
    if qr_code_data:
        print(f"Detected QR code with data: {qr_code_data}")
    else:
        print("No QR code detected in the screenshot.")

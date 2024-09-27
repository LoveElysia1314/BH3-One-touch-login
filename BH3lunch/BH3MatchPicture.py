import cv2
import numpy as np
import pyautogui
import os
from pyzbar import pyzbar

# 从文件夹中读取所有图像


def read_images_from_folder(folder_path):
    images = []
    filenames = os.listdir(folder_path)  # 获取文件夹中所有文件名
    for filename in filenames:
        img = cv2.imread(os.path.join(folder_path, filename))  # 读取图像文件
        if img is not None:
            images.append(img)  # 如果图像读取成功，添加到列表中
    return images

# 捕获当前屏幕截图


def capture_screenshot():
    screenshot = pyautogui.screenshot()  # 使用pyautogui截图
    screenshot = cv2.cvtColor(np.array(screenshot),
                              cv2.COLOR_RGB2BGR)  # 转换颜色格式
    return screenshot

# 匹配屏幕截图与模板图像


def match_images(screen_img, template_img):
    gray_screen = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)  # 将屏幕截图转换为灰度图像
    gray_template = cv2.cvtColor(
        template_img, cv2.COLOR_BGR2GRAY)  # 将模板图像转换为灰度图像

    res = cv2.matchTemplate(gray_screen, gray_template,
                            cv2.TM_CCOEFF_NORMED)  # 模板匹配
    threshold = 0.9  # 设置匹配阈值
    loc = np.where(res >= threshold)  # 获取匹配位置

    for pt in zip(*loc[::-1]):
        # 返回匹配位置的中心坐标
        return pt[0] + gray_template.shape[1] // 2, pt[1] + gray_template.shape[0] // 2
    return None

# 在屏幕上查找并点击图像


def find_and_click_image():
    input_folder = "input"  # 输入文件夹路径
    images = read_images_from_folder(input_folder)  # 读取输入文件夹中的所有图像
    screen_img = capture_screenshot()  # 捕获当前屏幕截图

    for template_img in images:
        match = match_images(screen_img, template_img)  # 进行图像匹配
        if match:
            x, y = match
            pyautogui.click(x, y)  # 在匹配位置点击
            pyautogui.moveTo(1, 1, duration=0.2)  # 将鼠标移动到左上角以防挡住二维码
            return x, y
    return None

# 检测屏幕截图中的二维码


def detect_qr_code():
    screen_img = capture_screenshot()  # 捕获当前屏幕截图
    gray_img = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)  # 将截图转换为灰度图像
    qr_codes = pyzbar.decode(gray_img)  # 解码二维码
    for qr_code in qr_codes:
        x, y, w, h = qr_code.rect  # 获取二维码位置和大小
        cv2.rectangle(screen_img, (x, y), (x + w, y + h),
                      (0, 255, 0), 2)  # 在截图中绘制矩形框
        qr_data = qr_code.data.decode('utf-8')  # 解码二维码数据
        return qr_data
    return None


# 主程序入口
if __name__ == "__main__":
    # 检测并点击输入文件夹中的图像
    result = find_and_click_image()
    if result:
        print(f"Clicked on image at coordinates: {result}")  # 输出点击位置
    else:
        print("No matching image found on the screen.")  # 没有找到匹配图像

    # 检测截图中的二维码
    qr_code_data = detect_qr_code()
    if qr_code_data:
        print(f"Detected QR code with data: {qr_code_data}")  # 输出二维码数据
    else:
        print("No QR code detected in the screenshot.")  # 没有检测到二维码

import asyncio
import json
from json.decoder import JSONDecodeError
import os.path
import socket
import sys
import time
import requests
from tkinter import Tk
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime

import psutil
from PIL import Image, ImageGrab
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyzbar.pyzbar import decode

# import bsgamesdk
import mainWindow
import loginDialog
# import mihoyosdk

# 组播组IP和端口
m_cast_group_ip = '239.0.1.255'
m_cast_group_port = 12585
bh_info = {}
config = {}
data = {}
global ui

def init_conf():
    # 配置文件检查
    global config
    conf_loop = True
    while conf_loop:
        if not os.path.isfile('./config.json'):
            write_conf()
        try:
            with open('./config.json') as fp:
                config = json.loads(fp.read())
                try:
                    if config['ver'] != 3:
                        print('配置文件已更新，请注意重新修改文件')
                        write_conf(config)
                        continue
                except KeyError:
                    print('配置文件已更新，请注意重新修改文件')
                    write_conf(config)
                    continue
        except JSONDecodeError:
            print('配置文件格式不正确 重新写入中...')
            write_conf()
            continue
        conf_loop = False
    print("配置文件检查完成")
    config['account_login'] = False


def write_conf(old=None):
    config_temp = json.loads('{"account":"","password":"","sleep_time":3,"ver":3,"clip_check":false,'
                             '"socket_send":false}')
    if old is not None:
        for key in config_temp:
            try:
                config_temp[key] = old[key]
            except KeyError:
                continue
    config_temp['ver'] = 3
    with open('./config.json', 'w') as f:
        output = json.dumps(config_temp, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(output)


class LoginThread(QThread):
    update_log = pyqtSignal(str)

    def run(self):
        asyncio.run(self.login())

    async def login(self):
        global config, bh_info
        # ui.loginBiliBtn.setText('登陆中...')
        self.printLog(f'登录B站账号{config["account"]}中...')
        import bsgamesdk
        bs_info = await bsgamesdk.login(config['account'], config['password'])
        if "access_key" not in bs_info:
            self.printLog('登录失败！')
            self.printLog(bs_info)
            ui.loginBiliBtn.setText("登陆账号")
            ui.loginBiliBtn.setDisabled(False)
            return
        self.printLog('登录成功！')
        self.printLog('登录崩坏3账号中...')
        import mihoyosdk
        bh_info = await mihoyosdk.verify(bs_info['uid'], bs_info['access_key'])
        if bh_info['retcode'] != 0:
            self.printLog('登录失败！')
            self.printLog(bh_info)
            return
        self.printLog('登录成功！')
        
        self.printLog('获取OA服务器信息中...')


        bh_ver = await mihoyosdk.getBHVer()


        self.printLog(f'当前崩坏3版本: {bh_ver}')

        oa = await mihoyosdk.getOAServer()
        if oa['retcode'] != 0:
            self.printLog('登录失败！')
            self.printLog(oa)
            return

        self.printLog('获取OA服务器成功！')
        ui.loginBiliBtn.setText("账号已登录")
        # ui.loginBiliBtn.setDisabled(True)
        config['account_login'] = True

        write_conf(config)

    def printLog(self, msg):
        print(str(msg))
        self.update_log.emit(str(msg))


class ParseThread(QThread):
    update_log = pyqtSignal(str)

    def run(self):
        asyncio.run(self.check())

    async def check(self):
        while True:
            if config['clip_check']:
                await parse_pic(self.printLog)
            time.sleep(config['sleep_time'])

    def printLog(self, msg):
        print(str(msg))
        self.update_log.emit(str(msg))


async def parse_pic(printLog):
    global bh_info

    if config['account_login']:

        im = ImageGrab.grabclipboard()
        # print('getting img...')
        # print(config)
        if isinstance(im, Image.Image):
            printLog('识别到图片,开始检测是否为崩坏3登陆码')
            result = decode(im)
            if len(result) >= 1:
                url = result[0].data.decode('utf-8')
                param = url.split('?')[1]
                params = param.split('&')
                ticket = ''
                for element in params:
                    if element.split('=')[0] == 'ticket':
                        ticket = element.split('=')[1]
                        break
                # print(ticket)
                if config['account_login']:
                    printLog('二维码识别成功，开始请求崩坏3服务器完成扫码')
                    import mihoyosdk
                    await mihoyosdk.scanCheck(printLog, bh_info, ticket)
                else:
                    if config['socket_send']:
                        printLog('开始发送广播')
                        send(printLog, url)
                    # printLog('local login mode')

                time.sleep(1)
                clear_clipboard()
            else:
                printLog('非登陆码,跳过')
    else:
        printLog('当前未登录或登陆中，跳过当前图片处理')


def clear_clipboard():
    from ctypes import windll
    if windll.user32.OpenClipboard(None):  # 打开剪切板
        windll.user32.EmptyClipboard()  # 清空剪切板
        windll.user32.CloseClipboard()  # 关闭剪切板


def send(printLog, url):
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                printLog('开始在网卡 ' + k + ' 发送广播')
                send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                try:
                    local_ip = socket.gethostbyname(item[1])
                    send_sock.bind((local_ip, m_cast_group_port))
                    message = "{\"scanner_data\":{\"url\":\"%s\",\"t\":%d}}" % (url, int(time.time()))
                    send_sock.sendto(message.encode(), (m_cast_group_ip, m_cast_group_port))
                    printLog('在网卡 ' + k + ' 发送广播成功')
                except OSError:
                    printLog('在网卡 ' + k + ' 发送广播失败')


def login_accept():
    ui.backendLogin = LoginThread()
    ui.backendLogin.update_log.connect(window.printLog)
    ui.backendLogin.start()


def deal_password(string):
    global config
    config['password'] = string


def deal_account(string):
    global config
    config['account'] = string

def printLog(msg):
    ui.logText.append(msg)


class SelfMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SelfMainWindow, self).__init__(parent)

    @staticmethod
    def printLog(msg):
        print(msg)
        # ui.logText.append(msg)

    @staticmethod
    def login():
        global config
        if config['account_login']:
            ui.logText.append("账号已登录")
            ui.loginBiliBtn.setText("账号已登录")
            # ui.loginBiliBtn.setDisabled(True)
        ui.logText.append("开始登陆账号")
        # self.loginBiliBtn.setText("test")
        # asyncio.run(main())
        ui.loginBiliBtn.setText("登陆中")
        ui.loginBiliBtn.setDisabled(True)

        dialog = loginDialog.LoginDialog(window)
        dialog.account.textChanged.connect(deal_account)
        dialog.password.textChanged.connect(deal_password)
        dialog.show()
        dialog.accepted.connect(login_accept)

    # ui.autoLoginCheck.clicked.connect()

    # asyncio.run(main())

    @staticmethod
    def qrCodeSwitch(boolean):
        if boolean:
            ui.clipCheck.setText("当前状态:启用")
        else:
            ui.clipCheck.setText("当前状态:关闭")
        config['clip_check'] = boolean
        write_conf(config)

    @staticmethod
    def broadcastSwitch(boolean):
        if boolean:
            ui.broadcastCheck.setText("当前状态:启用")
        else:
            ui.broadcastCheck.setText("当前状态:关闭")
        config['socket_send'] = boolean
        write_conf(config)


def on_loaded():
    print(webview.windows[0].load_url)


if __name__ == '__main__':
    init_conf()

    # 预初始化b服验证码
    if not have_runtime():#没有webview2 runtime
        install_runtime()

    app = QApplication(sys.argv)
    window = SelfMainWindow()
    ui = mainWindow.Ui_MainWindow()
    ui.setupUi(window)
    try:
        if config['account'] != '':
            ui.logText.append("配置文件已有账号，尝试登录中...")
            ui.backendLogin = LoginThread()
            ui.backendLogin.update_log.connect(window.printLog)
            ui.backendLogin.start()
        if config['clip_check']:
            ui.clipCheck.setText("当前状态:启用")
        else:
            ui.clipCheck.setText("当前状态:关闭")
        ui.clipCheck.setChecked(config['clip_check'])
        if config['socket_send']:
            ui.broadcastCheck.setText("当前状态:启用")
        else:
            ui.broadcastCheck.setText("当前状态:关闭")
        ui.broadcastCheck.setChecked(config['socket_send'])
    except KeyError:
        write_conf(config)
        print("配置文件异常，重置并跳过登录")
    ui.backendClipCheck = ParseThread()
    ui.backendClipCheck.update_log.connect(window.printLog)
    ui.backendClipCheck.start()


    # window = webview.create_window('Hello world', 'https://github.com/cssxsh/mirai-hibernate-plugin/issues/12', frameless=True)
    
    # webview.start()
    sys.exit(app.exec_())
    window.events.loaded += on_loaded


async def sendPost(target, data, noReturn = False):
    session = requests.Session()
    session.trust_env = False
    res = session.post(url=target, data=data)
    if noReturn:
        return
    if res is None:
        printLog(res)
        printLog("请求错误，正在重试...")
        return sendPost(target,data,noReturn)
    return res.json()

async def sendGet(target):
    session = requests.Session()
    session.trust_env = False
    res = session.get(url=target)    
    if res is None:
        printLog(res)
        printLog("请求错误，正在重试...")
        return sendGet(target)
    return res.json()

async def sendBiliPost(url, data):
    header = {
        "User-Agent": "Mozilla/5.0 BSGameSDK",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "line1-sdk-center-login-sh.biligame.net"
    }    
    session = requests.Session()
    session.trust_env = False
    try:
        res = session.post(url=url, data=data, headers=header)
    except:
        
        printLog("请求错误，3s后重试...")
        time.sleep(3)
        return sendBiliPost(url,data)
    if res is None:
        printLog(res)
        printLog("请求错误，正在重试...")
        return sendBiliPost(url,data)
    # print(res)
    return res.json()


def make_captch(gt,challenge,gt_user):
    capurl=f"https://game.bilibili.com/sdk/geetest/?captcha_type=1&challenge={challenge}&gt={gt}&userid={gt_user}&gs=1"

    root=Tk()
    root.title('pywebview for tkinter test')
    root.geometry('1200x600+5+5')

    frame=WebView2(root,500,500)
    frame.pack(side='left')
    frame.load_url(capurl)
    # webview.windows[0].load_url(capurl)

    

# package cmd --> pyinstaller --clean -Fw main.py --collect-all pyzbar ### 请用32位环境打包 ###

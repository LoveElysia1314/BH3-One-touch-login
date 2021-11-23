import psutil
import sys
import socket
import time
import os.path
import bsgamesdk
import mihoyosdk
import asyncio
import json
from pyzbar.pyzbar import decode
from PIL import Image, ImageGrab

# 组播组IP和端口
mcast_group_ip = '239.0.1.255'
mcast_group_port = 12585
bhinfo = {}
cfg = {}
async def parse_pic(cfg,bhinfo=None):
    im = ImageGrab.grabclipboard()
    # print('getting img...')
    # print(cfg)
    if isinstance(im, Image.Image):
        print('found image.')
        result = decode(im)
        if (len(result) >= 1):
            url = result[0].data.decode('utf-8')
            param = url.split('?')[1]
            params = param.split('&')
            ticket = ''
            for element in params:
                if element.split('=')[0] == 'ticket':
                    ticket = element.split('=')[1]
                    break
            # print(ticket)
            if bhinfo == None:
                print('boardcast mode')
                send(url)
            else:
                print('local login mode')
                await mihoyosdk.scanCheck(bhinfo,ticket)
            time.sleep(1)
            clear_clipboard()
        else:
            print('no url... skip')
def write_conf(old=None):
    cfge = json.loads('{"account":"","password":"","sleep_time":3}')
    if old != None:
       for key in cfge:
           try:
               cfge[key] = old[key]
           except KeyError:
               continue 
    with open('./config.json', 'w') as f:
        output = json.dumps(cfge, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(output)
        
async def main():
    conf_loop = True
    while conf_loop:
        if os.path.isfile('./config.json') == False:
            write_conf()
        with open('./config.json') as fp:
            cfg = json.loads(fp.read())
            try:
                if cfg['ver'] != 2:
                    print('配置文件已更新，请注意重新修改文件')
                    write_conf(cfg)
                    continue
            except KeyError:
                print('配置文件已更新，请注意重新修改文件')
                write_conf(cfg)
                continue
        conf_loop = False
    if cfg['account'] != '':
        print('found account, try to login')
        bsinfo = await bsgamesdk.login(cfg['account'], cfg['password'])
        print(bsinfo['uid'])
        print(bsinfo['access_key'])
        bhinfo = await mihoyosdk.verify(bsinfo['uid'], bsinfo['access_key'])
        if bhinfo['retcode'] != 0:
            print('login failed.')
            print(bhinfo)
            return
        print('getting img...')
        while True:
            await parse_pic(cfg,bhinfo)
            time.sleep(cfg['sleep_time'])
    else:
        print('getting img...')
        while True:
            await parse_pic(cfg)
            time.sleep(cfg['sleep_time'])
def clear_clipboard():
    from ctypes import windll
    if windll.user32.OpenClipboard(None):  # 打开剪切板
        windll.user32.EmptyClipboard()  # 清空剪切板
        windll.user32.CloseClipboard()  # 关闭剪切板
def send(url):
    info = psutil.net_if_addrs()
    for k,v in info.items():
        for item in v:
            if item[0] == 2 and not item[1]=='127.0.0.1':
                print('send msg on'+k)
                send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                try:
                    local_ip = socket.gethostbyname(item[1])
                    send_sock.bind((local_ip, mcast_group_port))
                    message = "{\"scanner_data\":{\"url\":\"%s\",\"t\":%d}}" % (url,int(time.time()))
                    print(message)
                    send_sock.sendto(message.encode(), (mcast_group_ip, mcast_group_port))
                    print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: message send finish')
                except OSError:
                    print('send msg on '+k+' failed.')

if __name__ == '__main__':
    asyncio.run(main())


## package cmd --> pyinstaller --clean -F main.py --collect-all pyzbar
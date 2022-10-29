import hashlib
import hmac
import json
import time
from main import sendGet, sendPost



url = 'https://api-sdk.mihoyo.com/bh3_cn/combo/granter/login/v2/login'
verifyBody = '{"device":"0000000000000000","app_id":"1","channel_id":"14","data":{},"sign":""}'
verifyData = '{"uid":1,"access_key":"590"}'
scanResultR = '{"device":"0000000000000000","app_id":1,"ts":1637593776681,"ticket":"","payload":{},"sign":""}'
scanPayloadR = '{"raw":"","proto":"Combo","ext":""}'
scanRawR = '{"heartbeat":false,"open_id":"","device_id":"0000000000000000","app_id":"1","channel_id":"14","combo_token":"","asterisk_name":"崩坏3桌面扫码器用户","combo_id":"","account_type":"2"}'
scanExtR = '{"data":{}}'
scanDataR = '{"accountType":"2","accountID":"","accountToken":"","dispatch":{}}'
scanCheckR = '{"app_id":"1","device":"0000000000000000","ticket":"abab","ts":1637593776066,"sign":"abab"}'
    
local_dispatch = json.loads('{}')
local_bh_ver = '5.8.0'
has_dispatch = False
has_bh_ver = False

def bh3Sign(data):
    # print("data:"+data)
    key = '0ebc517adb1b62c6b408df153331f9aa'
    sign = hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
    # print("sign:"+sign)
    return sign


def makeSign(data):
    sign = ""
    data2 = ""
    for key in sorted(data):
        if key == 'sign':
            continue
        data2 += f"{key}={data[key]}&"
    data2 = data2.rstrip('&').replace(' ', '')
    # print(data2)
    sign = bh3Sign(data2)
    data['sign'] = sign
    return data


async def getBHVer(cache_bh_ver=None):
    global has_bh_ver,local_bh_ver

    if has_bh_ver:
        return local_bh_ver
    feedback = await sendGet('https://api.scanner.hellocraft.xyz/update',cache_bh_ver)
    # printLog('云端版本号')
    local_bh_ver = feedback['bh_ver']
    has_bh_ver = True
    return local_bh_ver


async def getOAServer():   
    global has_dispatch,local_dispatch

    if has_dispatch:
        return local_dispatch

    bh_ver = await getBHVer()
    timestamp = int(time.time())
    oa_main_url = 'https://global2.bh3.com/query_dispatch?'
    param = f'version={bh_ver}_gf_android_bilibili&t={timestamp}'
    feedback = await sendPost(oa_main_url + param, '')
    # print(feedback)
    timestamp = int(time.time())
    param = f'?version={bh_ver}_gf_android_bilibili&t={timestamp}'
    dispatch_url = feedback['region_list'][0]['dispatch_url'] + param
    # print(dispatch_url)
    dispatch = await sendPost(dispatch_url + param, '')

    has_dispatch = True

    local_dispatch = dispatch
    # print(dispatch)
    return dispatch


async def scanCheck(printLog, bh_info, ticket):
    check = json.loads(scanCheckR)
    check['ticket'] = ticket
    check['ts'] = int(time.time())
    check = makeSign(check)
    post_body = json.dumps(check).replace(' ', '')
    feedback = await sendPost('https://api-sdk.mihoyo.com/bh3_cn/combo/panda/qrcode/scan', post_body)
    if feedback['retcode'] != 0:
        printLog('请求错误！可能是二维码已过期')
        printLog(feedback)
        return
    else:
        await scanConfirm(printLog, bh_info, ticket)


async def scanConfirm(printLog, bhinfoR, ticket):
    bhinfo = bhinfoR['data']
    # print(bhinfo)
    scan_result = json.loads(scanResultR)
    scan_data = json.loads(scanDataR)
    scan_data['dispatch'] = await getOAServer()
    scan_data['accountID'] = bhinfo['open_id']
    scan_data['accountToken'] = bhinfo['combo_token']
    scan_ext = json.loads(scanExtR)
    scan_ext['data'] = scan_data
    scan_raw = json.loads(scanRawR)
    scan_raw['open_id'] = bhinfo['open_id']
    scan_raw['combo_id'] = bhinfo['combo_id']
    scan_raw['combo_token'] = bhinfo['combo_token']
    scan_payload = json.loads(scanPayloadR)
    scan_payload['raw'] = json.dumps(scan_raw)
    scan_payload['ext'] = json.dumps(scan_ext)
    scan_result['payload'] = scan_payload
    scan_result['ts'] = int(time.time())
    scan_result['ticket'] = ticket
    scan_result = makeSign(scan_result)
    post_body = json.dumps(scan_result).replace(' ', '')
    # print(post_body)
    feedback = await sendPost('https://api-sdk.mihoyo.com/bh3_cn/combo/panda/qrcode/confirm', post_body)
    if feedback['retcode'] == 0:
        printLog('扫码成功！')
    else:
        printLog('扫码失败！')
        printLog(feedback)


async def verify(uid, access_key):
    print(f'verify with uid={uid}')
    data = json.loads(verifyData)
    data['uid'] = uid
    data['access_key'] = access_key
    body = json.loads(verifyBody)
    body['data'] = json.dumps(data)
    # print(json.dumps(body))
    body = makeSign(body)
    # print(json.dumps(body))
    feedback = await sendPost(url, json.dumps(body).replace(' ', ''))
    return feedback

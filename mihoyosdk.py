from typing import Coroutine
import json
import time
import hashlib
import rsacr
import hmac
import base64
from requests import post
import asyncio

url = 'https://api-sdk.mihoyo.com/bh3_cn/combo/granter/login/v2/login'
verifyBody='{"device":"0000000000000000","app_id":"1","channel_id":"14","data":{},"sign":""}'
verifyData='{"uid":1,"access_key":"590"}'
scanResultR = '{"device":"0000000000000000","app_id":1,"ts":1637593776681,"ticket":"","payload":{},"sign":""}'
scanPayloadR = '{"raw":"","proto":"Combo","ext":""}'
scanRawR = '{"heartbeat":false,"open_id":"","device_id":"0000000000000000","app_id":"1","channel_id":"14","combo_token":"","asterisk_name":"崩坏3外置扫码器用户","combo_id":"","account_type":"2"}'
scanExtR = '{"data":{}}'
scanDataR = '{"accountType":"2","accountID":"","accountToken":"","dispatch":{}}'
scanCheckR = '{"app_id":"1","device":"0000000000000000","ticket":"abab","ts":1637593776066,"sign":"abab"}'

async def sendPost(url,data):
    res = post(url=url,data=data)
    #print(res)
    return res.json()
    
def bh3Sign(data):
    print("data:"+data)
    key = '0ebc517adb1b62c6b408df153331f9aa'
    sign = hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
    print("sign:"+sign)
    return sign

def setsign(data):
    sign=""
    data2=""
    for key in sorted(data):
        if key == 'sign':
            continue
        data2+=f"{key}={data[key]}&"
    data2=data2.rstrip('&').replace(' ','')
    #print(data2)
    sign=bh3Sign(data2)
    data['sign'] = sign
    return data

async def getOAServer():
    bh_ver = '5.3.0'
    timestamp = int(time.time())
    oaMainUrl = 'https://global2.bh3.com/query_dispatch?'
    param = f'version={bh_ver}_gf_android_bilibili&t={timestamp}'
    feedback = await sendPost(oaMainUrl+param,'')
    print(feedback)
    timestamp = int(time.time())
    param = f'?version={bh_ver}_gf_android_bilibili&t={timestamp}'
    dispatchUrl = feedback['region_list'][0]['dispatch_url']+param
    print(dispatchUrl)
    dispatch = await sendPost(dispatchUrl+param,'')
    print(dispatch)
    return dispatch

async def scanCheck(bhinfo,ticket):
    check = json.loads(scanCheckR)
    check['ticket'] = ticket
    check['ts'] = int(time.time())
    check = setsign(check)
    postBody = json.dumps(check).replace(' ','')
    feedback = await sendPost('https://api-sdk.mihoyo.com/bh3_cn/combo/panda/qrcode/scan', postBody)
    if feedback['retcode'] != 0:
        print('二维码已过期')
        return
    await scanConfirm(bhinfo,ticket)
    
async def scanConfirm(bhinfoR,ticket):
    bhinfo = bhinfoR['data']
    print(bhinfo)
    scanResult = json.loads(scanResultR)
    scanData = json.loads(scanDataR)
    scanData['dispatch'] = await getOAServer()
    scanData['accountID'] = bhinfo['open_id']
    scanData['accountToken'] = bhinfo['combo_token']
    scanExt = json.loads(scanExtR)
    scanExt['data'] = scanData
    scanRaw = json.loads(scanRawR)
    scanRaw['open_id'] = bhinfo['open_id']
    scanRaw['combo_id'] = bhinfo['combo_id']
    scanRaw['combo_token'] = bhinfo['combo_token']
    scanPayload = json.loads(scanPayloadR)
    scanPayload['raw'] = json.dumps(scanRaw)
    scanPayload['ext'] =json.dumps(scanExt)
    scanResult['payload'] = scanPayload
    scanResult['ts'] = int(time.time())
    scanResult['ticket'] = ticket
    scanResult = setsign(scanResult)
    postBody = json.dumps(scanResult).replace(' ','')
    print(postBody)
    feedback = await sendPost('https://api-sdk.mihoyo.com/bh3_cn/combo/panda/qrcode/confirm', postBody)
    print(feedback)
    
async def verify(uid,access_key):
    print(f'verfiy with uid={uid}, access_key = {access_key}')
    data = json.loads(verifyData)
    data['uid'] = uid
    data['access_key'] = access_key
    body = json.loads(verifyBody)
    body['data'] = json.dumps(data)
    #print(json.dumps(body))
    body = setsign(body)
    #print(json.dumps(body))
    feedback = await sendPost(url, json.dumps(body).replace(' ',''))
    return feedback
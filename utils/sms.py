#coding=utf8
import os
import traceback
import requests
import urllib
import json

def send_register_msg_253(tel, regcode):
    url = os.environ.get('DX_253_URL', 'http://smssh1.253.com/msg/send/json')
    data = {    
        "account" : os.environ.get('DX_253_ACCOUNT', ''), #//用户在253云通讯平台上申请的API账号    
        "password" : os.environ.get('DX_253_PASSWORD', ''), #//用户在253云通讯平台上申请的API账号对应的API密钥    
        "msg" : u"【%s】您的注册验证码是：%s"%(os.environ.get('DX_253_NAME', ''), regcode), #//短信内容。长度不能超过536个字符    
        "phone" : tel, #//手机号码。多个手机号码使用英文逗号分隔    
    }

    try:
        r = requests.post(url, json=data, headers={"Content-type": "application/json"})
        ret = r.json()
        if ret['code'] == '0':
            return True, ''
        err = 'code: %s  msg: %s'%(ret['code'], ret['errorMsg'])
    except:
        err = traceback.format_exc()

    return False, err

if __name__ == '__main__':
    os.environ['DX_253_ACCOUNT'] = ''
    os.environ['DX_253_PASSWORD'] = ''
    ok, msg = send_register_msg_253('17621761471', '9527')
    print (msg)
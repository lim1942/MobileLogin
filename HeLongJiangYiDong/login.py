import os
import time
import base64
import random
import hashlib
import requests
from PIL import Image
from io import  BytesIO

from encrypt import des_encode
requests.packages.urllib3.disable_warnings()

PHONE = input("input your phone ....")
PWD = input("input your service password ....")
encryptPwd = None
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json; charset=utf-8",
    "Referer": "http://hl.10086.cn/apps/login/unifylogin.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
}


def get_info(serviceName, channelId="12034"):
    tim = str(time.time())
    l_tim, r_tim = tim.split('.')
    r_tim = r_tim.ljust(3, '0')
    dd = l_tim + r_tim[:4]
    cc = hashlib.md5((dd + 'CM_201606').encode("utf8")).hexdigest()
    en_str = base64.b64encode(cc.encode("utf8")).decode("utf-8")
    ymd_hms_m = time.strftime("%Y%m%d%H%M%S", time.localtime(int(l_tim))) + r_tim[:4]
    ran = str(random.randint(100, 999)) + str(random.randint(100, 999))
    info = """{"serviceName":"%s","header":{"version":"1.0","timestamp":%s,"digest":"%s","conversationId":"%s"},"data":{"channelId":"%s"}}""" % (
        serviceName, dd, en_str, ymd_hms_m + ran, channelId)

    return info


def login():
    global encryptPwd
    sess = requests.session()

    # 1 get cookie
    url = "http://hl.10086.cn/apps/login/unifylogin.html"
    sess.get(url,headers=headers,verify=False)

    # 2 check tel
    url = f"http://hl.10086.cn/rest/common/validate/validateHLPhone/?phone_no={PHONE}"
    resp = sess.get(url,headers=headers,verify=False)
    if not resp.text.__contains__("黑龙江移动号码校验成功"):
        print("手机号码校验错误")
        os._exit(0)

    # 3 get captcha
    url = f"http://hl.10086.cn/rest/authImg?type=0&rand={random.random()}"
    resp = sess.get(url, headers=headers, verify=False)
    imageBuffer = BytesIO()
    imageBuffer.write(resp.content)
    im = Image.open(imageBuffer)
    im.show()
    captchaValue = input("Please input captcha ... ")

    # 4 evaluate captcha
    url = f"http://hl.10086.cn/rest/common/vali/valiImage?imgCode={captchaValue}"
    resp = sess.get(url,headers=headers,verify=False)
    if not resp.text.__contains__("验证码输入正确"):
        print("对不起，你输入的图片验证码错误，请重新输入！")
        os._exit(0)

    # 5 get exponent & modulus
    url = 'http://hl.10086.cn/rest/rsa/aes-key'
    resp = sess.get(url,headers=headers,verify=False)
    json_data = resp.json()
    exponent = json_data['data']['exponent']
    modulus = json_data['data']['modulus']
    encryptPwd = des_encode(PWD,modulus,exponent)

    # 6 do login
    url = "http://hl.10086.cn/rest/login/sso/doUnifyLogin/"
    data = {
        "userName": PHONE,
        "passWord": encryptPwd,
        "pwdType": "01",
        "clientIP": captchaValue
    }
    resp = sess.post(url,headers=headers,json=data,verify=False)
    if not resp.text.__contains__("success"):
        print("100000")  #密码输入不符合规则！
        print("2036")    #您的账户名与密码不匹配，请重新输入
        print("20346")   #账户被锁定
        os._exit(0)
    artifact = resp.json()["data"]

    # 7 login callback
    url = f"http://www.hl.10086.cn/rest/login/unified/callBack/?artifact={artifact}&backUrl="
    sess.get(url,headers=headers,verify=False)

    # 8 login action
    url = "https://login.10086.cn/SSOCheck.action?channelID=12034&backUrl=http%3A%2F%2Fhl.10086.cn%2Fapps%2Flogin%2Fmy.html"
    sess.get(url, headers=headers, verify=False)

    # 9 send call-sms code
    url = "http://hl.10086.cn/rest/sms/sendSmsMsg"
    data = {
        "func_code": "000004",
        "sms_type": "2",
        "phone_no": "",
        "sms_params": ""
    }
    sess.post(url, headers=headers, json=data, verify=False)  # 尊敬的用户,短信码发送成功
    sess.post(url, headers=headers, json=data, verify=False)  # 尊敬的用户,短信码发送成功
    smsCode = input("please input sms code ...")

    # 10 evaluate call-sms code
    url = f"http://hl.10086.cn/rest/sms/checkSmsCode?func_code=000004&sms_type=2&phone_no=&sms_code={smsCode}"
    sess.get(url, headers=headers, verify=False)  # 随机短信验证码输入正确  随机短信验证码输入错误

    # 11 check login state
    url = "http://www1.10086.cn/web-Center/authCenter/assertionQuery.do"
    data = {"requestJson":get_info("if008_query_user_assertion")}
    resp = sess.post(url,data=data,headers=headers,verify=False)
    print(resp.text)


    print(sess.cookies.get_dict())
    print("======================")
    print("======================")
    print("======================")
    print("======================")
    return sess.cookies.get_dict()



def crawl():
    cookies = login()
    sess = requests.session()

    # 个人信息
    url = "http://hl.10086.cn/rest/session/custInfo"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 个人信息2
    url = "http://hl.10086.cn/rest/busi/optional-pkg-change/qryUserInfo"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 品牌信息
    url = "http://hl.10086.cn/rest/qry/custinfoquery/qryBrandName"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 积分信息
    url = "http://hl.10086.cn/rest/qry/pointquery/qryCurScoreDet"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 余额信息
    url = "http://hl.10086.cn/rest/qry/balancequery/index"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 星级查询
    url = "http://hl.10086.cn/rest/qry/custstarquery/index"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 缴费查询
    url = "http://hl.10086.cn/rest/qry/payhisquery/index?beginDate=201904&endDate=201904"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 账单查询
    url = "http://hl.10086.cn/rest/qry/realtimefeequery/queryBillDetail" #当月账单
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)
    url = "http://hl.10086.cn/rest/qry/billquery/qryBillHome?user_seq=000003&yearMonth=201903"
    resp = sess.get(url,headers=headers,verify=False,cookies=cookies)
    print(resp.text)

    # 语音详单
    url = f"http://hl.10086.cn/rest/qry/billdetailquery/channelQuery?select_type=72&time_string=201904&xuser_word={encryptPwd}&recordPass="
    resp = sess.get(url, headers=headers, verify=False, cookies=cookies)
    print(resp.text)

    # 短信详单
    url = f"http://hl.10086.cn/rest/qry/billdetailquery/channelQuery?select_type=74&time_string=201904&xuser_word={encryptPwd}&recordPass="
    resp = sess.get(url, headers=headers, verify=False, cookies=cookies)
    print(resp.text)


    # # send info code
    # # 两次短信时间必须间隔一分钟，第二次输错会影响第一次的输入
    # url = "http://hl.10086.cn/rest/sms/sendSmsMsg"
    # data = {
    #     "func_code": "000015",
    #     "sms_type": "2",
    #     "phone_no": "",
    #     "sms_params": ""
    # }
    # sess.post(url, headers=headers, json=data, verify=False,cookies=cookies)  # 尊敬的用户,短信码发送成功
    # smsCode = input("please input sms code ...")
    #
    # # evaluate info code
    # url = f"http://hl.10086.cn/rest/sms/checkSmsCode?func_code=000015&sms_type=2&phone_no=&sms_code={smsCode}"
    # sess.get(url, headers=headers, verify=False,cookies=cookies)  # 随机短信验证码输入正确  随机短信验证码输入错误
    #
    # # 个人信息
    # url = "http://hl.10086.cn/rest/qry/custinfoquery/index"
    # resp = sess.get(url, headers=headers, verify=False, cookies=cookies)
    # print(resp.text)


crawl()
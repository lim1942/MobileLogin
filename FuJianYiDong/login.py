import os
import re
import execjs
import random
import  requests
from io import BytesIO
from PIL import Image
requests.packages.urllib3.disable_warnings()


PHONE = input("input your phone ....")
PASSWORD = input("input your service password ....")

SAMLart = None
SESS = requests.session()
HEADERS = {
"Connection":"keep-alive",
"Cache-Control":"max-age=0",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWeb"
             "Kit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image"
         "/apng,*/*;q=0.8,application/signed-exchange;v=b3",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"zh-CN,zh;q=0.9",
}



def encrypt(source):
    with open('encrypt.js', encoding='utf-8') as f:
        js = f.read()
    ctx = execjs.compile(js)
    target = ctx.call("enString",source)
    return target


def login():

    global SAMLart

    # 1 index page
    url = "https://fj.ac.10086.cn/login"
    resp = SESS.get(url, headers=HEADERS, verify=False)
    SPID = re.search(r'd="spid" value="(.*?)"',resp.text).group(1)

    # 2 get captcha
    url = "https://fj.ac.10086.cn/common/image.jsp"
    resp = SESS.get(url,headers=HEADERS,verify=False)
    imgBuffer = BytesIO()
    imgBuffer.write(resp.content)
    captchaImg = Image.open(imgBuffer)
    captchaImg.show()
    captchaValue = input("please input captcha value ... ")

    # 3 do login
    url = "https://fj.ac.10086.cn/Login"
    data = {
    "type": "B",
    "backurl": "https://fj.ac.10086.cn//4login/backPage.jsp",
    "errorurl": "https://fj.ac.10086.cn//4login/errorPage.jsp",
    "spid": SPID,
    "RelayState": "type=B;backurl=http%3A%2F%2Fwww.fj.10086.cn%2Fmy%2F;nl=3;"
                  "loginFrom=null",
    "mobileNum": PHONE,
    "servicePassword": encrypt(PASSWORD),
    "smsValidCode": "",
    "validCode": captchaValue,
    "Password-type": "",
    "button": "登录",
    }
    resp = SESS.post(url,data=data,headers=HEADERS,verify=False)
    if resp.text.__contains__("https://login.10086.cn/AddUID.action?TransactionID"):
        pass
    elif resp.text.__contains__("尊敬的用户，您输入的密码错误，请您重新输入！"):
        print("服务密码失败，重新登录 ！！！")
        os._exit(0)
    elif resp.text.__contains__("尊敬的用户，您好！请您输入正确的图形验证码后重试，谢谢！"):
        print("图像验证码错误，重新登录 ！！！")
        os._exit(0)
    contentUrl = re.search(r"replace\('(.*?)'\)",resp.text).group(1)
    SAMLart = re.search(r"SAMLart(?:=|%3D)(.*?)(?:&|%26)",contentUrl).group(1)

    # 4 get content url
    SESS.get(contentUrl,headers=HEADERS,verify=False)

    # 5 get my page
    url = f"http://www.fj.10086.cn/my/?SAMLart={SAMLart}&RelayState=type=B;backurl=" \
        f"http%3A%2F%2Fwww.fj.10086.cn%2Fmy%2F;nl=3;loginFrom=null"
    SESS.get(url, headers=HEADERS, verify=False)

    # 6 login score 1
    url = "https://www.fj.10086.cn/service/user/isLogined.do?type=B&loginFrom=https" \
          "%3A%2F%2Fwww.fj.10086.cn%2Fservice%2Ffj_comm%2Finclude%2FloginFilter.jsp"
    resp = SESS.get(url,headers=HEADERS,verify=False)
    contentUrl = re.search(r"replace\('(.*?)'\)",resp.text).group(1)

    # 7 login score 2
    resp = SESS.get(contentUrl, headers=HEADERS, verify=False)
    contentUrl = re.search(r"replace\('(.*?)'\)", resp.text).group(1)

    # 8 login score 3
    SESS.get(contentUrl, headers=HEADERS, verify=False)

    # 9 login userInfo index 1
    url = "https://www.fj.10086.cn/my/user/getUserInfo.do"
    SESS.get(url, headers=HEADERS, verify=False)

    # 10 login userInfo index 2
    url = "https://www.fj.10086.cn/my/index.jsp?id_type=YANZHENGMA"
    SESS.get(url, headers=HEADERS, verify=False)

    # 11 login userInfo send captcha
    url = "https://fj.ac.10086.cn/common/image.jsp"
    resp = SESS.get(url, headers=HEADERS, verify=False)
    imgBuffer = BytesIO()
    imgBuffer.write(resp.content)
    captchaImg = Image.open(imgBuffer)
    captchaImg.show()
    captchaValue = input("please input captcha value ... ")

    # 12 login userInfo auth captcha and send smsCode
    url = f"https://fj.ac.10086.cn/SMSCodeSend?spid={SPID}&mobileNum={PHONE}&" \
        f"validCode={captchaValue}&errorurl=http://www.fj.10086.cn/my/login/send4.jsp"
    resp = SESS.get(url, headers=HEADERS, verify=False)
    if resp.text.__contains__('"错误代码："'):
        pass
    elif resp.text.__contains__("错误代码：尊敬的用户，您好！请您输入正确的图形验证码后重试，谢谢！"):
        print("图像验证码错误，发送短信失败 ！！！")
        os._exit(0)
    smsCode = input("please input sms code ... ")

    # 13 login userInfo login 1
    url = "https://fj.ac.10086.cn/Login"
    data = {
    "s02": "false",
    "Password": "",
    "Password-type": "",
    "spid": SPID,
    "validCode": captchaValue,
    "servicePassword": "",
    "n1": "1",
    "sso": "0",
    "RelayState": "1",
    "ocs_url": "",
    "sp_id": "",
    "do_login_type": "",
    "isValidateCode": "1",
    "type": "A",
    "smscode": smsCode,
    "mobileNum": PHONE,
    "agentcode": "",
    "backurl": "https://www.fj.10086.cn/my/ssoAssert.jsp?typesso=C&CALLBACK_URL"
               "=https://www.fj.10086.cn/my/user/getUserInfo.do",
    "errorurl": "https://www.fj.10086.cn/my/login/send.jsp",
    "smsValidCode": smsCode,
    "validCodes": captchaValue,
    "smscode1": smsCode,
    }
    resp = SESS.post(url, data=data, headers=HEADERS, verify=False)
    if resp.text.__contains__('https://login.10086.cn/AddUID.action?TransactionID'):
        pass
    elif resp.text.__contains__("错误代码：尊敬的用户，您好！请您输入正确的短信验证码后重试，谢谢！"):
        print("输入的短信验证码错误 ！！！")
        os._exit(0)
    elif resp.text.__contains__("错误代码：尊敬的用户，您好！短信验证码已失效，请您重新获取短信验证码后重试，谢谢！"):
        print("输入的短信验证码错误 ！！！")
        os._exit(0)
    SAMLart = re.search(r'SAMLart" value="(.*?)"', resp.text).group(1)

    # 14 login userInfo login 2
    url = "https://www.fj.10086.cn/my/ssoAssert.jsp"
    data = {
        "typesso": "C",
        "AppSessionId": "NotExist",
        "SAMLart": SAMLart,
        "isEncodePassword": "2",
        "displayPic": "1",
        "RelayState": "1",
        "isEncodeMobile": "1",
        "CALLBACK_URL": "https://www.fj.10086.cn/my/user/getUserInfo.do",
        "displayPics": "mobile_sms_login:0===sendSMS:0===mobile_servicepasswd_login:0",
    }
    SESS.post(url, data=data, headers=HEADERS, verify=False)

    cookies = SESS.cookies.get_dict()
    print(cookies)
    return cookies



def crawl():

    # 1 个人信息 line 3269
    url = f"https://www.fj.10086.cn/my/user/getUserInfo.do?AppSessionId=NotExist&" \
        f"SAMLart={SAMLart}&isEncodePassword=2&displayPic=1&RelayState=1&isEncodeM" \
        f"obile=1&CALLBACK_URL=https://www.fj.10086.cn/my/user/getUserInfo.do&displayPics="
    resp = SESS.get(url,headers=HEADERS,verify=False)
    print(resp.text)

    # 2 积分查询 line 2568
    url = "https://www.fj.10086.cn/service/points/query/queryQqtCent.do"
    resp = SESS.get(url,headers=HEADERS,verify=False)
    print(resp.text)

    # 3 套餐查询  line 3365
    url = "https://www.fj.10086.cn/my/info/queryTaocanMessage1.do"
    resp = SESS.get(url,headers=HEADERS,verify=False)
    print(resp.text)

    # 4 余额查询   line 3349
    url = "https://www.fj.10086.cn/my/fee/query/queryCallFeeSs.do"
    resp = SESS.get(url,headers=HEADERS,verify=False)
    print(resp.text)

    # 5 充值信息  line 13
    url = "https://www.fj.10086.cn/my/fee/query/queryMoneyRecord.do?starttimes=2019" \
          "-03-01&endtimes=2019-04-18"
    resp = SESS.post(url, headers=HEADERS, verify=False)
    print(resp.text)

    # 6 账单查询  line 588
    url = "https://www.fj.10086.cn/my/fee/query/queryServiceFee.do?query_month=201902"
    resp = SESS.get(url,headers=HEADERS,verify=False)
    print(resp.text)

    # 7 语音详单
    url = f"https://www.fj.10086.cn/my/fee/query/queryNewServiceDetail.do?rom=" \
        f"{random.random()}&start_month_xdcs=201904"
    data = {
    "search": "search_ajax",
    "class_id": "2",
    "tel_user_id": "undefined",
    "is_ims_flag": "1",
    }
    resp = SESS.post(url,data=data,headers=HEADERS,verify=False)
    print(resp.text)

    # 8 短信详单
    url = f"https://www.fj.10086.cn/my/fee/query/queryNewServiceDetail.do?rom=" \
        f"{random.random()}&start_month_xdcs=201904"
    data = {
    "search": "search_ajax",
    "class_id": "4",
    "tel_user_id": "undefined",
    "is_ims_flag": "1",
    }
    resp = SESS.post(url,data=data,headers=HEADERS,verify=False)
    print(resp.text)




login()
crawl()


import base64
import hashlib
import requests
import random
from PIL import Image
from Crypto.Cipher import AES
from io import  BytesIO
requests.packages.urllib3.disable_warnings()

HEADERS = {
"Connection":"keep-alive",
"Cache-Control":"max-age=0",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
"Accept":"text/html,application/xhtml+xml,application/xml;"
         "q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
"Referer":"http://login.189.cn/web/login",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"zh-CN,zh;q=0.9",
}
PHONE = input("input your phone ....")
PASSWORD = input("input your service password ....")


def encrypt(text):
    """aes加密"""
    def get_md5_key():
        m = hashlib.md5()
        m.update("login.189.cn".encode("utf-8"))
        return m.hexdigest()
    def add_to_16(text):
        if len(text.encode('utf-8')) % 16:
            add = 16 - (len(text.encode('utf-8')) % 16)
        else:
            add = 0
        text = text + ('\n' * add)
        print(text.encode('utf-8'))
        return text.encode('utf-8')

    key = get_md5_key().encode('utf-8')
    mode = AES.MODE_CBC
    iv = b'1234567812345678'
    text = add_to_16(text)
    cryptos = AES.new(key, mode, iv)
    cipher_text = cryptos.encrypt(text)
    return base64.b64encode(cipher_text)


def login():

    Sess = requests.session()

    # 1 get captcha
    url = f"https://login.189.cn/web/captcha?undefined&source" \
        f"=login&width=100&height=37&{random.random()}"
    r = Sess.get(url,headers=HEADERS,verify=False)
    f = BytesIO()
    f.write(r.content)

    # 2 do login
    im = Image.open(f)
    im.show()
    url = "https://login.189.cn/web/login"
    data = {
        "Account":PHONE,
        "UType":"201",
        "ProvinceID":"12",
        "AreaCode":"",
        "CityNo":"",
        "RandomFlag":"0",
        "Password":encrypt(PASSWORD),
        "Captcha":input("please input captcha ..."),
    }
    HEADERS['Referer'] = "http://login.189.cn/web/login"
    r = Sess.post(url, headers=HEADERS, data=data, verify=False)
    print(r.text)
    # 我的欢go  -- 正常
    # 验证码不正确
    # 密码过于简单[ECS]
    # 您的密码错误！再连续*次输入错误，账号将被锁！

    # 3 do login2 ticket
    url = "http://www.189.cn/login/skip/ecs.do?method=skip&" \
          "platNo=93507&toStUrl=http://service.sh.189.cn/service/self_index"
    Sess.get(url,headers=HEADERS,verify=False)

    # 4 do login3 service account
    url = "https://service.sh.189.cn/service/mobileLogin"
    Sess.get(url,headers=HEADERS,verify=False)

    # 5 send sms code
    url = f"https://service.sh.189.cn/service/service/authority/query/billdetail/sendCode.do?" \
        f"flag=1&devNo={PHONE}&moPingType=LOCAL"
    r = Sess.get(url, headers=HEADERS, verify=False)
    print(r.text)
    # "CODE": "0", -- 正常
    # "CODE": "ME10001"	  -- 发送过于频繁，1分钟后再发

    # 6 evaluate sms code
    sms_code = input("please sms code ... ")
    url = f"https://service.sh.189.cn/service/service/authority/query/billdetail/validate.do?" \
        f"input_code={sms_code}&selDevid={PHONE}&flag=nocw&checkCode=%E9%AA%8C%E8%AF%81%E7%A0%81"
    r = Sess.get(url, headers=HEADERS, verify=False)
    print(r.text)
    # "CODE": "0", -- 正常
    # "CODE": "ME10001",   -- 验证码输入错误


    cookies = Sess.cookies.get_dict()
    return cookies



def crawl():

    cookies = login()
    sess = requests.session()

    # 个人信息
    url = "https://service.sh.189.cn/service/my/basicinfo.do"
    r = sess.post(url,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)

    # 套餐信息
    url = "https://service.sh.189.cn/service/my/deviceinfo.do"
    data = {"devNo":PHONE}
    r = sess.post(url,headers=HEADERS,data=data,verify=False,cookies=cookies)
    print(r.text)

    # 余额查询
    url = "https://service.sh.189.cn/service/balanceQuery/balance"
    data = {"serialNum":PHONE}
    r = sess.post(url,data=data,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)

    # 星级查询
    url = "https://service.sh.189.cn/service/service/authority/query/getUserStar.do"
    r = sess.post(url,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)

    # 积分查询
    url = "https://service.sh.189.cn/service/service/authority/queryInfo/getMyPointsByCrmid.do"
    r = sess.post(url,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)

    # 充值记录
    url = f"https://service.sh.189.cn/service/service/authority/query/rechargePage.do?" \
        f"begin=0&end=10&channel_wt=1&total=on&payment_no={PHONE}&beginDate=" \
        f"2019-04-01&endDate=2019-04-30&channelf=1"
    r = sess.get(url,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)

    # 语音详单
    url = f"https://service.sh.189.cn/service/service/authority/query/billdetailQuery.do?" \
        f"begin=0&end=10&flag=1&devNo={PHONE}&dateType=now&bill_type=SCP&moPingType=" \
        f"LOCAL&startDate=2019-04-01&endDate=2019-04-14"
    r = sess.get(url,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)

    # 短信详单
    url = f"https://service.sh.189.cn/service/service/authority/query/billdetailQuery.do?" \
        f"begin=0&end=10&flag=1&devNo={PHONE}&dateType=now&bill_type=SMSC&moPingType=" \
        f"LOCAL&startDate=2019-04-01&endDate=2019-04-14"
    r = sess.get(url,headers=HEADERS,verify=False,cookies=cookies)
    print(r.text)



crawl()



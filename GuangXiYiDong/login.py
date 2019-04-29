import re
import execjs
import requests
from PIL import Image
from io import  BytesIO
requests.packages.urllib3.disable_warnings()



SESS = requests.session()
PHONE = input("input your phone ....")
PWD = input("input your service password ....")
HEADER = {
"Connection":"keep-alive",
"Cache-Control":"max-age=0",
"Upgrade-Insecure-Requests":"1",
"Content-Type":"application/x-www-form-urlencoded",
"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
'Referer': "http://gx.10086.cn/wodeyidong/mymob/xiangdan.jsp"
}

accId = ""


def encrypt(source):
    with open('encrypt.js', encoding='utf-8') as f:
        js = f.read()
    ctx = execjs.compile(js)
    target = ctx.call("tdes_encrypt",source,"8kd14a-3kdc-85391")
    return target


print(encrypt("001942"))

def login():
    global accId

    # 1 login-page
    url = "https://gx.ac.10086.cn/SSOArtifact?artifact=-1&backUrl=https%3A%2F%2Fgx.ac.10086.cn%2FSSOArtifact%3Fspid%3DD4B0EB12CE6FA73739733C21E49FFAB3007813ED6D51AC65D92FEB5435038891DD901D9B7459D8E2%26RelayState%3Dtype%3DB%3Bbackurl%3Dhttp%253A%252F%252Fwww.gx.10086.cn%252Fwodeyidong%252FindexMyMob.jsp%3Bnl%3D3%3BloginFrom%3Dhttp%3A%2F%2Fservice.gx.10086.cn%2F"
    resp = SESS.get(url,headers=HEADER,verify=False)
    spid = re.search('id="spid" value="(.+?)"',resp.text).group(1)


    # 2 get-captcha
    url = "https://gx.ac.10086.cn/common/image.jsp"
    resp = SESS.get(url,headers=HEADER,verify=False)
    imageBuffer = BytesIO()
    imageBuffer.write(resp.content)
    im = Image.open(imageBuffer)
    im.show()
    captchaValue = input("Please input captcha ... ")


    # 3 login-action
    url = "https://gx.ac.10086.cn/Login"
    data = {
    "type": "B",
    "backurl": "https://gx.ac.10086.cn/4logingx/backPage.jsp",
    "errorurl": "https://gx.ac.10086.cn/4logingx/errorPage.jsp",
    "spid": spid,
    "RelayState": "type=A;backurl=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp;nl=3;loginFrom=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp",
    "isEncrypt": "true",
    "mobileNum": PHONE,
    "servicePassword": encrypt(PWD),
    "smsValidCode": "",
    "validCode": captchaValue,
    "isValidateCode": "0",
    }
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    contentUrl = re.search(r"location.replace\('(.+?)'\)",resp.text).group(1)
    # TransactionID =
    # 尊敬的用户，你输入的验证码错误，请重新输入！
    # 尊敬的用户，您的账户名与密码不匹配，请重新输入！


    # 4 login-content-url
    resp = SESS.get(contentUrl, headers=HEADER, verify=False)
    SAMLart = re.search(r"callAssert\('(.+?)'\)",resp.text).group(1)


    # 5 login-indexMyMob
    url = "http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp"
    data ={
    "SAMLart": SAMLart,
    "RelayState": "type=A;backurl=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp;nl=3;loginFrom=http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp",
    "myaction": "http://www.gx.10086.cn/wodeyidong/indexMyMob.jsp",
    "netaction": "http://www.gx.10086.cn/padhallclient/netclient/customer/businessDealing",
    }
    SESS.post(url, data=data, headers=HEADER, verify=False)


    # 6 login-wodeyidong
    url = "http://gx.10086.cn/wodeyidong/mymob/czjffjl.jsp"
    resp = SESS.get(url, headers=HEADER, verify=False)
    SAMLRequest = re.search(r'name="SAMLRequest" value="([\s\S]+?)"',resp.text).group(1).replace("\n","",10)

    # 7 login-wodeyidong-confirm
    url = "https://gx.ac.10086.cn/POST"
    data = {
    "SAMLRequest":SAMLRequest,
    "RelayState":"type=A;nl=1;backurl=http%3A%2F%2Fgx.10086.cn%2Fwodeyidong%2FindexMyMob.jsp;"
    }
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    SAMLart = re.search(r'name="SAMLart" value="(.+?)"',resp.text).group(1)


    # 8 login-indexMyMob-confirm
    url = "http://gx.10086.cn/wodeyidong/indexMyMob.jsp"
    data = {
    "AppSessionId": "NotExist",
    "SAMLart": SAMLart,
    "tokena": "",
    "isEncodePassword": "1",
    "displayPic": "0",
    "RelayState": "type=A;nl=1;backurl=http%3A%2F%2Fgx.10086.cn%2Fwodeyidong%2FindexMyMob.jsp;",
    "isEncodeMobile": "1",
    "displayPics": "mobile_sms_login:999===sendSMS:999===mobile_servicepasswd_login:0",
    }
    SESS.post(url, data=data, headers=HEADER, verify=False)


    # 9-1 pay-info-index
    url = "http://gx.10086.cn/wodeyidong/mymob/czjffjl.jsp"
    SESS.get(url, headers=HEADER, verify=False)
    # 9-2 pay-info-init
    url = "http://gx.10086.cn/wodeyidong/ecrm/querypayfee/QueryPayFeeAction/initBusi.menu"
    data = {
    "is_first_render": "true",
    "_menuId": "410900003562",
    "_lastCombineChild": "false",
    "_zoneId": "busimain",
    "_buttonId": "",
    }
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    accId = re.search(r'name="accId"[\S\s]+?value="(.+?)"',resp.text).group(1)


    # 10-1 详单查询首页
    url = "http://gx.10086.cn/wodeyidong/mymob/xiangdan.jsp"
    SESS.get(url, headers=HEADER, verify=False)
    # 10-2 详单查询初始化
    url = "http://gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/initBusi.menu"
    data = {
    "is_first_render": "true",
    "_menuId": "410900003558",
    "_lastCombineChild": "false",
    "_zoneId": "busimain",
    "_buttonId": "",
    }
    SESS.post(url, data=data, headers=HEADER, verify=False, allow_redirects=False)
    # 10-3 详单查询发送短信
    url = "http://gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/sendSecondPsw.menu"
    data = {
    "is_first_render": "true",
    "_menuId": "410900003558",
    "_buttonId": "",
    }
    SESS.post(url, data=data, headers=HEADER, verify=False,allow_redirects=False)
    smsCode = input("please input smsCode ... ")
    # 10-4 详单查询验证短信
    url = "http://gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/checkSecondPsw.menu"
    data = {
    "input_random_code": smsCode,
    "input_svr_pass": PWD,
    "cardCustName": "",
    "regNo_v_base64": "",
    "ui_radio_val": "",
    "base_verify_transaction_id": "",
    "UnifyAuthCheck": "",
    "UnifyAuthCheckMust": "",
    "UnifyAuthCheckChoos": "",
    "UnifySmsInput": "",
    "UnifySvrInput": "",
    "UnifyIdentityInput": "",
    "is_first_render": "true",
    "_zoneId": "_sign_errzone",
    "_menuId": "410900003558",
    "_buttonId": "other_sign_btn",
    }
    SESS.post(url, data=data, headers=HEADER, verify=False, allow_redirects=False)
    # 短信验证码错误, 请重新输入!



    cookies = SESS.cookies.get_dict()
    print(cookies)

    return cookies


def crawl():

    # 1 个人信息
    url = "http://www.gx.10086.cn/wodeyidong"
    resp = SESS.post(url, headers=HEADER, verify=False)
    print(resp.text)


    # 2 爬取余额
    url = "http://gx.10086.cn/wodeyidong/public/LoginAction/getUserAccInfo.action"
    resp = SESS.post(url, headers=HEADER, verify=False)
    print(resp.text)

    # 3 充值记录
    url ="http://gx.10086.cn/wodeyidong/ecrm/querypayfee/QueryPayFeeAction/queryHisBusi.menu"
    data = {
    "start_date": "2019-04-01",
    "end_date": "2019-04-23",
    "checkedIndex": "-1",
    "phoneId": PHONE,
    "accId": accId,
    "OperatorNbr": "8001",
    "orgId": "71001001",
    "page_start_date": "2019-04-01",
    "page_end_date": "2019-04-23",
    "queryType": "1",
    "is_first_render": "true",
    "_zoneId": "list-container",
    "_menuId": "410900003562",
    "_buttonId": "query-btn",
    }
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    print(resp.text)

    # 4 通话详单
    url = "http://gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/queryDetailDoPage.menu"
    data = {
    "queryMonth": "2019-04",
    "queryType": "1",
    "detailType": "1",
    "oldPhoneId": "",
    "oldRegId": "",
    "svnsn": "",
    "bankflag": "",
    "start_time": "2019-04-01",
    "end_time": "2019-04-24",
    "iPage": "0",  #翻页参数
    "queryTypeList": "1",
    "queryMonthList": "2019-04",
    "queryDetailTypeList": "3",
    "linkType": "3",
    "iPara": "",
    "is_first_render": "true",
    "_zoneId": "queryResult",
    "_menuId": "410900003558",
    "_buttonId": "",
    }
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    print(resp.text)

    # 5 短信详单
    url = "http://gx.10086.cn/wodeyidong/ecrm/queryDetailInfo/QueryDetailInfoAction/queryDetailDoPage.menu"
    data= {
    "queryMonth": "2019-04",
    "queryType": "1",
    "detailType": "3",
    "oldPhoneId": "",
    "oldRegId": "",
    "svnsn": "",
    "bankflag": "",
    "start_time": "2019-04-01",
    "end_time": "2019-04-25",
    "iPage": "0",   #翻页参数
    "queryTypeList": "1",
    "queryMonthList": "2019-04",
    "queryDetailTypeList": "3",
    "linkType": "3",
    "iPara": "",
    "is_first_render": "true",
    "_zoneId": "queryResult",
    "_menuId": "410900003558",
    "_buttonId": "",
    }
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    print(resp.text)

    # 6-1 账单查询首页
    url = "http://gx.10086.cn/wodeyidong/mymob/zdcx.jsp"
    SESS.get(url, headers=HEADER, verify=False)
    # 6-2 账单查询初始化
    url = "http://gx.10086.cn/wodeyidong/ecrm/querymonthbill/QueryMonthBillAction/initBusi.menu"
    data = {
    "is_first_render": "true",
    "_menuId": "410900003557",
    "_lastCombineChild": "false",
    "_zoneId": "busimain",
    "_buttonId": "",
    }
    SESS.post(url, data=data, headers=HEADER, verify=False,allow_redirects=False)
    data = {
    "queryDetail": "no",
    "isMyMob": "true",
    "month_type_value": "",
    "query_type_value": "0",
    "month_selected_type": "201903",
    "query_type_selected": "0",
    "is_first_render": "true",
    "_zoneId": "month-bill-list-container",
    "_menuId": "410900003557",
    "_buttonId": "queryBtn",
    }
    # 6-3 账单爬取
    url = "http://gx.10086.cn/wodeyidong/ecrm/querymonthbill/QueryMonthBillAction/queryBusi.menu"
    resp = SESS.post(url, data=data, headers=HEADER, verify=False)
    print(resp.text)



login()
crawl()



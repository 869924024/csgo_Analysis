import json
import re

import mysql.connector
import requests

# 数据库连接配置
db_config = {
    "host": "www.douyacai.work",
    "user": "csgo",
    "password": "hjj2819597",
    "database": "csgo",
    "charset": "utf8",
    "pool_name": "csgo_pool",
    "pool_size": 25,
}

# 接码平台token
platform_token = "hjj869924024-3023061510023121399162938"
# 接码平台关键词（短信接码关键件，悠悠有品-悠悠优品，buff-网易）
platform_keyword = "悠悠优品"
# platform_keyword = "网易"


# 悠悠有品post请求头
youpinHeaders = {
    "content-type": "application/json",
    "apptype": "3",
    "version": "5.1.1",
    "authorization": "Bearer ",
    "content-encoding": "gzip",
    "devicesysversion": "13.6",
    "app-version": "5.1.1",
    "api-version": "1.0",
    "accept": "*/*",
    "accept-encoding": "gzip",
    "accept-language": "zh-Hans;q=1.0, en;q=0.9",
    "platform": "ios",
    "devicetoken": "17A06643-B466-45ED-8495-15D11313572B",
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwNTdmMjlkMWZiYmU0MjQ1OWFkYjA2NjMyMTQ2N2YwZCIsIm5hbWVpZCI6IjMzNjM4MjMiLCJJZCI6IjMzNjM4MjMiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzM2MzgyMyIsIk5hbWUiOiJZUDAwMDMzNjM4MjMiLCJuYmYiOjE2ODYwNjA0ODAsImV4cCI6MTY4NjkyNDQ4MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.Pn_xsEidIEa0ZxY1ZvHAGP76_8BVVRoWrcxXKxs2Sm4',
    "user-agent": ""
}

#  接码平台get请求头
platformHeaders = {
    "content-type": "application/json",
    "Host": "ysqdouyin.online",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 "
                  "Accept: */*",
    "Connection": "keep-alive"
}


def youpinGetUserInfo(token):
    """
    Parameters
    token：用户token
    ----------
    Returns
    data["Mobile"]：用户手机号
    -------
    :Author:  huangjiajia
    :Create:  2023/6/15 22:29
    :Describe：token获取用户信息（返回token）
    """

    # 请求头
    headers = {
        "content-type": "application/json",
        "apptype": "3",
        "version": "5.1.1",
        "authorization": "Bearer ",
        "content-encoding": "gzip",
        "devicesysversion": "13.6",
        "app-version": "5.1.1",
        "api-version": "1.0",
        "accept": "*/*",
        "accept-encoding": "gzip",
        "accept-language": "zh-Hans;q=1.0, en;q=0.9",
        "platform": "ios",
        'Authorization': token,
    }

    # 请求URL
    url = "https://api.youpin898.com/api/user/Account/GetUserInfo"

    # 发送POST请求
    response = requests.get(url, headers=headers, timeout=5)

    # 解析响应数据
    response_data = json.loads(response.text)
    data = response_data["Data"]
    print("用户名：", data["NickName"], "Mobile:", data["Mobile"])

    if data["Mobile"]:
        # 连接数据库
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        sqlselect = "select * from youpin_phone_token where token=%s"
        cursor.execute(sqlselect, (token,))
        result = cursor.fetchone()
        if not result[1]:
            sqlupdate = "update youpin_phone_token set mobile=%s where token=%s"
            cursor.execute(sqlupdate, (data["Mobile"], token))
            db.commit()
            cursor.close()
        return data["Mobile"]


def getPlatformMobile():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  huangjiajia
    :Create:  2023/6/15 22:48
    :Describe：获取接码平台手机号
    """

    url = "http://ysqdouyin.online/open-api/getPhone?token=%s&proj=%s" % (platform_token, platform_keyword)
    response = requests.get(url, headers=platformHeaders, timeout=5)
    response_data = json.loads(response.text)
    if not response_data["data"]:
        print("接码平台无手机号")
        return
    return response_data["data"]


def paltformGetMsg(mobile):
    """
    Parameters
    mobile：手机号
    ----------
    Returns
    -------
    :Author:  huangjiajia
    :Create:  2023/6/16 00:45
    :Describe：
    """
    platform_keyword = "悠悠有品"
    url = "http://ysqdouyin.online/open-api/getMsg?token=%s&proj=%s&phoneNo=%s" % (
        platform_token, platform_keyword, mobile)
    print(url)
    response = requests.get(url, headers=platformHeaders, timeout=10)
    response_data = json.loads(response.text)
    if response_data["code"] == 200:
        print("接码平台获取验证码成功mobile:", mobile, "验证码：", response_data["data"])
        if "尚未收到" not in response_data["data"]:
            code_match = re.search(r"\d{6}", response_data["data"])
            if code_match:
                code = code_match.group()
                return code
    return


def youpinSendCode(mobile):
    """
    Parameters
    mobile：手机号
    ----------
    Returns
    -------
    :Author:  huangjiajia
    :Create:  2023/6/16 00:14
    :Describe：悠悠有品发送验证码到手机
    """
    url = "https://api.youpin898.com/api/user/Auth/SendSignInSmsCode"
    data = {
        "Mobile": mobile,
        "SessionId": "a2238f5d-9530-4d67-abc2-b88066f9e580"
    }
    # 发送POST请求
    response = requests.post(url, headers=youpinHeaders, data=json.dumps(data))
    response_data = json.loads(response.text)
    if response_data["Msg"] == "发送成功":
        print("验证码发送成功mobile:", mobile)
        return True
    return False


def youpinLogin(mobile, code):
    """
    Parameters
    mobile：手机号
    code：验证码
    ----------
    Returns
    -------
    :Author:  huangjiajia
    :Create:  2023/6/16 00:28
    :Describe：悠悠有品登陆获取toke
    """
    url = "https://api.youpin898.com/api/user/Auth/SmsSignIn"
    data = {
        "Mobile": mobile,
        "Code": code,
        "SessionId": "a2238f5d-9530-4d67-abc2-b88066f9e580",
        "TenDay": 1
    }

    response = requests.post(url, headers=youpinHeaders, data=json.dumps(data))
    response_data = json.loads(response.text)
    if response_data["Msg"] == "登录成功":
        print("登陆成功token: Bearer", response_data["Data"]["Token"])
        return "Bearer " + response_data["Data"]["Token"]
    return


if __name__ == '__main__':
   getPlatformMobile()

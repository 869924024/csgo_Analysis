# @Time : 2023/6/16 14:47
# @Author : douyacai
# @Version：V 0.1
# @File : youpin_getToken.py
# @desc : 悠悠有品获取token Api
import global_var
import requests
import json


def youpinSendCode(mobile):
    """
    Parameters
    mobile：手机号
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 00:14
    :Describe：悠悠有品发送验证码到手机
    """
    url = "https://api.youpin898.com/api/user/Auth/SendSignInSmsCode"
    data = {
        "Mobile": mobile,
        "SessionId": "a2238f5d-9530-4d67-abc2-b88066f9e580"
    }
    # 发送POST请求
    response = requests.post(url, headers=global_var.youpinHeaders, data=json.dumps(data))
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
    :Author:  douyacai
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

    response = requests.post(url, headers=global_var.youpinHeaders, data=json.dumps(data))
    response_data = json.loads(response.text)
    if response_data["Msg"] == "登录成功":
        print("登陆成功token: Bearer", response_data["Data"]["Token"])
        return "Bearer " + response_data["Data"]["Token"]
    return



def youpinGetUserInfo(token):
    """
    Parameters
    token：用户token
    ----------
    Returns
    data["Mobile"]：用户手机号
    -------
    :Author:  douyacai
    :Create:  2023/6/15 22:29
    :Describe：token获取用户信息（返回token）
    """

    # 每个线程单独token
    global_var.youpinHeaders['authorization'] = token

    # 请求URL
    url = "https://api.youpin898.com/api/user/Account/GetUserInfo"

    # 发送POST请求
    response = requests.get(url, headers=global_var.youpinHeaders, timeout=5)

    # 解析响应数据
    response_data = json.loads(response.text)
    data = response_data["Data"]
    print("用户名：", data["NickName"], "Mobile:", data["Mobile"])
    if data["Mobile"]:
            # 连接数据库
        connection = global_var.get_db_connection()
        cursor = connection.cursor()
        sqlselect = "select * from youpin_phone_token where token=%s"
        cursor.execute(sqlselect, (token,))
        result = cursor.fetchone()
        if not result[1]:
            sqlupdate = "update youpin_phone_token set mobile=%s where token=%s"
            cursor.execute(sqlupdate, (data["Mobile"], token))
            connection.commit()
            cursor.close()
            print("更新手机号成功mobile:", data["Mobile"])
        return data["Mobile"]



if __name__ == '__main__':
    youpinGetUserInfo("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwMzIzZDk3NTcyZjM0N2ZlOTVkMmVkYTdmOTE2YjMyOCIsIm5hbWVpZCI6IjM0MTUwMzgiLCJJZCI6IjM0MTUwMzgiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNTAzOCIsIk5hbWUiOiJZUDAwMDM0MTUwMzgiLCJuYmYiOjE2ODY4MDk3NzAsImV4cCI6MTY4NzY3Mzc3MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.3menpqZTZevReeFMP57QRAYDzf6fvriJ1NxobTVV7wE")
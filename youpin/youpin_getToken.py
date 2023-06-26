# @Time : 2023/6/16 14:47
# @Author : douyacai
# @Version：V 0.1
# @File : youpin_getToken.py
# @desc : 悠悠有品获取token Api
import time

from global_var import global_config
import requests
import json
from otherplatform import platformCode


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
    response = requests.post(url, headers=global_config.youpinHeaders, data=json.dumps(data))
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

    response = requests.post(url, headers=global_config.youpinHeaders, data=json.dumps(data))
    response_data = json.loads(response.text)
    if response_data["Msg"] == "登录成功":
        print("登陆成功token: Bearer", response_data["Data"]["Token"])
        return "Bearer " + response_data["Data"]["Token"]
    return


def youpinGetUserInfo(token, connection):
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
    global_config.youpinHeaders['authorization'] = token

    # 请求URL
    url = "https://api.youpin898.com/api/user/Account/GetUserInfo"

    # 发送POST请求
    response = requests.get(url, headers=global_config.youpinHeaders, timeout=5)

    # 解析响应数据
    response_data = json.loads(response.text)
    # 若response_data存在字段Data则说明token有效
    if "Data" not in response_data:
        print("token失效token:", token)
        deleteToken(token)
        return

    data = response_data["Data"]
    print("用户名：", data["NickName"], "Mobile:", data["Mobile"])
    if data["Mobile"]:
        # 连接数据库
        cursor = connection.cursor()
        sqlselect = "select * from youpin_phone_token where token=%s"
        cursor.execute(sqlselect, (token,))
        result = cursor.fetchone()
        if result and not result[1]:
            sqlupdate = "update youpin_phone_token set mobile=%s where token=%s"
            cursor.execute(sqlupdate, (data["Mobile"], token))
            connection.commit()
            cursor.close()
            print("更新手机号成功mobile:", data["Mobile"])
        return data["Mobile"]


def deleteToken(token):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 18:10
    :Describe：删除过期的token
    """
    connection = global_config.get_db_connection()
    cursor = connection.cursor()
    sqldelete = "delete from youpin_phone_token where token=%s"
    cursor.execute(sqldelete, (token,))
    connection.commit()
    cursor.close()
    print("删除过期token成功token:", token)


def checkDBToken(tokens):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 17:37
    :Describe：批量获取数据库已存在的token并校验是否过期(由于公共类如果使用会发生循环依赖，所以进行修改)
    """
    connection = global_config.get_db_connection()
    print("开始检查数据库所有token是否过期")
    new_tokens = []
    for index in tokens:
        mobile = youpinGetUserInfo(index, connection)
        if not mobile and mobile is None:
            continue
        new_tokens.append(index)
    tokens = new_tokens
    if len(global_config.tokens) <= 40:
        print("数据库token数量不足40个，开始补充token")
        insertTokenToDB(40 - len(global_config.tokens))
    print("检查数据库所有token是否过期结束")
    global_config.close_db_connection(connection)
    return tokens


def insertTokenToDB(loop):
    """
    Parameters
    loop: 循环次数
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/17 14:49
    :Describe：执行集成接码平台和悠悠有品获取token并存入数据库
    """
    for i in range(loop):
        # 步骤1: 接码平台获取手机号
        mobile = platformCode.getPlatformMobile()
        total_time = 5  # 通话时间
        while not mobile:
            if total_time > 60:
                print("接码平台获取失败，检查接码平台是否正常")
                return
            print("未获取到手机号，等待5s后重新获取")
            total_time += 5
            time.sleep(5)
            mobile = platformCode.getPlatformMobile()

        # 步骤2: 悠悠发送验证码
        success = youpinSendCode(mobile)
        if not success:
            print("验证码发送失败，检查接口是否正常")
            return

        # 步骤3: 等待15秒，接码平台获取验证码
        code = None
        wait_time = 15  # 初始等待时间为15秒
        total_time = 15  # 通话时间
        while not code:
            youpinSendCode(mobile)
            time.sleep(wait_time)
            code = platformCode.getPaltformMsg(mobile)
            wait_time = 15  # 下次等待时间为15秒
            total_time += wait_time
            # 若等待时间超过1分钟，重新开始流程
            if total_time > 60:
                break
            print("等待{}秒后尝试获取验证码".format(wait_time))
        if total_time > 60:
            print("等待超时，执行失败，重新开始流程")
            continue
        # 步骤4: 调用悠悠的登陆获取token
        token = youpinLogin(mobile, code)
        if not token:
            print("登陆失败，检查接口是否正常")
            return

        # 步骤5: 将token和mobile存入数据库
        saveTokenToDB(token, mobile)

        # 步骤6: 更新token
        global_config.tokens.append(token)


def saveTokenToDB(token, mobile):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/17 15:09
    :Describe：存入token和mobile到数据库
    """
    connection = global_config.get_db_connection()
    cursor = connection.cursor()
    sqlinsert = "insert into youpin_phone_token(token, mobile) values(%s, %s)"
    cursor.execute(sqlinsert, (token, mobile))
    connection.commit()
    cursor.close()
    print("存入token和mobile到数据库成功token:", token, "mobile:", mobile)
    global_config.close_db_connection(connection)


if __name__ == '__main__':
    checkDBToken(global_config.tokens)

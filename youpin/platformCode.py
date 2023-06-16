import json
import re
import requests
import global_var


# 接码平台token
platform_token = "hjj869924024-3023061510023121399162938"
# 接码平台关键词（短信接码关键件，悠悠有品-悠悠优品，buff-网易）
platform_keyword = "悠悠优品"
# platform_keyword = "网易"


def getPlatformMobile():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/15 22:48
    :Describe：获取接码平台手机号
    """

    url = "http://ysqdouyin.online/open-api/getPhone?token=%s&proj=%s" % (platform_token, platform_keyword)
    response = requests.get(url, headers=global_var.platformHeaders, timeout=5)
    response_data = json.loads(response.text)
    if not response_data["data"]:
        print("接码平台无手机号")
        return
    return response_data["data"]


def getpaltformMsg(mobile):
    """
    Parameters
    mobile：手机号
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 00:45
    :Describe：
    """
    platform_keyword = "悠悠有品"
    url = "http://ysqdouyin.online/open-api/getMsg?token=%s&proj=%s&phoneNo=%s" % (
        platform_token, platform_keyword, mobile)
    print(url)
    response = requests.get(url, headers=global_var.platformHeaders, timeout=10)
    response_data = json.loads(response.text)
    if response_data["code"] == 200:
        print("接码平台获取验证码成功mobile:", mobile, "验证码：", response_data["data"])
        if "尚未收到" not in response_data["data"]:
            code_match = re.search(r"\d{6}", response_data["data"])
            if code_match:
                code = code_match.group()
                return code
    return

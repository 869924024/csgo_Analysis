# @Time : 2023/6/16 14:47
# @Author : douyacai
# @Version：V 0.1
# @File : platformCode.py
# @desc : 接码平台Api

import json
import re
import requests
from global_var import global_config
global_config = global_config()
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

    url = "http://ysqdouyin.online/open-api/getPhone?token=%s&proj=%s" % (global_config.platform_token, global_config.platform_keyword)
    response = requests.get(url, headers=global_config.platformHeaders, timeout=5)
    response_data = json.loads(response.text)
    if not response_data["data"]:
        print("接码平台无手机号")
        return
    return response_data["data"]


def getPaltformMsg(mobile):
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
    url = "http://ysqdouyin.online/open-api/getMsg?token=%s&proj=%s&phoneNo=%s" % (
        global_config.platform_token, global_config.platform_keyword, mobile)
    print(url)
    response = requests.get(url, headers=global_config.platformHeaders, timeout=10)
    response_data = json.loads(response.text)
    if response_data["code"] == 200:
        print("接码平台获取验证码成功mobile:", mobile, "验证码：", response_data["data"])
        if "尚未收到" not in response_data["data"]:
            code_match = re.search(r"\d{6}", response_data["data"])
            if code_match:
                code = code_match.group()
                return code
    return



if __name__ == '__main__':
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 17:33
    :Describe：批量接码操作
    """
    for i in range(10):
        mobile = getPlatformMobile()
        if mobile:
            code = getPaltformMsg(mobile)
            if code:
                print("接码平台获取验证码成功mobile:", mobile, "验证码：", code)
                break
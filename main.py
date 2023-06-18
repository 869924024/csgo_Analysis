# @Time : 2023/6/17 14:36
# @Author : douyacai
# @Version：V 0.1
# @File : main.py
# @desc : 操作在这里执行

from youpin import youpin_template
from youpin import youpin_getToken
import global_var
from otherplatform import *

if __name__ == '__main__':
    # 接码平台获取token插入数据库
     youpin_getToken.insertTokenToDB(10)

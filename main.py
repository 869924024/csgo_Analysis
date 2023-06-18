# @Time : 2023/6/17 14:36
# @Author : douyacai
# @Version：V 0.1
# @File : main.py
# @desc : 操作在这里执行

from youpin import youpin_template
from youpin import youpin_getToken
from global_var import global_config
from otherplatform import *

global_config = global_config()
from youpin.schedul import youpin_commdity_sell

if __name__ == '__main__':
    # 检查数据库tokens
    #youpin_getToken.checkDBToken(global_config.tokens)
    # 接码平台获取token插入数据库
    # youpin_getToken.insertTokenToDB(10)
    # 批量分页获取饰品模版数据，批量爬取饰品数据落库es-在售、短租、长租等
    youpin_commdity_sell.multiThreadCcrawlCommodityDataToTime()

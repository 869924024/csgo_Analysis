# @Time : 2023/6/17 20:38
# @Author : douyacai
# @Version：V 0.1
# @File : log_uils.py
# @desc :
# 当前日期
import datetime
import logging
import os
from global_var import global_config
global_config=global_config()

current_date = datetime.date.today().strftime("%Y-%m-%d")
# 日志文件名
log_filename = os.path.join(global_config.log_config["filename"], f"ElasticSearch_Python_{current_date}.log")
log_directory = os.path.dirname(log_filename)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 配置日志
logging.basicConfig(filename=log_filename, level=logging.ERROR)

def refresh_logging():
    global log_filename

    # 获取当前日期
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # 检查当前日期是否与日志文件名中的日期一致
    if current_date not in log_filename:
        # 更新日志文件名
        log_filename = os.path.join(global_config.log_config["filename"], f"ElasticSearch_insert_{current_date}.log")
        # 配置日志
        logging.basicConfig(filename=log_filename, level=logging.ERROR)

if __name__ == '__main__':
    logging.info("test")
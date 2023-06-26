# @Time : 2023/6/17 20:38
# @Author : douyacai
# @Version：V 0.1
# @File : log_uils.py
# @desc :
import datetime
import logging
import os

# 日志配置
log_config = {
    "filename": "/Users/huangjiajia/project/python/csgo_Analysis/log/",  # 日志输出路径，需要对应修改
    "format": "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
}

current_date = datetime.date.today().strftime("%Y-%m-%d")
log_filename = os.path.join(log_config["filename"], f"ElasticSearch_Python_{current_date}.log")
log_directory = os.path.dirname(log_filename)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 创建根日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建文件处理程序
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.ERROR)
file_handler.setLevel(logging.INFO)
# 创建控制台处理程序
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setLevel(logging.INFO)

# 创建日志格式器
formatter = logging.Formatter(log_config["format"])

# 将格式器添加到处理程序
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理程序添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def refresh_logging():
    global log_filename

    current_date = datetime.date.today().strftime("%Y-%m-%d")

    if current_date not in log_filename:
        print("更新日志文件配置，时间：", current_date)
        log_filename = os.path.join(log_config["filename"], f"ElasticSearch_insert_{current_date}.log")
        log_directory = os.path.dirname(log_filename)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        file_handler.filename = log_filename

if __name__ == '__main__':
    logging.info("测试日志记录")
    logging.error("测试日志记录")
    logging.debug("测试日志记录")
    logging.warning("测试日志记录")

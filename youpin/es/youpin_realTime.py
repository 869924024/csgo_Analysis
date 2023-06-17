# @Time : 2023/6/17 16:02
# @Author : douyacai
# @Version：V 0.1
# @File : youpin_realTime.py
# @desc : 悠悠有品实时爬取落库es
from elasticsearch import Elasticsearch
from global_var import global_config
import uuid
import logging
import datetime
import os

global_config = global_config()



def insert_data_to_es(index_name, data):
    try:
        # 创建Elasticsearch实例
        es = Elasticsearch(
            hosts=[global_config.esHost],
            http_auth=(global_config.username, global_config.password)
        )

        # 生成唯一的document_id
        document_id = str(uuid.uuid4())

        # 插入数据
        es.index(index=index_name, id=document_id, body=data)
        # 日志记录成功信息
        logging.info(
            f"Elastic Search Data inserted successfully. Index: {index_name}, Document ID: {document_id},Data: {data}")
    except Exception as e:

        # 异常处理
        logging.error(f"Elastic Search Failed to insert data. Error: {str(e)}")


data = {
    "minReferencePrice": 35449,
    "Id": 1627,
    "CommodityName": "AK-47 | 二西莫夫 (略有磨损)",
    "CommodityHashName": "AK-47 | Asiimov (Minimal Wear)",
    "GroupHashName": "AK-47 | Asiimov",
    "IconUrl": "https://youpin.img898.com/economy/image/7ed3a58260a511ec86c8dca9049909c3",
    "MinPrice": 3553,
    "LeaseUnitPrice": 0.47,
    "LongLeaseUnitPrice": 0.35,
    "LeaseDeposit": 356,
    "LeasePriceScale": None,
    "OnSaleCount": 2027,
    "OnLeaseCount": 345,
    "TypeName": "步枪",
    "Rarity": "隐秘",
    "Quality": "普通",
    "Exterior": "略有磨损",
    "Timestamp": "1686757564550"
}
index_name = "youpin_commodity_2023.6.23"

if __name__ == '__main__':
    insert_data_to_es(index_name, data)

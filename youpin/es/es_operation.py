# @Time : 2023/6/17 16:02
# @Author : douyacai
# @Version：V 0.1
# @File : es_operation.py
# @desc : 悠悠有品实时爬取落库es
#################
# 本地导入（控制台启动需要）
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
#################
import logging
import warnings
from datetime import datetime

from more_itertools import chunked
from elastic_transport import SecurityWarning
from elasticsearch import Elasticsearch
from urllib3.exceptions import InsecureRequestWarning
from global_var import global_config
import uuid
import log_uils
from elasticsearch.helpers import bulk

# 忽略警告，减少日志，生产环境慎用
warnings.filterwarnings("ignore", category=InsecureRequestWarning)
warnings.filterwarnings("ignore", category=SecurityWarning)


def insert_data_to_es(index_name, data):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/18 13:35
    :Describe：es插入数据
    """
    try:
        # 信号量，防止es链接池耗尽
        global_config.es_semaphore.acquire()
        log_uils.refresh_logging()
        es_url = "{}:{}".format(global_config.es_config["host"], global_config.es_config["port"])
        # 创建Elasticsearch实例
        es = Elasticsearch(
            hosts=[es_url],
            basic_auth=(global_config.es_config["username"], global_config.es_config["password"]),
            # ca_certs=global_config.es_config["ca_certs"],  # 证书
            #verify_certs=False,  # 不校验证书
            request_timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )

        # 生成唯一的document_id
        document_id = str(uuid.uuid1())

        # 插入数据
        es.index(index=index_name, id=document_id, document=data)
        # 日志记录成功信息
        logging.info(
            f"Elastic Search Data inserted Successfully!!! Index: {index_name}, Document ID: {document_id}")
    except Exception as e:
        logging.error(f"Elastic Search Failed to insert data!!! Error: {str(e)}")
    finally:
        # 释放信号量
        global_config.es_semaphore.release()

def bulk_insert_data_to_es(index_name, data_list, batch_size):
    """
    Parameters
    ----------
    index_name : str
        索引名称
    data_list : list
        数据列表
    batch_size : int
        每个批次的大小
    """
    try:
        # 信号量，防止ES连接池耗尽
        global_config.es_semaphore.acquire()
        if len(data_list) == 0 or not data_list:
            logging.info(f"Empty data_list, no need to bulk_insert data to ES. data_list: {data_list}")
            return
        log_uils.refresh_logging()
        es_url = "{}:{}".format(global_config.es_config["host"], global_config.es_config["port"])
        # 创建Elasticsearch实例
        es = Elasticsearch(
            hosts=[es_url],
            basic_auth=(global_config.es_config["username"], global_config.es_config["password"]),
            # ca_certs=global_config.es_config["ca_certs"],  # 证书
            # verify_certs=False,  # 不校验证书
            request_timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )

        # 将数据按批次大小切分成多个批次
        data_batches = list(chunked(data_list, batch_size))

        # 遍历每个批次插入数据
        for batch in data_batches:
            # 构建批量插入请求
            actions = [
                {
                    "_index": index_name,
                    "_id": str(uuid.uuid1()),
                    "_source": data
                }
                for data in batch
            ]

            # 使用bulk插入数据
            success, _ = bulk(es, actions)

            # 检查插入是否成功
            if success:
                #logging.info(f"Successfully bulk_insert {len(batch)} documents to ES.") #注释掉减少日志
                pass
            else:
                logging.error("Failed to bulk_insert documents to ES.")
    except Exception as e:
        logging.error(f"Elastic Search Failed to bulk_insert data!!! Error: {str(e)}")
    finally:
        # 释放信号量
        global_config.es_semaphore.release()


if __name__ == '__main__':
    # 测试批量写入es
    data_list = [
        {
            "minReferencePrice": 35449,
            "Id": 1627,
            "CommodityName": "AK-47 | 二西莫夫 (略有磨损)6",
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
            "Timestamp": "1686584759000"
        },
        {
            "minReferencePrice": 35449,
            "Id": 222,
            "CommodityName": "AK-47 | 二西莫夫 (略有磨损)6",
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
            "Timestamp": "1686584795000"
        }
    ]
    # 获取当前日期
    current_date = datetime.now().date()
    # 生成新的索引名称
    new_index_name = f"{global_config.commodity_prefix}{current_date.year}.{current_date.month}.{current_date.day}"

    bulk_insert_data_to_es(new_index_name, data_list, 1000)

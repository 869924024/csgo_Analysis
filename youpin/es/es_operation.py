# @Time : 2023/6/17 16:02
# @Author : douyacai
# @Version：V 0.1
# @File : es_operation.py
# @desc : 悠悠有品实时爬取落库es
import datetime
import time

from elasticsearch import Elasticsearch
from global_var import global_config
import uuid
from log_uils import logger
import log_uils

global_config = global_config()


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
    log_uils.refresh_logging()
    try:
        es_url = "{}:{}".format(global_config.es_config["host"], global_config.es_config["port"])
        # 创建Elasticsearch实例
        es = Elasticsearch(
            hosts=[es_url],
            basic_auth=(global_config.es_config["username"], global_config.es_config["password"])
        )

        # 生成唯一的document_id
        document_id = str(uuid.uuid1())

        # 插入数据
        es.index(index=index_name, id=document_id, document=data)
        # 日志记录成功信息
        logger.info(
            f"Elastic Search Data inserted Successfully!!! Index: {index_name}, Document ID: {document_id},Data: {data}")
    except Exception as e:
        logger.error(f"Elastic Search Failed to insert data!!! Error: {str(e)}")



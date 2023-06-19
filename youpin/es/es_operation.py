# @Time : 2023/6/17 16:02
# @Author : douyacai
# @Version：V 0.1
# @File : es_operation.py
# @desc : 悠悠有品实时爬取落库es
import logging
from elasticsearch import Elasticsearch
from global_var import global_config
import uuid
import log_uils
from elasticsearch.helpers import bulk

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
        log_uils.refresh_logging()
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
        logging.info(
            f"Elastic Search Data inserted Successfully!!! Index: {index_name}, Document ID: {document_id}")
    except Exception as e:
        logging.error(f"Elastic Search Failed to insert data!!! Error: {str(e)}")


def bulk_insert_data_to_es(index_name, data_list):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/18 22:09
    :Describe： 批量插入数据到ES
    """
    try:
        if len(data_list) == 0 or not data_list:
            logging.info(f"Empty data_list, no need to bulk_insert data to ES. data_list: {data_list}")
            return
        log_uils.refresh_logging()
        es_url = "{}:{}".format(global_config.es_config["host"], global_config.es_config["port"])
        # 创建Elasticsearch实例
        es = Elasticsearch(
            hosts=[es_url],
            basic_auth=(global_config.es_config["username"], global_config.es_config["password"])
        )

        # 构建批量插入请求
        actions = [
            {
                "_index": index_name,
                "_id": str(uuid.uuid1()),
                "_source": data
            }
            for data in data_list
        ]

        # 使用bulk插入数据
        success, _ = bulk(es, actions)

        # 检查插入是否成功
        if success:
            logging.info(f"Successfully bulk_insert {len(data_list)} documents to ES.")
        else:
            logging.error("Failed to bulk_insert documents to ES.")

    except Exception as e:
        logging.error(f"Elastic Search Failed to bulk_insert data!!! Error: {str(e)}")

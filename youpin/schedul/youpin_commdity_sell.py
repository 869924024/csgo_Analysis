# @Time : 2023/6/18 13:37
# @Author : douyacai
# @Version：V 0.1
# @File : youpin_commdity_sell.py
# @desc : 定时任务，每天定时爬取悠悠有品商品销售数据
import copy
import datetime
import time
from global_var import global_config
from youpin.es import es_operation
from youpin import youpin_template
from concurrent.futures import ThreadPoolExecutor
import logging
import log_uils
global_config = global_config()


def getCommodityIndexName():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/18 13:35
    :Describe：获取饰品索引名称
    """

    # 获取当前日期
    current_date = datetime.datetime.now().date()
    # 生成新的索引名称
    new_index_name = f"{global_config.commodity_prefix}{current_date.year}.{current_date.month}.{current_date.day}"
    return new_index_name


def crawlCommodityData(index, page_size):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/18 13:58
    :Describe：爬取饰品数据落库es-在售、短租、长租等
    """
    # 获取token
    token = global_config.tokens[index]
    # 获取模版信息
    dataList = youpin_template.batchTemplate_FromDBId(index, page_size, token)
    # 获取索引名称
    index_name = getCommodityIndexName()
    logging.info(f"爬取开始——当前token：{token}，当前下标：{index}，操作数据量：{page_size}，当前索引名称：{index_name}")
    # logging.info(f"当前token：{token}，当前下标：{index}，操作数据量：{page_size}，当前索引名称：{index_name}，数据集合：{dataList}")
    # 插入数据到es
    es_operation.bulk_insert_data_to_es(index_name, dataList)
    logging.info(f"爬取开始结束当前token：{token}，当前下标：{index}，操作数据量：{page_size}，当前索引名称：{index_name}")

def multiThreadCcrawlCommodityDataToTime():
    # 开始时间
    start_time = time.time()
    print(f"批量爬取饰品数据落库es-在售、短租、长租等开始!!!!,开始时间：{start_time}s")
    logging.info(f"批量爬取饰品数据落库es-在售、短租、长租等开始!!!!,开始时间：{start_time}s")
    log_uils.refresh_logging()
    # 获取token数量
    tokenslen = len(global_config.tokens)
    # 获取数据库中的饰品模版总数
    template_count = global_config.commodity_template_count
    # 每页大小
    page_size = template_count // tokenslen + 1
    # 总页数
    total_page = template_count // page_size + 1
    executor = ThreadPoolExecutor(max_workers=len(global_config.tokens))  # 使用多线程进行并发请求
    for index in range(1,total_page):
        executor.submit(crawlCommodityData, index, page_size)
        time.sleep(0.5)  # 等待一小段时间，避免请求过于频繁
    executor.shutdown(wait=True)  # 等待所有任务完成
    # 结束时间
    end_time = time.time()
    logging.info(f"批量爬取饰品数据落库es-在售、短租、长租等完成!!!!,开始时间：{start_time},结束时间：{end_time},耗时：{end_time - start_time}s")
    print(f"批量爬取饰品数据落库es-在售、短租、长租等完成!!!!,开始时间：{start_time},结束时间：{end_time},耗时：{end_time - start_time}s")
if __name__ == '__main__':
    multiThreadCcrawlCommodityDataToTime()
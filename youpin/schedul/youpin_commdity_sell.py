# @Time : 2023/6/18 13:37
# @Author : douyacai
# @Version：V 0.1
# @File : youpin_commdity_sell.py
# @desc : 定时任务，每天定时爬取悠悠有品商品销售数据
from datetime import datetime
import time

import schedule

from global_var import global_config
from youpin.es import es_operation
from youpin import youpin_template, youpin_getToken
from concurrent.futures import ThreadPoolExecutor
import logging
import log_uils


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
    current_date = datetime.now().date()
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
    token = global_config.tokens[index-1]
    # 获取索引名称
    index_name = getCommodityIndexName()
    logging.info(f"爬取开始，当前下标：{index}，操作数据量：{page_size}，开始下标：{(index - 1) * page_size}，结束下标：{index * page_size}，当前索引名称：{index_name}")
    # 获取模版信息
    dataList = youpin_template.batchTemplate_FromDBId(index, page_size, token)
    # 插入数据到es
    es_operation.bulk_insert_data_to_es(index_name, dataList)
    logging.info(f"爬取结束，当前标识：{index}，操作数据量：{page_size}，开始下标：{(index - 1) * page_size}，结束下标：{index * page_size}，当前索引名称：{index_name}")

def multiThreadCcrawlCommodityDataToTime():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/19 00:13
    :Describe：批量分页获取饰品模版数据，批量爬取饰品数据落库es-在售、短租、长租等
    """
    # 开始时间计算
    start_time = time.time()
    start_time_str = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"批量爬取饰品数据落库es-在售、短租、长租等开始!!请耐心等等（可以开启数据打印观察）!!,开始时间：{start_time_str}")
    # 刷新日志
    log_uils.refresh_logging()
    # 获取token数量
    tokenslen = len(global_config.tokens)
    # 获取数据库中的饰品模版总数
    template_count = global_config.commodity_template_count
    # 每页大小
    page_size = template_count // tokenslen+1
    executor = ThreadPoolExecutor(max_workers=tokenslen+1)  # 使用多线程进行并发请求
    for index in range(1, tokenslen+1):
        executor.submit(crawlCommodityData, index, page_size)
        time.sleep(1)  # 等待一小段时间，避免请求过于频繁
    executor.shutdown(wait=True)  # 等待所有任务完成
    # 结束时间
    end_time = time.time()
    end_time_str = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(
        f"批量爬取饰品数据落库es-在售、短租、长租等完成!!!!,开始时间：{start_time_str},结束时间：{end_time_str},耗时：{time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}")

def job():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/19 20:29
    :Describe：定时任务执行的方法
    """
    youpin_getToken.checkDBToken(global_config.tokens)
    multiThreadCcrawlCommodityDataToTime()

# 每15分钟运行一次 job 函数
schedule.every(15).minutes.do(job)

def checkJob():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/19 20:23
    :Describe：定时任务，每天每10分钟定时爬取悠悠有品商品销售数据
    """
    job()  # 执行一次任务
    while True:
        schedule.run_pending()
        time.sleep(1)
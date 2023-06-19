import copy
import time
import requests
import json
from global_var import global_config
from concurrent.futures import ThreadPoolExecutor
import logging
import log_uils
import traceback



# 创建锁对象 间隔一定毫秒一次请求，不然会被熔断(不用锁，改成不同账号请求不会熔断)
# lock = threading.Lock()


def getTemplateinfo(template_id, local_headers):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/18 13:51
    :Describe：单个饰品模版或数据-post请求-悠悠有品
    """
    # 请求数据
    data = {
        "appVersion": "5.1.1",
        "gameId": 730,
        "SessionId": "17A06643-B466-45ED-8495-15D11313572B",
        "AppType": "3",
        "templateId": template_id,
        "Platform": "ios",
        "Version": "5.1.1",
        "listType": 15,
    }

    # 请求URL
    url = "https://api.youpin898.com/api/homepage/v2/detail/template/info"

    # 发送POST请求
    response = requests.post(url, headers=local_headers, data=json.dumps(data), timeout=5)

    # 解析响应数据
    response_data = json.loads(response.text)

    # 提取饰品数据
    template_info = response_data["Data"]["TemplateInfo"]
    # template_info 为null返回
    if not template_info:
        return
    # 因为会频繁打印，好像会影响效率，所以注释掉（想看完整数据的话可以取消注释）
    # logging.info(f"获取饰品模版数据成功，饰品模版id：{template_id},饰品模版数据：{template_info},时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    return template_info


def batchTemplate_FromDBId(page, page_size, thread_token):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 13:36
    :Describe：分页从数据库获取批量饰品模版数据
    """
    try:
        # 创建 headers 的副本
        local_headers = copy.deepcopy(global_config.youpinHeaders)
        # 每个线程单独token
        local_headers['authorization'] = thread_token
        # 获取数据库连接
        connection = global_config.get_db_connection()
        # 获取当前页
        current_page = page
        # 获取当前页的起始位置
        start = (current_page - 1) * page_size
        # 获取饰品模版id
        sql_select = "SELECT id FROM youpin_template limit %s,%s"
        cursor = connection.cursor()
        cursor.execute(sql_select, (start, page_size))
        result = cursor.fetchall()
        # 关闭游标
        cursor.close()
        # 关闭数据库连接
        global_config.close_db_connection(connection)
        dataList = []
        # 遍历饰品模版id
        for template_id in result:
            # 获取饰品模版数据
            template_info = getTemplateinfo(template_id[0], local_headers)
            # template_info 为null返回
            if not template_info:
                logging.error(f"饰品id：{template_id[0]}不存在")
                continue
            # 添加"Timestamp": time.time() * 1000,到饰品模版数据【重要】
            template_info["Timestamp"] = time.time() * 1000
            # 添加到列表
            dataList.append(template_info)
            # 间隔一定毫秒一次请求，不然会被熔断
            time.sleep(0.35)
        # 返回饰品模版数据
        return dataList
    except Exception as e:
        logging.error("批量获取饰品模版数据异常：%s", traceback.format_exc())



def inserTemplate_FromID(template_id, connection, local_headers):
    """
    Parameters
    template_id：饰品id
    connection：数据库连接
    local_headers：请求头
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 13:29
    :Describe：检查饰品模版是否存在，不存在则插入
    """

    try:
        # 获取锁
        # lock.acquire()

        # 判断数据是否已存在
        sql_select = "SELECT * FROM youpin_template WHERE id = %s"
        cursor = connection.cursor()
        cursor.execute(sql_select, (template_id,))
        result = cursor.fetchone()
        if result:
            # print("饰品id：", result[0], "饰品名:", result[1], "数据已存在，不进行插入操作")
            cursor.close()
            return

        # 提取饰品数据
        template_info = getTemplateinfo(template_id, local_headers)
        # template_info 为null返回
        if not template_info:
            #print("饰品id：", template_id, "不存在")
            cursor.close()
            return

        # 插入数据到数据库
        sql_insert = "INSERT INTO youpin_template (Id,CommodityName, CommodityHashName, GroupHashName, IconUrl, TypeName, Exterior, Rarity, Quality) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (template_info["Id"], template_info["CommodityName"], template_info["CommodityHashName"],
                  template_info["GroupHashName"], template_info["IconUrl"], template_info["TypeName"],
                  template_info["Exterior"], template_info["Rarity"], template_info["Quality"])
        cursor.execute(sql_insert, values)
        connection.commit()
        cursor.close()
        print("饰品：", template_info["CommodityName"], " Id:", template_info["Id"], "插入成功")
    except Exception as e:
        logging.exception("任务执行失败: %s", traceback.format_exc())

    # finally:
    # 在finally块中释放锁，确保即使发生异常也能释放锁
    # lock.release()


def getAllTemolate(pageIndex, pageSize, thread_token):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 13:36
    :Describe：
    """

    # 请求数据
    data = {
        "Platform": "ios",
        "maxLongPrice": "",
        "maxPrice": "",
        "Version": "5.1.1",
        "keyWords": "",
        "gameId": 730,
        "sortType": 0,
        "AppType": "3",
        "SessionId": "17A06643-B466-45ED-8495-15D11313572B",
        "listSortType": 0,
        "pageIndex": pageIndex,
        "pageSize": pageSize,
        "filterMap": {
            "Rarity": [],
            "Exterior": [],
            "Type": [],
            "Quality": []
        },
        "minLongPrice": "",
        "minPrice": "",
        "maxDepositPrice": "",
        "minDepositPrice": "",
        "listType": 10
    }
    # 创建 headers 的副本
    local_headers = copy.deepcopy(global_config.youpinHeaders)
    # 每个线程单独token
    local_headers['authorization'] = thread_token

    # 请求URL
    url = "https://api.youpin898.com/api/homepage/new/es/template/GetCsGoPagedList"

    # 发送POST请求
    response = requests.post(url, headers=local_headers, data=json.dumps(data))
    # 解析响应数据
    response_data = json.loads(response.text)
    data_list = response_data["Data"]
    print("第" + pageIndex + "页", str(data_list))
    connection = global_config.get_db_connection()
    for data in data_list:
        id = data["Id"]
        inserTemplate_FromID(id, connection, local_headers)
    global_config.close_db_connection(connection)
    print("第" + pageIndex + "页数据插入完成")


def batchTemplate_FromID(start, end, thread_token):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/16 13:36
    :Describe：批量扫描饰品模版
    """

    print("检查范围：", start, "-", end, " 使用token:", thread_token)
    connection = global_config.get_db_connection()
    # 创建 headers 的副本
    local_headers = copy.deepcopy(global_config.youpinHeaders)
    # 每个线程单独token
    local_headers['authorization'] = thread_token
    try:
        # 从start到end循环
        for id in range(start, end):
            inserTemplate_FromID(id, connection, local_headers)
    except Exception as e:
        print("任务执行失败:", str(e))
    finally:
        global_config.close_db_connection(connection)
    print("完成范围扫描：", start, "-", end, " 使用token:", thread_token)


def batchTemplate_FromPage():
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/17 14:34
    :Describe：批量爬取饰品模版 （数据库数据为空时使用）
    """
    log_uils.refresh_logging()
    # 计算开始使用时间
    type = 1  # 1:从指定ID开始爬(推荐用这个) 2:从第一页开始爬（1-100页,不推荐,youpin的分页随机给饰品的数据，有时候会有重复的，所以跑多几次，保证数据的完整性）
    start = time.time()
    executor = ThreadPoolExecutor(max_workers=len(global_config.tokens) + 1)  # 使用多线程进行并发请求
    total = 150000  # id总数
    if type == 1:
        rangIndex = total / len(global_config.tokens)
        for i in range(0, len(global_config.tokens) + 1):
            thread_token = global_config.tokens[i % len(global_config.tokens)]  # 为每个线程选择一个令牌
            executor.submit(batchTemplate_FromID, int(i * rangIndex), int((i + 1) * rangIndex),
                            thread_token)  # 提交任务给线程池并发执行
            time.sleep(0.1)  # 等待一小段时间，避免请求过于频繁
    else:
        # 重复请求多次，保证数据的完整性
        for i in range(1, 101):
            for j in range(1, 101):  # 获取前100页数据
                thread_token = global_config.tokens[j % len(global_config.tokens)]  # 为每个线程选择一个令牌
                executor.submit(getAllTemolate, str(j), 100, thread_token)  # 提交任务给线程池并发执行
                time.sleep(0.5)  # 等待一小段时间，避免请求过于频繁
    executor.shutdown(wait=True)  # 等待所有任务完成
    # 计算结束使用时间
    end = time.time()
    print("所有数据插入完成", "总耗时：", end - start, "秒")


if __name__ == '__main__':
    batchTemplate_FromPage()

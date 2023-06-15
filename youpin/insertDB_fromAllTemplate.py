import sys
import threading
import time
import logging
import requests
import json
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

# 创建锁对象 间隔一定毫秒一次请求，不然会被熔断
lock = threading.Lock()

# 数据库连接配置
db_config = {
    "host": "www.douyacai.work",
    "user": "csgo",
    "password": "hjj2819597",
    "database": "csgo",
    "charset": "utf8",
    "pool_name": "csgo_pool",
    "pool_size": 25,
}

# 请求头
headers = {
    "content-type": "application/json",
    "apptype": "3",
    "version": "5.1.1",
    "authorization": "Bearer ",
    "content-encoding": "gzip",
    "devicesysversion": "13.6",
    "app-version": "5.1.1",
    "api-version": "1.0",
    "accept": "*/*",
    "accept-encoding": "gzip",
    "accept-language": "zh-Hans;q=1.0, en;q=0.9",
    "platform": "ios",
    "devicetoken": "17A06643-B466-45ED-8495-15D11313572B",
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwNTdmMjlkMWZiYmU0MjQ1OWFkYjA2NjMyMTQ2N2YwZCIsIm5hbWVpZCI6IjMzNjM4MjMiLCJJZCI6IjMzNjM4MjMiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzM2MzgyMyIsIk5hbWUiOiJZUDAwMDMzNjM4MjMiLCJuYmYiOjE2ODYwNjA0ODAsImV4cCI6MTY4NjkyNDQ4MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.Pn_xsEidIEa0ZxY1ZvHAGP76_8BVVRoWrcxXKxs2Sm4',
    "content-length": "168",
    "user-agent": "",
}
# # 连接数据库
# db = mysql.connector.connect(**db_config)
# cursor = db.cursor()

# 创建连接池
db_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)


def inserTemplate_FromID(template_id, connection):
    try:
        # 获取锁
        lock.acquire()
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

        # 判断数据是否已存在
        sql_select = "SELECT * FROM youpin_template WHERE id = %s"
        cursor = connection.cursor()
        cursor.execute(sql_select, (template_id,))
        result = cursor.fetchone()
        if result:
            # print("饰品id：", result[0], "饰品名:", result[1], "数据已存在，不进行插入操作")
            cursor.close()
            return

        # 请求URL
        url = "https://api.youpin898.com/api/homepage/v2/detail/template/info"

        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)

        # 解析响应数据
        response_data = json.loads(response.text)

        # 提取饰品数据
        template_info = response_data["Data"]["TemplateInfo"]
        # template_info 为null返回
        if not template_info:
            # print("饰品id：", template_id, "不存在")
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
        logging.exception("任务执行失败: %s", str(e))
    finally:
        # 10毫秒后释放锁
        time.sleep(0.01)
        # 在finally块中释放锁，确保即使发生异常也能释放锁
        lock.release()



def getAllTemolate(pageIndex, pageSize):
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

    # 请求URL
    url = "https://api.youpin898.com/api/homepage/new/es/template/GetCsGoPagedList"

    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # 解析响应数据
    response_data = json.loads(response.text)
    data_list = response_data["Data"]
    print("第" + pageIndex + "页", str(data_list))
    connection = db_pool.get_connection()
    for data in data_list:
        id = data["Id"]
        inserTemplate_FromID(id, connection)
    connection.close()
    print("第" + pageIndex + "页数据插入完成")


def batchTemplate_FromID(start, end):
    print("检查范围：", start, "-", end)
    connection = db_pool.get_connection()
    try:
        # 从start到end循环
        for id in range(start, end):
            inserTemplate_FromID(id, connection)
    except Exception as e:
        print("任务执行失败:", str(e))
    finally:
        connection.close()



if __name__ == "__main__":
    # 计算开始使用时间
    type = 1  # 1:从指定ID开始爬(推荐用这个) 2:从第一页开始爬（1-100页,不推荐,youpin的分页随机给饰品的数据，有时候会有重复的，所以跑多几次，保证数据的完整性）
    start = time.time()
    executor = ThreadPoolExecutor(max_workers=10)  # 使用10个线程进行并发请求
    if type == 1:
        for i in range(1, 150):
            executor.submit(batchTemplate_FromID, (i - 1) * 1000, i * 1000)  # 提交任务给线程池并发执行
            time.sleep(0.1)  # 等待一小段时间，避免请求过于频繁
    else:
        # 重复请求多次，保证数据的完整性
        for i in range(1, 101):
            for j in range(1, 101):  # 获取前100页数据
                executor.submit(getAllTemolate, str(j), 100)  # 提交任务给线程池并发执行
                time.sleep(0.5)  # 等待一小段时间，避免请求过于频繁
    executor.shutdown(wait=True)  # 等待所有任务完成
    # 计算结束使用时间
    end = time.time()
    print("所有数据插入完成", "总耗时：", end - start, "秒")
    try:
        # 关闭连接池
        db_pool.close()
    except Exception as e:
        print("关闭连接池时出现异常:", str(e), "强制退出程序")
        sys.exit(1)  # 退出程序或进行其他错误处理

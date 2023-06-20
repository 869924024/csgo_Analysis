# @Time : 2023/6/16 13:05
# @Author : douyacai
# @Version：V 0.1
# @File : global_var.py.py
# @desc : 全局配置类
import logging
from threading import Semaphore
import threading
import mysql.connector
from elasticsearch import Elasticsearch

import log_uils


class global_config:
    _instance = None

    # 令牌列表(越多令牌爬取得越快)，数据库如果有令牌，优先使用数据库令牌
    tokens = [
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiNWI1ODEyMWE5MDY0OGU0YTE5NDAxYzNiZjliNjU1NSIsIm5hbWVpZCI6IjM0MTM3ODciLCJJZCI6IjM0MTM3ODciLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxMzc4NyIsIk5hbWUiOiJZUDAwMDM0MTM3ODciLCJuYmYiOjE2ODY3OTM2NTksImV4cCI6MTY4NzY1NzY1OSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.QSOSxCYqduPOP2P94nVQG75dBwPeAWrGWKyjAsO-_1I',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwNTdmMjlkMWZiYmU0MjQ1OWFkYjA2NjMyMTQ2N2YwZCIsIm5hbWVpZCI6IjMzNjM4MjMiLCJJZCI6IjMzNjM4MjMiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzM2MzgyMyIsIk5hbWUiOiJZUDAwMDMzNjM4MjMiLCJuYmYiOjE2ODYwNjA0ODAsImV4cCI6MTY4NjkyNDQ4MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.Pn_xsEidIEa0ZxY1ZvHAGP76_8BVVRoWrcxXKxs2Sm4',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYTM1NWVjYjhkZTE0N2U5YmM2ZGNiMmMwOGRiN2YwNSIsIm5hbWVpZCI6IjM0MTM5MjMiLCJJZCI6IjM0MTM5MjMiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxMzkyMyIsIk5hbWUiOiJZUDAwMDM0MTM5MjMiLCJuYmYiOjE2ODY3OTU0NjQsImV4cCI6MTY4NzY1OTQ2NCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.QFLLcr-v6RbE5mLhDhg9jpjd6BLma04t4C7CDli4BUo',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyZWUxOWFkOTc3MDU0Zjk4ODNjNjcyMTdkYjYwMjczYSIsIm5hbWVpZCI6IjM0MTM5NTYiLCJJZCI6IjM0MTM5NTYiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxMzk1NiIsIk5hbWUiOiJZUDAwMDM0MTM5NTYiLCJuYmYiOjE2ODY3OTU4NzMsImV4cCI6MTY4NzY1OTg3MywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.l2vR-mY0FbUnZYDKT97BBqk0LKZySm8HCqxk-srzAOI',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1Y2E1YWQxM2Q0NDc0NjU2YWVmNWMyMTc5Mjk5MmQ0MiIsIm5hbWVpZCI6IjM0MTM5NjIiLCJJZCI6IjM0MTM5NjIiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxMzk2MiIsIk5hbWUiOiJZUDAwMDM0MTM5NjIiLCJuYmYiOjE2ODY3OTU5NzYsImV4cCI6MTY4Njc5Nzc3NiwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.KrlBcKTHjza_zejVTylKrrjZnAmKttCXkXiWkKVVO0A',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYTdlY2ZlZmYxYzE0NmJmOTVjOWFhODhjMjhmZTg3MSIsIm5hbWVpZCI6IjM0MTQwMTEiLCJJZCI6IjM0MTQwMTEiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNDAxMSIsIk5hbWUiOiJZUDAwMDM0MTQwMTEiLCJuYmYiOjE2ODY3OTY1MTcsImV4cCI6MTY4NzY2MDUxNywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ._x5ptKihN0SStpqJYk8bfUrMKo8oTGkIc-kriiXoySw',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkYjE2NmExZmU5MDk0NWVmYWExNjRjZDhiNDU4M2IyNCIsIm5hbWVpZCI6IjI4MDU5MDQiLCJJZCI6IjI4MDU5MDQiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMjgwNTkwNCIsIk5hbWUiOiJZUDAwMDI4MDU5MDQiLCJuYmYiOjE2ODY3OTY3NzQsImV4cCI6MTY4NzY2MDc3NCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.kfbkbha-FqcZUZDfstTlLAahVUoPR22vSzm5M73jCk8',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiMDI0MDhmMWNkYzQ0YzY1YTdmNTQzNTk1NmFjZDgxNSIsIm5hbWVpZCI6IjI2OTYzNjQiLCJJZCI6IjI2OTYzNjQiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMjY5NjM2NCIsIk5hbWUiOiJZUDAwMDI2OTYzNjQiLCJuYmYiOjE2ODY4MDE3OTIsImV4cCI6MTY4NzY2NTc5MiwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.JpiG8G3VwQmp27m2AS-Ufkwt4K_x4FEl4yAyBuUz2YA',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxNzAzNTA4YWE2ZTM0ZmIxODdiYzRkNGI0ZjU4NzI2ZSIsIm5hbWVpZCI6IjI2OTYzMjMiLCJJZCI6IjI2OTYzMjMiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMjY5NjMyMyIsIk5hbWUiOiJZUDAwMDI2OTYzMjMiLCJuYmYiOjE2ODY4MDE2MTgsImV4cCI6MTY4NzY2NTYxOCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.TVSIrH9R1vP_NzNBpwD_7M6nevInIQXQSi1H6BvQpt8',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3OWYxODhmY2Q4Mjg0MmJmYjE4YTg5NGY5YTQ3NmQ5MSIsIm5hbWVpZCI6IjMxMTE1NjIiLCJJZCI6IjMxMTE1NjIiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzExMTU2MiIsIk5hbWUiOiJZUDAwMDMxMTE1NjIiLCJuYmYiOjE2ODY4MDE2NTcsImV4cCI6MTY4NzY2NTY1NywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.HYzJaahkIGdzUNAI5K4mcLgmFzjI_5-f6Md685jYVMo',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwZjkwN2ExMTUyOWU0YWUzOWY4YTVkOWEwMTdkZWMwNiIsIm5hbWVpZCI6IjI2OTYxODgiLCJJZCI6IjI2OTYxODgiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMjY5NjE4OCIsIk5hbWUiOiJZUDAwMDI2OTYxODgiLCJuYmYiOjE2ODY4MDE4NTAsImV4cCI6MTY4NzY2NTg1MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.R44bICqWxofOe1CmZfuXMMfhhGeNCxFVeO48HVYBsms',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwZjkwN2ExMTUyOWU0YWUzOWY4YTVkOWEwMTdkZWMwNiIsIm5hbWVpZCI6IjI2OTYxODgiLCJJZCI6IjI2OTYxODgiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMjY5NjE4OCIsIk5hbWUiOiJZUDAwMDI2OTYxODgiLCJuYmYiOjE2ODY4MDE4NTAsImV4cCI6MTY4NzY2NTg1MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.R44bICqWxofOe1CmZfuXMMfhhGeNCxFVeO48HVYBsms',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5YjU5YTFlOTVjNjA0NGM5OGYwNWMyYzQxMTUwMDM4ZiIsIm5hbWVpZCI6IjM0MTQ4NDEiLCJJZCI6IjM0MTQ4NDEiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNDg0MSIsIk5hbWUiOiJZUDAwMDM0MTQ4NDEiLCJuYmYiOjE2ODY4MDc1ODcsImV4cCI6MTY4NzY3MTU4NywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.W85UTJ473XHaRXX9qRdLjqOeHSmSa-haOx5xYw-BNGw',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwZWE5MmI3N2Q0NjQ0ZTg0OTRlMGJiMGIyMmRhNDE3OCIsIm5hbWVpZCI6IjM0MTQ5MjYiLCJJZCI6IjM0MTQ5MjYiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNDkyNiIsIk5hbWUiOiJZUDAwMDM0MTQ5MjYiLCJuYmYiOjE2ODY4MDg0NzMsImV4cCI6MTY4NzY3MjQ3MywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.w-lK0ryw5fux_GvO4u4Q0GznYBWzhyPGa8Hm0BvarJ4',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkODMxOWRhNjg1ZjA0ZTMyOTlhMGFkZjYwMTU1OWVmZCIsIm5hbWVpZCI6IjM0MTQ5MzIiLCJJZCI6IjM0MTQ5MzIiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNDkzMiIsIk5hbWUiOiJZUDAwMDM0MTQ5MzIiLCJuYmYiOjE2ODY4MDg1NTgsImV4cCI6MTY4NzY3MjU1OCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.qGFBV3Eu4lSDBhaYPkaOKgNsrT7R9O6QS01TEmjmx-s',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiYzY5NmMzNzI4YjI0MGM1ODA5NzE4NGI3ODIxYjdiYSIsIm5hbWVpZCI6IjM0MTQ5NTQiLCJJZCI6IjM0MTQ5NTQiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNDk1NCIsIk5hbWUiOiJZUDAwMDM0MTQ5NTQiLCJuYmYiOjE2ODY4MDg3MzEsImV4cCI6MTY4NzY3MjczMSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.ViYhQXS0m97XOcmCrxA8WCisk_ixtfHjmlc4Q0zSsHk',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiMTQ2MWI5MGI5OGU0MGQzODc2NmM3ZDY0Yzg0Yzg0NiIsIm5hbWVpZCI6IjMyMzU0NzUiLCJJZCI6IjMyMzU0NzUiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzIzNTQ3NSIsIk5hbWUiOiJZUDAwMDMyMzU0NzUiLCJuYmYiOjE2ODY4MDg4NjcsImV4cCI6MTY4NzY3Mjg2NywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.gWT8hBMPMBAhoSZaor23h-IChds8S0U_9KD_juQornA',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2NzAxNjRlMzc0ODU0OWU0OTVjMTBhYTM0M2UzMWEyZiIsIm5hbWVpZCI6IjM0MTQ5ODYiLCJJZCI6IjM0MTQ5ODYiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNDk4NiIsIk5hbWUiOiJZUDAwMDM0MTQ5ODYiLCJuYmYiOjE2ODY4MDkwMzEsImV4cCI6MTY4NzY3MzAzMSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.SFzsA_kS4bJJRabq4wgV7dadZPXQjs-BOVTQentVFqM',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyYzIxYjc2YjhlNzM0MjY1YTgyYzJmZDBlYWI2OTVjMSIsIm5hbWVpZCI6IjMwMjIwOTEiLCJJZCI6IjMwMjIwOTEiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzAyMjA5MSIsIk5hbWUiOiJZUDAwMDMwMjIwOTEiLCJuYmYiOjE2ODY4MDkxMjMsImV4cCI6MTY4NzY3MzEyMywiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.C3Vo-CH8ng2Ery4TkM6daJjk-x-FkHBeq7IpVFrsEKY',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjM2ZmNjJlYjYzM2E0MmY0OGU4Zjg4NTk0YjgwM2U5YiIsIm5hbWVpZCI6IjMzMDY2MzIiLCJJZCI6IjMzMDY2MzIiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzMwNjYzMiIsIk5hbWUiOiJZUDAwMDMzMDY2MzIiLCJuYmYiOjE2ODY4MDkzMzksImV4cCI6MTY4NzY3MzMzOSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.FKNvo3mv5A8-C45kiZvKiLJT_N3avlPbuAhzHd63GY4',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhOWFhZjdlYjI0MmY0NmRlYjU4NDIyNjZhMzRmNmYwOCIsIm5hbWVpZCI6IjM0MTUwMjYiLCJJZCI6IjM0MTUwMjYiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNTAyNiIsIk5hbWUiOiJZUDAwMDM0MTUwMjYiLCJuYmYiOjE2ODY4MDk2NTgsImV4cCI6MTY4NzY3MzY1OCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.46Ww7fXaYa3O2Xi9hFDE29Ae6N97IGZxhdyP1qVbqbo',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJkZTRhNzIyOTYxNzc0ZTUwODk2ZGE3YWQ5ZDhiYTIwZCIsIm5hbWVpZCI6IjMzMDc0MDIiLCJJZCI6IjMzMDc0MDIiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzMwNzQwMiIsIk5hbWUiOiJZUDAwMDMzMDc0MDIiLCJuYmYiOjE2ODY4MDk3MTksImV4cCI6MTY4NzY3MzcxOSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.NIfN3oku15fOrJc_TktAeIWzNJaoZ7XPdOaflFcVodg',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwMzIzZDk3NTcyZjM0N2ZlOTVkMmVkYTdmOTE2YjMyOCIsIm5hbWVpZCI6IjM0MTUwMzgiLCJJZCI6IjM0MTUwMzgiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNTAzOCIsIk5hbWUiOiJZUDAwMDM0MTUwMzgiLCJuYmYiOjE2ODY4MDk3NzAsImV4cCI6MTY4NzY3Mzc3MCwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.3menpqZTZevReeFMP57QRAYDzf6fvriJ1NxobTVV7wE',
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI4ZjIyZDllYmNiOTU0MjhmOWQzMzg2MGFlZmY1YjJhYSIsIm5hbWVpZCI6IjM0MTUwNDIiLCJJZCI6IjM0MTUwNDIiLCJ1bmlxdWVfbmFtZSI6IllQMDAwMzQxNTA0MiIsIk5hbWUiOiJZUDAwMDM0MTUwNDIiLCJuYmYiOjE2ODY4MDk4MDksImV4cCI6MTY4NzY3MzgwOSwiaXNzIjoieW91cGluODk4LmNvbSIsImF1ZCI6InVzZXIifQ.NSq-2vcBjRPnnB39Myn0R0C4CVJKi3p_8iZweMHzZDE',
        # 添加更多令牌
    ]
    pool_size = 25  # 各种连接池大小,越大爬取速度越快，调试时可以调小

    # 数据库连接配置
    db_config = {
        "host": "www.douyacai.work",
        "user": "csgo",
        "password": "hjj2819597",
        "database": "csgo",
        "charset": "utf8",
        "pool_name": "csgo_pool",
        "pool_size": pool_size,
    }

    # 请求头
    youpinHeaders = {
        "content-type": "application/json",
        "apptype": "3",
        "version": "5.1.1",
        "content-encoding": "gzip",
        "devicesysversion": "13.6",
        "app-version": "5.1.1",
        "api-version": "1.0",
        "accept": "*/*",
        "accept-encoding": "gzip",
        "accept-language": "zh-Hans;q=1.0, en;q=0.9",
        "platform": "ios",
        "user-agent": "",
    }

    #  接码平台get请求头
    platformHeaders = {
        "content-type": "application/json",
        "Host": "ysqdouyin.online",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 "
                      "Accept: */*",
        "Connection": "keep-alive"
    }

    # 接码平台token
    platform_token = "hjj869924024-3023061510023121399162938"
    # 接码平台关键词（短信接码关键件，悠悠有品-悠悠有品，buff-网易）
    platform_keyword = "悠悠有品"
    # platform_keyword = "网易"

    # es配置
    es_config = {
        "host": "https://www.douyacai.work",
        "port": 9200,
        "username": "elastic",
        "password": "hjj2819597",
        "ca_certs": "/Users/huangjiajia/project/python/csgo_Analysis/cert/http_ca.pem"  # 证书，要验证就必须有
    }

    commodity_prefix = "youpin_commodity_"  # es索引前缀（饰品在售、出租等）

    commodity_template_count = 0  # 饰品模版总数 从数据库加载

    # 加锁，防止多线程对数据库连接池的连接操作出现异常（可能会导致效率下降，尽量在批量操作时，仅仅获取一个连接，使用完后再释放）
    db_lock = threading.Lock()
    # 信号量，控制数据库连接池的大小,防止多线程过多使用连接导致数据库池耗尽
    db_semaphore = Semaphore(pool_size)
    # 信号量，控制es连接池的大小,防止多线程过多使用连接导致es池耗尽
    es_semaphore = Semaphore(pool_size)
    '''
    ========================================================================================================================
    公共配置 ☝️
    
    公共方法 👇
    ========================================================================================================================
    '''

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    # 初始化
    def __init__(self):
        db_Tokens = self.getDBToken()
        if db_Tokens:
            # 初始化令牌
            self.tokens = db_Tokens
        else:
            logging.info("数据库中没有可用token,使用配置文件中token")
        # 初始化饰品模版总数
        if self.commodity_template_count == 0:
            self.commodity_template_count = self.getDBCommodityTemplateCount()

    # 数据库连接池
    def get_db_pool(self):
        self.db_lock.acquire()
        self.db_semaphore.acquire()
        try:
            # 若存在链接池则直接返回
            if hasattr(self, "pool"):
                return self.pool
            # 不存在则创建
            else:
                self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.db_config)
                return self.pool
        finally:
            self.db_lock.release()

    # db获取链接
    def get_db_connection(self):
        return self.get_db_pool().get_connection()

    def close_db_connection(self, conn):
        self.db_lock.acquire()
        try:
            conn.close()
        finally:
            self.db_semaphore.release()
            self.db_lock.release()

    # db连接池关闭
    def close_db_pool(self):
        if hasattr(self.pool, "pool"):
            self.pool.close()
            delattr(self.pool, "pool")
    '''
    ========================================================================================================================
    公共方法 ☝️
    
    私有方法 👇（其他模块不要引用，可能会引起循环依赖）
    ========================================================================================================================
    '''

    def getDBToken(self):
        """
        Parameters
        ----------
        Returns
        -------
        :Author:  douyacai
        :Create:  2023/6/16 17:37
        :Describe：批量获取数据库已存在的token
        """
        connection = self.get_db_connection()
        cursor = connection.cursor()
        sqlselect = "select * from youpin_phone_token"
        cursor.execute(sqlselect)
        result = cursor.fetchall()
        cursor.close()
        self.close_db_connection(connection)
        if not result:
            return []
        logging.info("数据库token获取成功，总数：%s" % len(result))
        return [tup[2] for tup in result]

    def getDBCommodityTemplateCount(self):
        """
        Parameters
        ----------
        Returns
        -------
        :Author:  douyacai
        :Create:  2023/6/18 17:29
        :Describe：数据库模版总数
        """
        connection = self.get_db_connection()
        cursor = connection.cursor()
        sqlselect = "select count(*) from youpin_template"
        cursor.execute(sqlselect)
        result = cursor.fetchone()
        if not result:
            logging.error("数据库模版总数获取失败")
            return 0
        logging.info("数据库模版总数获取成功，总数：%s" % result[0])
        cursor.close()
        self.close_db_connection(connection)
        return result[0]


global_config = global_config()

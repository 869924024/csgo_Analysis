import copy
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

# 令牌列表(越多令牌爬取得越快)
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

# 数据库连接配置
db_config = {
    "host": "www.douyacai.work",
    "user": "csgo",
    "password": "hjj2819597",
    "database": "csgo",
    "charset": "utf8",
    "pool_name": "csgo_pool",
    "pool_size": len(tokens)+1,
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


def inserTemplate_FromID(template_id, connection, local_headers):
    try:
        # 获取锁
        # lock.acquire()
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
        response = requests.post(url, headers=local_headers, data=json.dumps(data), timeout=5)

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
    # finally:
    # 在finally块中释放锁，确保即使发生异常也能释放锁
    # lock.release()


def getAllTemolate(pageIndex, pageSize, thread_token):
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
    local_headers = copy.deepcopy(headers)
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
    connection = db_pool.get_connection()
    for data in data_list:
        id = data["Id"]
        inserTemplate_FromID(id, connection, local_headers)
    connection.close()
    print("第" + pageIndex + "页数据插入完成")


def batchTemplate_FromID(start, end, thread_token):
    print("检查范围：", start, "-", end)
    connection = db_pool.get_connection()
    # 创建 headers 的副本
    local_headers = copy.deepcopy(headers)
    # 每个线程单独token
    local_headers['authorization'] = thread_token
    try:
        # 从start到end循环
        for id in range(start, end):
            inserTemplate_FromID(id, connection, local_headers)
    except Exception as e:
        print("任务执行失败:", str(e))
    finally:
        connection.close()
    print("完成范围扫描：", start, "-", end)


if __name__ == "__main__":
    # 计算开始使用时间
    type = 1  # 1:从指定ID开始爬(推荐用这个) 2:从第一页开始爬（1-100页,不推荐,youpin的分页随机给饰品的数据，有时候会有重复的，所以跑多几次，保证数据的完整性）
    start = time.time()
    executor = ThreadPoolExecutor(max_workers=len(tokens))  # 使用多线程进行并发请求
    total = 150000  # id总数
    if type == 1:
        rangIndex = total / len(tokens)
        for i in range(0, len(tokens) + 1):
            thread_token = tokens[i % len(tokens)]  # 为每个线程选择一个令牌
            executor.submit(batchTemplate_FromID, i * rangIndex, (i + 1) * rangIndex, thread_token)  # 提交任务给线程池并发执行
            time.sleep(0.1)  # 等待一小段时间，避免请求过于频繁
    else:
        # 重复请求多次，保证数据的完整性
        for i in range(1, 101):
            for j in range(1, 101):  # 获取前100页数据
                thread_token = tokens[j % len(tokens)]  # 为每个线程选择一个令牌
                executor.submit(getAllTemolate, str(j), 100, thread_token)  # 提交任务给线程池并发执行
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

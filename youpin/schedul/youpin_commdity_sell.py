# @Time : 2023/6/18 13:37
# @Author : douyacai
# @Version：V 0.1
# @File : youpin_commdity_sell.py
# @desc : 定时任务，每天定时爬取悠悠有品商品销售数据
import datetime
import time
from global_var import global_config

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


def buildCommodityDataToTime(data):
    """
    Parameters
    ----------
    Returns
    -------
    :Author:  douyacai
    :Create:  2023/6/18 13:35
    :Describe：构建饰品在售数据-时间戳
    """
    # 构建商品数据
    commodity_data = {
        "minReferencePrice": data["minReferencePrice"],
        "Id": data["Id"],
        "CommodityName": data["CommodityName"],
        "CommodityHashName": data["CommodityHashName"],
        "GroupHashName": data["GroupHashName"],
        "IconUrl": data["IconUrl"],
        "MinPrice": data["MinPrice"],
        "LeaseUnitPrice": data["LeaseUnitPrice"],
        "LongLeaseUnitPrice": data["LongLeaseUnitPrice"],
        "LeaseDeposit": data["LeaseDeposit"],
        "LeasePriceScale": data["LeasePriceScale"],
        "OnSaleCount": data["OnSaleCount"],
        "OnLeaseCount": data["OnLeaseCount"],
        "TypeName": data["TypeName"],
        "Rarity": data["Rarity"],
        "Quality": data["Quality"],
        "Exterior": data["Exterior"],
        "Timestamp": time.time() * 1000
    }
    return commodity_data


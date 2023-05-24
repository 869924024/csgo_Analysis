import requests
import json
import mysql.connector

# 建立MySQL数据库连接
db = mysql.connector.connect(
    host="www.douyacai.work",
    user="csgo",
    password="hjj2819597",
    database="csgo"
)

# 创建游标对象
cursor = db.cursor()

# 爬取数据并插入到prices表
prices_url = "your_prices_data_url"
response = requests.get(prices_url)
prices_data = json.loads(response.text)

for price_data in prices_data:
    id = price_data["id"]
    product_id = price_data["product_id"]
    price_type = price_data["price_type"]
    price = price_data["price"]
    timestamp = price_data["timestamp"]

    # 插入数据到prices表
    insert_prices_query = "INSERT INTO prices (id, product_id, price_type, price, timestamp) VALUES (%s, %s, %s, %s, %s)"
    insert_prices_values = (id, product_id, price_type, price, timestamp)
    cursor.execute(insert_prices_query, insert_prices_values)

# 爬取数据并插入到products表
products_url = "your_products_data_url"
response = requests.get(products_url)
products_data = json.loads(response.text)

for product_data in products_data:
    id = product_data["id"]
    pro_id = product_data["pro_id"]
    name = product_data["name"]
    description = product_data["description"]
    category = product_data["category"]
    image_url = product_data["image_url"]

    # 插入数据到products表
    insert_products_query = "INSERT INTO products (id, pro_id, name, description, category, image_url) VALUES (%s, %s, %s, %s, %s, %s)"
    insert_products_values = (id, pro_id, name, description, category, image_url)
    cursor.execute(insert_products_query, insert_products_values)

# 提交事务并关闭数据库连接
db.commit()
cursor.close()
db.close()

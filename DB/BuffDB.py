import random

import requests
import mysql.connector
import time

# 数据库连接配置
db_config = {
    'user': 'csgo',
    'password': 'hjj2819597',
    'host': 'www.douyacai.work',
    'database': 'csgo',
    'raise_on_warnings': True
}

# 创建数据库连接
cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()


# 爬取数据并插入表中
def crawl_and_insert_data():
    page_num = 1
    while True:
        # 发送请求获取数据
        session = requests.Session()
        url = f"https://buff.163.com/api/market/goods?game=csgo&page_num={page_num}&use_suggestion=0&_=1684772175087"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'cookie': 'Device-Id=Fpje5vRClUbKwR536nYj; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=2rS7x09EWk5PmMAg5JFeDMW8x95UCIKfI4_vEDA9Eq1n.6Js.4TFkUCTdnN4ICVHVUWqQ75JuP2_uIsS1PWYzwKK720CPnQI84yp03jwNlH_g_.gzundNLqoL1h1jnI6yZXYG1Y6txN3_XFItPSz78zLIv2PhgwMm0lv_3sKchXEvaqShgQugpJ1m_TmAGfjHy00fVW4_0W.8muaAstg9mQE6bhwd4JKhNta5FIR7tunB; S_INFO=1684776893|0|0&60##|18377740524; P_INFO=18377740524|1684776893|1|netease_buff|00&99|null&null&null#gud&440300#10#0|&0||18377740524; remember_me=U1095294936|xErIJUpVjzpPAzKcmaYmPLk2Ky5ejOJD; session=1-jpRr6gktHM-cvkBJsSDRHbntqmk0FSM5-8OsY9DTrqWb2038841472; csrf_token=IjUxZTY4NjVhMmYwZjBmOTM3YzJjZjIwOGRlNTNhOGFhZGQ5NjFiZTQi.F0060A.N90gLp3cF_M-Bv81F4o8EPG1dqA',
            'Device-Id':'Fpje5vRClUbKwR536nYj',
            'game': 'csgo',
            'csrf_token': 'IjUxZTY4NjVhMmYwZjBmOTM3YzJjZjIwOGRlNTNhOGFhZGQ5NjFiZTQi.F005cQ.l-swLILkpruytXRaj_PvyUGbvzQ',
            'P_INFO': '18377740524|1684776893|1|netease_buff|00&99|null&null&null#gud&440300#10#0|&0||18377740524',
            'remember_me': 'U1095294936|xErIJUpVjzpPAzKcmaYmPLk2Ky5ejOJD'
            ''
        }

        response = session.get(url, headers=headers)
        page_size = response.json()['data']['page_size']
        total_count = response.json()['data']['total_count']
        total_page = response.json()['data']['total_page']
        print(f"当前页数：{page_num}，每页数量：{page_size}，总数量：{total_count}，总页数：{total_page}")
        data = response.json()
        print(data)
        # code为Login Required则跳过
        if data['code'] == 'Login Required':
            continue
        # 处理每个饰品的数据
        for item in data['data']['items']:
            # 获取饰品数据
            product_id = item['id'] if 'id' in item else ""
            name = item['name'] if 'name' in item else ""
            short_name = item['short_name'] if 'short_name' in item else ""
            image_url = item["goods_info"]["icon_url"] if "icon_url" in item["goods_info"] else ""
            print(f"饰品id：{product_id}，饰品名称：{name}，饰品简称：{short_name}，饰品图片地址：{image_url}")
            #获得饰品标签
            tags = item["goods_info"]["info"]["tags"] if "tags" in item["goods_info"]["info"] else ""
            #遍历所有标签，category、category_group、custom、itemset、quality、rarity、sticker_v2、stickercapsule、stickercategory、tournament、tournamentteam、type、weapon、weaponcase、exterior、
            for tag_category, tag in tags.items():
                print(tag)
                #获得饰品标签id,若无则为空
                tag_id = tag["id"] if "id" in tag else ""
                #获得饰品标签的类型
                tag_type = tag["category"] if "category" in tag else ""
                #获得饰品标签的名称
                tag_name = tag["internal_name"] if "internal_name" in tag else ""
                #获得饰品标签的值
                tag_value = tag["localized_name"] if "localized_name" in tag else ""
                print(f"饰品标签id：{tag_id}，饰品标签类型：{tag_type}，饰品标签名称：{tag_name}，饰品标签值：{tag_value}")
                insert_tags(product_id,tag_id, tag_type, tag_name, tag_value);
            # 检查饰品是否已存在
            select_query = "SELECT id FROM products WHERE id = %s"
            cursor.execute(select_query,(str(product_id),))
            existing_product = cursor.fetchall()

            if len(existing_product) > 0:
                # 若饰品已存在，则更新
                update_query = "UPDATE products SET name = %s , short_name = %s, image_url = %s WHERE id = %s"
                update_values = (name, short_name, image_url, product_id)
                cursor.execute(update_query, update_values)
                continue

            # 插入数据到products表中
            insert_query = "INSERT INTO products (id, name, short_name, image_url) VALUES (%s, %s, %s, %s)"
            insert_values = (str(product_id),name,short_name, image_url)
            cursor.execute(insert_query, insert_values)
            print("------------------------------------------------------------------------------------------------")

        # 提交事务
        cnx.commit()

        # 增加页数，以获取下一页数据
        page_num += 1

        # 随机间隔5-15分钟后继续爬取下一页数据
        time.sleep(random.randint(5, 15) * 60)
        #爬取一定次数休息几小时
        if page_num % 100 == 0:
            time.sleep(random.randint(3, 5) * 60 * 60)

        # 若页数总页数，则重置页数
        if page_num >= total_page+1:
            page_num = 1

    # 关闭数据库连接
    cursor.close()
    cnx.close()

# 插入标签表
def insert_tags(productsId,tagsId,category,internal_name,localized_name):
    # 检查标签是否已存在
    select_query = "SELECT id FROM tags WHERE id = %s"
    cursor.execute(select_query, (str(tagsId),))
    existing_tag = cursor.fetchall()

        # 若标签已存在，则更新
    if len(existing_tag) > 0:
        update_query = "UPDATE tags SET category = %s, internal_name = %s, localized_name = %s WHERE id = %s"
        update_values = (category, internal_name, localized_name,str(id))
        cursor.execute(update_query, update_values)
        return

    # 插入数据到tags表中
    insert_query = "INSERT INTO tags (id, category, internal_name, localized_name) VALUES (%s, %s, %s, %s)"
    insert_values = (str(tagsId), category, internal_name, localized_name)
    cursor.execute(insert_query, insert_values)
    print(f"插入标签成功！标签ID：{id}，标签类型：{category}，标签内部名称：{internal_name}，标签本地化名称：{localized_name}")

    # 关联饰品和标签
    insert_query = "INSERT INTO product_labels(product_id, label_id) VALUES (%s, %s)"
    insert_values = (str(productsId), str(tagsId))
    cursor.execute(insert_query, insert_values)
    print(f"关联饰品和标签成功！关联饰品ID：{productsId}，关联标签ID：{tagsId}")
    # 提交事务
    cnx.commit()

# 调用函数执行爬取和插入操作
crawl_and_insert_data()



#-- csgo.products definition
# CREATE TABLE `products` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `pro_id` varchar(255) DEFAULT NULL COMMENT '饰品id',
#   `name` varchar(255) DEFAULT NULL COMMENT '名称',
#   `short_name` varchar(255) DEFAULT NULL COMMENT '简称',
#   `image_url` varchar(255) DEFAULT NULL COMMENT '图片',
#   PRIMARY KEY (`id`),
#   KEY `idx_product_id` (`pro_id`),
#   KEY `products_id_IDX` (`id`,`pro_id`) USING BTREE,
#   KEY `products_name_IDX` (`name`) USING BTREE,
#   KEY `products_category_IDX` (`short_name`) USING BTREE
# ) ENGINE=MyISAM AUTO_INCREMENT=272 DEFAULT CHARSET=utf8;

# -- csgo.tags definition
#
# CREATE TABLE `tags` (
#   `id` varchar(100) NOT NULL COMMENT 'id',
#   `category` varchar(100) DEFAULT NULL COMMENT '类别',
#   `internal_name` varchar(100) DEFAULT NULL COMMENT '内部名称',
#   `localized_name` varchar(100) DEFAULT NULL COMMENT '名称',
#   KEY `tags_id_IDX` (`id`,`category`) USING BTREE,
#   KEY `tags_category_IDX` (`category`) USING BTREE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='饰品标签';

# -- csgo.product_labels definition
#
# CREATE TABLE `product_labels` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `product_id` varchar(11) DEFAULT NULL COMMENT '产品ID',
#   `label_id` varchar(11) DEFAULT NULL COMMENT '标签ID',
#   PRIMARY KEY (`id`),
#   KEY `idx_product_id` (`product_id`),
#   KEY `idx_label_id` (`label_id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='饰品标签关联表';
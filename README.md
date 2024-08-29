大学第一次做一个完整大型数据爬取方案设计和开发，其中遇到很多问题，最后正常部署，稳定运行了大半年一年自动注册自动登录自动更新token定时爬取等等，然后某天突然发现悠悠有品限制登陆了，后续就没有时间去维护，
感兴趣的可以看看，基本这一套流程是满足市面上的所有采集爬取的需求的，或者遇到问题可以看看我这个找找灵感。


# csgo饰品平台爬取（可做大盘走势等）
对csgo饰品平台爬取（饰品售价、租金等），利用es存储。
目前完成平台：某某有品。
后期可以自行扩展平台，添加前端展示做大盘，也可以用来做数据分析、时间序列算法搞预测等等，底层大体框架是没问题的。
kibana一些大盘图（频率没调很快，机器太拉，如果你账户够多机器够好的话1分钟全量爬一次都行）：
![WechatIMG9770](https://github.com/869924024/csgo_Analysis/assets/53663993/506b1eac-0a27-41c5-ac7d-f709730c9614)
![WechatIMG14543](https://github.com/user-attachments/assets/82667174-18a0-4390-bd9f-aada11438a58)
![WechatIMG1542](https://github.com/869924024/csgo_Analysis/assets/53663993/83e0b81c-8be8-4ced-9e57-b613db6e228e)

整体架构：
## 1.1数据结构设计
### 1.1.1所有饰品的模版（mysql youpin_template）
由于模版不用实时爬取，或者定时任务，则存入数据库。
-- 饰品模版类 
![image](https://github.com/869924024/csgo_Analysis/assets/53663993/41e08a23-d315-4df9-9f0f-6c4710075fe5)


`CREATE TABLE `youpin_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '模版id\n',
  `CommodityName` varchar(255) DEFAULT NULL COMMENT '饰品全名',
  `CommodityHashName` varchar(255) DEFAULT NULL COMMENT '饰品hash名\n',
  `GroupHashName` varchar(255) DEFAULT NULL COMMENT '饰品分组名\n',
  `IconUrl` varchar(255) DEFAULT NULL COMMENT '图片\n',
  `TypeName` varchar(255) DEFAULT NULL COMMENT '类型名称',
  `Exterior` varchar(255) DEFAULT NULL COMMENT '外观信息',
  `Rarity` varchar(255) DEFAULT NULL COMMENT '稀有度',
  `Quality` varchar(255) DEFAULT NULL COMMENT '质量\n',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`) USING BTREE,
  KEY `name` (`CommodityName`) USING BTREE,
  KEY `groupName` (`GroupHashName`) USING BTREE,
  KEY `id_name_groupName` (`id`,`CommodityName`,`GroupHashName`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=104318 DEFAULT CHARSET=utf8;`
  


-- 账号token缓存表 （全自动接码创建账号并存储到表中，缓存过期自动执行登陆）
`CREATE TABLE `youpin_phone_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mobile` varchar(255) DEFAULT NULL,
  `token` varchar(5000) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8;`


## 1.2饰品的在售、出租、求购的价格和数量（es存储）
定时任务30分钟爬取一次所有商品的数据（大概1w5），考虑到是增量的爬取，所以用es进行存储，机器预计有一台先做单机存储，后续出现瓶颈再考虑优化或扩展。
1. 创建一个以"youpin_commodity_*"的索引模版，用于存储饰品数据。 （不同平台可以考虑不同的索引设计）
2. 为每个商品创建一个文档，文档包含商品的所有字段（重点：Timestamp使用的是时间戳，会有坑）。  
3.  使用ES的聚合功能来计算每小时饰品数据的统计信息，如平均价格、最低价格等。 
4. 2分片，2副本应该差不多，先不考虑分布式。
1. 创建名为"youpin_commodity_*"的索引：
PUT _template/youpin_commodity
{
  "index_patterns": ["youpin_commodity_*"],
  "settings": {
    "number_of_shards": 2, 
    "number_of_replicas": 2
  },
  "mappings": {
    "properties": {
      "minReferencePrice": {
        "type": "integer"
      },
      "Id": {
        "type": "integer"
      },
      "CommodityName": {
        "type": "text"
      },
      "CommodityHashName": {
        "type": "text"
      },
      "GroupHashName": {
        "type": "text"
      },
      "IconUrl": {
        "type": "text"
      },
      "MinPrice": {
        "type": "float"
      },
      "LeaseUnitPrice": {
        "type": "float"
      },
      "LongLeaseUnitPrice": {
        "type": "float"
      },
      "LeaseDeposit": {
        "type": "integer"
      },
      "LeasePriceScale": {
        "type": "float"
      },
      "OnSaleCount": {
        "type": "integer"
      },
      "OnLeaseCount": {
        "type": "integer"
      },
      "TypeName": {
        "type": "text"
      },
      "Rarity": {
        "type": "text"
      },
      "Quality": {
        "type": "text"
      },
      "Exterior": {
        "type": "text"
      },
	  "Timestamp": {
		"type": "date"
      }
    }
  }
}
2. 插入商品数据：（索引确定某天时间，存储时间使用时间戳）
PUT /youpin_commodity_2023.6.23/_doc/2
{
  "minReferencePrice": 35449,
  "Id": 1627,
  "CommodityName": "AK-47 | 二西莫夫 (略有磨损)",
  "CommodityHashName": "AK-47 | Asiimov (Minimal Wear)",
  "GroupHashName": "AK-47 | Asiimov",
  "IconUrl": "https://youpin.img898.com/economy/image/7ed3a58260a511ec86c8dca9049909c3",
  "MinPrice": 3553,
  "LeaseUnitPrice": 0.47,
  "LongLeaseUnitPrice": 0.35,
  "LeaseDeposit": 356,
  "LeasePriceScale": null,
  "OnSaleCount": 2027,
  "OnLeaseCount": 345,
  "TypeName": "步枪",
  "Rarity": "隐秘",
  "Quality": "普通",
  "Exterior": "略有磨损",
  "Timestamp": "1686757564550"
}
3. 搜索商品数据：
POST /commodity/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "CommodityName": "二西莫夫"
          }
        },
        {
          "match": {
            "Exterior": "略有磨损"
          }
        }
      ]
    }
  },
  "sort": [
    {
      "SteamPrice": {
        "order": "asc"
      }
    }
  ],
  "size": 10,
  "from": 0
}
## 1.3 token记录（不同平台对应自己的token表）

`
CREATE TABLE `youpin_phone_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mobile` varchar(255) DEFAULT NULL,
  `token` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8;`

平台对接api：
根网址（baseUrl）：
http://ysqdouyin.online/open-api/
接口组成为：【根网址】/【接口名】?【参数】
示例：
http://ysqdouyin.online/open-api/getToken?username=zhangsan&password=123
接口名	参数	说明
getToken	username：必填，用户名 password：必填，密码	根据用户名和密码获取到永久使用的token，调用其他接口时均需要携带此token，此接口每个用户每10分钟只能调用1次，请勿每次调用其他接口时都要重新获取一遍token，用户的token获取后是不会过期的，当再一次调用getToken接口时，之前获取的token便会失效，用户名和密码为在平台中注册的用户名和密码
getPhone	token：必填，调用getToken接口获得到的token，proj：选填，关键词，如果填写则会根据传入的值进行过滤号码，否则可能会出现获取到之前已经获取过的号码，比如传入为“陌陌”那么就不会获取到之前已经获取到过陌陌验证码的手机号了	随机获取一个手机号，后面可根据这个手机号来获取对应的验证码,此接口每个ip有2秒钟调用限制
getMsg	token：必填，调用getToken接口获得到的token，phoneNo：必填，传入使用getPhone接口获取到的手机号，proj：必填，传入要获取验证码的关键字	根据手机号和关键字获取验证码,调用此接口成功获取到验证码后会进行扣除一条短信，和平台一致,此接口每个ip有2秒钟调用限制
在集成接码平台后，每一个手机号获取的token要记录下来，后期批量使用。

### 1.3.1 悠悠有品接码流程（已经实现自动化接码，自动检测过期，自动获取新token和自动注册）
1. 接码获取接码平台手机号
2. 调用悠悠发送验证码
3. 接码平台获取当前手机号验证码
4. 调悠悠接口注册
5. 注册后调接口修改密码，之后就不需要接码了
6. 如以上步骤都成功，则将信息存入数据库
7. 往后token过期（最多10天），直接查数据库获取手机号密码调接口，即可。
1.4后端数据流转图

1.5前端展示？（待定）
1.6预测算法实现（待定）
# 2.爬取整体思路设计
## 2.1所有饰品模版（python）
1. 老思路，分析接口，记录于（apifox）。
2. 爬取过程就不写了，老思路，直接调接口（注意：请求前尽量先查数据库，若不存在再去请求，减少链接次数）
3. 优化设计：启动多线程并发分页爬取，数据库使用连接池保持持续落库。
2.2饰品的在售、出租、求购的价格和数量（es,定好饰品模版，根据模版创建对应索引，索引带上时间）
1. 遍历数据库所有的模版id，多线程去请求并写入es（看情况是否需要消息队列去减少链接，若单体服务顶不住可能得弄集群）
2. 需要支持：1.多账号，2.多代理，3.爬取间隔=最小熔断时间
3. 
# 3.反爬机制的处理
## 3.1多账号请求 （单账号多线程速度太快会被限流）
利用接码平台注册多个账号，并提取token，多线程多个token进行请求（还不知道ip是否会影响，若影响则需要每个账号一个代理）
全自动接码创建账号并存储到表中，缓存过期自动执行。
## 3.2ip代理
暂时未出现，若出现封ip现象，则可能进行接口ip隔离，利用ip池等解决

## 3.3请求熔断机制
目前也仅仅发现是针对账号的qps做的限流

# 4.目前问题
## 4.1 项目运行没问题，过几天后会卡住，有可能造成了死锁
解决方案：看是否能找出死锁的现场，或者对用锁的地方try catch，利用finaly释放锁，实在不行就只能去掉锁。

**已经解决**:调整了锁后，不再出现死锁现象。
## 4.2 项目一个月后数据达到3000w条，而且服务器承受不住es很慢，内存、cpu、硬盘都干满了。
解决方案：项目改造，不做全饰品爬取，做成少量饰品监听的自动交易策略系统（自用），这样可以不用es用mysql就可以了，后续再拓展。

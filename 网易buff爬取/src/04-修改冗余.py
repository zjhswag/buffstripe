import concurrent.futures
import gc
import json
import logging

import requests
import os
import urllib3
from function import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

start_time = int(time.time() * 1000)

# 导入枪和查找适合的磨损区间
json_file_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'merged_data.json')
with open(json_file_path, 'r', encoding='utf-8') as f:
    buy_guns = json.load(f)

# 接收notification的响应头传给市场请求头的cookie,修改请求参数的地方,wearcategory2
market_params = {
    "game": "csgo",
    "page_num": "1",
    "max_price": "300",
    # legendary_weapon,legendary_weapon
    # legendary_weapon是保密，ancient是隐秘，剩下一个是受限
    "rarity": "mythical_weapon,legendary_weapon,legendary_weapon",
    "quality": "normal,strange",
    "exterior": "wearcategory0,wearcategory1",
    "tab": "selling",
    "use_suggestion": "0",
    "_": int(time.time() * 1000)
}
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("csgo_gun.log", encoding='utf-8'),
                    ])

logger = logging.getLogger(__name__)
i = 0
while True:
    i += 1
    # 通过csgo_url给notification接口产生csrf和session
    res = requests.get(url=csgo_url, headers=headers_csgo)

    # 获取csrf_token，通过notification接口，不需要自带csrf_token
    cf1, sid1 = get_csrf(res)

    # 传递产生的csrf和session给notification接口
    new_headers = update_headers_with_csrf(headers, cf1, sid1)

    # 传递notification产生的csrf和session给市场接口
    res2 = requests.get(url=notification_url, headers=new_headers, params=base_params)

    # 传递给市场刷新接口
    cf2, sid2 = get_csrf(res2)
    new_headers = update_headers_with_csrf(headers, cf2, sid2)

    # 防止请求过快
    time.sleep(5)
    f1 = time.time() * 1000

    # 市场刷新接口，传入参数为崭新，略磨，皮肤隐秘程度，设置价格等
    # first_url = "https://buff.163.com/api/market/goods?"
    res3, data, new_headers = try_again(new_headers, first_url, market_params)

    if data is not None:
        # 存储市场接口返回来最新枪的数据，枪名，最低价格，在售数量
        guns = []
        for item in data:
            gun = {
                'name': item.get('name', None),
                'sell_min_price': item.get('sell_min_price', None),
                'sell_num': item.get('sell_num', None),
                'id': item.get('id', None)
            }
            guns.append(gun)
        # print("本次查询到的枪为:", guns[:6])

        # 买枪函数
        def query_gun(gun, head):
            try:
                retries = 0
                max_retries = 5
                delay = 1
                gun_id = gun['id']
                name = gun['name']
                buy_paint = search_wearpaint(name, buy_guns)
                buy_base_url = f'https://buff.163.com/goods/{gun["id"]}?'

                res4 = requests.get(url=buy_base_url, headers=head,
                                    params=query_params)  # 根据id,差不多是notification的作用,得到csrf和session
                cf4, sid4 = get_csrf(res4)
                new_headers = update_headers_with_csrf(headers, cf4, sid4)

                search_params = {"game": "csgo",
                                 "goods_id": f"{gun_id}",
                                 "page_num": "1",
                                 "sort_by": "default",
                                 "mode": "",
                                 "allow_tradable_cooldown": "1",
                                 "_": int(time.time() * 1000)
                                 }

                res5, data, new_headers = try_again(new_headers, search_url, search_params)
                st_price = res5.json()['data']["goods_infos"][f"{gun_id}"]['steam_price_cny']
                if data is not None and buy_paint is not None:
                    for item in data[:6]:
                        paintwear = item['asset_info']['paintwear']
                        paintwear = float(paintwear)
                        price = float(item['price'])  # 购买价格
                        sell_id = item['id']
                        alipay_error = None
                        bank_error = None
                        sp, st = decide_buy(gun['sell_min_price'], st_price)
                        if price <= sp and price <= st:
                            if paintwear <= buy_paint:
                                buy_params = {"game": "csgo",
                                              "sell_order_id": f"{sell_id}",
                                              "goods_id": f"{gun_id}",
                                              "price": f"{price}",
                                              "allow_tradable_cooldown": "0",
                                              "cdkey_id": "",
                                              "_": int(time.time() * 1000)
                                              }
                                res6 = requests.get(url=buy_url, headers=new_headers, params=buy_params)  # 获取支付方式接口
                                cf6, sid6 = get_csrf(res6)
                                new_headers = update_headers_with_csrf(headers, cf6, sid6)
                                new_headers["X-Csrftoken"] = cf6
                                methods = res6.json()['data']['pay_methods']  # 获取到的支付方式,寻找合适的购买方式的皮肤
                                for method in methods:
                                    if method['name'] == '支付宝支付':
                                        alipay_error = method['error']
                                    elif method['name'] == 'BUFF余额-银行卡':
                                        bank_error = method['error']
                                if alipay_error != "该饰品暂不支持此支付方式":
                                    buy_params_last = {
                                        "game": "csgo",
                                        "goods_id": f"{gun_id}",
                                        "sell_order_id": f"{sell_id}",
                                        "price": f"{price}",
                                        "pay_method": f'{49}',  # 支付方式
                                        "allow_tradable_cooldown": "0",
                                        "token": "",
                                        "cdkey_id": "",
                                        "hide_non_epay": "false"
                                    }
                                    res7 = requests.post(url=buy_last, headers=new_headers, json=buy_params_last)  # 支付结束
                                    logger.info(f'购买成功{name},{paintwear},{res7},{res7.text}')
                                    print(res7.json())

                                elif bank_error != "该饰品暂不支持此支付方式":
                                    buy_params_last = {
                                        "game": "csgo",
                                        "goods_id": f"{gun_id}",
                                        "sell_order_id": f"{sell_id}",
                                        "price": f"{price}",
                                        "pay_method": f'{1}',  # 支付方式
                                        "allow_tradable_cooldown": "0",
                                        "token": "",
                                        "cdkey_id": "",
                                        "hide_non_epay": "false"
                                    }
                                    res7 = requests.post(url=buy_last, headers=new_headers, json=buy_params_last)  # 支付结束
                                    logger.info(f'购买成功{name},{paintwear},{res7},{res7.text}')
                                    print(res7.json())
                                else:
                                    print(f"没有合适的支付方式,可买的枪为{gun['name']},磨损: {paintwear}, 价格: {price}")
                            else:
                                logger.info(f'磨损不合适{name},磨损为{paintwear},可买最大磨损为{buy_paint}')
                        else:
                            logger.info(
                                f"该枪支: {name}不可购买,价格不合适价格: {price},上限{sp},steam处理价格{st}")
                            continue

                return gun['name'], gun['sell_min_price']
            except requests.RequestException as e:
                return str(e)


        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_gun = {executor.submit(query_gun, gun, new_headers): gun for gun in guns[:4]}
            for future in concurrent.futures.as_completed(future_to_gun):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    # print("moo")
                    logger.error(f'Generated an exception: {exc}')

        last_time = int(time.time() * 1000)
        print(f"这是第{i}次刷新:")
        print('程序查询时间为:', last_time - f1, 'ms')
        print('程序运行时间为:', last_time - start_time, 'ms')

    if i % 400 == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('清空控制台')
    del guns
    del results
    del data
    gc.collect()


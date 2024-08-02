"""
1.设定按照保密，隐秘，军规，受限，崭新，略磨，酒精，暗金，普通
2. 接口参数
    1.4*2*3 = 24 个文件，设计传入3个参数，paint,rare,kind，不传的话默认为null
    2.价格参数，从多少开始查，以及按照什么排列
3.一次查一
4.json里面保存查的最大磨损，或者为no
5.怎么样算完成？
"""
import json
import os
import re
import time
from lxml import etree

import requests

market_url = "https://buff.163.com/api/market/goods?"  # 首页面
notification = "https://buff.163.com/api/message/notification?"
search_gun = "https://buff.163.com/api/market/goods/sell_order?"
market_header = {
    "Cookie": "Device-Id=3QkxxQrsLtKqchD4k3sQ; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=UrZNC_spvrT3N91QJ1gjqk8UYf4VfnKF5Ymn_ySB77.915ST1ltocJrH1XEACJmhO5_lfBaQ0p62FHoRYQIVwRV5yMQxD4.yrZ7fwmtUGblQoCQD7VBKNEBWIrlD7V5JmUtTzKu67czez5hQl1iV6kFlhJEwO7Z.2gJkxtkb5cYgHvXP2lhW5c74aSDtvsg8ydcSJmiq_FeeRWJUcm7ORM4jQwap8.Q2pqjXmIj0mME3r; S_INFO=1718866601|0|0&60##|16670494952; P_INFO=16670494952|1718866601|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|gNrj9KdjJjhslohwFqqauRzgYwRcDlGf;steam_verify_result=",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://buff.163.com/market/csgo",
    "Upgrade-Insecure-Requests": "1"
}
# 需要seid
no_head = {
    "Cookie": "Device-Id=3QkxxQrsLtKqchD4k3sQ; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=UrZNC_spvrT3N91QJ1gjqk8UYf4VfnKF5Ymn_ySB77.915ST1ltocJrH1XEACJmhO5_lfBaQ0p62FHoRYQIVwRV5yMQxD4.yrZ7fwmtUGblQoCQD7VBKNEBWIrlD7V5JmUtTzKu67czez5hQl1iV6kFlhJEwO7Z.2gJkxtkb5cYgHvXP2lhW5c74aSDtvsg8ydcSJmiq_FeeRWJUcm7ORM4jQwap8.Q2pqjXmIj0mME3r; S_INFO=1718866601|0|0&60##|16670494952; P_INFO=16670494952|1718866601|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|gNrj9KdjJjhslohwFqqauRzgYwRcDlGf; session=1-wV4Lo0_nKodSTjj1-x0R6MQy7mfjgu48p-xY7CGVBTHM2043728555; steam_verify_result=",
    "Referer": "https://buff.163.com/market/sell_order/on_sale?game=csgo&mode=2,5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
search_header = {
    "Cookie": "Hm_lvt_f8682ef0d24236cab0e9148c7b64de8a=1709623940; vinfo_n_f_l_n3=801eba530a3c1593.1.1.1709623939065.1709624085379.1709631285413; Device-Id=x6E3DzVuXF8y73bMsSwB; _ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; timing_user_id=time_xDEGX9zJ51; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=mRPEAxw0LmfaZbFd3a873ux59gOgjvpj9LeArKiEwwfjhziQhoRng7uIhvST17edWzroxE2bM6D_YInHLb5yqHyzKcbZaFfKuPwxqeRmVpobn1bawyE.lSE95uoawyz7emRQ3.4Dwg3N3zdbohGyDXYod7SqWwPf_B7XZRXpzgLJEGOy5i3kpbpAUtL1AI.HWJ55KkbmDz.ONOqCexBdcNFtbq26Jfb_6Otve5tMecSUu; S_INFO=1718541027|0|0&60##|16670494952; P_INFO=16670494952|1718541027|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|hGuodAt4tonQdepucPv4uQkMThobuTLg; to_steam_processing_click240616T00846138521=1; steam_verify_result=",
    "Referer": "https://buff.163.com/goods",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
gun_url_header = {
    "Cookie": "Hm_lvt_f8682ef0d24236cab0e9148c7b64de8a=1709623940; vinfo_n_f_l_n3=801eba530a3c1593.1.1.1709623939065.1709624085379.1709631285413; Device-Id=x6E3DzVuXF8y73bMsSwB; _ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; timing_user_id=time_xDEGX9zJ51; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=mRPEAxw0LmfaZbFd3a873ux59gOgjvpj9LeArKiEwwfjhziQhoRng7uIhvST17edWzroxE2bM6D_YInHLb5yqHyzKcbZaFfKuPwxqeRmVpobn1bawyE.lSE95uoawyz7emRQ3.4Dwg3N3zdbohGyDXYod7SqWwPf_B7XZRXpzgLJEGOy5i3kpbpAUtL1AI.HWJ55KkbmDz.ONOqCexBdcNFtbq26Jfb_6Otve5tMecSUu; S_INFO=1718541027|0|0&60##|16670494952; P_INFO=16670494952|1718541027|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|hGuodAt4tonQdepucPv4uQkMThobuTLg; to_steam_processing_click240616T00846138521=1; steam_verify_result=",
    "Referer": "https://buff.163.com/market/csgo",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}


def get_csrf(res):
    """
    提取csrf_token，
    # 保持健壮性应该如下：
        # print(cookies)
        # for cookie in cookies:
        #     if 'csrf_token' in cookie:
        # break
    """
    # print('headers:',res.headers)
    set_cookie_header = res.headers.get('set-cookie')
    ct = None
    session = None
    if set_cookie_header:
        cookies = set_cookie_header.split(';')
        # print(cookies[0])
        ct = cookies[2].split('=')[2]
        session = cookies[0].split('=')[1]
        # print('session:',session,'cookie:',ct)
    return ct, session

    # '保密普通久经.json', '保密普通崭新.json'


# '保密普通略磨.json',
# '保密暗金久经.json', '保密暗金崭新.json', '保密暗金略磨.json'
#  '保密普通久经.json', '保密普通崭新.json', '保密普通略磨.json'
# ,
    # '隐秘普通久经.json', '隐秘普通崭新.json', '隐秘普通略磨.json',
    # '隐秘暗金久经.json', '隐秘暗金崭新.json', '隐秘暗金略磨.json'
    # '保密暗金久经.json', '保密暗金崭新.json', '保密暗金略磨.json',
    # '受限暗金久经.json', '受限暗金崭新.json', '受限暗金略磨.json'
json_files = [
    # '保密普通久经.json', '保密普通崭新.json', '保密普通略磨.json',
    # '受限普通久经.json', '受限普通崭新.json', '受限普通略磨.json',
    # '保密暗金久经.json', '保密暗金崭新.json', '保密暗金略磨.json',
    # '受限暗金久经.json', '受限暗金崭新.json', '受限暗金略磨.json'
    "军规普通崭新.json","军规暗金崭新1.json"
]

base_path = os.path.join(os.path.dirname(__file__), '..', 'dist')
for json_file in json_files:
    json_file_path = os.path.join(base_path, json_file)
    print('正在弄',json_file)
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            no_buy_guns = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        no_buy_guns = {}


# ancient_weapon ---隐秘
# normal --- 普通
# wearcategory0 --- 崭新
# 根据选择设定参数
    try:
        if "隐秘" in json_file:
            rare = "ancient_weapon"
        elif "保密" in json_file:
            rare = "legendary_weapon"
        elif "受限" in json_file:
            rare = "mythical_weapon"
        else:
            rare = "rare_weapon"
        kind = 'normal' if "普通" in json_file else 'strange'
        if "崭新" in json_file:
            paint = "wearcategory0"
        elif "略磨" in json_file:
            paint = "wearcategory1"
        else:
            paint = "wearcategory2"

        print(rare, kind, paint)
        count = 1
        set_price = 90
        set_max = 100
        no_pa = {
            "_": int(time.time() * 1000)
        }
        market_params = {
            "game": "csgo",
            "page_num": f"{count}",
            "min_price": f'{set_price}',
            "max_price": f'{set_max}',
            "rarity": f"{rare}",
            "quality": f"{kind}",
            "exterior": f"{paint}",
            "sort_by": "price.asc",
            "tab": "selling",
            "use_suggestion": "0",
            "_": int(time.time() * 1000)
        }
        gun_params = {
            "from": "market"
        }
        res2 = requests.get(url=notification, headers=no_head, params=no_pa)
        cf2, sid2 = get_csrf(res2)
        new_headers = market_header.copy()
        new_headers["Cookie"] = market_header["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"

        res = requests.get(url=market_url, headers=new_headers, params=market_params)

        total_count = int(res.json()["data"]["total_count"])
        total_page = int(res.json()["data"]["total_page"])
        print(total_count, total_page)

        search_count = 0
        for i in range(total_page):
            print(f'查询第{i + 1}页')
            market_params = {
                "game": "csgo",
                "page_num": f"{i + 1}",
                "min_price": f'{set_price}',
                "max_price": f'{set_max}',
                "rarity": f"{rare}",
                "quality": f"{kind}",
                "exterior": f"{paint}",
                "sort_by": "price.asc",
                "tab": "selling",
                "use_suggestion": "0",
                "_": int(time.time() * 1000)
            }
            res2 = requests.get(url=notification, headers=no_head, params=no_pa)
            cf2, sid2 = get_csrf(res2)
            new_headers = market_header.copy()
            new_headers["Cookie"] = market_header["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"

            res = requests.get(url=market_url, headers=new_headers, params=market_params)
            data = res.json()["data"]["items"]
            guns = []
            for item in data:
                gun = {
                    'name': item.get('name', None),
                    'sell_min_price': item.get('sell_min_price', None),
                    'id': item.get('id', None)
                }
                guns.append(gun)

            for gun in guns:
                time.sleep(0.5)
                search_count += 1
                sell_min = float(gun["sell_min_price"])
                print('正在查询第', search_count, "个", gun['name'], '在售最低为', sell_min)
                res2 = requests.get(url=notification, headers=no_head, params=no_pa)
                cf2, sid2 = get_csrf(res2)

                new_headers = gun_url_header.copy()
                new_headers["Cookie"] = gun_url_header["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"
                gun_url = f"https://buff.163.com/goods/{gun['id']}?"
                res = requests.get(url=gun_url, headers=new_headers, params=gun_params)
                pattern = re.compile(r'paintwear_choices: (\[\[.*?\]\])', re.DOTALL)
                match = pattern.search(res.text)
                if match:
                    paintwear_choices_str = match.group(1)
                    paintwear_choices = json.loads(paintwear_choices_str)
                else:
                    print("No paintwear_choices found in the HTML content.")

                cf2, sid2 = get_csrf(res)
                if paint == "wearcategory0":
                    no_buy_guns[gun["name"]] = '0.001'
                else:
                    no_buy_guns[gun["name"]] = 'no'

                new_headers = search_header.copy()
                new_headers["Cookie"] = search_header["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"
                for paintwear_choice in paintwear_choices:
                    max_retries = 3  # 最大重试次数
                    delay = 1  # 初始延迟时间，单位为秒
                    retries = 0
                    search_params = {
                        "game": "csgo",
                        "goods_id": f"{gun['id']}",
                        "page_num": "1",
                        "sort_by": "default",
                        "mode": "",
                        "allow_tradable_cooldown": "1",
                        "min_paintwear": f"{paintwear_choice[0]}",
                        "max_paintwear": f"{paintwear_choice[1]}",
                        "_": int(time.time() * 1000)
                    }
                    print(paintwear_choice[0],paintwear_choice[1])
                    while retries < max_retries:
                        try:
                            res = requests.get(url=search_gun, headers=new_headers, params=search_params)
                            data = res.json().get('data', {}).get('items', [])
                            if data:
                                sell_price = float(data[0]['price'])
                                break  # 成功获取数据，跳出循环
                        except json.JSONDecodeError as e:
                            print(f"JSONDecodeError: {e}")
                            print("Response text:", res.text)

                        retries += 1
                        print(f"太快了,Retrying... ({retries}/{max_retries})")
                        time.sleep(delay)
                        time.sleep(12)
                        delay *= 2  # 指数退避
                        print(delay)
                    if retries == max_retries:
                        print(f"Failed to get data for after {max_retries} retries.")
                        no_buy_guns[gun["name"]] = 'no_search'
                        sell_price = 0
                        break

                    ration = (sell_price - sell_min) / sell_price * 100
                    print(gun['name'], paintwear_choice, sell_price, ration)
                    time.sleep(1)  # 每个请求之间的延迟，避免过于频繁
                    if sell_price <= 2:
                        if ration > 31:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 2 < sell_price <= 3:
                        if ration > 30:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 3 < sell_price <= 10:
                        if ration > 30:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 10 < sell_price <= 15:
                        if ration > 25:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 15 < sell_price <= 20:
                        if ration > 20:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 20 < sell_price <= 30:
                        if ration > 18:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 30 < sell_price <= 50:
                        if ration > 16:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 50 < sell_price <= 90:
                        if ration > 14:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 80 < sell_price <= 100:
                        if ration > 10:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    elif 100 < sell_price <= 200:
                        if ration > 8:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
                    else:
                        if ration > 7.85:
                            no_buy_guns[gun["name"]] = paintwear_choice[1]
                        else:
                            print("no")
                            break
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(no_buy_guns, f, ensure_ascii=False, indent=4)
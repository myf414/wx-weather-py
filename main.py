import requests
from datetime import datetime, date
import random

# ========== 配置区 ==========
# 高德城市编码 西昌:513401 越西:513434
CITY_CODE = "513401"
# 高德天气key
AMAP_KEY = ""
# 多人生日列表，格式：{"name":"名字","birthday":"MM-DD"}
BIRTHDAY_LIST = [
    {"name": "毛", "birthday": "5-25"},
    {"name": "赵", "birthday": "08-20"},
]
# 每日随机英文短句
SENTENCES = [
    {"en":"They who cannot do as they would, must do as they can.","ch":"不能如愿而行，也须尽力而为。"},
    {"en":"The best preparation for tomorrow is doing your best today.","ch":"对明天做好的准备就是今天做到最好。"},
    {"en":"Keep on going never give up.","ch":"勇往直前，决不放弃。"}
]
# ============================

def get_weather(city_code, amap_key):
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city_code}&key={amap_key}&extensions=base"
    resp = requests.get(url).json()
    print("高德返回数据：",resp)
    if resp["status"] != "1":
        raise Exception("高德天气请求失败！")
    live = resp["lives"][0]
    data = {}
    data["city_name"] = live["city"]
    data["weather"] = live["weather"]
    data["now_temp"] = live["temperature"]
    data["wind_dir"] = live["winddirection"]
    data["max_temp"] = live["temperature"]
    data["min_temp"] = live["temperature"]
    return data

def calc_birthday_countdown(birthday_list):
    today = date.today()
    res_text = ""
    for item in birthday_list:
        m,d = map(int, item["birthday"].split("-"))
        b_day = date(today.year, m, d)
        if b_day < today:
            b_day = date(today.year+1, m, d)
        days = (b_day - today).days
        res_text += f"距离{item['name']}的生日还有{days}天\n"
    return res_text.strip()

def calc_china_day():
    start = date(1949,10,1)
    today = date.today()
    return (today - start).days

def get_random_sentence():
    return random.choice(SENTENCES)

def push_pushplus(token, title, content):
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": "html"
    }
    res = requests.post(url, json=payload)
    return res.json()

if __name__ == "__main__":
    import os
    amap_key = os.environ["AMAP_KEY"]
    ptoken = os.environ["PUSHPLUS_TOKEN"]

    weather_data = get_weather(CITY_CODE, amap_key)
    birthday_text = calc_birthday_countdown(BIRTHDAY_LIST)
    china_day = calc_china_day()
    sen = get_random_sentence()

    today_str = datetime.now().strftime("%Y-%m-%d %A")
    msg_content = f"""
<span style="color:#995522">{today_str}</span>
地区(┌・ω・┐)：{weather_data['city_name']}
天气(◍•ᴗ•◍)：{weather_data['weather']}
当前气温：{weather_data['now_temp']}℃
当前风向：{weather_data['wind_dir']}
今天是新中国成立的第{china_day}天
{birthday_text}
今日建议：{weather_data['weather']}，天气炎热，建议停止户外运动，选择在室内进行低强度运动。

<span style="color:#bb8822">{sen['en']}</span>
<span style="color:#bb8822">{sen['ch']}</span>
"""
    push_pushplus(ptoken, "☁今日天气", msg_content)
    print("推送完成")

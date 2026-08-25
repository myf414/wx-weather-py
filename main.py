import requests
from datetime import datetime, date

# ========== 配置区 ==========
# 城市ID，和风天气城市ID，越西县：101272706
CITY_ID = "101272706"
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

def get_weather(city_id, key):
    # 获取实时天气
    now_url = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={key}"
    # 获取日出日落
    astro_url = f"https://devapi.qweather.com/v7/astronomy/sun?location={city_id}&key={key}"
    # 获取空气质量
    air_url = f"https://devapi.qweather.com/v7/air/now?location={city_id}&key={key}"

    resp_now = requests.get(now_url).json()
    resp_astro = requests.get(astro_url).json()
    resp_air = requests.get(air_url).json()

    data = {}
    data["city_name"] = resp_now["location"]["name"]
    data["weather"] = resp_now["now"]["text"]
    data["now_temp"] = resp_now["now"]["temp"]
    data["feels_like"] = resp_now["now"]["feelsLike"]
    data["wind_dir"] = resp_now["now"]["windDir"]
    data["sunrise"] = resp_astro["sunrise"]
    data["sunset"] = resp_astro["sunset"]
    data["pm25"] = resp_air["now"]["pm2p5"]
    data["air_quality"] = resp_air["now"]["category"]
    # 取当日最高最低
    data["max_temp"] = resp_now["now"]["temp"]
    data["min_temp"] = resp_now["now"]["temp"]

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
    # 新中国成立 1949‑10‑01
    start = date(1949,10,1)
    today = date.today()
    return (today - start).days

def get_random_sentence():
    import random
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
    qkey = os.environ["QWEATHER_KEY"]
    ptoken = os.environ["PUSHPLUS_TOKEN"]

    weather_data = get_weather(CITY_ID, qkey)
    birthday_text = calc_birthday_countdown(BIRTHDAY_LIST)
    china_day = calc_china_day()
    sen = get_random_sentence()

    today_str = datetime.now().strftime("%Y-%m-%d %A")
    # 消息内容，和截图排版保持一致，支持emoji
    msg_content = f"""
<span style="color:#995522">{today_str}</span>
地区(┌・ω・┐)：{weather_data['city_name']}
天气(◍•ᴗ•◍)：{weather_data['weather']}
最低气温：{weather_data['min_temp']}℃
最高气温：{weather_data['max_temp']}℃
当前气温：{weather_data['now_temp']}℃
当前风向：{weather_data['wind_dir']}
pm2.5值：{weather_data['pm25']}
空气质量：{weather_data['air_quality']}
日出时间：{weather_data['sunrise']}
日落时间：{weather_data['sunset']}
今天是新中国成立的第{china_day}天
{birthday_text}
今日建议：{weather_data['weather']}，天气炎热，建议停止户外运动，选择在室内进行低强度运动。

<span style="color:#bb8822">{sen['en']}</span>
<span style="color:#bb8822">{sen['ch']}</span>
"""
    push_pushplus(ptoken, "☁今日天气", msg_content)
    print("推送完成")

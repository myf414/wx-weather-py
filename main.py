import requests
from datetime import datetime, date
import random
import os

# ========== 配置区 ==========
CITY_CODE = "513401"

BIRTHDAY_LIST = [
    {"name": "毛", "birthday": "12-20"},
    {"name": "赵", "birthday": "09-08"},
]

SENTENCES = [
    {"en": "They who cannot do as they would, must do as they can.", "ch": "不能如愿而行，也须尽力而为。"},
    {"en": "The best preparation for tomorrow is doing your best today.", "ch": "对明天做好的准备就是今天做到最好。"},
    {"en": "Keep on going never give up.", "ch": "勇往直前，决不放弃。"}
]
# ============================


def get_weather(city_code, amap_key):
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city_code}&key={amap_key}&extensions=base"
    resp = requests.get(url).json()
    print("高德返回数据：", resp)
    if resp["status"] != "1":
        raise Exception("高德天气请求失败！")
    live = resp["lives"][0]
    data = {
        "city_name": live["city"],
        "weather": live["weather"],
        "now_temp": live["temperature"],
        "wind_dir": live["winddirection"],
        # 高德base接口没有最高最低温、pm2.5、日出日落，这里先留占位
        "temp_low": "29",
        "temp_high": "40",
        "pm25": "17",
        "aqi": "优",
        "sunrise": "06:14",
        "sunset": "19:15"
    }
    return data


def calc_birthday_countdown(birthday_list):
    today = date.today()
    res_text = ""
    for item in birthday_list:
        m, d = map(int, item["birthday"].split("-"))
        b_day = date(today.year, m, d)
        if b_day < today:
            b_day = date(today.year + 1, m, d)
        days = (b_day - today).days
        res_text += f"<span style='color:#994477'>距离{item['name']}的生日还有{days}天</span><br>"
    return res_text.strip()


def calc_china_day():
    start = date(1949, 10, 1)
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
    print("PushPlus返回：", res.json())
    return res.json()


if __name__ == "__main__":
    amap_key = os.environ["AMAP_KEY"]
    push_token = os.environ["PUSHPLUS_TOKEN"]

    weather_data = get_weather(CITY_CODE, amap_key)
    birthday_text = calc_birthday_countdown(BIRTHDAY_LIST)
    china_day = calc_china_day()
    sen = get_random_sentence()

    today_str = datetime.now().strftime("%Y-%m-%d %A")

    msg_content = f"""
<div style="font-size:16px;line-height:1.8;">
<span style="color:#995522">{today_str}</span><br>
<span>地区(┌・ω・┐)：</span><span style="color:#228822">{weather_data['city_name']}</span><br>
<span>天气(◍•ᴗ•◍)：</span><span style="color:#772299">{weather_data['weather']}</span><br>
<span>最低气温：</span><span style="color:#2288bb">{weather_data['temp_low']}℃</span><br>
<span>最高气温：</span><span style="color:#dd4422">{weather_data['temp_high']}℃</span><br>
<span>当前气温：</span><span style="color:#2288bb">{weather_data['now_temp']}℃</span><br>
<span>当前风向：</span><span style="color:#2288bb">{weather_data['wind_dir']}</span><br>
<span>pm2.5值：</span><span style="color:#224488">{weather_data['pm25']}</span><br>
<span>空气质量：</span><span style="color:#772299">{weather_data['aqi']}</span><br>
<span>日出时间：</span><span style="color:#224488">{weather_data['sunrise']}</span><br>
<span>日落时间：</span><span style="color:#224488">{weather_data['sunset']}</span><br>
<span>今天是新中国成立的第</span><span style="color:#223388">{china_day}</span><span>天</span><br>
{birthday_text}
<span>今日建议：</span><span style="color:#552299">阴，且天气炎热，建议停止户外运动，进行低强度运动。</span><br><br>
<span style="color:#bb9944">{sen['en']}</span><br>
<span style="color:#bb9944">{sen['ch']}</span>
</div>
"""

    push_pushplus(push_token, "☁今日天气", msg_content)
    print("推送完成")

import requests
from datetime import datetime, date
import random
import os

# =====================【配置区，修改这里】=====================
CITY_CODE = "513434"          # 当前城市高德编码
HOME_CITY_CODE = "513434"     # 家乡城市高德编码
LOVE_DATE = date(2024, 6,15)  # 你们恋爱第一天，格式：年,月,日
BIRTHDAY_LIST = [
    {"name": "毛dear", "birthday": "05-25"},
]
# 节假日日期（公历）
NEW_YEAR = date(2027, 1, 1)    # 元旦
SPRING_FESTIVAL = date(2027, 2, 6) # 春节
# 随机电影库
MOVIE_LIST = [
    {"name":"西线无战事","score":"8.6"},
    {"name":"星际穿越","score":"9.4"},
    {"name":"肖申克的救赎","score":"9.7"},
    {"name":"阿甘正传","score":"9.5"},
    {"name":"盗梦空间","score":"9.4"},
    {"name":"泰坦尼克号","score":"9.5"},
]
# 每日一句文案
SENTENCE_LIST = [
    "草在结它的种子，风在摇它的叶子，我们站着不说话，就十分美好。",
    "再冷的天你一笑我就暖了。",
    "玫瑰不用长高，晚霞自会俯腰，爱意随风奔跑，温柔漫过山腰。",
    "你若决定灿烂，山无遮，海无拦。",
    "勇敢的人先享受世界。"
]
# ==============================================================

def get_weather(city_code, amap_key):
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city_code}&key={amap_key}&extensions=base"
    resp = requests.get(url).json()
    print("高德返回数据：", resp)
    if resp["status"] != "1":
        raise Exception("高德天气请求失败！")
    # 修复点！lives是列表，必须 [0] 取出第一条数据
    if not resp["lives"]:
        raise Exception("没有查到天气数据！")
    live = resp["lives"][0]
    data = {
        "city_name": live["city"],
        "weather": live["weather"],
        "now_temp": live["temperature"],
        "wind_dir": live["winddirection"],
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

def calc_love_days():
    today = date.today()
    delta = today - LOVE_DATE
    return delta.days

def calc_day_diff(target_date):
    today = date.today()
    return (target_date - today).days

def get_random_movie():
    return random.choice(MOVIE_LIST)

def get_random_sentence():
    return random.choice(SENTENCE_LIST)

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
    push_token1 = os.environ["PUSHPLUS_TOKEN"]
    push_token2 = os.environ.get("PUSHPLUS_TOKEN2") # 第二个接收人，可选

    # 获取天气
    weather_now = get_weather(CITY_CODE, amap_key)
    weather_home = get_weather(HOME_CITY_CODE, amap_key)

    # 计算各种倒计时
    birthday_text = calc_birthday_countdown(BIRTHDAY_LIST)
    love_days = calc_love_days()
    day_newyear = calc_day_diff(NEW_YEAR)
    day_spring = calc_day_diff(SPRING_FESTIVAL)

    movie = get_random_movie()
    sentence = get_random_sentence()

    now_dt = datetime.now()
    today_str = now_dt.strftime("%Y-%m-%d %A")

    # 温馨提示文本
    temp = int(weather_now["now_temp"])
    if temp <= 10:
        tip = "[室外温度过低，记得多穿点衣服保暖]"
    elif temp >= 30:
        tip = "[天气炎热，注意防暑多喝水]"
    else:
        tip = "[天气适宜，保持好心情]"

    msg_content = f"""
<div style="font-size:16px;line-height:1.8;">
<span style="color:#22bb44">[记得晚上早点睡觉哈，然后做个好梦！]</span><br>
<span>把酒言欢的时候，你是否还在拼搏，秋风送爽的时候，你是否还在加班，我的关心，才最最珍贵，今夜我还在想着你入睡，晚安，亲爱的！</span><br>
<span>所在城市：</span><span style="color:#2288bb">{weather_now['city_name']}</span><br>
<span>当前时间：</span><span style="color:#2288bb">{now_dt.strftime("%Y-%m-%d %H:%M:%S")} {today_str}</span><br>
<span>今日天气：</span><span style="color:#772299">{weather_now['weather']}</span><br>
<span>今日风向：</span><span style="color:#2288bb">{weather_now['wind_dir']}</span><br>
<span>当前温度：</span><span style="color:#dd4422">{weather_now['now_temp']}℃</span><br>
<span style="color:#22bb44">{tip}</span><br>
{birthday_text}
<span style='color:#994477'>距离元旦还有{day_newyear}天</span><br>
<span style='color:#994477'>距离春节还有{day_spring}天</span><br>
<span style='color:#994477'>今天是我们恋爱的第{love_days}天</span><br>
===家乡:{weather_home['city_name']} 天气:{weather_home['weather']}===<br>
<span>今日评分最高电影：</span><span style="color:#bb44bb">{movie['name']}:{movie['score']}分</span><br>
<span>每日一句：</span><br>
<span style="color:#22bb44">{sentence}</span>
</div>
"""

    push_pushplus(push_token1, "☁今日天气", msg_content)
    if push_token2 is not None:
        push_pushplus(push_token2, "☁今日天气", msg_content)
    print("全部推送完成")

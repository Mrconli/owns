import requests
import time
import random
from datetime import datetime, timedelta

heartbeat_url = 'https://m.51daili.com/wap/user/index.html'
signin_url = 'https://m.51daili.com/wap/user/signin.html'

headers = {
    'Host': 'm.51daili.com',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Origin': 'https://m.51daili.com',
    'User-Agent': '',
    'Connection': 'keep-alive',
    'Referer': 'https://m.51daili.com/wap/user/index.html',
    'Content-Length': '2',
    'Cookie': '',
}

data = {}

def send_heartbeat():
    try:
        response = requests.post(heartbeat_url, json=data, headers=headers)
        print(f"{datetime.now()} - Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"{datetime.now()} - Error")

def send_signin():
    try:
        response = requests.post(signin_url, json=data, headers=headers)
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"{datetime.now()} - Error")
    except requests.RequestException as e:
        print(f"{datetime.now()} - Error")

def get_random_time():
    now = datetime.now()
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    random_time = now.replace(hour=random_hour, minute=random_minute, second=random_second)
    if random_time < now:
        random_time += timedelta(days=1)
    return random_time

next_random_run_time = get_random_time()
heartbeat_interval = 25 * 60

while True:
    now = datetime.now()
    
    if now >= next_random_run_time:
        send_signin()
        next_random_run_time = get_random_time()
    
    send_heartbeat()
    
    time.sleep(heartbeat_interval)

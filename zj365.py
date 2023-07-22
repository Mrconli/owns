'''
new Env("中健365")
每日签到领现金0.18，到账微信
入口：#小程序://中健365达人/vacWkbjhWEe5mSl
抓包：https://dc.zhongjian365.com/域名里面的 X-Auth-Key
变量名：zj365ck，多号 @ 隔开
cron 0 7 * * *
v1.0
'''

import datetime
from lib2to3.pygram import python_grammar_no_print_and_exec_statement
import os
import time
import random
import base64
import requests
import hashlib
import uuid
import json

now = str(round(time.time()*1000))
cookies= os.getenv("zj365ck")

class DY:
    def __init__(self, cookie):
        self.cookie = cookie.split("#")[0]
        

    def run(self):
        print(f"========开始进行今日签到========")
        point_ss , point_s = self.sign()
        print(f"签到奖励--状态码：{point_ss}")
        print(f"签到奖励--{point_s}")
        print(f"========开始进行抽奖========")
        self.luckdraw()


    def sign(self):
        url = f"https://dc.zhongjian365.com/api/activity_clockin/signIn"
        payload = '{}'
        headers = {
           'X-Auth-Key': self.cookie,
           'xweb_xhr': '1',
           'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
           'Content-Type': 
           'application/json',
           'Accept': '*/*',
           'Host': 'dc.zhongjian365.com',
           'Connection': 'keep-alive'
        }
        response = requests.request("POST", url=url, headers=headers , data=payload)
        if response.status_code == 200:
            if response.json().get("code") == "200":
                point_s = "签到成功"
                point_ss = response.json()
                return point_s , point_ss
            else:
                point_s = response.json().get('code')
                point_ss = response.json().get('msg')
                return point_s  , point_ss

    def luckdraw(self):
        url = f"https://dc.zhongjian365.com/api/activity_clockin/luckyDraw"
        payload = '{"to_day":"'+str(datetime.datetime.now()).split(" ")[0]+'"}'
        headers = {
           'X-Auth-Key': self.cookie,
           'xweb_xhr': '1',
           'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
           'Content-Type': 
           'application/json',
           'Accept': '*/*',
           'Host': 'dc.zhongjian365.com',
           'Connection': 'keep-alive'
        }
        response = requests.request("POST", url=url, headers=headers , data=payload)
        if response.status_code == 200:
            if response.json().get("code") == "200":
                point_lk = "抽奖成功"
                name = response.json().get('data').get('prize_name')
                amount = response.json().get('data').get('amount')
                print(f"抽奖奖励--状态码：{point_lk}")
                print(f"抽奖奖励--[{name}]{amount}元")
            else:
                point_lk = response.json().get('code')
                point_ss = response.json().get('msg')
                print(f"抽奖奖励--状态码：{point_lk}")
                print(f"抽奖奖励--{point_ss}")

if __name__ == "__main__":
    cookies = cookies.split("@")
    print(f"【中建365】共检测到{len(cookies)}个账号")
    print(f"==========================================")
    print(f"中建365达人   by:Mrconli\n 每日签到0.1\n")
    i = 1
    for cookie in cookies:
        print(f"========【账号{i}】开始运行脚本========")
        i += 1
        DY(cookie).run()
        
        time.sleep(random.randint(5, 10))
        if i > len(cookies):
            break
        else:
            print("延迟些许,准备下一账号")

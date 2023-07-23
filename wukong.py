"""
cookies格式 url#cookie#argus#ladon
wkllq_ck = "url#cookie#argus#ladon"
"""


import requests
import random
import time
import urllib.parse
import json

cookies = ""
ua = ""
num = 30  # 循环参数


class DY:
    def __init__(self, cookie):
        self.url = cookie.split("#")[0]
        self.cookie = cookie.split("#")[1]
        self.argus = cookie.split("#")[2]
        self.ladon = cookie.split("#")[3]

    def run(self):
        jbsl = self.user()
        jb1 = jbsl
        print("========开始做任务========")
        self.daily_sign()
        self.hot_board()
        self.video_coin()
        self.eat_coin()
        self.treasure_box()
        print("========开始无限刷金币========")
        for i in range(num):
            tt = random.randint(50, 70)
            print(f"开宝箱奖励金币--休息{tt}秒")
            time.sleep(tt)
            i = i + 1
            point, point2 = self.open_box()
            print(f"第{i}次开宝箱奖励金币--{point2}")
            print(f"第{i}次开宝箱奖励金币--{point}")
        print("========开始账号查资产========")
        jbsl = self.user()
        jb2 = jbsl
        jbzg = jb2 - jb1
        print("========开始计算总收益========")
        print(f"本次运行脚本共获得金币--{jbzg}")

    def user(self):
        url = f"https://api5-normal-hl.toutiaoapi.com/luckycat/sj/v1/income/page_data?_request_from=web&{self.url}"
        headers = {
            'User-Agent': ua,
            'x-argus': self.argus,
            'x-ladon': self.ladon,
            'Cookie': self.cookie,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("err_no") == 0:
                jbjj = response_json.get('data').get('score_balance') / 33000
                jbj = round(jbjj, 2)
                print(f"当前金币：{response_json.get('data').get('score_balance')}金币 现金：{jbj} 元")
                jbsl = response_json.get('data').get('score_balance')
            else:
                print(f"获取用户信息出错{response_json}")
                jbsl = 0
        else:
            print("用户数据过期或者错误")
            jbsl = 0
        return jbsl

    def daily_sign(self):
        url = f"https://api5-normal-lf.toutiaoapi.com/luckycat/gip/v1/daily/sign/done?{self.url}"
        body = "{\"is_double\":false}"
        headers = {
            'User-Agent': ua,
            'x-argus': self.argus,
            'x-ladon': self.ladon,
            'Cookie': self.cookie,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("err_no") == 0:
                reward_amount = response_json.get('data').get('reward_amount')
                print(f"[每日签到]获得金币: {reward_amount}")
                return True
            else:
                print(f"[每日签到]失败：{response_json.get('err_tips')}")
                return True
        else:
            print("请求失败")
        return False

    def hot_board(self):
        url = f"https://api5-normal-lf.toutiaoapi.com/luckycat/gip/v1/daily/hot_board/done?{self.url}"
        body = "{\"search_position\":\"tab_gold_task\"}"
        headers = {
            'User-Agent': ua,
            'x-argus': self.argus,
            'x-ladon': self.ladon,
            'Cookie': self.cookie,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("err_no") == 0:
                reward_amount = response_json.get('data').get('reward_amount')
                print(f"[浏览热点]获得金币: {reward_amount}")
                return True
            else:
                print(f"[浏览热点]失败：今日已完成")
                return True
        else:
            print(f"请求失败")
        return False

    def video_coin(self):
        url = f"https://api5-normal-lf.toutiaoapi.com/luckycat/gip/v:version/daily/video_reading/done?{self.url}"
        body = "body=null"
        headers = {
            'User-Agent': ua,
            'x-argus': self.argus,
            'x-ladon': self.ladon,
            'Cookie': self.cookie,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("err_no") == 0:
                reward_amount = response_json.get('data').get('reward_amount')
                print(f"[视频金币]获得金币: {reward_amount}")
                return True
            else:
                print(f"[视频金币]失败：今日已领取")
                return True
        else:
            print(f"请求失败")
        return False

    def eat_coin(self):
        current_hour = time.localtime().tm_hour
        if (5 <= current_hour <= 9) or (11 <= current_hour <= 14) or (17 <= current_hour <= 20) or (21 <= current_hour <= 24):
            url = f"https://api5-normal-lf.toutiaoapi.com/luckycat/gip/v1/daily/eat/done?{self.url}"
            body = "{}"
            headers = {
                'User-Agent': ua,
                'x-argus': self.argus,
                'x-ladon': self.ladon,
                'Cookie': self.cookie,
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Connection': 'keep-alive'
            }
            response = requests.post(url, headers=headers, data=body)
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get("err_no") == 0:
                    score_amount = response_json.get('data').get('score_amount')
                    print(f"[吃饭赚钱]获得金币: {score_amount}")
                    return True
                else:
                    print(f"[吃饭赚钱]失败：该时间段已领取")
                    return True
            else:
                print(f"请求失败")
            return False
        else:
            print(f"[吃饭赚钱]失败：不在时间段内")
        return False

    def treasure_box(self):
        url = f"https://api5-normal-lf.toutiaoapi.com/luckycat/gip/v1/daily/treasure_box/detail?{self.url}"
        headers = {
            'User-Agent': ua,
            'x-argus': self.argus,
            'x-ladon': self.ladon,
            'Cookie': self.cookie,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("err_no") == 0 and response_json.get('data').get('left_seconds') != 0:
                print(f"[开启宝箱]失败：还差{response_json.get('data').get('left_seconds')}秒")
                return True
            else:
                url = f"https://api5-normal-lf.toutiaoapi.com/luckycat/gip/v1/daily/treasure_box/done?{self.url}"
                body = "{\"auto_open\":false}"
                headers = {
                    'User-Agent': ua,
                    'x-argus': self.argus,
                    'x-ladon': self.ladon,
                    'Cookie': self.cookie,
                    'Content-Type': 'application/json',
                    'Accept': '*/*',
                    'Connection': 'keep-alive'
                }
                response = requests.post(url, headers=headers, data=body)
                if response.status_code == 200:
                    response_json = response.json()
                    print(f"[开启宝箱]获得金币: {response_json.get('data').get('reward_amount')}")
                    return True
                else:
                    print(f"请求失败")
                    return False
        else:
            print(f"请求失败")
        return False

    def open_box(self):
        url = f"https://api5-normal-hl.toutiaoapi.com/luckycat/gip/v1/cooperate/exciad/done?{self.url}"
        body = "{\"task_id\":4108,\"exci_extra\":{\"cid\":1572200687669348,\"req_id\":\"20230701160644C93FF92F37A3A1714A5C\",\"rit\":80047},\"extra\":{\"stage_score_amount\":[],\"track_id\":\"\",\"draw_score_amount\":null,\"draw_track_id\":null,\"task_id\":\"\",\"task_name\":\"\",\"enable_fuzzy_amount\":false,\"custom_id\":null}}"
        headers = {
            'User-Agent': ua,
            'x-argus': self.argus,
            'x-ladon': self.ladon,
            'Cookie': self.cookie,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            response_json = response.json()
            point2 = response_json.get('err_tips')
            if response_json.get("err_tips") == "成功":
                point = response_json.get('data').get('reward_amount')
                return point2, point
            else:
                point = "已经上限了"
                return point2, point
        else:
            print(f"开宝箱接口请求失败，状态码：{response.status_code}")
            return None, None


if __name__ == "__main__":
    cookies = cookies.split("@")
    print(f"【悟空浏览器】共检测到{len(cookies)}个账号")
    print("==========================================")
    print("悟空浏览器自用版(小毛)   by：偷CK的六舅哥\n7.3 悟空浏览器刷视频，不黑一天1-2块左右\n暂时未写异常处理，bug提交 https://t.me/jiangyutck")
    i = 1
    for cookie in cookies:
        print(f"========【账号{i}】开始运行脚本========")
        i += 1
        DY(cookie).run()
        time.sleep(random.randint(5, 10))
        if i > len(cookies):
            break
        else:
            print("延迟一小会，准备跑下一个账号")

# 软件：美团app
# 功能：每日赚钱
# A版，用户部分信息，适用于不会抓包用户，B版信息更全，更真实，适用于抓包用户，目前两个版本都正常跑。自己选择。
# 抓包 game.meituan.com/earn-daily/msg/post，进入活动会有一堆这个请求，全部cookie
# 变量名称 mtck = cookie  多账号@分割
# 跑之前进活动看下，是否正常，后续不用管，draw = 0 为0不抽奖，为1抽奖。抽奖是没有问题，自行决定
# 定时 : 一天一次
# 每日随机提现，默认不开启，没抓

# new Env('美团每日赚钱APP')
# cron: 2 6,11,19 * * *

import os
import random
import re
import string
import time

import requests

cookies = os.getenv("mt50ck")
ua = ''
draw = 0  # 为0不抽奖，为1抽奖。抽奖是没有问题，自行决定


class MT:
    current_time = int(round(time.time() * 1000))
    url = 'https://game.meituan.com/earn-daily/msg/post'

    def __init__(self, cookie):
        self.cookie = cookie
        try:
            self.uuid = re.search(r"uuid=(.*?);", self.cookie).group(1)
            self.cityid = re.search(r"cityid=(.*?);", self.cookie).group(1)
            self.token = re.search(r"token=(.*?);", self.cookie).group(1)
            self.userId = re.search(r"userId=(.*?);", self.cookie).group(1)
        except AttributeError:
            self.uuid = None
            self.cityid = None
            self.token = None
            self.userId = None

        characters = string.digits + string.ascii_lowercase
        self.nonce_str = ''.join(random.choice(characters) for _ in range(16))
        self.headers = {
            'Host': 'game.meituan.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'acToken': 'undefined',
            'mToken': 'undefined',
            'User-Agent': ua,
            'Origin': 'https://awp.meituan.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://awp.meituan.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': self.cookie,
            'Content-Type': 'application/json'
        }
        self.base_data = {
            "acToken": None,
            "riskParams": {
                "ip": "",
                "fingerprint": 'undefined',
                "cityId": self.cityid,
                "platform": 4,
                "app": 0,
                "version": "12.9.209",
                "uuid": self.uuid
            }
        }

    def run(self):
        self.login()
        self.task_list()
        self.get_user_info()

    def send_request(self, url=None, headers=None, data=None, method='GET', cookies=None):
        if url is None:
            url = self.url
        if headers is None:
            headers = self.headers
        with requests.Session() as session:
            session.headers.update(headers)
            if cookies is not None:
                session.cookies.update(cookies)

            try:
                if method == 'GET':
                    response = session.get(url, timeout = 3)
                elif method == 'POST':
                    response = session.post(url, json = data, timeout = 3)
                else:
                    raise ValueError('Invalid HTTP method.')

                response.raise_for_status()
                return response.json()

            except requests.Timeout as e:
                print("请求超时:", str(e))

            except requests.RequestException as e:
                print("请求错误:", str(e))

            except Exception as e:
                print("其他错误:", str(e))

    # 随机延迟默认1-1.5s
    def sleep(self, min_delay=1, max_delay=2):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    # 登录
    def login(self):
        url = f'https://game.meituan.com/earn-daily/login/loginMgc?gameType=10402&mtUserId={self.userId}&mtToken={self.token}&mtDeviceId={self.uuid}&nonceStr={self.nonce_str}&externalStr={"cityId":{self.cityid}}'
        return_data = self.send_request(url)
        self.sleep()
        if return_data['code'] != 0:
            return return_data['desc']

        access_token = return_data['response'].get('accessToken')
        self.headers['acToken'] = access_token
        self.headers['mToken'] = self.token
        self.base_data['acToken'] = access_token

    # task_list
    def task_list(self):
        payload = self.base_data.copy()
        payload['protocolId'] = 1001
        payload['data'] = {
            "externalStr": f'{{"cityId": \'{self.cityid}\'}}'
        }
        return_data = self.send_request(data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            return return_data['desc']
        task_list = return_data['data'].get('taskInfoList')
        sign_state = return_data['data'].get('signInPopModel').get('rewardModelList')

        # 浏览任务
        for task in task_list:
            task_id = task['id']
            if task_id in [15099, 15278, 780]:
                continue
            daily_finish = task.get('dailyFinishTimes')
            max_finish = task.get('mgcTaskBaseInfo', {}).get('curPeriodMaxFinishTimes')
            name = task.get('mgcTaskBaseInfo', {}).get('viewTitle')
            if daily_finish == max_finish:
                print(f'今日已完成:{name}')
                continue
            num = max_finish - daily_finish
            for _ in range(num):
                self.go_shoping(task_id, name)

        # 每日签到
        for sign in sign_state:
            current = sign.get('current', False)
            state = sign.get('state', 0)

            if not current:
                continue
            if state == 2:
                print('今日已打卡签到')
                break
            print('去完成:现金打卡')
            self.sign_in()
            break
        self.sleep()
        new_data = self.send_request(data = payload, method = 'POST')
        base_model = new_data['data'].get('playerBaseModel', {})
        # 开红包
        packet_amount = base_model.get('redPacketInfo').get('leftRedPacketAmount')
        draw_info = base_model.get('lotteryInfo').get('leftLotteryTimesAmount')
        if packet_amount == 0:
            print('今日红包已经开完了')
        else:
            print(f'今日可开红包次数:{packet_amount}次')
            for _ in range(packet_amount):
                self.open_packet()

        # 抽奖
        if draw_info == 0:
            print('剩余抽奖次数为0')
        else:
            print(f'今日可抽奖次数:{draw_info}次')
            if not draw:
                print('已关闭抽奖')
            else:
                for _ in range(draw_info):
                    self.draw()

    # task
    def go_shoping(self, task_id, name):
        def send_shoping(protocol_id):
            payload = self.base_data.copy()
            payload['protocolId'] = protocol_id
            payload['data'] = {
                "taskId": task_id,
                "externalStr": f'{{"cityId": \'{self.cityid}\'}}'
            }
            return_data = self.send_request(data = payload, method = 'POST')
            if return_data['code'] != 200:
                return return_data['desc']

        send_shoping(1004)
        print(f'完成任务: [{name}]')
        time.sleep(random.randint(5, 10))
        send_shoping(1005)
        print(f'领取任务: [{name}] 奖励成功')

    # 签到
    def sign_in(self):
        payload = self.base_data.copy()
        payload['protocolId'] = 1007
        payload['data'] = {}
        return_data = self.send_request(data = payload, method = 'POST')
        self.sleep()

        if return_data['code'] != 200:
            return return_data['desc']
        content = return_data['data'].get('remitNotificationModelList')[0].get('content')
        print(content)

    # 开红包
    def open_packet(self):
        max_cash_token = 49.98

        payload = self.base_data.copy()
        payload['protocolId'] = 1008
        payload['data'] = {}
        return_data = self.send_request(data = payload, method = 'POST')
        self.sleep
        if return_data['code'] != 200:
            print(return_data)
            return
        reward_list = return_data['data'].get('rewardModelList')
        remit_models = return_data['data'].get('remitNotificationModels')
        activity_info = return_data.get('data').get('playerBaseModel').get('activityCycleInfo')
        cash_token = activity_info.get('cashToken') / 100.0
        content = remit_models[0].get('content') if remit_models else None

        if content:
            print(content)
        else:
            rewards = [value['amount'] / 100.0 if cash_token < max_cash_token else value['amount']
                       for value in reward_list if value['rewarded']]

            if rewards:
                for reward in rewards:
                    print(f'开红包获得:{reward}金额' if cash_token < max_cash_token else f'开红包获得:{reward}金币')

    # 抽奖
    def draw(self):
        payload = self.base_data.copy()
        payload['protocolId'] = 1010
        payload['data'] = {}
        return_data = self.send_request(data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data)
            return

        data = return_data['data']
        current_reward = data.get('currentReward', {})
        rewarded_model = current_reward.get('rewardedCouponModel')

        if rewarded_model:
            name = rewarded_model.get('name')
            print(f'抽奖获得:{name}')
        else:
            seq = current_reward.get('seq')
            amount = current_reward.get('amount')
            reward_list = return_data['data'].get('rewardModelList', [])
            rewards_dict = {value.get('seq'): value for value in reward_list}

            resource_type = rewards_dict.get(seq, {}).get('resourceType', None)

            if resource_type == 5:
                print(f'抽奖获得: {amount}金币')
            elif resource_type == 9 or resource_type == 3:
                num = amount // 100
                print(f'抽奖获得: {num}元提现券')
            else:
                print('抽了个啥')

    # 获取用户信息
    def get_user_info(self):
        payload = self.base_data.copy()
        payload['protocolId'] = 1012
        payload['data'] = {}
        return_data = self.send_request(data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            return return_data['desc']

        activity_info = return_data.get('data').get('activityCycleInfo')
        cash_token = activity_info.get('cashToken') / 100.0
        coin_token = activity_info.get('coinToken')
        expire_time = activity_info.get('expireTime')

        surplus_time = expire_time - self.current_time
        day = int(surplus_time / (1000 * 60 * 60 * 24))
        print(f'每日赚钱余额:{cash_token}，{coin_token}金币')
        print(f'本期剩余天数:{day},请注意过期时间哦')


if __name__ == "__main__":
    cookies = cookies.split("@")
    mt = f"美团共获取到{len(cookies)}个账号"
    print(mt)

    for i, cookie in enumerate(cookies, start = 1):
        print(f"\n======== ▷ 第 {i} 个账号 ◁ ========")
        MT(cookie).run()
        print("\n随机等待5-10s进行下一个账号")
        time.sleep(random.randint(5, 10))

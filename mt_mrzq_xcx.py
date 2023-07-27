# 软件：美团app
# 功能：每日赚钱
# A版，用户部分信息，适用于不会抓包用户，B版信息更全，更真实，适用于抓包用户，目前两个版本都正常跑。自己选择。
# 抓包 https://passport.meituan.com/useraccount/ilogin微信登录，复制链接，抓取userId=xx&token=xxx
# 变量名称 mtck = userId=xx&token=xxx  多账号@分割
# 跑之前进活动看下，是否正常，后续不用管，draw = 0 为0不抽奖，为1抽奖。抽奖是没有问题，自行决定
# 定时 : 一天一次
# 每日随机提现，默认不开启，没抓

# new Env('美团每日赚钱-小程序')
# cron: 2 6,11,19 * * *

import os
import random
import re
import string
import time

import requests

cookies = os.getenv("mtck")
draw = 0  # 为0不抽奖，为1抽奖。抽奖是没有问题，自行决定


class MT:
    current_time = int(round(time.time() * 1000))
    url = 'https://game.meituan.com/earn-daily/msg/post'

    def __init__(self, cookie, uuid):
        self.cookie = cookie
        userid_match = re.search(r'userId=(\d+)', self.cookie)
        token_match = re.search(r'token=([A-Za-z0-9_-]+)', self.cookie)

        if userid_match and token_match:
            self.userId = userid_match.group(1)
            self.token = token_match.group(1)
        else:
            print("未找到userid和token值")
        self.uuid = uuid

        characters = string.digits + string.ascii_lowercase
        self.nonce_str = ''.join(random.choice(characters) for _ in range(16))
        self.headers = {
            'Host': 'game.meituan.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'acToken': 'undefined',
            'mToken': 'undefined',
            'User-Agent': self.get_ua(),
            'Origin': 'https://awp.meituan.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://awp.meituan.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'utm_medium=android;uuid={self.uuid};token={self.token};mt_c_token={self.token};',
            'Content-Type': 'application/json'
        }
        self.base_data = {
            "acToken": None,
            "riskParams": {
                "ip": "",
                "fingerprint": 'undefined',
                "cityId": "1",
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

    # 随机ua
    def get_ua(self):
        android_version = f'{random.randint(10, 12)}.0'  # 随机生成 Android 版本号
        chrome_version = f'{random.randint(80, 90)}.0.{random.randint(4000, 5000)}.210'  # 随机生成 Chrome 版本号
        ua_string = f'Mozilla/5.0 (Linux; Android {android_version}; {self.get_model()}) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_version} Mobile Safari/537.36 TitansX/12.9.1 KNB/1.2.0 android/{android_version} mt/com.sankuai.meituan/12.9.209 App/10120/12.9.209 MeituanGroup/12.9.209'
        return ua_string

    def get_model(self):
        models = ['M2012K10C', '22041211AC', 'ABR-AL80', 'AGT-AN00', 'M2011K2C']
        return random.choice(models)

    # 登录
    def login(self):
        url = f'https://game.meituan.com/earn-daily/login/loginMgc?gameType=10402&mtUserId={self.userId}&mtToken={self.token}&mtDeviceId={self.uuid}&nonceStr={self.nonce_str}&externalStr=%7B%22cityId%22%3A%221%22%7D'
        return_data = self.send_request(url)
        self.sleep()
        if return_data['code'] != 0:
            return print(return_data)

        access_token = return_data['response'].get('accessToken')
        self.headers['acToken'] = access_token
        self.headers['mToken'] = self.token
        self.base_data['acToken'] = access_token

    # task_list
    def task_list(self):
        payload = self.base_data.copy()
        payload['protocolId'] = 1001
        payload['data'] = {
            "externalStr": f'{{"cityId": \'"1"\'}}'
        }
        return_data = self.send_request(data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data)
            return
        task_list = return_data['data'].get('taskInfoList')
        sign_state = return_data['data'].get('signInPopModel').get('rewardModelList')

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

        time.sleep(2)
        new_data = self.send_request(data = payload, method = 'POST')
        base_model = new_data['data'].get('playerBaseModel', {})
        # 开红包
        packet_amount = base_model.get('redPacketInfo').get('leftRedPacketAmount')

        if packet_amount == 0:
            print('今日红包已经开完了')
        else:
            print(f'今日可开红包次数:{packet_amount}次')
            for _ in range(packet_amount):
                self.open_packet()
        time.sleep(2)
        new_data2 = self.send_request(data = payload, method = 'POST')
        base_model2 = new_data2['data'].get('playerBaseModel', {})
        draw_info = base_model2.get('lotteryInfo').get('leftLotteryTimesAmount')

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
                "externalStr": f'{{"cityId": \'"1"\'}}'
            }
            return_data = self.send_request(data = payload, method = 'POST')
            if return_data['code'] != 200:
                print(return_data)
                return

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
            print(return_data)
            return
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
            print(return_data)
            return

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

    current_uuid_index = 0  # 将当前UUID索引初始化为0
    uuids_list = [
        "00000000000005A71494E8805428A93A5EBB6E00282BDA167095351831885613",
        "0000000000000E757A5DF300944AF82C239A47442EB26A168979373388967298",
        "0000000000000FE39E282D85D4184826D7A3CB6BDEE71A168979301991229841",
        "000000000000026CD052477C44C26964557ABBE7B24C7A168980721534295742"
    ]

    for i, cookie in enumerate(cookies, start = 1):
        print(f"\n======== ▷ 第 {i} 个账号 ◁ ========")
        uuid = uuids_list[current_uuid_index]
        current_uuid_index = (current_uuid_index + 1) % len(uuids_list)

        MT(cookie, uuid).run()

        print("\n随机等待5-10秒进行下一个账号")
        time.sleep(random.randint(5, 10))

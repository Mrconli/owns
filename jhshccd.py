# 软件:建行活动，奋斗季cc豆 功能：每日营收，签到 浏览任务，答题，抽奖，专区任务
# 先开抓包，先开抓包，抓的是微信端api/flow/nf/shortLink/redirect/ccb_gjb会有两个，要那个带true的，wParam参数就可以
# 专区任务，进app专区微信也行抓任意cookie里面含有_ck_bbq_224，全部cookie
# 格式 ccdck = wParam参数值#xxx
# 定时：一天两次

new Env('建行生活奋斗季cc豆')
cron: 22 8,19 * * *

import os
import random
import re
import time
from datetime import datetime

import requests

app_ua = 'Mozilla/5.0 (Linux; Android 11; M2011K2C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36/CloudMercWebView'

ccb_cookie = os.getenv("ccdck")


# self.bus_token可以刷新
class CCD:
    user_region = None
    zhc_token = None
    wx_uuid = None
    base_header = {
        'Host': 'm3.dmsp.ccb.com',
        'accept': 'application/json, text/plain, */*',
        'user-agent': app_ua,
        'origin': 'https://m3.dmsp.ccb.com',
        'x-requested-with': 'com.tencent.mm',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json'
    }
    token_headers = {
        'Host': 'event.ccbft.com',
        'accept': 'application/json, text/plain, */*',
        'user-agent': app_ua,
        'origin': 'https://event.ccbft.com',
        'x-requested-with': 'com.tencent.mm',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json'
    }

    def __init__(self):
        self.w_param = ccb_cookie.split("#")[0]
        self.zq_cookie = ccb_cookie.split("#")[1]
        self.bus_headers = {
            'Host': 'fission-events.ccbft.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'accept': 'application/json, text/plain, */*',
            'x-csrf-token': None,
            'x-requested-with': 'XMLHttpRequest',
            'authorization': None,
            'user-agent': app_ua,
            'origin': 'https://fission-events.ccbft.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://fission-events.ccbft.com/a/224/kmenz5Zd/game',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': self.zq_cookie,
            'content-type': 'application/json'
        }

    def run(self):
        self.get_token()
        self.region()
        self.user_info()
        self.sign_in()
        self.getlist()
        self.answer_state()
        print('-----专区任务-----')
        time.sleep(random.randint(3, 5))
        self.get_csrftoken()
        self.get_user_ccd()

    # 随机延迟默认1-1.5
    def sleep(self, min_delay=1, max_delay=1.5):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def send_request(self, url, headers, data=None, method='GET', cookies=None):
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

    # 获取token
    def get_token(self):
        url = 'https://event.ccbft.com/api/flow/nf/shortLink/redirect/ccb_gjb?shareMDID=ZHCMD_8460172f-48b2-4612-a069-f04611760445&shareDepth=1&CCB_Chnl=6000199'
        payload = {
            "appId": "wxd513efdbf26b5744",
            "shortId": "polFsWD2jPnjhOx9ruVBcA",
            "archId": "ccb_gjb",
            "wParam": self.w_param,
            "channelId": "wx", "ifWxFirst": True
        }

        return_data = self.send_request(url, headers = self.token_headers, data = payload, method = 'POST')
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        redirect_url = return_data['data'].get('redirectUrl')
        self.wx_uuid = return_data['data'].get('wxUUID')
        token = self.extract_token(redirect_url)
        if token:
            self.zhc_token = token
            self.auth_login(token)

    def extract_token(self, redirect_url):
        start_token_index = redirect_url.find("__dmsp_token=") + len("__dmsp_token=")
        end_token_index = redirect_url.find("&", start_token_index)

        token = None
        if start_token_index != -1 and end_token_index != -1:
            token = redirect_url[start_token_index:end_token_index]
        return token

    # 登录
    def auth_login(self, token):
        url = 'https://m3.dmsp.ccb.com/api/businessCenter/auth/login'
        payload = {"token": token, "channelId": "wx"}
        return_data = self.send_request(url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return

    # 获取用户地区代码
    def region(self):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/gis/getAddress?zhc_token={self.zhc_token}'
        payload = {"lgt": 116.495434, "ltt": 40.3976539, "flag": 1}
        return_data = self.send_request(url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        self.user_region = return_data['data'].get('code')

    # 查询用户等级
    def user_info(self):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/mainVenue/getUserState?zhc_token={self.zhc_token}'
        return_data = self.send_request(url, headers = self.base_header, method = 'POST')

        if return_data['code'] != 200:
            print(return_data['message'])
            return
        current_level = return_data['data'].get('currentLevel')
        need_exp = return_data['data'].get('needGrowthExp') - return_data['data'].get('currentLevelGrowthExp')
        level = return_data['data'].get('currentProtectLevel')
        reward_id = return_data['data'].get('zhcRewardInfo').get('id')
        reward_type = return_data['data'].get('zhcRewardInfo').get('rewardType')
        reward_value = return_data['data'].get('zhcRewardInfo').get('rewardValue')
        print(f"当前用户等级{current_level}级")
        print(f"距下一级还需{need_exp}成长值")
        self.income(level, reward_id, reward_type, reward_value)

    # 每日营收
    def income(self, level, reward_id, reward_type, reward_value):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/mainVenue/receiveLevelReward?zhc_token={self.zhc_token}'
        payload = {"level": level, "rewardId": reward_id, "levelRewardType": reward_type}
        return_data = self.send_request(url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return

        print(f"今日营收: {reward_value}cc豆")

    # 签到
    def sign_in(self):
        signin_url = f'https://m3.dmsp.ccb.com/api/businessCenter/taskCenter/signin?zhc_token={self.zhc_token}'
        signin_payload = {"taskId": 96}
        return_data = self.send_request(url = signin_url, headers = self.base_header, data = signin_payload,
                                        method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        print(return_data['message'])

        # print('未知错误')

    # 获取浏览任务列表
    def getlist(self):
        list_url = f'https://m3.dmsp.ccb.com/api/businessCenter/taskCenter/getTaskList?zhc_token={self.zhc_token}'
        payload = {"publishChannels": "03", "regionId": self.user_region}  # 440300

        return_data = self.send_request(url = list_url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return

        task_list = return_data['data'].get('浏览任务')
        for value in task_list:
            complete_status = value['taskDetail'].get('completeStatus')
            if complete_status == '02':
                print(f"{value['taskName']}:已完成")
                continue
            task_id = value['id']
            task_name = value['taskName']
            print(f'去完成{task_name}')
            self.browse(task_id, task_name)
            self.receive(task_id)

    # 执行浏览任务
    def browse(self, task_id, task_name):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/taskCenter/browseTask?zhc_token={self.zhc_token}'
        payload = {"taskId": task_id, "browseSec": 1}
        return_data = self.send_request(url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        print(return_data['message'])

    # 领取奖励
    def receive(self, task_id):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/taskCenter/receiveReward?zhc_token={self.zhc_token}'
        payload = {"taskId": task_id}
        return_data = self.send_request(url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        print(return_data['message'])

    # 获取答题state
    def answer_state(self):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/zhcUserDayAnswer/getAnswerStatus?zhc_token={self.zhc_token}'
        return_data = self.send_request(url, headers = self.base_header)
        if return_data['code'] == 200:
            if return_data['data'].get('answerState') == 'Y':
                return print(return_data['message'])
            else:
                # 获取今日题目
                print('获取今日题目')
                self.get_question()
        else:
            return print(return_data['message'])

    # 获取题目
    def get_question(self):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/zhcUserDayAnswer/queryQuestionToday?zhc_token={self.zhc_token}'
        return_data = self.send_request(url, headers = self.base_header)
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        question_id = return_data['data'].get('questionId')
        remark = return_data['data'].get('remark')
        answer_list = return_data['data'].get('answerList')
        if remark:
            # 匹配答案
            print('开始匹配正确答案')
            # 去除标点符号的正则表达式模式
            pattern = r"[，。？！“”、]"

            remark_cleaned = re.sub(pattern, "", remark)

            max_match_count = 0
            right_answer_id = None

            # 遍历答案列表，与remark进行匹配
            for answer in answer_list:
                answer_id = answer["id"]
                answer_result = answer["answerResult"]
                answer_cleaned = re.sub(pattern, "", answer_result)

                match_count = 0
                for word in answer_cleaned:
                    if word in remark_cleaned:
                        match_count += 1
                        remark_cleaned = remark_cleaned.replace(word, "", 1)

                if match_count > max_match_count:
                    max_match_count = match_count
                    right_answer_id = answer_id
            print("匹配成功，开始答题")
            self.answer(question_id, right_answer_id)
        else:
            print('暂无提示随机答题')
            right_answer_id = random.choice(answer_list)['id']
            self.answer(question_id, right_answer_id)

    # 答题
    def answer(self, question_id, answer_ids):
        url = f'https://m3.dmsp.ccb.com/api/businessCenter/zhcUserDayAnswer/userAnswerQuestion?zhc_token={self.zhc_token}'
        payload = {"questionId": question_id, "answerIds": answer_ids}
        return_data = self.send_request(url, headers = self.base_header, data = payload, method = 'POST')
        self.sleep()
        if return_data['code'] != 200:
            print(return_data['message'])
            return
        print(return_data['message'])

    # ---------下面是精彩专区任务--------
    def get_csrftoken(self):
        url1 = 'https://event.ccbft.com/api/flow/nf/shortLink/redirect/ccb_gjb?CCB_Chnl=6000110'
        url2 = 'https://fission-events.ccbft.com/a/224/kmenz5Zd?CCB_Chnl=6000110'
        payload1 = '{{"appId":"wxd513efdbf26b5744","shortId":"jd9H3uCkzHaQBn8aeq5NWQ","archId":"ccb_gjb","channelId":"wx","ifWxFirst":false,"wxUUID":"{}"}}'.format(

            self.wx_uuid)
        headers = {
            'Host': 'fission-events.ccbft.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': app_ua,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'x-requested-with': 'com.ccb.longjiLife',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'referer': 'https://event.ccbft.com/',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': self.zq_cookie
        }
        return_data = requests.post(url1, headers = self.token_headers, data = payload1).json()
        if return_data['code'] != 200:
            return print(return_data['message'])

        redirect_url = return_data['data'].get('redirectUrl')
        requests.get(url = redirect_url, headers = headers)
        try:
            res = requests.get(url = url2, headers = headers)
            data = res.text
            csrf_token_pattern = r'<meta\s+name=csrf-token\s+content="([^"]+)">'
            authorization_pattern = r'<meta\s+name=Authorization\s+content="([^"]+)">'

            csrf_token_match = re.search(csrf_token_pattern, data)
            authorization_match = re.search(authorization_pattern, data)

            if csrf_token_match and authorization_match:
                csrf_token = csrf_token_match.group(1)
                authorization = authorization_match.group(1)
                self.bus_headers['x-csrf-token'] = csrf_token
                self.bus_headers['authorization'] = f'Bearer {authorization}'
                self.sleep()
                print('--代发专区--')
                self.game_id()
                print('--养老专区--')
                self.turn()
                print('--跨境专区--')
                self.border_draw()
                print('--商户专区--')
                self.shoplist()
                print('--消保专区--')
                print('-登山游戏-')
                self.fire()
            else:
                print('CSRF token or Authorization not found.')
        except requests.RequestException as e:
            print(f"请求异常: {e}")

    # 代发专区
    def game_id(self):
        url = 'https://fission-events.ccbft.com/activity/dmspsalary/startGame/224/kmenz5Zd'
        return_data = self.send_request(url, headers = self.bus_headers, method = 'POST')
        if return_data['status'] != 'success':
            return print(return_data['message'])
        game_id = return_data['data'].get('game_id')
        self.do_game(game_id)

    def do_game(self, game_id):
        url1 = 'https://fission-events.ccbft.com/activity/dmspsalary/gameInfo/224/kmenz5Zd'
        url2 = 'https://fission-events.ccbft.com/activity/dmspsalary/doneGame/224/kmenz5Zd'
        ticket = random.randint(1100, 1200)
        payload_time = {"game_id": game_id}
        payload_grade = {"game_id": game_id, "ticket": ticket}

        return_data1 = self.send_request(url1, headers = self.bus_headers, data = payload_time, method = 'POST')

        if return_data1['status'] != 'success':
            return print(return_data1['message'])
        print('随机等待15秒，模拟正常游戏时间')
        time.sleep(random.randint(15, 20))

        return_data2 = self.send_request(url2, headers = self.bus_headers, data = payload_grade, method = 'POST')
        self.sleep()
        if return_data2['status'] != 'success':
            return print(return_data2['message'])
        prizename = return_data2['data'].get('prizename')
        print(f'获得奖励:{prizename}')

    # 养老专区 翻翻卡每日一次免费
    def turn(self):
        url = 'https://fission-events.ccbft.com/activity/dmspolddraw/draw/224/xPOLaama'
        return_data = self.send_request(url, headers = self.bus_headers, method = 'POST')
        self.sleep()
        if return_data['status'] != 'success':
            print(return_data['message'])
            return
        print(f"{return_data['message']}---{return_data['data'].get('prizename')}")

    # 跨境专区
    def border_draw(self):
        url1 = 'https://fission-events.ccbft.com/activity/dmspkjanswer/getUserInfo/224/dmR48R3D'
        url2 = 'https://fission-events.ccbft.com/Component/draw/commonDrawPrize/224/dmR48R3D'
        return_data1 = self.send_request(url1, headers = self.bus_headers)
        if return_data1['status'] != 'success':
            return print(return_data1['message'])
        remain = return_data1['data'].get('remain')
        if remain == '0':
            return print('当前剩余抽奖次数为0')

        return_data2 = self.send_request(url2, headers = self.bus_headers, method = 'POST')
        self.sleep()
        if return_data2['status'] != 'success':
            print(return_data2['message'])
            return
        print(f"{return_data2['message']}---{return_data2['data'].get('prizename')}")

    # 商户专区 掷骰子任务列表
    def shoplist(self):
        index_url = 'https://fission-events.ccbft.com/Common/activity/getActivityInfo/224/gPpYzxmE'
        url = 'https://fission-events.ccbft.com/Component/task/lists/224/gPpYzxmE'
        self.send_request(index_url, headers = self.bus_headers)
        time.sleep(1)
        return_data = self.send_request(url, headers = self.bus_headers)
        self.sleep()
        if return_data['status'] != 'success':
            print(return_data['message'])
            return
        task_list = return_data['data'].get('userTask')
        for value in task_list:
            complete_status = value['finish']
            if complete_status == 1:
                print('已完成该任务，继续浏览下一个任务')
                continue
            task_id = value['id']
            url = 'https://fission-events.ccbft.com/Component/task/do/224/gPpYzxmE'
            payload = {"id": task_id}
            return_data = self.send_request(url, headers = self.bus_headers, data = payload, method = 'POST')
            time.sleep(random.randint(5, 6))
            if return_data['status'] != 'success':
                print(return_data['message'])
                return
            print('浏览完成')
        print('已完成全部任务，去掷骰子')
        self.throw()

    def throw(self):
        url1 = 'https://fission-events.ccbft.com/activity/dmspshzq/getIndex/224/gPpYzxmE'
        return_data1 = self.send_request(url1, headers = self.bus_headers)
        self.sleep()
        if return_data1['status'] != 'success':
            print(return_data1['message'])
            return
        remain_num = return_data1['data'].get('remain_num')
        if remain_num == '0':
            return print('当前没有骰子了')
        num = int(remain_num)
        for _ in range(num):
            url2 = 'https://fission-events.ccbft.com/activity/dmspshzq/drawPrize/224/gPpYzxmE'
            payload = {}
            return_data2 = self.send_request(url2, headers = self.bus_headers, data = payload, method = 'POST')
            time.sleep(random.randint(5, 6))
            if return_data2['status'] != 'success':
                print(return_data2['message'])
                continue
            add_step = return_data2['data'].get('add_step')
            current_step = return_data2['data'].get('current_step')
            prize_name = return_data2['data'].get('prize_name')
            print(f"前进步数:{add_step},当前步数:{current_step}\n获得奖励:{prize_name}")

    # 消保专区
    def fire(self):
        num_url = 'https://fission-events.ccbft.com/activity/dmspxbmountain/getUserInfo/224/8ZWX263w'  # 游戏次数
        return_data_num = self.send_request(num_url, headers = self.bus_headers)
        self.sleep()
        if return_data_num['status'] != 'success':
            print(return_data_num['message'])
            return
        remain_num = return_data_num['data'].get('remain_num')
        if remain_num == '0':
            return print('当前剩余游戏次数为0')
        for _ in range(int(remain_num)):
            id_url = 'https://fission-events.ccbft.com/activity/dmspxbmountain/startChallenge/224/8ZWX263w'  # 游戏id
            return_data_id = self.send_request(id_url, headers = self.bus_headers, method = 'POST')
            if return_data_id['status'] != 'success':
                print(return_data_id['message'])
                continue
            game_id = return_data_id['data']
            time.sleep(2)
            index_url = 'https://fission-events.ccbft.com/Common/activity/getActivityInfo/224/8ZWX263w'
            headers = self.bus_headers.copy()
            headers['cookie'] = headers.get('cookie', '') + '; l_id=' + game_id
            data = self.send_request(url = index_url, headers = headers)
            if data['status'] != 'success':
                print(data['message'])
                continue
            print('获取成功，开始登山游戏')
            time.sleep(25)

            game_url = 'https://fission-events.ccbft.com/activity/dmspxbmountain/doChallenge/224/8ZWX263w'  # 开始游戏
            payload_game = {"stage": 20, "score": 200, "l_id": game_id}
            return_data3 = self.send_request(game_url, headers = self.bus_headers, data = payload_game, method = 'POST')

            if return_data3['status'] != 'success':
                print(return_data3['message'])
                continue
            print(return_data3['message'])
            url4 = 'https://fission-events.ccbft.com/Component/draw/commonDrawPrize/224/8ZWX263w'  # 开始抽奖
            payload2 = {}
            return_data4 = self.send_request(url4, headers = self.bus_headers, data = payload2, method = 'POST')
            self.sleep()
            print(return_data4['message'])
            self.sleep(3,6)

    # 查询cc豆及过期cc豆时间
    def get_user_ccd(self):
        url_get_ccd = f'https://m3.dmsp.ccb.com/api/businessCenter/user/getUserCCD?zhc_token={self.zhc_token}'
        url_get_expired_ccd = f'https://m3.dmsp.ccb.com/api/businessCenter/user/getUserCCDExpired?zhc_token={self.zhc_token}'
        payload_get_ccd = {}
        payload_get_expired_ccd = {}

        try:
            return_data1 = self.send_request(url_get_ccd, headers = self.base_header, data = payload_get_ccd,
                                             method = 'POST')
            self.sleep()
            return_data2 = self.send_request(url_get_expired_ccd, headers = self.base_header,
                                             data = payload_get_expired_ccd, method = 'POST')

            if return_data1['code'] != 200:
                raise Exception(return_data1['message'])
            elif return_data2['code'] != 200:
                raise Exception(return_data2['message'])

            count1 = return_data1['data'].get('userCCBeanInfo').get('count')
            count2 = return_data2['data'].get('userCCBeanExpiredInfo').get('count')
            expire_date_str = return_data2['data'].get('userCCBeanExpiredInfo').get('expireDate')

            if expire_date_str:
                expire_date = datetime.fromisoformat(expire_date_str)
                formatted_date = expire_date.strftime('%Y-%m-%d %H:%M:%S')
                print(f'当前cc豆:{count1}，有{count2} cc豆将于{formatted_date}过期')
            else:
                print("expire_date_str is empty")

        except Exception as e:
            print(str(e))


CCD().run()

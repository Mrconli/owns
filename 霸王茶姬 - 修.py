"""
霸王茶姬签到

打开微信小程序抓webapi.qmai.cn里面的qm-user-token(一般在请求头里)填到变量bwcjck里面即可

支持多用户运行

多用户用&或者@隔开
例如账号1：10086 账号2： 1008611
则变量为10086&1008611
export bwcjck=""

cron: 0 0,7 * * *
const $ = new Env("MK霸王茶姬签到");
"""
import requests
import re
import os
import time
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)

#分割变量
if 'bwcjck' in os.environ:
    bwcjck = re.split("@|&",os.environ.get("bwcjck"))
    print(f'查找到{len(bwcjck)}个账号\n----------------------')
else:
    bwcjck = ''
    print('无bwcjck变量')



# 发送通知消息
# PUSHPLUS
Token = os.environ.get('PUSH_PLUS_TOKEN')
def push(content):
    if Token != '1':
        headers = {'Content-Type': 'application/json'}
        json = {"token": Token, 'title': '霸王茶姬', 'content': content, "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')
    else:
        print('')

def yx(ck):
    headers = {'qm-user-token': ck,'User-Agent': 'Mozilla/5.0 (Linux; Android 14; 2201122C Build/UKQ1.230917.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160065 MMWEBSDK/20231202 MMWEBID/2247 MicroMessenger/8.0.47.2560(0x28002F30) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64 MiniProgramEnv/android','qm-from': 'wechat'}
    dl = requests.get(url='https://webapi.qmai.cn/web/catering/crm/personal-info',headers=headers).json()
    if dl['message'] == 'ok':
        print(f"账号：{dl['data']['mobilePhone']}登录成功")
        data = {"activityId":"947079313798000641","appid":"10086"}
        lq = requests.post(url='https://webapi.qmai.cn/web/cmk-center/sign/takePartInSign',data=data,headers=headers).json()
        if lq['message'] == 'ok':
            print(f"签到情况：获得{lq['data']['rewardDetailList'][0]['rewardName']}：{lq['data']['rewardDetailList'][0]['sendNum']}")
        else:
            print(f"签到情况：{lq['message']}")


def main():
    z = 1
    for ck in bwcjck:
        try:
            print(f'登录第{z}个账号')
            #print('----------------------')
            yx(ck)
            print('----------------------')
            z = z + 1
        except Exception as e:
            print('未知错误1')
            push('脚本出问题，需调整')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('未知错误2')
        push('脚本出问题，需调整')
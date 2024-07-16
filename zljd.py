""""
cron: 2 8 * * *
new Env('金陵酒店')
MK集团本部
环境变量 zxjl 多号@分割
ck格式 抓包ck全部值#备注
"""
import os
import time
import requests
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)

class ACInstance:
    def __init__(self, ck):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; RMX3562 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.122 Mobile Safari/537.36 XWEB/1260053 MMWEBSDK/20240501 MMWEBID/2307 MicroMessenger/8.0.50.2701 (0x2800323C) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64 miniProgram/wx476ba9475c801433",
            'Cookie': ck
        }

    def sign(self):
        url = "https://80809.activity-12.m.duiba.com.cn/ctool/getCredits?_=" + str(int(time.time() * 1000))
        response = requests.get(url, headers=self.headers)
        data = response.json()
        if data['code'] == '0000000':
            credits = data['data']['credits']
            print(f"签到成功获得{credits}分")
            return f"签到成功获得{credits}分"
        else:
            msg = data['msg']
            print(msg)
            return msg

def send(msg):
    # 发送通知的函数实现，可以是调用微信、邮件等通知服务
    print(f"发送通知: {msg}")

if __name__ == "__main__":
    zxjl = os.environ.get('zxjl')
    if not zxjl:
        print("请设置环境变量后运行")
    else:
        zxjl_list = zxjl.split('@')
        for num, zxjl_item in enumerate(zxjl_list, start=1):
            try:
                cookie, note = zxjl_item.split('#')
                ac_instance = ACInstance(cookie)
                print(f"=====开始执行第{num}个账号 {note}=====")
                result_msg = ac_instance.sign()
                send(result_msg)
                print("===============================")
            except ValueError:
                print(f"第{num}个账号格式错误，请检查环境变量设置")
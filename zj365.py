import requests,os,time,sys,datetime
from notify import send
'''
new Env("中健365")
每日签到领现金0.1-0.2，自动秒到到账微信
入口：#小程序://中健365达人
抓包：https://dc.zhongjian365.com/域名里面的X-Auth-Key
变量名：zjck，多号换行
cron 0 7 * * *
v1.0
'''

notify = True#关闭通知为False

# version = sys.version.split(" ")
# ver = version[0].split(".")
# if int(ver[1]) != 10:
#     print(f"你的青龙python版本为{sys.version},请使用py3.10运行此脚本")

ck = os.getenv("zjck")
ck1 = ck.split("\n")
v = 1.0
def sign():
   url = "https://dc.zhongjian365.com/api/activity_clockin/signIn"
   payload = ""
   headers = {
      'X-Auth-Key': au,
      'xweb_xhr': '1',
      'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
      'Content-Type': 'application/json',
      'Accept': '*/*',
      'Host': 'dc.zhongjian365.com',
      'Connection': 'keep-alive'
   }

   res = requests.request("POST", url, headers=headers, data=payload)
   if res.status_code == 200:
      if res.json().get("code") ==200:
         print(f"{res.json().get('msg')}")
      elif res.json().get("code") ==201:
         print(f"{res.json().get('msg')}")
      elif res.json().get("code") ==202:
         print(f"{res.json().get('msg')}")
      elif res.json().get("code") ==302:
         print(f"{res.json().get('msg')},填写正确数据")
      else:
         print("未知错误",res.json())
   else:
      print("数据错误或者失效",res.json())
def cj():
    url = "https://dc.zhongjian365.com/api/activity_clockin/luckyDraw"

    payload = '{"to_day":"'+str(datetime.datetime.now()).split(" ")[0]+'"}'
    headers = {
        'Host': 'dc.zhongjian365.com',
        'Connection': 'keep-alive',
        'Content-Length': '23',
        'referer': 'https://servicewechat.com/wx064ad776729638f4/80/page-frame.html',
        'X-Auth-Key': au,
        'xweb_xhr': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6945',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh',

    }
    res = requests.request("POST", url, headers=headers, data=payload)
    if res.status_code == 200:
        if res.json().get("code") == 200:
            print(f"抽奖获得{res.json().get('data').get('amount')}元")
        elif res.json().get("code") == 201:
            print(f"{res.json().get('msg')}")
        elif res.json().get("code") == 202:
            print(f"{res.json().get('msg')}")
        elif res.json().get("code") == 302:
            print(f"{res.json().get('msg')},填写正确数据")
        else:
            print("未知错误", res.json())
    else:
        print("数据错误或者失效", res.json())

log_content = ''
class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        global log_content
        self.level.write(message)
        log_content += message

    def flush(self):
        return None
sys.stdout = LoggerWriter(sys.stdout)
gg = requests.request("GET", "https://ghproxy.com/https://raw.githubusercontent.com/241793/bucai2/main/gg")
if gg.status_code ==200:
    print(gg.text)
else:
    print("网路连接超时")
print(f"当前执行【中健365签到现金】 v{v}")
print(f"检测有【{len(ck1)}】个号")
for i in range(len(ck1)):
   au = ck1[i]
   print(f"==========账号{i+1}开始运行==========")
   sign()
   time.sleep(2)
   cj()
   if len(ck1)> i+1:
      print("\n=5秒后运行下一账号=\n")
      time.sleep(5)
if notify == True:
   send("中健365签到通知",log_content)

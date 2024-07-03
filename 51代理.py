import requests

url = 'https://m.51daili.com/wap/user/signin.html'

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

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")
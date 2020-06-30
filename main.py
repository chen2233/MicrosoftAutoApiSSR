# -*- coding: UTF-8 -*-
import os
import requests as req
import json
from pathlib import Path
import time
import random

# 先注册 Azure应用,确保应用有以下权限:
# files: Files.Read.All、Files.ReadWrite.All、Sites.Read.All、Sites.ReadWrite.All
# user: User.Read.All、User.ReadWrite.All、Directory.Read.All、Directory.ReadWrite.All
# mail: Mail.Read、Mail.ReadWrite、MailboxSettings.Read、MailboxSettings.ReadWrite
# 注册后一定要再点代表xxx授予管理员同意,否则 OutLook API 无法调用

# 拼接存 refresh_token 的 gist 文件路径
filepath = Path.cwd() / os.environ["GIST_ID"] / os.environ["GIST_TEXT"]

api_list = [
    r'https://graph.microsoft.com/v1.0/drive/root',
    r'https://graph.microsoft.com/v1.0/me/drive',
    r'https://graph.microsoft.com/v1.0/me/drive/recent',
    r'https://graph.microsoft.com/v1.0/me/drive/root',
    r'https://graph.microsoft.com/v1.0/me/drive/root/children',
    r'https://graph.microsoft.com/v1.0/me/messages',
    r'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
    r'https://graph.microsoft.com/v1.0/me/mailFolders',
    r'https://graph.microsoft.com/v1.0/me/onenote/sections',
    r'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
    r'https://graph.microsoft.com/v1.0/users',
]


def get_token(old_refresh_token):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': old_refresh_token,
        'client_id': os.environ["CONFIG_ID"],
        'client_secret': os.environ["CONFIG_KEY"],
        'redirect_uri': 'http://localhost:42791/'
    }
    html = req.post(
        'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        data=data,
        headers=headers)

    json_text = json.loads(html.text)

    with filepath.open(mode='w', encoding='utf-8') as file:
        file.write(json_text['refresh_token'])

    return json_text['access_token']


def main_invoke():
    file = filepath.open(mode='r', encoding='utf-8')
    old_refresh_token = file.read()
    file.close()

    access_token = get_token(old_refresh_token)
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json'
    }

    random.shuffle(api_list)  # 执行洗牌算法，使得每次相邻调用的顺序不一致

    try:
        for api_url in api_list:
            if random.random() > 0.88:  # 12%几率不执行
                continue
            time.sleep(random.uniform(1, 10))
            if req.get(api_url, headers=headers).status_code == 200:
                print("调用成功: ", api_url)
            else:
                print("调用异常: ", api_url)

        print('此次运行结束时间为: ', time.asctime(time.localtime(time.time())))
    except:
        print("调用出现异常，pass")
        pass


for _ in range(random.randint(4, 8)):  # 执行4-8次
    time.sleep(random.uniform(30, 600))  # 间隔30-600s
    main_invoke()

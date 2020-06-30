# 置顶
该项目是在 [InspAlgo/clockwork](https://github.com/InspAlgo/clockwork) 项目的基础上修改而来。调节了运行时间、调用的API的次数和概率。  
以下为原介绍：

# clockwork
该项目是在 [wangziyingwen/AutoApiSecret](https://github.com/wangziyingwen/AutoApiSecret) 项目的基础上修改而来。原项目不能将 refresh_token 信息进行隐藏，本项目通过使用 GitHub 的私有 gist 来存储 refresh_token 信息，达到了将 refresh_token 隐藏的目的。

## gist 准备
如下图所示，创建私有 gist，`****_token.txt` 这个名称自拟。  
![](https://user-images.githubusercontent.com/30190529/85358306-e9e9b580-b545-11ea-9a3c-43acba6736ae.png)  

在项目的 Secrets 中，新建 **GIST_HTTPS_WITH_TOKEN**、**GIST_ID**、**GIST_TEXT** 三个机密。  
1. **GIST_HTTPS_WITH_TOKEN** 存的是 gist 的 HTTPS 形式链接（`https://gist.github.com/****gist-id****.git`），以用于 git clone，需要注意的是该链接需要携带 GitHub 账号的 access token 信息，在个人的 `Settings/Developer settings/Personal access tokens` 中生成一个可以有创建 gist 权限的 token 即可。将 token 信息放到 gist 的 HTTPS 中，最后形式是 `https://****token****@gist.github.com/****gist-id****.git` 。  
2. **GIST_ID** 存的是 gist 的 id 编号，即 `https://****token****@gist.github.com/****gist-id****.git` 中的 `****gist-id****` 部分。  
3. **GIST_TEXT** 是 gist 中存放 token 的文件名称，包括文件后缀，如上图中的 `****_token.txt`。  

## gist 使用
在 GitHub Actions 的配置文件中（本项目是 `.github/workflows/auto_invoke.yml`）中，通过 `git clone $GIST_HTTPS` 先将 gist 克隆下来（克隆下来的 gist 项目与 main.py 同目录），再在 `main.py` 中访问 `****_token.txt`。`****_token.txt` 的路径是通过当前路径、**GIST_ID** 和 **GIST_TEXT** 拼接而成的。    

```python
# 拼接存 refresh_token 的 gist 文件路径
filepath = Path.cwd() / os.environ["GIST_ID"] / os.environ["GIST_TEXT"]
```

当本次任务结束后，再将 gist 推送回 GitHub 上，由于之前 git clone 使用的 HTTPS 携带了 token，所以在填好用户名及邮箱后直接推送即可，如 `yml` 中所示。**注意：由于 git clone 是在当前项目下生成的 gist 项目，故需要 cd 转移到 gist 文件夹内再推送。**  

```yml
- name: Push Gist # 上传新的 refresh_token 到 gist 
  env:
    GIST_ID: ${{ secrets.GIST_ID }}
  run: |
    git config --global user.email "ClockworkRobot@email.com"
    git config --global user.name "ClockworkRobot"
    cd $GIST_ID && git add . && git commit -m "update new refresh_token" && git push origin master
```  
gist 推送截图如下。  
![](https://user-images.githubusercontent.com/30190529/85361179-c7f43100-b54d-11ea-9b14-1f7e0fbb95ee.png)  

## workflow 的相关简化  

参考了原项目中由 [bindog](https://github.com/bindog) 提交的 PR [simplify the workflow and read the secret from environment variables #21](https://github.com/wangziyingwen/AutoApiSecret/pull/21) ，python 接口调用要携带的 id 和 secret 将直接从环境中获取。    

```
yml 中向环境中添加相关变量
env: 
  CONFIG_ID: ${{ secrets.CONFIG_ID }}

python 从环境中获取相关变量
id = os.environ["CONFIG_ID"]
```

## python 脚本的部分改动  

将相关调用的 API 链接放到列表中，并在每次执行循环调用前使用洗牌算法打乱顺序。   

```python
# API 链接列表
api_list = [
    r'https://graph.microsoft.com/v1.0/me/drive/root',
    r'https://graph.microsoft.com/v1.0/me/drive',
    r'https://graph.microsoft.com/v1.0/drive/root',
    r'https://graph.microsoft.com/v1.0/users',
    r'https://graph.microsoft.com/v1.0/me/messages',
    r'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
    r'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
    r'https://graph.microsoft.com/v1.0/me/drive/root/children',
    r'https://graph.microsoft.com/v1.0/me/mailFolders',
    r'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
]

# 洗牌，打乱顺序
random.shuffle(api_list)
```

同时还增加了随机时间，如 `time.sleep(60 * random.randrange(1, 8))` 和 `time.sleep(random.randrange(2, 12))` 以进行随机调用。  

## 致谢

+   [wangziyingwen](https://github.com/wangziyingwen) ， [AutoApiSecret](https://github.com/wangziyingwen/AutoApiSecret)   
+    [bindog](https://github.com/bindog) ， [simplify the workflow and read the secret from environment variables #21](https://github.com/wangziyingwen/AutoApiSecret/pull/21)   

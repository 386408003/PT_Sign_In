# PT站点自动操作

本项目主要是为了实现一些PT站点的自动化建立的，由于工作太忙，更新非常佛系，玩PT也比较佛系，懒得刷流，够用就行，目前规划有下面几项：

1. 朱雀这种玩游戏的（只实现自动放技能，一键升级）    √
2. 好大、海胆、52PT（需要攒题库）这种无法自动签到的    √
3. 大青虫、库非这种群聊区领福利的    √
4. 类似馒头这种需要时不时登录的
6. 红叶就搞不了了
7. 有CF盾的应该也搞不了



### 1. 朱雀自动释放技能

自动释放技能后会进行角色批量升级，需要搭配青龙面板。

众所周知，朱雀技能使用类似青龙这种任务面板实现不了自动释放技能，因为周期是24小时，如果是23.5小时那就刚刚好了，所以写了下面脚本，通过获取下次技能释放时间来动态设置青龙面板脚本执行时间。

1. 使用方式，将整个项目放入青龙面板 -> 脚本管理 -> 放置合适位置。
2. 青龙面板系统设置 -> 应用设置 -> 新建应用，记录下 ClientId，ClientSecret，青龙面板地址。
3. 新建或修改定时任务，命令/脚本 填写上面文件中的 main.py 文件路径，查看 F12 记录下任务的 id, name, command, label。
4. 修改 main.py，注释掉不需要的代码，如果只需要朱雀释放技能和批量升级可以只留下 28 和 30 行。
5. 登录朱雀记录下朱雀的 Cookie 和 csrf_token 的值。
6. 通过上述获取的参数，复制 /config/template.ini 模块并重命名为 /config/settings.ini，然后修改 settings.ini 配置文件。
7. 点击运行青龙面板的任务即可，后续理论上会到期的只有朱雀的 cookie。
8. 目前已知问题，如果脚本执行失败（网络原因），导致下次执行时间没有更新，由于过了当时的执行时间，会自动延至下一年，导致任务失效，有几种处理方案，出问题概率特别小，所以还没搞
   - 将下次执行时间顺延至第二天的那个时候。
   - 另起定时任务每10分钟执行，当技能任务时间延至下一年后，更新下次执行时间。
   - 做邮件推送，手工维护。



### 2. 站点签到功能

我有哪些站都写配置文件里面了，没有的站可以自己配置，如果有不适配的也可以联系我，复制对应的日志信息，我给适配，理论上配置好了配置文件，应该能适配所有网站吧。

1. 支持所有GET请求的网站（有CF盾的有可能失败）

2. 支持好大

3. 支持海胆

4. 支持52PT（题库在 /sign_in/sign_52pt.py 文件中）

5. 理论上配置好了配置文件，支持所有网站

6. 已知问题

   - 代理程序优化，需要先将所有请求的方法抽离出来搞成工具类。

     ```py
     proxies = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}
     r = requests.post(u, json=data, headers=headers, proxies=proxies)
     ```

   - 有CF盾的网站无法签到

   - 感觉配置文件对新手并不是很友好，虽然我已经尽量加注释，在程序里面做了处理



### 3. 群聊区福利

1. 目前有群聊区福利的我只有库非、大青虫。
2. 已知问题（目前全都是运行就会发布一次群聊信息）：
   - 群聊区多数是每日领一次
   - 大青虫的VIP和彩虹ID每月领一次
   - 下载量不确定领取间隔




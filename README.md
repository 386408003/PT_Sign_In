# PT站点自动操作

本项目主要是为了实现一些PT站点的自动化建立的，由于工作太忙，更新非常佛系，玩PT也比较佛系，懒得刷流，够用就行，目前规划有下面几项：

1. 朱雀这种玩游戏的（也只规划了自动放技能）
2. 好大、海胆这种无法自动签到的
3. 大青虫、库非这种群聊区领福利的
4. 52PT需要攒题库
5. 红叶就搞不了了
6. 有CF盾的应该也搞不了了

### 1. 朱雀自动释放技能

目前仅有自动释放技能的功能，需要搭配青龙面板。

众所周知，朱雀技能使用类似青龙这种任务面板实现不了自动释放技能，因为周期是24小时，如果是23.5小时那就刚刚好了，所以写了下面脚本，通过获取下次技能释放时间来动态设置青龙面板脚本执行时间。

1. 使用方式，将 zhuque 目录下三个文件放入青龙面板 -> 脚本管理 -> 可以自己新建个目录放这三个文件。
2. 青龙面板系统设置 -> 应用设置 -> 新建应用，记录下 ClientId，ClientSecret，青龙面板地址。
3. 新建或修改定时任务，命令/脚本 填写上面文件种的 zhuque.py 文件路径，查看 F12 记录下任务的 id, name, command, label。
4. 登录朱雀记录下朱雀的 Cookie 和 csrf_token 的值。
5. 通过上述获取的参数，修改 config.ini 配置文件，里面有注释。
6. 点击运行青龙面板的任务即可，后续理论上会到期的只有朱雀的 cookie。



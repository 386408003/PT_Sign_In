# -*- coding: utf-8 -*-
import time
from datetime import datetime
import requests
import qinglong

# 获取配置类
conf = qinglong.QL().conf["zhuque"]
# 请求头
headers = {
    'Referer': 'https://zhuque.in/gaming/genshin/character/list',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'X-Csrf-Token': conf.get('csrf_token')
}
# Cookies
cookies = {
    'connect.sid': conf.get('cookie')
}
# 技能类型
magic_type = {
    1: "获得灵石",
    2: "灵石加成",
    3: "免除冷却",
    4: "双倍灵石"
}


# 定义一个发送 get 请求方法，方便后面的重复调用
def get(url):
    try:
        session = requests.Session()
        session.cookies.update(cookies)
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response
        else:
            print(response, '响应异常！')
            exit()
    except Exception as e:
        print('请求异常！！！')
        print(e)


# 定义一个发送 post 请求方法，方便后面的重复调用
def post(url, data):
    try:
        session = requests.Session()
        session.cookies.update(cookies)
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response
        else:
            print(response, '响应异常！')
            exit()
    except Exception as e:
        print('请求异常！！！')
        print(e)


# 打印角色列表，并获取最近的技能释放时间
def get_min_next_time():
    url = 'https://zhuque.in/api/gaming/listGenshinCharacter'
    response = get(url).json()
    characters = response['data']['characters']
    min_time = 5000000000
    for character in characters:
        info = character['info']
        if len(info) > 0:
            rank = character['rank']
            name = character['name']
            magic = character['magic']
            # 时间样例：1701162076
            next_time = info['next_time']
            level = info['level']
            # 1: "获得灵石", 2: "灵石加成", 技能参与计算最小时间
            # 其中 灵石加成 这个技能单个角色加成10%，两个角色就会叠加为20%，所以时间到即可执行，无需考虑时间间隔
            # 这个技能类型让我一度以为我的代码逻辑有问题，太坑了
            # 3 和 4 这俩技能释放也不会修改技能时间，还好一开始我就设置了最大超时次数，要不一直在那获取时间释放技能，就 GG 了
            if magic == 1 or magic == 2:
                min_time = min(min_time, next_time)
            # 格式化时间，打印角色列表
            # next_timestamp = time.localtime(next_time)
            # next_time = time.strftime("%Y-%m-%d %H:%M:%S", next_timestamp)
            # 打印所有角色的信息
            # print('角色品级：', rank, '星，等级：', level, '级，技能：', magic_type[magic], '，下次技能时间：', next_time, '角色名：', name)
    return min_time


# 批量释放
def character_fire():
    url = 'https://zhuque.in/api/gaming/fireGenshinCharacterMagic'
    data = {
        "all": 1,
        "resetModal": True
    }
    response = post(url, data).json()
    status = response['status']
    if status == 200:
        bonus = response['data']['bonus']
        print('批量释放成功，一共获得：', bonus, '灵石')
    else:
        print('批量释放失败')


# 通过时间戳转换为青龙面板 cron 表达式
def get_cron_from_time(ts):
    # 将时间戳转换为 datetime 对象
    date_obj = datetime.fromtimestamp(ts)
    # 获取月份
    month = date_obj.month
    # 获取日期
    day = date_obj.day
    # 获取小时
    hour = date_obj.hour
    # 获取分钟
    minute = date_obj.minute
    # 获取秒数
    second = date_obj.second
    # 构建青龙面板可用的 cron 表达式
    check_in_type = conf.get("check_in_type", fallback='minute')
    if check_in_type == 'minute':
        return f"{minute} {hour} {day} {month} ?"
    else:
        return f"{second} {minute} {hour} {day} {month} ?"


# 朱雀一键释放技能
def check_in():
    # 获取下一次任务执行时间
    min_next_time = get_min_next_time()
    print('首次计算下次执行时间为：', min_next_time, "\n")
    # 最大重试次数（防止死循环）
    max_retry = int(conf.get("max_retry", fallback=5))
    # 当前重试次数
    current_retry = 1
    # 循环判断是否需要再次执行（触发免除冷却时间技能或执行失败重试几次）
    while True:
        if current_retry > max_retry:
            # 可在此处添加邮件通知，结束循环
            break
        # 获取当前时间
        now_ts = int(datetime.now().timestamp())
        print('本次循环时间：', now_ts)
        # 当前时间比最小技能释放时间大立即执行
        if min_next_time < now_ts:
            # 时间比当前时间小应该无需等待
            # time.sleep(2)
            print('执行技能时间：', datetime.now().timestamp())
            # 朱雀一键释放技能
            character_fire()
            # 获取下一次任务执行时间
            min_next_time = get_min_next_time()
        # 最小技能释放时间大于当前时间一分钟跳出循环
        elif min_next_time > now_ts + 60:
            break
        # 一分钟内的就等它一分钟，给它执行了
        else:
            # 加一秒缓冲时间
            time.sleep(min_next_time - now_ts + 1)
            print('执行技能时间：', datetime.now().timestamp())
            # 朱雀一键释放技能
            character_fire()
            # 获取下一次任务执行时间
            min_next_time = get_min_next_time()
        current_retry = current_retry + 1
        print('重新计算下次执行时间为：', min_next_time, "\n")
    cron = get_cron_from_time(min_next_time)
    # 设置下次定时任务执行时间
    qinglong.QL().update_cron(cron)


if __name__ == '__main__':
    # 经测试青龙面板 v2.15.16 版本支持输入秒，但不会触发执行
    # 由于最开始是按秒实现的，既然实现了，也不想删除了，万一只是是我哪里操作不对，又或者是这个版本的面板存在的 BUG 呢
    # 只在开发中进行了自测，因为面板不支持，没有经过实际环境测试，实际环境手动单次触发没有问题
    check_in()

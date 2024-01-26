import re
import json
import time
import requests
from src.commons.log import logger
from src.commons import config


# 更新到青龙面板
# 这个脚本是 52pojie 里面 Fujj 这位大佬写好的，我拿来改了改，地址是：
# https://www.52pojie.cn/forum.php?mod=viewthread&tid=1617118
# 具体改动位置是做了 token 的缓存，因为文章里面作者说了过期时间是30天
# 偷懒没有在程序里面校验 token 是否过期，然后自动续期，而是直接写死了 29 天更新 token
# 如需更改可搜索：29*24*60*60，修改 29 为想要的数字即可，或者直接修改配置文件里面的 expire_date
# 然后是添加了 update_cron 这个方法，用于更新对应任务的 cron 表达式
class QL:
    def __init__(self, ck=None, phone=None):
        self.section = 'qinglong'
        self.host = config.read_config(self.section, 'host')
        self.client_id = config.read_config(self.section, 'client_id')
        self.client_secret = config.read_config(self.section, 'client_secret')
        self.ck = ck
        self.phone = phone
        self.token = None
        expire_date_str = config.read_config(self.section, 'expire_date')
        if expire_date_str is not None:
            self.expire_date = float(expire_date_str)
            # 没过期就从配置文件取，过期了重新获取
            if time.time() < self.expire_date:
                self.token = config.read_config(self.section, 'token')
            else:
                self.token = self.get_token()
        else:
            self.token = self.get_token()

    # 获取 Token，有效期30天，所以做下缓存
    def get_token(self):
        if self.token is None:
            url = f'{self.host}open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}'
            response = requests.request('GET', url).json()
            logger.info('获取青龙面板的 Token: {}', response)
            # 获取 Token 并设置缓存到配置文件
            token = response['data']['token']
            config.write_config(self.section, 'token', token)
            # 29天重新获取
            config.write_config(self.section, 'expire_date', str(time.time() + 29*24*60*60))
            config.save_config()
            return token
        else:
            return self.token

    # 比对 ck 进行更新，如果未启用，进行启用
    def match_ck(self):
        pt_pin = str(re.findall(r'pt_pin=(.+?);', self.ck)[0])
        logger.info('手机号码 {} 的 pt_pin: {}', self.phone, pt_pin)
        ck_list = self.get_all_ck()
        for ck in ck_list:
            if pt_pin in str(ck['value']):
                logger.info('匹配成功，匹配到当前变量: {}', ck)
                _id = ck['id']
                remark = ck['remarks']
                logger.info('-------------------')
                logger.info('开始更新 {} 的 ck', remark)
                self.update_ck(remark, _id)
                if ck['status'] == 1:
                    logger.info('{} 开始启用', remark)
                    self.start_ck(_id)
                return
        self.add_ck()
        logger.info('新增 {} 手机号码的 ck', self.phone)
        return

    # 获取所有的变量
    def get_all_ck(self):
        t = int(round(time.time() * 1000))
        url = f'{self.host}open/envs?searchValue=&t={str(t)}'
        payload = ''
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        response = requests.request('GET', url, headers=headers, data=payload).json()
        return response['data']

    # 更新变量
    def update_ck(self, remark=None, _id=None):
        t = int(round(time.time() * 1000))
        url = f'{self.host}open/envs?t={str(t)}'
        payload = json.dumps({
            'name': 'JD_COOKIE',
            'value': self.ck,
            'remarks': remark,
            'id': _id
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        requests.request('PUT', url, headers=headers, data=payload)
        return

    # 添加变量
    def add_ck(self):
        t = int(round(time.time() * 1000))
        url = f'{self.host}open/envs?t={str(t)}'
        payload = json.dumps([
            {
                'value': self.ck,
                'name': 'JD_COOKIE',
                'remarks': self.phone
            }
        ])
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        requests.request('POST', url, headers=headers, data=payload)
        return

    # 启用变量
    def start_ck(self, _id):
        t = int(round(time.time() * 1000))
        url = f'{self.host}open/envs/enable?t={str(t)}'
        payload = json.dumps([
            _id
        ])
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        requests.request('PUT', url, headers=headers, data=payload)
        return

    # 更新定时任务的定时规则 cron = '0 10 * * *'
    def update_cron(self, cron):
        t = int(round(time.time() * 1000))
        url = self.host + 'open/crons?t=' + str(t)
        command = config.read_config(self.section, 'task_label')
        arr = []
        if command is not None:
            arr = command.split(',')
        payload = json.dumps({
            'name': config.read_config(self.section, 'task_name'),
            'command': config.read_config(self.section, 'task_command'),
            'schedule': cron,
            'labels': arr,
            'id': config.read_config(self.section, 'task_id')
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        response = requests.request('PUT', url, headers=headers, data=payload).json()
        logger.info('更新 朱雀魔力 任务时间表达式：{}， 更新结果Code为：{}', cron, response['code'])
        return

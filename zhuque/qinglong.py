import re
import json
import time
import requests
import configparser


# 更新到青龙面板
# 这个脚本是 52pojie 里面 Fujj 这位大佬写好的，我拿来改了改，地址是：
# https://www.52pojie.cn/forum.php?mod=viewthread&tid=1617118
# 具体改动位置是做了 token 的缓存，因为文章里面作者说了过期时间是30天
# 偷懒没有在程序里面校验 token 是否过期，然后自动续期，而是直接写死了 29 天更新 token
# 如需更改可搜索：29*24*60*60，修改 29 为想要的数字即可，或者直接修改配置文件里面的 expire_date
# 然后是添加了 update_cron 这个方法，用于更新对应任务的 cron 表达式
class QL:
    def __init__(self, ck=None, phone=None):
        # 青龙面板地址、账号密码
        conf = configparser.RawConfigParser()
        conf.read("./config.ini", encoding='UTF-8')
        self.conf = conf
        self.host = conf["ql"].get('host')
        self.client_id = conf["ql"].get('client_id')
        self.client_secret = conf["ql"].get('client_secret')
        self.ck = ck
        self.phone = phone
        self.token = None
        expire_date_str = conf["ql"].get('expire_date')
        if expire_date_str is not None:
            self.expire_date = float(expire_date_str)
            # 没过期就从配置文件取，过期了重新获取
            if time.time() < self.expire_date:
                self.token = conf["ql"].get('token')
            else:
                self.token = self.get_token()
        else:
            self.token = self.get_token()

    # 获取 Token，有效期30天，所以做下缓存
    def get_token(self):
        if self.token is None:
            url = self.host + "open/auth/token?client_id={}&client_secret={}".format(self.client_id, self.client_secret)
            response = requests.request("GET", url).json()
            print("获取青龙面板的Token:", response)
            # 获取 Token 并设置缓存到配置文件
            token = response["data"]["token"]
            self.conf.set("ql", "token", token)
            # 29天重新获取
            self.conf.set("ql", "expire_date", str(time.time() + 29*24*60*60))
            self.conf.write(open("./config.ini", "w"))
            return token
        else:
            return self.token

    # 比对 ck 进行更新，如果未启用，进行启用
    def match_ck(self):
        pt_pin = str(re.findall(r"pt_pin=(.+?);", self.ck)[0])
        print("手机号码{}的pt_pin:".format(self.phone), pt_pin)
        ck_list = self.get_all_ck()
        for ck in ck_list:
            if pt_pin in str(ck["value"]):
                print("匹配成功，匹配到当前变量:", ck)
                _id = ck["_id"]
                remark = ck["remarks"]
                print("-------------------")
                print("开始更新{}的ck".format(remark))
                self.update_ck(remark, _id)
                if ck["status"] == 1:
                    print("{}启用成功".format(remark))
                    self.start_ck(_id)
                return
        self.add_ck()
        print("新增{}手机号码的ck".format(self.phone))
        return

    # 获取所有的变量
    def get_all_ck(self):
        t = int(round(time.time() * 1000))
        url = self.host + "open/envs?searchValue=&t=" + str(t)
        payload = ""
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        response = requests.request("GET", url, headers=headers, data=payload).json()
        print("获取青龙面板所有的变量进行比对")
        return response["data"]

    # 更新变量
    def update_ck(self, remark=None, _id=None):
        t = int(round(time.time() * 1000))
        url = self.host + "open/envs?t=" + str(t)
        payload = json.dumps({
            "name": "JD_COOKIE",
            "value": self.ck,
            "remarks": remark,
            "_id": _id
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        print("更新变量")
        requests.request("PUT", url, headers=headers, data=payload)
        return

    # 添加变量
    def add_ck(self):
        t = int(round(time.time() * 1000))
        url = self.host + "open/envs?t=" + str(t)
        payload = json.dumps([
            {
                "value": self.ck,
                "name": "JD_COOKIE",
                "remarks": self.phone
            }
        ])
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        print("添加变量")
        requests.request("POST", url, headers=headers, data=payload)
        return

    # 启用变量
    def start_ck(self, _id):
        t = int(round(time.time() * 1000))
        url = self.host + "open/envs/enable?t=" + str(t)
        print(_id)
        id_list = [_id]
        payload = json.dumps(
            id_list
        )
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        print("启用ck：", payload)
        requests.request("PUT", url, headers=headers, data=payload)
        return

    # 更新定时任务的定时规则 cron = '0 10 * * *'
    def update_cron(self, cron):
        t = int(round(time.time() * 1000))
        url = self.host + "open/crons?t=" + str(t)
        command = self.conf["ql"].get('task_label')
        arr = []
        if command is not None:
            arr = command.split(",")
        payload = json.dumps({
            "name": self.conf["ql"].get('task_name'),
            "command": self.conf["ql"].get('task_command'),
            "schedule": cron,
            "labels": arr,
            "id": self.conf["ql"].get('task_id')
        })
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        response = requests.request("PUT", url, headers=headers, data=payload).json()
        print("更新 朱雀魔力 任务时间表达式：", cron, "， 更新结果Code为：", response["code"])
        return


if __name__ == '__main__':
    ck = 'pt_key=33JiC5lOADBAJIqAX8UDhNHkh_qypfyAyQkqWu5ADdZgHkudbNtdlSkBEOIMxO73oT_npf__Hvc;pt_pin=jd_67r828540e7yd;'
    # 如果知道手机号码，可以传 phone 作为标记，不然账号太多会比较乱
    QL().get_token()

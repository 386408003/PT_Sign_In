import json
import time
import requests
from lxml import etree
from ast import literal_eval
from urllib.parse import urlparse, urlencode
from src.commons.config_sign import read_section, read_config
from src.sign_in.sign_52pt import sign_in

section = 'Standard'
# 获取配置文件中的 UA 信息
user_agent = read_config(section, 'user_agent')
# 站点请求超时时间
timeout = int(read_config(section, 'timeout'))
# 支持代理
proxies = read_config(section, 'proxies')
if proxies is None or proxies == '':
    proxies = {}
else:
    proxies = literal_eval(proxies)


# 定义一个发送 get 请求方法，方便后面的重复调用
def get(url, cookies, headers):
    try:
        session = requests.Session()
        session.cookies.update(cookies)
        response = session.get(url, headers=headers, timeout=timeout, proxies=proxies)
        if response.status_code == 200:
            return response
        else:
            print(f'网站：{url} 响应异常，错误码：{response.status_code}')
            return response
            # exit()
    except Exception as e:
        print(f'网站：{url} 请求异常！！！')
        print(e)


# 定义一个发送 post 请求方法，方便后面的重复调用
def post(url, data, cookies, headers):
    try:
        session = requests.Session()
        session.cookies.update(cookies)
        response = session.post(url, headers=headers, data=data, timeout=timeout, proxies=proxies)
        if response.status_code == 200:
            return response
        else:
            print(f'网站：{url} 响应异常，错误码：{response.status_code}')
            return response
            # exit()
    except Exception as e:
        print(f'网站：{url} 请求异常！！！')
        print(e)


# 初始化所有要签到的站点信息
def init_web_sites():
    site_section = 'WebSite'
    sites = []
    # 遍历配置文件中的所有站点
    for key, _ in read_section(site_section):
        if key.startswith('url_'):
            # 获取网站配置索引
            index = int(key.split('_')[1])
            name = read_config(site_section, f"name_{index}")
            # 判断是否需要签到
            no_sign = read_config(site_section, f"no_sign_{index}")
            if no_sign is not None:
                print(f'{name} 已配置 no_sign 标记，将跳过签到')
                continue
            # 读取配置文件，初始化网站配置信息
            url = read_config(site_section, key)
            cookie = read_config(site_section, f"cookie_{index}")
            method = read_config(site_section, f"method_{index}")
            data = read_config(site_section, f"data_{index}")
            referer = read_config(site_section, f"referer_{index}")
            xpath = read_config(site_section, f"xpath_{index}")
            shout_msg = read_config(site_section, f"shout_msg_{index}")
            shout_xpath = read_config(site_section, f"shout_xpath_{index}")
            # 获取所有配置的网站信息
            sites.append(WebSite(index, url, name, cookie, method, data, referer, xpath, shout_msg, shout_xpath))
    return sites


# 站点信息类
class WebSite:
    # 初始化方法
    def __init__(self, _index, _url, _name, _cookie, _method='GET',
                 _data=None, _referer=None, _xpath=None, _shout_msg=None, _shout_xpath=None):
        self.index = _index
        self.url = _url
        self.name = _name
        # 将 Cookie 字符串解析为字典形式
        cookies_dict = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in _cookie.split('; ')}
        self.cookie = cookies_dict
        if _method is None:
            self.method = 'GET'
        else:
            self.method = _method
        # 将参数转为字典类型
        if _data is not None:
            try:
                self.data = eval(_data)
            except SyntaxError:
                self.data = _data
                print("字符串的语法无效")
        else:
            self.data = _data
        self.referer = _referer
        if _xpath is None:
            self.xpath = '//table[@class="mainouter"]//h2/text()'
        elif _xpath == 'None':
            self.xpath = None
        else:
            self.xpath = _xpath
        self.shout_msg = _shout_msg
        self.shout_xpath = _shout_xpath
        # 接收签到结果
        self.response = ''

    # 获取请求头
    def get_header(self):
        if self.referer is None:
            headers = {
                'User-Agent': user_agent
            }
        else:
            headers = {
                'Referer': self.referer,
                'User-Agent': user_agent
            }
        return headers

    # 判断签到是否成功
    def is_sign_success(self, response):
        if response is None:
            self.response = '请求或响应异常，签到失败！'
            return
        if self.xpath is None:
            self.response = response.text
        else:
            # 一般 GET 请求返回的都是 HTML
            # 使用 XPath 提取元素的内容
            root = etree.HTML(response.text)
            sign_mark = root.xpath(self.xpath)
            if len(sign_mark) == 0:
                # 冰淇淋以及上述通用xpath不适配的，使用此通用xpath再次解析
                sign_mark = root.xpath('//h2[@align="left"]/text()')
                if len(sign_mark) == 0:
                    if response.status_code == 403:
                        self.response = f"签到失败，可能由于CF盾导致。"
                    else:
                        # 部分站点未登录
                        sign_mark = root.xpath('//table[@class="mainouter"]//h1/text()')
                        if len(sign_mark) == 0:
                            self.response = f"网站返回Code：{response.status_code}，签到结果未知，未登录或未适配。"
                        else:
                            self.response = f"Cookie失效，{sign_mark[0]}"
                else:
                    self.response = sign_mark[0]
            else:
                mark = sign_mark[0]
                # 多次签到有些网站会提示抱歉
                if '抱歉' == mark:
                    self.response = f'{mark}，已签到，无需重复签到！'
                # 海胆提示：小海胆开小差了，刷新后再来试试吧! 其实已经签到成功
                elif '小海胆开小差了' in mark:
                    self.response = '签到成功'
                # 学校首次签到与后续返回有差异，后续都可使用此关键词判断，故直接使用这个关键词进行判断了
                elif '最近消息' == mark:
                    self.response = '签到成功'
                else:
                    self.response = mark

    # 签到
    def sign_in(self):
        if self.name == '52PT':
            response = sign_in(self.url, self.cookie)
            self.response = response
        else:
            if self.method == 'POST':
                response = post(self.url, self.data, self.cookie, self.get_header())
            else:
                response = get(self.url, self.cookie, self.get_header())
            # 处理返回值，并将签到结果保存到对象属性中
            self.is_sign_success(response)

    # 判断喊话是否成功
    def is_shout_success(self, response):
        html = etree.HTML(response.text)
        results = html.xpath(self.shout_xpath)
        for line in results:
            # TODO 获取用户预注册 ID
            if '@zhufeng' in line:
                line = line.replace(' @zhufeng ', '').replace('\n', '')
                self.response = f'{self.response}\n领取结果：{line}'
                break

    # 喊话
    def shout(self):
        # 未配置喊话内容不进行喊话
        if self.shout_msg is None or self.shout_msg == '':
            return
        msg_array = json.loads(self.shout_msg)
        parsed_url = urlparse(self.url)
        for msg in msg_array:
            data = {
                'shbox_text': msg['msg'],
                'shout': '我喊',
                'sent': 'yes',
                'type': 'shoutbox'
            }
            # 查询喊话结果
            # url = 'https://kufei.org/shoutbox.php?type=shoutbox'
            # url = 'https://cyanbug.net/shoutbox.php?type=shoutbox'
            # 构建喊话的 URL
            # url = 'https://kufei.org/shoutbox.php?' + urlencode(data)
            url = f"{parsed_url.scheme}://{parsed_url.netloc}/shoutbox.php?{urlencode(data)}"
            response = get(url, self.cookie, self.get_header())
            # 处理返回值，并将喊话结果保存到对象属性中
            self.is_shout_success(response)
            # 防止喊话过快
            time.sleep(2)

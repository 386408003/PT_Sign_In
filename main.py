from src.commons.log import logger
from src.commons.qinglong import QL
from zhuque.zhuque import check_in, character_train
from sign_in.sign_in import init_web_sites
from commons.config import read_section, read_config


if __name__ == '__main__':

    # 设置京东 Cookie 信息，支持多账号，phone 其实是备注
    section = 'jingdong'
    cookies = []
    for key, _ in read_section(section):
        if key.startswith('cookie_'):
            # 获取网站配置索引
            index = int(key.split('_')[1])
            phone = read_config(section, f"phone_{index}")
            ck = read_config(section, key)
            cookie = {'phone': phone, 'ck': ck}
            cookies.append(cookie)
    for cookie in cookies:
        QL(cookie['ck'], cookie['phone']).match_ck()

    # 朱雀释放技能
    # 经测试青龙面板 v2.15.16 版本支持输入秒，但不会触发执行
    # 由于最开始是按秒实现的，既然实现了，也不想删除了，万一只是是我哪里操作不对，又或者是这个版本的面板存在的 BUG 呢
    # 只在开发中进行了自测，因为面板不支持，没有经过实际环境测试，实际环境手动单次触发没有问题
    check_in()
    # 一键升级所有角色
    character_train()

    # 一键签到
    # 遗留问题：CF 盾的网站，PTT 第一次访问返回什么
    # 获取所有配置的网站信息
    web_sites = init_web_sites()
    for site in web_sites:
        # 签到
        site.sign_in()
        # 喊话
        site.shout()
    # 统一打印签到和喊话结果
    for site in web_sites:
        logger.info(f"站点名称：{site.name}，签到结果：{site.response}")

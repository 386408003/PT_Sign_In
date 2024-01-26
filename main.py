from src.commons.qinglong import QL
from zhuque.zhuque import check_in


if __name__ == '__main__':
    cookies = [{
        'phone': '12345678901',
        'ck': 'pt_key=33JiC5lOADBAJIqAX8UDhNHkh_qypfyAyQkqWu5ADdZgHkudbNtdlSkBEOIMxO73oT_npf__Hvc;pt_pin=jd_67r828540e7yd;'
    }]

    # 设置京东 Cookie 信息，支持多账号，phone 其实是备注
    for cookie in cookies:
        QL(cookie['ck'], cookie['phone']).match_ck()

    # 朱雀释放技能
    # 经测试青龙面板 v2.15.16 版本支持输入秒，但不会触发执行
    # 由于最开始是按秒实现的，既然实现了，也不想删除了，万一只是是我哪里操作不对，又或者是这个版本的面板存在的 BUG 呢
    # 只在开发中进行了自测，因为面板不支持，没有经过实际环境测试，实际环境手动单次触发没有问题
    check_in()

from src.commons.qinglong import QL


if __name__ == '__main__':
    cookies = [{
        'phone': '12345678901',
        'ck': 'pt_key=33JiC5lOADBAJIqAX8UDhNHkh_qypfyAyQkqWu5ADdZgHkudbNtdlSkBEOIMxO73oT_npf__Hvc;pt_pin=jd_67r828540e7yd;'
    }]

    # 如果知道手机号码，可以传 phone 作为标记，不然账号太多会比较乱
    for cookie in cookies:
        QL(cookie['ck'], cookie['phone']).match_ck()

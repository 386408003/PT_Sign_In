# -*- coding: utf-8 -*-
import requests
from lxml import etree
from src.commons.log import logger

# 题库
questions = [
    ('2', ['1']),
    ('3', ['1']),
    ('5', ['2','4','8']),
    ('7', ['1','4','8']),
    ('8', ['1','2']),
    ('10', ['1','8']),
    ('11', ['1']),
    ('12', ['1']),
    ('13', ['1','2','4']),
    ('14', ['1','2','4']),
    ('15', ['1']),
    ('16', ['1','2','4']),
    ('19', ['4','8']),
    ('20', ['1','4']),
    ('21', ['1','2']),
    ('22', ['1','2','4','8']),
    ('24', ['1']),
    ('25', ['1']),
    ('26', ['1']),
    ('30', ['1'])
]

headers = {
    'Referer': 'https://52pt.site/index.php',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
url = 'https://52pt.site/bakatest.php'
xpath = '//*[@id="outer"]/table[1]/tr/td/b/font/text()'
cookies = {}


# 获取问题 ID
def get_question_id():
    session = requests.Session()
    session.cookies.update(cookies)
    response = session.get(url, headers=headers)
    logger.info('查询问题ID完毕！')
    html = etree.HTML(response.text)
    # 标题
    # tr_title = html.xpath('//form/table/tr[1]/td/text()')[0]
    # 选项的 key 和 value
    tr_options = html.xpath('//form/table/tr[2]/td/input')
    # 选项的内容
    # contents = html.xpath('//form/table/tr[2]/td/input/following-sibling::text()')
    # # 心情输入框
    # tr_textarea = html.xpath('//form/table/tr[3]/td/textarea')[0]
    # area_name = tr_textarea.xpath('./@name')[0]
    # area_text = tr_textarea.xpath('./text()')[0]
    # # 提示信息（没有提示信息的时候，不知道会不会没有这个 tr）
    # tips = html.xpath('//form/table/tr[4]/td/text()')[0]
    # # 表单按钮
    # tr_button = html.xpath('//form/table/tr[5]/td/input')
    # print('题目：', tr_title)
    # for option, content in zip(tr_options, contents):
    #     input_name = option.xpath('./@name')[0]
    #     input_value = option.xpath('./@value')[0]
    #     input_type = option.xpath('./@type')[0]
    #     print('选项：type=%-8s, name=%-11s, value=%-3s, 内容：%s'
    #           % (input_type, input_name, input_value.strip(), content.strip()))
    # print('选项：type=textarea, name=%-22s, 内容：%s' % (area_name, area_text))
    # print(tips)
    for option in tr_options:
        input_name = option.xpath('./@name')[0]
        input_value = option.xpath('./@value')[0]
        if input_name == 'questionid':
            return 200, input_value.strip()
    if tr_options is None or len(tr_options) == 0:
        results = html.xpath(xpath)
        return 300, results[0]
    else:
        return 300, '获取问题ID失败，请检查Cookie是否失效！'


# 通过问题 ID 获取答案
def get_answer(question_id):
    # 签到参数
    answer = [
        ('questionid', question_id),
        ('usercomment', '此刻心情:无'),
        ('submit', '提交')
    ]
    answer_ids = []
    for ques_id, ans_ids in questions:
        if question_id == ques_id:
            answer_ids = ans_ids
    if len(answer_ids) <= 0:
        return 300, f'题目编号：{question_id} 题库中不存在，请维护题库！'
    for answer_id in answer_ids:
        answer.append(('choice[]', answer_id))
    logger.info(f'已从题库找到问题 {question_id} 的答案，签到请求参数为：{answer}')
    return 200, answer


# 签到
def sign_in(_url, _cookie):
    global url, cookies
    url = _url
    cookies = _cookie
    status, question = get_question_id()
    if status != 200:
        return question
    status, answer = get_answer(question)
    if status != 200:
        return answer
    session = requests.Session()
    session.cookies.update(cookies)
    response = session.post(url, headers=headers, data=answer)
    logger.info('52PT 签到完毕！')
    html = etree.HTML(response.text)
    results = html.xpath('//*[@id="outer"]/table[1]/tr/td/b/font/text()')
    return results[0]

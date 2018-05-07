# coding=utf-8
import requests
import hashlib
import logging

global user_id, token


def md5(password):
    '''
    明文密码转化成MD5
    :param password: 明文密码
    :return:  32位MD5码
    '''
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    return m.hexdigest()

def test_func(method = 'post', url = '/user/register', data = None, files = None, timeout=3):
    global user_id, token
    baseurl = dict['baseurl']
    if 'pass' in data.keys():
        data['pass'] = md5(data['pass'])
    try:
        if 'user_id' in data.keys():
            if 'default' == data['user_id']:
                data['user_id'] = user_id
        if 'token' in data.keys():
            if 'default' == data['token']:
                data['token'] = token
        if method == ('post' or 'POST'):
            result = requests.post(baseurl+url, data, files=files, timeout=timeout)
        elif method == ('get' or 'GET'):
            result = requests.get(baseurl+url, data)
        resopnse = result.json()
        #待修改
        #print(resopnse)
        assert resopnse['msg'] == 'Succeeded', logging.error('请求失败 %s' % resopnse)
        # 将最近一次登录后的user_id和token保存到全局变量
        if url == '/user/login':
            user_id = resopnse['user']['user_id']
            token = resopnse['user']['token']
        logging.info('---------Pass---------')
    except BaseException as e:
        logging.error('something wrong %s' % e)

def run():
    for i in dict['testcases']:
        if 'files' in i.keys():
            test_func(i['method'], i['url'], i['data'], i['files'])
        else:
            test_func(i['method'], i['url'], i['data'])


dict = {
    'baseurl': 'http://offline.api.slightech.com',
    'testcases': [
        {
            'method': 'post',
            'url': '/user/login',
            'data': {
                'email': 'test1@test.com',
                'pass': '123456'
            }
        },
        {
            'method': 'post',
            'url': '/user/avatar',
            'data': {
                'user_id': 'default',
                'token': 'default',
                'pic': 'avatar.jpg'
            },
            'files': {'pic': open('avatar.jpg', 'rb')}
        }
    ]
}
# 配置日志信息
logging.basicConfig(filename='apilog.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
# 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 设置日志打印格式
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)


run()
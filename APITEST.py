# coding=utf-8
import requests
import hashlib
import logging
import json
import time

global user_id, token, num, elaspedtime, passnum
num = 0
passnum = 0

def md5(password):
    '''
    明文密码转化成MD5
    :param password: 明文密码
    :return:  32位MD5码
    '''
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    return m.hexdigest()

def logg(method, url, elapsedtime, result, casenum, response):
    logging.info('--------------------------------')
    if result:
        result = 'Pass'
    else:
        result = 'Failed'
    jsonstr = json.dumps(response, indent=1)
    logging.info('用例'+str(casenum)+':'+'-----------'+str(result)+'-----------')
    logging.info('请求方法 --- '+method)
    logging.info('请求url --- '+url)
    logging.info('响应时间 --- '+str(elapsedtime))
    logging.info('返回结果 --- ')
    logging.info(jsonstr)

def endlog(passnum, casenum, allelapsedtime):
    rate = 100*(passnum/casenum)
    logging.info('-----------Tests run:'+str(casenum)+'  Passed:'+str(passnum)+'  Pass rate:%.2f%% -------------------------' % rate)
    logging.info('-----------Average response time: %.4f ------------------------------------' % (allelapsedtime/2))
    logging.info('-----------------------------------------------------------------------------')


def test_func(method='post', url='/user/register', data=None, files=None, num=0, timeout=3):
    global user_id, token, elaspedtime, passnum
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
        #单个case花费的响应时间
        elaspedtime = result.elapsed.total_seconds()
        #所有case花费的响应时间
        if resopnse['msg'] == 'Succeeded':
            # 将最近一次登录后的user_id和token保存到全局变量
            if url == '/user/login':
                user_id = resopnse['user']['user_id']
                token = resopnse['user']['token']
            logg(method, url, elaspedtime, True, num, resopnse)
            passnum += 1
        else:
            logg(method, url, elaspedtime, False, num, resopnse)
    except BaseException as e:
        logging.error('something wrong: %s' % e)
        elaspedtime = 0
    return elaspedtime, passnum

def run():
    starttime = time.localtime(time.time())
    prtstime = time.strftime("%Y-%m-%d %H:%M:%S", starttime)
    allelaspedtime = 0
    for i in dict['testcases']:
        global num
        num += 1
        if 'files' in i.keys():
            oncetime = test_func(i['method'], i['url'], i['data'], i['files'], num=num)[0]
        else:
            oncetime = test_func(i['method'], i['url'], i['data'], num=num)[0]
        # 所有case花费的响应时间
        allelaspedtime += oncetime

    endtime = time.localtime(time.time())
    prtetime = time.strftime("%Y-%m-%d %H:%M:%S", endtime)
    logging.info('-----------Start from '+prtstime+' to '+prtetime+' ------------')
    endlog(passnum, num, allelaspedtime)



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
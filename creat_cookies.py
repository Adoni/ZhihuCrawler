# coding=utf-8

from __future__ import unicode_literals, print_function

from zhihu_oauth import ZhihuClient

TOKEN_FILE = 'token.pkl'

for i, client_info in enumerate(open('./cookies/client_info_list.data')):
    print('------',i,'------')
    client_info = client_info.strip().split(' ')
    print(client_info)
    assert(len(client_info)==2)
    client = ZhihuClient()
    client.login_in_terminal(client_info[0], client_info[1])
    Cookies_File = './cookies/cookies%s.json' % i
    client.save_token(Cookies_File)

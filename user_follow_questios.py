from __future__ import unicode_literals, print_function
from RedisQueue import RedisQueue
from zhihu_oauth import ZhihuClient
import datetime
import time
import random
import sys
from timeout import timeout
import os
from utils import print_err
from pymongo import MongoClient

MAX_SLEEP_TIME = 15
Cookies_File = './cookies/cookies%s.json' % sys.argv[1]
global client
client = ZhihuClient()
if os.path.isfile(Cookies_File):
    client.load_token(Cookies_File)
else:
    client_info = open('./cookies/client_info_list.data').readlines()
    client_info = client_info[int(sys.argv[1])].strip().split('\t')
    client.login_in_terminal(client_info[0], client_info[1])
    client.save_token(Cookies_File)


def get_user_questions(uname):
    global client
    if uname == '':
        return
    print(uname)

    user_questions = dict()
    try:
        people = client.people(uname)
        user_questions['_id'] = uname
        user_questions['owner'] = uname
        user_questions['questions'] = []
        for q in people.following_questions:
            user_questions['questions'].append({
                'id': q.id,
                'title': q.title,
                #'detail': q.detail,
            })
    except Exception as e:
        print_err(e)
        print_err(uname)
        print_err("Something wrong when try to get user's followed topics")
        time.sleep(random.uniform(0, 5))

    return user_questions


if __name__ == '__main__':
    q = RedisQueue('follow_question_queue')
    sleep_time = 0
    db = MongoClient().zhihu.zhihu_follow_questions
    while 1:
        if (q.empty()):
            print('Finished at %s' % str(datetime.datetime.now()))
            print('Waiting ...')
        uname = q.get()
        uname = uname.decode()
        if db.find({'_id': uname}).count() > 0:
            continue

        try:
            with timeout(seconds=40):
                all_questions = get_user_questions(uname)
                if all_questions == {}:
                    continue
                elif all_questions is None:
                    sleep_time += random.uniform(1, 5)
                    print_err('Sleeping for %0.2f seconds' % sleep_time)
                    time.sleep(sleep_time)
                else:
                    db.insert(all_questions)
                    sleep_time -= 1
                    sleep_time = max(0, sleep_time)
                    time.sleep(random.uniform(1, 3))
        except TimeoutError:
            print_err('Timeout!')
            sleep_time += random.uniform(1, 5)
            print_err('Sleeping for %0.2f seconds' % sleep_time)
            time.sleep(sleep_time)
        if sleep_time > MAX_SLEEP_TIME:
            # refresh the client
            print_err('Refresh client!')
            client = ZhihuClient(Cookies_File)
            sleep_time = 0
    print('Done')

from __future__ import unicode_literals, print_function
from RedisQueue import RedisQueue
from zhihu_oauth import ZhihuClient, Answer, Article
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


def get_user_collections(uname):
    global client
    if uname == '':
        return
    print(uname)

    user_collections = dict()
    try:
        people = client.people(uname)
        user_collections['_id'] = uname
        user_collections['owner'] = uname
        user_collections['collections'] = dict()
        for collection in people.collections:
            user_collections['collections'][collection.title] = []
            for content in collection.contents:
                c_id = content.id
                q_id = -1
                if isinstance(content, Answer):
                    title = content.question.title
                    q_id = content.question.id
                elif isinstance(content, Article):
                    title = content.title
                user_collections['collections'][collection.title].append({
                    'id': c_id,
                    'q_id': q_id,
                    'title': title,
                    #'detail': q.detail,
                })
    except Exception as e:
        print_err(e)
        print_err(uname)
        ferr = open('./err.out', 'a')
        ferr.write(uname + '\n')
        print_err("Something wrong when try to get user's collections")
        time.sleep(random.uniform(0, 5))

    return user_collections


if __name__ == '__main__':
    q = RedisQueue('answer_queue')
    sleep_time = 0
    db = MongoClient().zhihu.zhihu_collections
    while 1:
        if (q.empty()):
            print('Finished at %s' % str(datetime.datetime.now()))
            print('Waiting ...')
        uname = q.get()
        try:
            uname = uname.decode()
        except:
            continue
        if db.find({'_id': uname}).count() > 0:
            continue

        try:
            with timeout(seconds=40):
                all_collections = get_user_collections(uname)
                if all_collections == {}:
                    continue
                elif all_collections is None:
                    sleep_time += random.uniform(1, 5)
                    print_err('Sleeping for %0.2f seconds' % sleep_time)
                    time.sleep(sleep_time)
                else:
                    db.insert(all_collections)
                    sleep_time -= 1
                    sleep_time = max(0, sleep_time)
                    time.sleep(random.uniform(1, 3))
        except TimeoutError:
            print_err('Timeout!')
            sleep_time += random.uniform(1, 5)
            print_err('Sleeping for %0.2f seconds' % sleep_time)
            time.sleep(sleep_time)
        except Exception as e:
            print_err('Unknown exception!!')
            print_err(e)
        if sleep_time > MAX_SLEEP_TIME:
            # refresh the client
            print_err('Refresh client!')
            client = ZhihuClient(Cookies_File)
            sleep_time = 0
    print('Done')

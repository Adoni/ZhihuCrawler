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


def get_followed_topics(uname):
    global client
    if uname == '':
        return
    print(uname)

    followed_topics = []

    try:
        people = client.people(uname)
        followed_topics.append(uname)
        for followed_topic in people.following_topics:
            followed_topics.append(
                followed_topic.id + '/' + followed_topic.name
            )
    except Exception as e:
        print_err(e)
        print_err(uname)
        print_err("Something wrong when try to get user's followed topics")
        time.sleep(random.uniform(0, 5))

    return followed_topics


if __name__ == '__main__':
    q = RedisQueue('user_followed_topics_queue')
    sleep_time = 0
    while 1:
        if (q.empty()):
            print('Finished at %s' % str(datetime.datetime.now()))
            print('Waiting ...')
        uname = q.get()
        uname = uname.decode()

        try:
            with timeout(seconds=40):
                all_followed_topics = get_followed_topics(uname)
                if all_followed_topics == []:
                    continue
                elif all_followed_topics is None:
                    sleep_time += random.uniform(1, 5)
                    print_err('Sleeping for %0.2f seconds' % sleep_time)
                    time.sleep(sleep_time)
                else:
                    user_followed_topics_file = open(
                        'user_followed_topics.data', 'a'
                    )
                    user_followed_topics_file.write(
                        '\t'.join(all_followed_topics)
                    )
                    user_followed_topics_file.write('\n')
                    user_followed_topics_file.flush()
                    user_followed_topics_file.close()
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

from RedisQueue import RedisQueue
from zhihu import ZhihuClient
import datetime
import random
import time
import sys
from timeout import timeout
from utils import print_err

MAX_SLEEP_TIME = 15
Cookies_File = './cookies/cookies%s.json' % sys.argv[1]
global client
client = ZhihuClient(Cookies_File)


def get_followees(uname):
    global client
    if uname == '':
        return None
    url = 'http://www.zhihu.com/people/%s' % uname
    print(url)
    followee_urls = []
    try:
        author = client.author(url)
        if author.followee_num == 0:
            return []
        for followee in author.followees:
            followee_url = followee.url[29:-1]
            followee_urls.append(followee_url)
    except Exception as e:
        print_err(e)
        print_err(uname)
        print_err("Something wrong when try to get user's followees")
        return None
    return followee_urls


if __name__ == '__main__':
    q = RedisQueue('user_followees_queue')
    sleep_time = 0
    while 1:
        if (q.empty()):
            print('Finished at %s' % str(datetime.datetime.now()))
            print('Waiting ...')
        uname = q.get()
        uname = uname.decode()
        try:
            with timeout(seconds=40):
                followee_urls = get_followees(uname)
                if followee_urls == []:
                    continue
                elif followee_urls is None:
                    sleep_time += random.uniform(1, 5)
                    print_err('Sleeping for %0.2f seconds' % sleep_time)
                    time.sleep(sleep_time)
                else:
                    user_followees_file = open('user_followees.data', 'a')
                    user_followees_file.write(
                        uname + '\t' + '\t'.join(
                            followee_urls
                        ) + '\n'
                    )
                    user_followees_file.flush()
                    user_followees_file.close()
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

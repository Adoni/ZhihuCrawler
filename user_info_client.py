from RedisQueue import RedisQueue
from zhihu import ZhihuClient
import datetime
import time
import random
import sys
from timeout import timeout
from termcolor import colored, cprint

MAX_SLEEP_TIME = 15
Cookies_File = './cookies/cookies%s.json' % sys.argv[1]
global client
client = ZhihuClient(Cookies_File)

print_err = lambda x: cprint(x, 'red')

def get_user_info(uname):
    global client
    if uname == '':
        return None
    url = 'http://www.zhihu.com/people/%s' % uname
    print(time.strftime('%Y-%m-%d %H:%M:%S') + '  ' + url)

    all_info = []
    try:
        author = client.author(url)
        # 获取用户url
        all_info.append(uname)
        # 获取用户名字
        all_info.append(author.name)
        # 当前用户是否为三零用户，其实是四零： 赞同0，感谢0，提问0，回答0
        try:
            all_info.append(str(author.is_zero_user()))
        except:
            all_info.append('Unknown')
        # 用户的性别
        all_info.append(author.gender)
        # 用户的所在地
        all_info.append(author.location)
        # 用户的行业
        all_info.append(author.business)
        # 用户的教育状况
        all_info.append(author.education)
        # 获取用户自我介绍
        all_info.append(author.motto)

        # 用户答案数量
        all_info.append(author.answer_num)
        # 收藏夹数量
        all_info.append(author.collection_num)
        # 获取用户关注的专栏数
        all_info.append(author.followed_column_num)
        # 获取用户关注的话题数
        all_info.append(author.followed_topic_num)
        # 获取关注了多少人
        all_info.append(author.followee_num)
        # 获取追随者数量
        all_info.append(author.follower_num)
        # 获取专栏文章数量
        all_info.append(author.post_num)
        # 获取提问数量
        all_info.append(author.question_num)
        # 获取收到的感谢数量
        all_info.append(author.thank_num)
        # 获取收到的的赞同数量
        all_info.append(author.upvote_num)

        # 获取用户头像图片地址
        all_info.append(author.photo_url)
        # 获取用户微博链接
        all_info.append(author.weibo_url)
    except Exception as e:
        print_err(e)
        print_err(uname)
        print_err("Something wrong when try to get user's information")
        return None
    all_info = map(lambda v: str(v), all_info)
    return all_info


if __name__ == '__main__':
    q = RedisQueue('user_info_queue')
    sleep_time = 0
    while 1:
        if (q.empty()):
            print('Finished at %s' % str(datetime.datetime.now()))
            print('Waiting ...')
        uname = q.get()
        uname = uname.decode()
        try:
            with timeout(seconds=40):
                all_info = get_user_info(uname)
                if all_info == []:
                    continue
                elif all_info == None:
                    sleep_time += random.uniform(1, 5)
                    print_err('Sleeping for %0.2f seconds' % sleep_time)
                    time.sleep(sleep_time)
                else:
                    user_info_file = open('user_info.data', 'a')
                    user_info_file.write('\t'.join(all_info))
                    user_info_file.write('\n')
                    user_info_file.flush()
                    user_info_file.close()
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

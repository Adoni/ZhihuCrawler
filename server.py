from RedisQueue import RedisQueue
import sys
import random

if __name__ == '__main__':
    target_map = {
        'user_info': ('user_info.data', 'user_info_queue'),
        'user_followed_topics':
        ('user_followed_topics.data', 'user_followed_topics_queue'),
    }
    if len(sys.argv) == 1:
        print('Please input the target: %s' % (', '.join(target_map.keys())))
        exit(0)
    target = target_map[sys.argv[1]]
    urls = [line[0:line.find('\t')] for line in open('./user_followees.data')]
    finished_urls = [line[0:line.find('\t')] for line in open(target[0])]
    urls = list(set(urls) - set(finished_urls))
    random.shuffle(urls)
    print('%d left.' % len(urls))
    q = RedisQueue(target[1])
    for url in urls:
        q.put(url)

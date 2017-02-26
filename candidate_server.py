import random
from RedisQueue import RedisQueue


def get_candidates_urls():
    seed_urls = set([line.strip() for line in open('./seeds.data')])
    finished_urls = set()
    all_urls = set()
    for line in open('user_followees.data'):
        line = line.strip().split('\t')
        finished_urls.add(line[0])
        all_urls.update(set(line[1:]))
    candidates_urls = list(all_urls - finished_urls)
    random.shuffle(candidates_urls)
    candidates_urls = list(seed_urls - finished_urls) + candidates_urls
    return candidates_urls


if __name__ == '__main__':
    candidates_urls = get_candidates_urls()
    print('%d candidates urls' % len(candidates_urls))
    #q = RedisQueue('user_followees_queue')
    #for url in candidates_urls:
    #    q.put(url)

from RedisQueue import RedisQueue
import sys
import random
from pymongo import MongoClient

if __name__ == '__main__':
    db = MongoClient()
    exists = db.zhihu.zhihu_questions
    exist_owners = []
    for e in exists.find():
        exist_owners.append(e['owner'])
    all_ids = [line.strip().split('\t')[0] for line in open('./user_followees.data')]
    candidates = list(set(all_ids) - set(exist_owners))
    queue = RedisQueue('question_queue')
    queue.clear()
    print('Count: %d' % len(candidates))
    for c in candidates[0:]:
        queue.put(c)

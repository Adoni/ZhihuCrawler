from pymongo import MongoClient
from pyltp import Segmentor


def insert_questions_from_answered_question():
    in_db = MongoClient().zhihu.user_answered_questions
    out_db = MongoClient().zhihu_network.questions
    existed_question_id = set(map(lambda q: q['_id'], out_db.find()))
    segmentor = Segmentor()
    segmentor.load("/Users/sunxiaofei/workspace/ltp_data/cws.model")
    for u in in_db.find():
        for a in u['answers']:
            if a['q_id'] in existed_question_id:
                continue
            existed_question_id.add(a['q_id'])
            if len(existed_question_id) % 1000 == 0:
                print(len(existed_question_id))
            words = segmentor.segment(a['title'].strip().replace(
                '\n', ' ').replace('\r', ' ').replace('\b', ' '))
            if len(words) < 3:
                continue
            out_db.insert({'_id': a['q_id'], 'title': ' '.join(words)})


def insert_questions_from_followed_question():
    in_db = MongoClient().zhihu.user_followed_questions
    out_db = MongoClient().zhihu_network.questions
    existed_question_id = set(map(lambda q: q['_id'], out_db.find()))
    segmentor = Segmentor()
    segmentor.load("/Users/sunxiaofei/workspace/ltp_data/cws.model")
    for u in in_db.find():
        for q in u['questions']:
            if q['id'] in existed_question_id:
                continue
            existed_question_id.add(q['id'])
            words = segmentor.segment(q['title'].strip().replace(
                '\n', ' ').replace('\r', ' ').replace('\b', ' '))
            if len(words) < 3:
                continue
            out_db.insert({'_id': q['id'], 'title': ' '.join(words)})


def insert_questions_from_asked_question():
    in_db = MongoClient().zhihu.user_asked_questions
    out_db = MongoClient().zhihu_network.questions
    existed_question_id = set(map(lambda q: q['_id'], out_db.find()))
    segmentor = Segmentor()
    segmentor.load("/Users/sunxiaofei/workspace/ltp_data/cws.model")
    for u in in_db.find():
        for q in u['questions']:
            if q['id'] in existed_question_id:
                continue
            existed_question_id.add(q['id'])
            if len(existed_question_id) % 1000 == 0:
                print(len(existed_question_id))
            words = segmentor.segment(q['title'].strip().replace(
                '\n', ' ').replace('\r', ' ').replace('\b', ' '))
            if len(words) < 3:
                continue
            out_db.insert({'_id': q['id'], 'title': ' '.join(words)})


def insert_questions_from_collected_question():
    in_db = MongoClient().zhihu.user_collected_questions
    out_db = MongoClient().zhihu_network.questions
    existed_question_id = set(map(lambda q: q['_id'], out_db.find()))
    segmentor = Segmentor()
    segmentor.load("/Users/sunxiaofei/workspace/ltp_data/cws.model")
    for u in in_db.find():
        for c_name, c_questions in u['collections'].items():
            for a in c_questions:
                if a['q_id'] == -1:
                    continue
                if a['q_id'] in existed_question_id:
                    continue
                existed_question_id.add(a['q_id'])
                if len(existed_question_id) % 1000 == 0:
                    print(len(existed_question_id))
                words = segmentor.segment(a['title'].strip().replace(
                    '\n', ' ').replace('\r', ' ').replace('\b', ' '))
                if len(words) < 3:
                    continue
                out_db.insert({'_id': a['q_id'], 'title': ' '.join(words)})


def delete_noise_question():
    db = MongoClient().zhihu_network.questions
    id_to_delete = []
    for q in db.find():
        if len(q['title'].split(' ')) < 3:
            id_to_delete.append(q['_id'])
    print(len(id_to_delete))
    for _id in id_to_delete:
        db.delete_one({'_id': _id})


def remove_enger_inline():
    db = MongoClient().zhihu_network.questions
    for q in db.find():
        if '\n' in q['title'] or '\r' in q['title'] or '\b' in q['title']:
            q['title'] = q['title'].replace('\n', ' ')
            q['title'] = q['title'].replace('\r', ' ')
            q['title'] = q['title'].replace('\b', ' ')
            db.update_one({'_id': q['_id']},
                          {'$set': {'title': q['title']}},
                          upsert=True)


def insert_user_list():
    keys = ['_id', 'name', 'is_zero_user', 'gender', 'location', 'business',
            'education', 'motto', 'answer_num', 'collection_num',
            'followed_column_num', 'followed_topic_num', 'followee_num',
            'follower_num', 'post_num', 'question_num', 'thank_num',
            'upvote_num', 'photo_url', 'weibo_url']
    out_db = MongoClient().zhihu_network.users
    existed_user_id = set(map(lambda u: u['_id'], out_db.find()))
    for line in open('./user_info.data'):
        line = line.strip().split('\t')
        try:
            assert (len(keys) == len(line))
        except:
            continue
        user = dict(zip(keys, line))
        if user['_id'] in existed_user_id:
            continue
        existed_user_id.add(user['_id'])
        for key in user:
            if key.endswith('_num'):
                user[key] = int(user[key])
        out_db.insert(user)


def insert_user_follow_user_list():
    out_db = MongoClient().zhihu_network.user_follow_user_adjacency_list
    existed_user_id = set(map(lambda u: u['_id'], out_db.find()))
    for line in open('./user_followees.data'):
        line = line.strip().split('\t')
        user = dict()
        user['_id'] = line[0]
        user['neibors'] = line[1:]
        if user['_id'] in existed_user_id:
            continue
        existed_user_id.add(user['_id'])
        out_db.insert(user)


def insert_user_follow_question_list():
    in_db = MongoClient().zhihu.user_followed_questions
    out_db = MongoClient().zhihu_network.user_follow_question_adjacency_list
    existed_user_id = set(map(lambda u: u['_id'], out_db.find()))
    for user in in_db.find():
        if user['_id'] in existed_user_id:
            continue
        existed_user_id.add(user['_id'])
        q_ids = [q['id'] for q in user['questions']]
        out_db.insert({'_id': user['_id'], 'neibors': q_ids})


def insert_user_ask_question_list():
    in_db = MongoClient().zhihu.user_asked_questions
    out_db = MongoClient().zhihu_network.user_ask_question_adjacency_list
    existed_user_id = set(map(lambda u: u['_id'], out_db.find()))
    for user in in_db.find():
        if user['_id'] in existed_user_id:
            continue
        existed_user_id.add(user['_id'])
        q_ids = [q['id'] for q in user['questions']]
        out_db.insert({'_id': user['_id'], 'neibors': q_ids})


def insert_user_collect_question_list():
    in_db = MongoClient().zhihu.user_collected_questions
    out_db = MongoClient().zhihu_network.user_collect_question_adjacency_list
    existed_user_id = set(map(lambda u: u['_id'], out_db.find()))
    for user in in_db.find():
        if user['_id'] in existed_user_id:
            continue
        existed_user_id.add(user['_id'])
        q_ids = []
        for _, c in user['collections'].items():
            q_ids += [q['q_id'] for q in c]
        out_db.insert({'_id': user['_id'], 'neibors': q_ids})


def insert_user_answer_question_list():
    in_db = MongoClient().zhihu.user_answered_questions
    out_db = MongoClient().zhihu_network.user_answer_question_adjacency_list
    existed_user_id = set(map(lambda u: u['_id'], out_db.find()))
    for user in in_db.find():
        if user['_id'] in existed_user_id:
            continue
        existed_user_id.add(user['_id'])
        q_ids = [a['q_id'] for a in user['answers']]
        out_db.insert({'_id': user['_id'], 'neibors': q_ids})


if __name__ == '__main__':
    # insert_questions_from_answered_question()
    # insert_questions_from_followed_question()
    # insert_questions_from_asked_question()
    # insert_questions_from_collected_question()
    #delete_noise_question()
    #remove_enger_inline()
    # insert_user_list()
    insert_user_follow_user_list()
    # insert_user_follow_question_list()
    # insert_user_ask_question_list()
    # insert_user_collect_question_list()
    # insert_user_answer_question_list()

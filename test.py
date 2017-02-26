def insert_user_list():
    keys = ['_id', 'name', 'is_zero_user', 'gender', 'location', 'business',
            'education', 'motto', 'answer_num', 'collection_num',
            'followed_column_num', 'followed_topic_num', 'followee_num',
            'follower_num', 'post_num', 'question_num', 'thank_num',
            'upvote_num', 'photo_url', 'weibo_url']
    out_db = MongoClient().zhihu_network.users
    for line in open('./user_info.data'):
        line = line.strip().split('\t')
        assert (len(keys) == len(line))
        user = dict(zip(keys, line))
        for key in user:
            if key.endswith('_num'):
                user[key] = int(user[key])
        out_db.insert(user)

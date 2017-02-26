from pymongo import MongoClient
import os
import requests
import shutil


def get_user_id_of_existed_photos():
    exist_photoes = os.listdir('./photos')
    user_id_of_existed_photos = [photo_name[:photo_name.find('.')]
                                 for photo_name in exist_photoes]
    return user_id_of_existed_photos


def download_photo(uid, db):
    user = db.find_one({'_id': uid})
    if user is None:
        return
    url = user['photo_url']
    extension = url[url.rfind('.') + 1:]
    try:
        assert (extension in ['jpg', 'png', 'jpeg'])
    except:
        print(uid)
        print(url)
        print(extension)
        raise
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open('./photos/' + uid + '.' + extension, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def main():
    db = MongoClient().zhihu_network.users
    # all_uid = [user['_id'] for user in db.find()]
    all_uid = [
        line[3:].strip()
        for line in open(
            '/Users/sunxiaofei/workspace/zhihu_multi/text_data/83095/nodes_0.data')
    ]
    exist_uid = get_user_id_of_existed_photos()
    print(len(exist_uid))
    print(len(all_uid))
    uid_to_download = list(set(all_uid) - set(exist_uid))
    print(len(uid_to_download))
    for i, uid in enumerate(uid_to_download):
        if (i % 100 == 0):
            print(i)
        try:
            download_photo(uid, db)
        except:
            continue
    print('Done')


if __name__ == '__main__':
    get_user_id_of_existed_photos()
    main()

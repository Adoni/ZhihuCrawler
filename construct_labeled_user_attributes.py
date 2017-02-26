from utils import get_location_labels, get_location_label

locations = get_location_labels()


def construct_labeled_user_attributes():
    fout = open('./zhihu_user_attributes.data', 'w')
    for line in open('./user_info.data'):
        line = line.strip().split('\t')
        if len(line) < 20:
            continue
        user_url = line[0]
        gender = line[3]
        location = get_location_label(line[4])
        profession=line[5]
        fout.write('||'.join([user_url, gender, 'None', location, profession]) + '\n')


def main():
    construct_labeled_user_attributes()
    pass


if __name__ == '__main__':
    main()

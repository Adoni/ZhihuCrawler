from collections import Counter
from utils import get_location_labels, get_location_label


def plot_count_changes(counts):
    from matplotlib import pyplot as plt
    x = range(1, len(counts) + 1)
    plt.plot(x, counts)
    plt.xlabel("中心节点数量")
    plt.ylabel("用户总量")
    plt.show()


locations = get_location_labels()


def user_info(num):
    distribute = []
    for line in open('./user_info.data'):
        line = line.strip().split('\t')
        if len(line) < 20:
            continue
        if num == 5:
            distribute.append(get_location_label(line[num - 1]))
        else:
            distribute.append(line[num - 1])
    print("Count: %d" % len(distribute))
    print("Distribute:")
    distribute = sorted(
        dict(Counter(distribute)).items(),
        key=lambda x: x[1],
        reverse=True)[:200]
    for k, v in distribute:
        print('%s\t%d' % (k, v))


def user_count_change():
    last_count = 0
    f = open('user_count_change.data', 'w')
    counts = []
    uids = set()
    for line in open('./user_followees.data'):
        uids.update(line.strip().split('\t'))
        last_count = len(uids)
        f.write('%d\n' % last_count)
        counts.append(last_count)
    plot_count_changes(counts)


def user_followees():
    pass


def main():
    # user_count_change()
    #user_info(4)
    # user_info(5)
    user_info(6)
 #   user_info(7)

    pass


if __name__ == '__main__':
    main()

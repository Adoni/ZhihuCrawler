from termcolor import cprint


def print_err(text):
    cprint(text, 'red')


def get_location_labels():
    labels = dict()
    with open('./location.label') as f_l:
        for line in f_l:
            line = line.strip().split(' ')
            value = line[0]
            for key in line:
                labels[key] = value
    return labels


locations = get_location_labels()


def get_location_label(location):
    if location == 'unknown':
        return 'None'
    for l in locations:
        if l in location:
            return locations[l]
    return 'None'

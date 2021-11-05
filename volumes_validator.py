import os

import utils as ut


def main():
    volumes = []
    without_volume = []
    for path in ut.paths:
        for file in os.listdir(path):
            v = ut.extract_volume_number(file)
            print(v, file)
            if v:
                volumes.append(v)
            else:
                without_volume.append(file)
    volumes = [
        str(j) for j in list(set([int(i) for i in volumes if i.isnumeric()]))
    ]
    print(volumes)
    print(without_volume)
    print(ut.separate_into_consistent_fragments(volumes))


if __name__ == '__main__':
    main()

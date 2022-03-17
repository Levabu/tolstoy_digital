import os

import utils as ut


def main():
    volumes = []
    without_volume = []
    files_counter = 0
    for path in ut.paths:
    # for path in ut.old_paths:
        for file in os.listdir(path):
            files_counter += 1
            v = ut.extract_volume_number(file)
            # print(v, file)
            if v == '41':
                print(file)
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
    print(files_counter)


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()

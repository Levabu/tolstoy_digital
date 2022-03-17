import os

import utils as ut


def main():
    files = []
    for path in ut.paths:
    # for path in ut.old_paths:
        for file_name in os.listdir(path):
            files.append(file_name)
    # files.sort()
    # with open('temp/old_files.txt', 'w') as file:
    # with open('temp/new_files.txt', 'w') as file:
    #     file.write('\n'.join(files))
    print('\n'.join(files))

    print(len(files))


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
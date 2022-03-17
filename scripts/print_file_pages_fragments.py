import os
import sys

import utils as ut


def main(filename=None, print_filename=True):
    if filename is None:
        try:
            filename = sys.argv[1]
        except IndexError:
            print('Не передан файл.')
            exit()
    try:
        pages, data = ut.get_pages_using_lxml(filename)
    except Exception as e:
        pages, data = ut.get_pages_using_re(filename)
    fragments = ut.separate_into_consistent_fragments(pages)
    if print_filename:
        # print(filename, fragments, sep='|', end='\n')
        # print(filename[2:], fragments, sep='|', end='\n')
        print(filename.split('/')[-1].lstrip('.'), fragments, sep='|', end='\n')


if __name__ == '__main__':
    main()

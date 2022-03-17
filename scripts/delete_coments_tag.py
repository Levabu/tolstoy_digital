import os

from lxml import etree

import print_file_pages_fragments
import split_volumes_utils as sp_ut
import utils as ut


def main():
    correct_filenames = sp_ut.correct_filenames('reference/correct_filenames.csv')
    path = '../../work/tolstoy_digital/new_and_newly_parsed/new_2.0/fiction_mixed/'
    for filename in os.listdir(path):
        if ut.extract_volume_number(filename) == '90':
            # print(filename)
            root = etree.fromstring(ut.read_xml(f'{path}{filename}', 'rb'))
            comments_tag = root.xpath('//ns:comments', namespaces={'ns': ut.xmlns_namespace})
            if comments_tag:
                comments_tag[0].getparent().remove(comments_tag[0])
                if filename in correct_filenames:
                    new_filename = correct_filenames[filename]
                else:
                    new_filename = filename
                with open(f'parse_volume/result/{new_filename}', 'w') as file:
                    file.write(etree.tostring(root, encoding='unicode'))
                print_file_pages_fragments.main(f'parse_volume/result/{new_filename}')
                os.remove(f'{path}{filename}')


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
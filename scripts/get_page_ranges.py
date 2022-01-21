import csv
import os
from pprint import pprint
import re

import utils as ut

PATHS_TO_FILES = [
    '../../work/tolstoy_digital/new_and_newly_parsed/fiction_and_essays_new',
    '../../work/tolstoy_digital/new_and_newly_parsed/letters_and_diaries_new/diaries',
    '../../work/tolstoy_digital/new_and_newly_parsed/letters_and_diaries_new/letters',
    '../../work/tolstoy_digital/new_and_newly_parsed/new',
]


def main():
    volumes = {}
    errors = []
    for path in PATHS_TO_FILES:
        for file in os.listdir(path):
            if file.rsplit('.')[-1] != 'xml':
                continue
            volume = ut.extract_volume_number(file)
            if not volume:
                num = re.search(r'\d+', file)
                if num is not None:
                    volume = num.group()
            if volume == '16':
                print(file)
            if volume not in volumes:
                volumes[volume] = []
            try:
                pages, data = ut.get_pages_using_lxml(os.path.join(path, file))
            except Exception as e:
                pages, data = ut.get_pages_using_re(os.path.join(path, file))
                errors.append([volume, file, e, pages])
                continue
            volumes[volume].extend(pages)

    for volume, pages in volumes.items():
        pages.sort(key=lambda x: int(x) if x.isnumeric() else 0)
        pages = ut.separate_into_consistent_fragments(pages)
        fragments = ut.extract_gaps_from_fragments(pages)
        volumes[volume] = [pages, fragments]
        volumes[volume][0] = '\n'.join([str(t) for t in pages])
        volumes[volume][1] = '\n'.join([str(t) for t in fragments])

    # pprint(volumes)

    with open('reference/volumes_ranges.csv', 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';', escapechar=' ')
        writer.writerows([(vol, frag[0], frag[1]) for vol, frag in volumes.items()])

    # pprint(errors)
    pass
    # ut.separate_into_consistent_fragments(sorted(volumes.keys(), key=lambda x: int(x) if x.isnumeric() else 0))  # volumes range


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
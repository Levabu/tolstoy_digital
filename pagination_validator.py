import csv
import os
import re
from pprint import pprint

import utils as ut


def main() -> None:
    # pattern = re.compile('<pb\s*n="(\d*?)"\s*\/>')
    # pattern = re.compile('<span\s*?class="npnumber">(\d*?)</span>')
    # pattern = re.compile('npnumber">(\d*?)</span>')

    all_counter = 0
    empty_pages = 0
    ok_counter = 0
    error_counter = 0
    all_to_csv = []
    ok_to_csv = []
    empty_to_csv = []
    inconsistent_to_csv = []
    used_tags = []
    for path in ut.paths:
        for file in os.listdir(path):
            all_counter += 1
            volume = ut.extract_volume_number(file)
            status = 'consistent'
            # xml = ut.read_xml(os.path.join(path, file), 'r')
            # pages = re.findall(pattern, xml.read())
            pages, data = ut.get_pages_using_re(os.path.join(path, file))
            # if file in ut.xmls_with_critical_errors:
            #     pages, data = ut.get_pages_using_re(os.path.join(path, file))
            #     # continue
            # else:
            try:
                pages, data = ut.get_pages_using_lxml(os.path.join(path, file))
            except Exception as e:
                pages, data = [], {'error': e}
            # print(file)
            # print(pages)
            if pages:
                should_be = ut.should_be_pages(pages)
                # fragments = ut.separate_into_consistent_fragments(pages)
                # print(file, fragments, extract_gaps_from_fragments(fragments))
                if ut.is_consistent_pagination(file, pages, should_be):
                    ok_counter += 1
                    # ok_to_csv.append((volume, file, separate_into_consistent_fragments(pages)))
                    # print(separate_into_consistent_fragments(pages), file)
                else:
                    error_counter += 1
                    # print(file)
                    fragments = ut.separate_into_consistent_fragments(pages)
                    gaps = ut.extract_gaps_from_fragments(fragments)
                    status = 'inconsistent'
                    # inconsistent_to_csv.append((volume, file, fragments, gaps))
                    # if 'hi_style_op' not in data and 'hi_style_np' not in data and 'pb' not in data:
                    tag_types = data.get('tag_types')
                    if (tag_types is not None and not any(
                            [i in tag_types for i in (
                                    'hi_style_op', 'hi_style_np', 'pb'
                            )
                             ]
                    )):
                        print(file)
                        print(data)
                        print(fragments)
                        print(pages)
                        print(should_be)
                    # print(gaps)

                    # pprint(pages)
                    # print()
                    # print(list(zip(pages, should_be)))
                    # pprint(list(zip(pages, should_be)))
            else:
                empty_pages += 1
                status = 'empty'
                # print(file)
                # empty_to_csv.append([volume, file])
            # all_to_csv.append([volume, file, status])

    print(all_counter, ok_counter, error_counter, empty_pages)
    # print(used_tags)

    # ut.write_to_csv(inconsistent_to_csv, 'inconsistent_pagess')
    # ut.write_to_csv(empty_to_csv, 'empty_pages')
    # ut.write_to_csv(all_to_csv, 'alll_files')
    # ut.write_to_csv(ok_to_csv, 'consistent_pages')
    pass


if __name__ == '__main__':
    main()

import os
from pprint import pprint
import re

import utils as ut


def main():
    # pattern = re.compile('npnumber')
    # pattern = re.compile('<span class="npnumber">441</span>')

    # pattern = re.compile(r'<span\s*?class="npnumber">\s*?(\d*?)\s*?</span>')
    # pattern = re.compile(r'<span\s*?class="opnumber">\s*?(\d*?)\s*?</span>')
    # pattern = re.compile(r'<hi\s*?rend="opnumber">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<hi\s*?style="opnumber">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<hi\s*?style="opnumber.*?">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<hi\s*?style="npnumber.*?">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<pb\s*n="(\d*?)"\s*\/>')

    equal = 0
    found = 0
    types_combinations = {}
    for path in ut.paths:
        for file in os.listdir(path):
            # print(file)
            if file in ut.xmls_with_critical_errors:
                continue
            pages, data = ut.get_pages_using_lxml(os.path.join(path, file))
            types = data.get('tag_types')
            if types is not None:
                types = tuple(types)
                if types not in types_combinations:
                    types_combinations[types] = 1
                    # print(types)
                else:
                    types_combinations[types] += 1
            if not pages:
                print(file)
            # pages1 = ut.get_pages_using_re(os.path.join(path, file))
            # print(pages)
            # if pages == pages1:
            #     equal += 1
            # else:
                # print(file)
            # if pages and data.get('tag_types') == {'hi_style_op', 'hi_style_np'}:
            #     print(pages, file)
            #     found += 1
                pass
    print(found, equal)
    pprint(types_combinations)


if __name__ == '__main__':
    ut.change_to_project_directory()
    # main()

    # pages, data = ut.get_pages_using_re('test_file.xml')
    pages, data = ut.get_pages_using_lxml('test_file.xml')
    # pages, data = ut.get_pages_using_lxml('test_file_1.xml')
    # print(pages, data)
    fragments = ut.separate_into_consistent_fragments(pages)
    print(pages)
    print(fragments)
    print(data)

    # pages, data = ut.get_pages_using_re('test_file.xml')
    # fragments = ut.separate_into_consistent_fragments(pages)
    # print(fragments)
    # print(ut.extract_gaps_from_fragments(fragments))
    # print(ut.get_pages_using_re('test_file.xml'))
    pass
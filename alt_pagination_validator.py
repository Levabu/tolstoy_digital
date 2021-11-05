import os
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
    for path in ut.paths:
        for file in os.listdir(path):
            # print(file)
            if file in ut.xmls_with_critical_errors:
                continue
            pages = ut.get_pages_using_lxml(os.path.join(path, file))
            # pages1 = ut.get_pages_using_re(os.path.join(path, file))
            print(pages)
            # if pages == pages1:
            #     equal += 1
            # else:
                # print(file)
            if pages:
                # print(pages, file)
                found += 1
                pass
    print(found, equal)


if __name__ == '__main__':
    # main()

    pages = ut.get_pages_using_lxml('test_file.xml')
    fragments = ut.separate_into_consistent_fragments(pages)
    print(fragments)
    print(ut.extract_gaps_from_fragments(fragments))
    # print(ut.get_pages_using_re('test_file.xml'))
    pass
import csv
import os
import re

from lxml import etree

old_paths = [
    '../../work/tolstoy_digital/TEI-master/fiction_and_essays',
    '../../work/tolstoy_digital/TEI-master/letters_and_diaries/letters/letters_with_norm_person',
    '../../work/tolstoy_digital/TEI-master/letters_and_diaries/letters/letters_with_NOTnorm_person',
    '../../work/tolstoy_digital/TEI-master/letters_and_diaries/diaries',
]

paths = [
    '../../work/tolstoy_digital/untouched_TEI-master/fiction_and_essays_new',
    '../../work/tolstoy_digital/untouched_TEI-master/letters_and_diaries_new/diaries',
    '../../work/tolstoy_digital/untouched_TEI-master/letters_and_diaries_new/letters',
]

patterns = {
    '<span class="number">num</span>': re.compile(r'<span\s*?class="npnumber">\s*?(\d*?)\s*?</span>'),
    '<span class="opnumber">num</span>': re.compile(r'<span\s*?class="opnumber">\s*?(\d*?)\s*?</span>'),
    '<hi rend="opnumber">num</hi>': re.compile(r'<hi\s*?rend="opnumber">\s*?(\d*?)\s*?</hi>'),
    '<hi style="opnumber">num</hi>': re.compile(r'<hi\s*?style="opnumber">\s*?(\d*?)\s*?</hi>'),
    '<hi style="opnumber something">num</hi>': re.compile(r'<hi\s*?style="opnumber.*?">\s*?(\d*?)\s*?</hi>'),
    '<hi style="npnumber something">num</hi>': re.compile(r'<hi\s*?style="npnumber.*?">\s*?(\d*?)\s*?</hi>'),
    '<pb n="num"/>': re.compile(r'<pb\s*n="(\d*?)"\s*/>')
}

pattern = (r'(<(span|hi)\s*?(class|style|rend)=\"(n|o)pnumber\">'
           r'\s*?(\d*?)\s*?</(span|hi)>)|(<pb\s*n=\"(\d*?)\"\s*/>)')

xmls_with_critical_errors = [
    '[«Вторая половина» «Юности»] 2.xml',
    '[«Вторая половина» «Юности». Глава 2. Троицын день] 2.xml',
    'Carthago delenda est. Черновое 39.xml',
    'В чем моя вера. 23.xml',
    'Как и зачем жить 36.xml',
    'Так что же нам делать 25.xml',
    'Утро помещика 4.xml',
    'Volume_71_S.L.TolstomuiL.A.Sulerzhickomu_323.xml'
]

xmlns_namespace = 'http://www.tei-c.org/ns/1.0'


real_tags = {
    'pb': '<pb n="1"></pb>',
    'span_class_op': '<span class="opnumber">1</span>',
    'span_class_np': '<span class="npnumber">1</span>',
    'hi_rend_op': '<hi rend="opnumber">1</hi>',
    'hi_rend_np': '<hi rend="npnumber">1</hi>',
    'hi_style_op': '<hi style="opnumber">1</hi>',
    'hi_style_np': '<hi style="npnumber">1</hi>',
}


def change_to_project_directory():
    abspath = os.path.abspath(__file__)
    dir_name = os.path.dirname(os.path.dirname(abspath))
    os.chdir(dir_name)


def should_be_pages(pages: list) -> list[str]:
    """Для ['3', '4', '10', '11'] будет ['3', '4', '5', '6']."""
    if not pages[0].isnumeric():
        return []
    first_page = int(pages[0])
    return [str(i) for i in range(first_page, first_page + len(pages))]


def is_consistent_pagination(file_name, pages, should_be=None):
    if should_be is None:
        should_be = should_be_pages(pages)
    return pages == should_be


def separate_into_consistent_fragments1(pages: list) -> list[tuple]:
    """Вида: [(1, 12), (14, 102), (206, 300)]."""
    if not pages:
        return []
    pages = [int(p) if p.isnumeric() else p for p in pages]
    start_ok_page = end_ok_page = pages.pop(0)
    fragments = []
    if not pages:
        return [(start_ok_page,)]
    while pages:
        page_num = pages.pop(0)
        if page_num - end_ok_page == 1:
            end_ok_page = page_num
            continue
        else:
            if start_ok_page == end_ok_page:
                fragments.append((start_ok_page,))
            else:
                fragments.append((start_ok_page, end_ok_page))
            start_ok_page = end_ok_page = page_num
    else:
        if start_ok_page == page_num:
            fragments.append((start_ok_page,))
        else:
            fragments.append((start_ok_page, page_num))
    return fragments


def separate_into_consistent_fragments(pages: list) -> list[tuple]:
    """Вида: [(1, 12), (14, 102), (107, 107), ('XIX',), (206, 300)]."""
    if not pages:
        return []
    pages = [int(p) if p.isnumeric() else p for p in pages]
    fragments = []
    if len(pages) == 1:
        return [(pages[0], pages[0])]
    prev_was_str = False
    start_ok_page = end_ok_page = None
    for i in range(len(pages)):
        if i == 0:
            if isinstance(pages[0], str):
                fragments.append((pages[0],))
                prev_was_str = True
            else:
                start_ok_page = end_ok_page = pages[0]
            continue
        if prev_was_str:
            start_ok_page = end_ok_page = pages[i]
        if isinstance(pages[i], str):
            prev_was_str = True
            if (start_ok_page and end_ok_page) is not None:
                fragments.append((start_ok_page, end_ok_page))
            fragments.append((pages[i],))
            continue
        if pages[i] - end_ok_page == 1:
            end_ok_page = pages[i]
            prev_was_str = False
            continue
        elif pages[i] == end_ok_page:
            if not prev_was_str:
                fragments.append((start_ok_page, end_ok_page))
        else:
            fragments.append((start_ok_page, end_ok_page))
        start_ok_page = end_ok_page = pages[i]
        prev_was_str = False
    else:
        if not isinstance(pages[-1], str):
            fragments.append((start_ok_page, end_ok_page))
    return fragments


def extract_gaps_from_fragments(fragments: list[tuple]) -> list[int]:
    """[(1, 10), ('abc',), (13, 100), (102, 110)] -> [?, ?, 2]"""
    gaps = []
    for i in range(len(fragments) - 1):
        left_edge = fragments[i][0] if len(fragments[i]) == 1 else fragments[i][1]
        right_edge = fragments[i + 1][0]
        if isinstance(left_edge, str) or isinstance(right_edge, str):
            gaps.append('?')
        else:
            gaps.append(right_edge - left_edge)
    return gaps


def write_to_csv(items, file_name) -> None:
    with open(f'reference/{file_name}.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(items)
        # for item in items:
        #     writer.writerow(item)


def extract_volume_number(file_name: str) -> str:
    file_name = file_name.rstrip('.xml').casefold()
    volume = file_name[-2:].strip()
    if 'volume' in file_name:
        volume = file_name.split('_')[1]
    if file_name.count('_') == 1 and all([i.isnumeric for i in file_name.split('_')]):
        volume = file_name[:2]
    if not volume.isnumeric():
        return ''
    return volume


def read_xml(xml, mode='r'):
    with open(xml, mode) as file:
        return file.read()


def get_pages_using_re_0(xml):
    """redundant. or not?"""
    file = read_xml(xml, 'r')
    pages = []
    for tag, pattern in patterns.items():
        ps = [p for p in re.findall(pattern, file)]
        if ps:
            pages.extend(ps)
    return pages, {}


def get_pages_using_re(xml):
    """redundant. or not?"""
    file = read_xml(xml, 'r')
    result = re.findall(pattern, file)
    pages = []
    for match in result:
        if not match[0]:
            pages.append(match[7])
        else:
            pages.append(match[4])
    return pages, {}


def get_pages_using_lxml(xml):
    file = read_xml(xml, 'rb')
    root = etree.fromstring(file)
    text_tag = root.xpath('//ns:text', namespaces={'ns': f'{xmlns_namespace}'})
    # print(xml)
    if text_tag:
        text_tag = text_tag[0]
    else:
        # print('no_text', xml)
        return [], {}
    inside_text_tag = [child for child in text_tag.iterdescendants()]
    tags = root.xpath(
        f'//ns:pb[@n]'
        '| //ns:span[contains(@class, "npnumber")]'
        '| //ns:span[contains(@class, "opnumber")]'
        '| //ns:hi[contains(@rend, "opnumber")]'
        '| //ns:hi[contains(@rend, "npnumber")]'
        '| //ns:hi[contains(@style, "opnumber")]'
        '| //ns:hi[contains(@style, "npnumber")]',
        namespaces={'ns': f'{xmlns_namespace}'}
    )
    tags = [
        tag for tag in tags
        if (not tag.getparent().tag == f'{{{xmlns_namespace}}}note'
            and tag in inside_text_tag)
    ]  # Не считать страницы в комментариях,
    # если они дублируются в основном тексте в теге note
    if not tags:
        return [], {}
    tag_types = {
        'pb': '//ns:pb[@n]',
        'span_class_op': '//ns:span[contains(@class, "opnumber")]',
        'span_class_np': '//ns:span[contains(@class, "npnumber")]',
        'hi_rend_op': '//ns:hi[contains(@rend, "opnumber")]',
        'hi_rend_np': '//ns:hi[contains(@rend, "npnumber")]',
        'hi_style_op': '//ns:hi[contains(@style, "opnumber")]',
        'hi_style_np': '//ns:hi[contains(@style, "npnumber")]',
    }
    pages = []
    # types_counter = 0
    types = set()
    data = {}
    for tag_type in tag_types:
        found = root.xpath(
            tag_types[tag_type], namespaces={'ns': f'{xmlns_namespace}'}
        )
        if found:
            # print(tag_type)
            # types_counter += 1
            types.add(tag_type)
    data.update({'tag_types': types})
    # print(types_counter, xml)

    tag_pairs = {
        ('hi_style_op', 'hi_style_np'): 'style',
        ('hi_rend_op', 'hi_rend_np'): 'rend',
        ('span_class_op', 'span_class_np'): 'class'
    }
    # print(tags)
    for tag in tags:
        page = tag.attrib.get('n') if 'n' in tag.attrib else ''
        if page:
            pages.append(page.strip())
            continue
        elif 'pb' in types and len(types) > 1:
            continue
        page = tag.text.strip()
        pages.append(page)
    if 'pb' in types:
        if pages[0].isnumeric():
            page = int(pages[0])
            pages.insert(0, str(page - 1))
            return pages, data

    for tag_pair, attr in tag_pairs.items():
        if types == {tag_pair[1]}:
            if pages[0].isnumeric():
                page = int(pages[0])
                pages.insert(0, str(page - 1))
                return pages, data
        if types == {tag_pair[0]}:
            if pages[-1].isnumeric():
                page = int(pages[-1])
                pages.append(str(page + 1))
        if types == set(tag_pair):
            pages = []
            for i in range(len(tags)):
                if tags[i].attrib.get(attr) == 'opnumber':
                    page = tags[i].text.strip()
                    pages.append(page)
        if tag_pair[1] in types:
            if tags[-1].attrib.get(attr) == 'npnumber':
                p = tags[-1].getparent()
                page = tags[-1].text.strip()
                text_items = [k for k in p.itertext()]
                if (any(text_items)
                        and not text_items[-1] == page
                        and text_items[-1].strip()
                ):
                    pages.append(page)
    return pages, data


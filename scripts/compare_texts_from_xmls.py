from pprint import pprint
import re

from lxml import etree

import utils as ut
import split_volumes_utils as sp_ut


def find_xml_text_tag(root):
    text_tag = root.xpath('//ns:text', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if not text_tag:
        text_tag = root.xpath('//text')
    if text_tag:
        text_tag = text_tag[-1]
    else:
        print('no_text')
        exit()
        # return [], {}
    # inside_text_tag = [child for child in text_tag.iterdescendants()]
    return text_tag


def extract_text_from_xml_text_tag(text_tag) -> str:
    # inside_text_tag = [child for child in text_tag.iterdescendants()]
    #
    # # text = ''.join([t for item in inside_text_tag for t in item.itertext()])
    # # text = [item.itertext for item in inside_text_tag]
    # texts = []
    # for item in inside_text_tag:
    #     # print(item)
    #     text = ''.join([t.strip(' \n') for t in item.itertext() if item is not None])
    #     texts.append(text)
    #     print('item', text)
    # text = ''.join(texts)
    # # text = sp_ut.minimize_text(text)
    text = etree.tostring(text_tag, encoding='unicode')
    return text
    pass


def get_xml_roots(source_1, source_2, from_file=True):
    text_1 = ut.read_xml(source_1, 'rb') if from_file else source_1
    text_2 = ut.read_xml(source_2, 'rb') if from_file else source_2
    root_1 = etree.fromstring(text_1)
    root_2 = etree.fromstring(text_2)
    return root_1, root_2


def extract_text_from_root(root):
    text_tag = find_xml_text_tag(root)
    return extract_text_from_xml_text_tag(text_tag)


def exclude_non_cyrrilic(text) -> str:
    text = ''.join(re.findall(r'[а-яА-Я\n ]', text))
    text = re.sub(r'( {2,}|\n)', '', text)
    words = re.split(' ', text)
    text = '\n'.join(words)
    # text = re.sub(r'( {2,})|(\n{2,})', '', text)
    return text


def exclude_some_tags(text, ignore_tags: list):
    text = f'<container>{text}</container>'
    root = etree.fromstring(text)

    for tag in ignore_tags:
        tags = root.xpath(f'//ns:{tag}', namespaces={'ns': f'{ut.xmlns_namespace}'})
        if not tags:
            tags = root.xpath(f'//{tag}')
        for element in tags:
            element.getparent().remove(element)

    # notes = root.xpath('//ns:note', namespaces={'ns': f'{ut.xmlns_namespace}'})
    # if not notes:
    #     notes = root.xpath('//note')
    # for note in notes:
    #     note.getparent().remove(note)
    #
    # regs = root.xpath('//ns:reg', namespaces={'ns': f'{ut.xmlns_namespace}'})
    # if not regs:
    #     regs = root.xpath('//reg')
    # for reg in regs:
    #     reg.getparent().remove(reg)

    text = etree.tostring(root, encoding='unicode')[len('<container>'):-len('</container>')]
    # breakpoint()
    return text


def compare_texts(source_1, source_2, ignore_tags=None, only_print_result=True, from_file=True):
    root_1, root_2 = get_xml_roots(source_1, source_2, from_file=from_file)
    text_1 = extract_text_from_root(root_1)
    text_2 = extract_text_from_root(root_2)
    if ignore_tags is not None:
        text_1, text_2 = exclude_some_tags(text_1, ignore_tags), exclude_some_tags(text_2, ignore_tags)

    rus_only_text1 = exclude_non_cyrrilic(text_1)
    rus_only_text2 = exclude_non_cyrrilic(text_2)
    single_line1 = rus_only_text1.replace('\n', '')
    single_line2 = rus_only_text2.replace('\n', '')

    if not only_print_result:
        print('originally: ', len(text_1), len(text_2))
        print('with spaces: ', len(rus_only_text1), len(rus_only_text2))
        print('single lines: ', len(single_line1), len(single_line2))

        print(single_line1 == single_line2)
    else:
        return single_line1 == single_line2

    if not only_print_result:
        with open('parse_volume/compare/result/compare1.txt', 'w') as file:
            file.write(rus_only_text1)
        with open('parse_volume/compare/result/compare2.txt', 'w') as file:
            file.write(rus_only_text2)
        with open('parse_volume/compare/result/compare_single1.txt', 'w') as file:
            file.write('\n'.join(list(single_line1)))
        with open('parse_volume/compare/result/compare_single2.txt', 'w') as file:
            file.write('\n'.join(list(single_line2)))
            file.write('\n'.join(list(single_line2)))

    pass


if __name__ == '__main__':
    ut.change_to_project_directory()
    old_text = 'test_file_1.xml'
    newly_parsed_text = 'test_file_2.xml'
    result = compare_texts(
        old_text,
        newly_parsed_text,
        # ignore_tags=['reg', 'note']
        ignore_tags=['reg', 'sic', 'corr'],
        only_print_result=True
    )

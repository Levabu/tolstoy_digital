import os
import re

from lxml import etree

from compare_texts_from_xmls import compare_texts
import utils as ut


def remove_edge_tag_pair(tag) -> str:
    tag_str = etree.tostring(tag, encoding='unicode')
    start = tag.text or ''
    # result = f'{start}'
    # for child in tag:
    #     result = f'{result}{etree.tostring(child, encoding="unicode")}'
    # return result
    return tag_str[tag_str.find('>') + 1:tag_str.rfind('<')] + (tag.tail or '')


def convert_text_0(text):
    """

    :param text: valid xml string
    :return:
    """
    # s = '''как запрещение <span class="opdelimiter">людям,<pb/> df</span><span class="opnumber">62</span> must<span class="npnumber">63</span><span class="npdelimiter">которые</span> дерутся за свою жизнь
    # е <span class="opdelimiter">hui <em>wferw</em> werf </span><span class="opnumber">62</span> m34r2 <n type="npnumber">23</n>'''
    xml = f'<cont>{text}</cont>'
    root = etree.fromstring(xml)
    for tag in root:
        # print(tag.attrib)
        if 'opdelimiter' in tag.values() or 'npdelimiter' in tag.values():
            parent = tag.getparent()
            text = remove_edge_tag_pair(tag)
            # print(text)
            if parent is not None:
                previous = tag.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + text
                else:
                    parent.text = (parent.text or '') + text
                parent.remove(tag)
        if 'opnumber' in tag.values():
            parent = tag.getparent()
            text = tag.tail
            if parent is not None:
                previous = tag.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + text
                else:
                    parent.text = (parent.text or '') + text
                parent.remove(tag)
        if 'npnumber' in tag.values():
            page_number = tag.text
            if not page_number.isnumeric():
                print('Error: ', page_number, ' ', 'is not numeric!!!')
            [tag.attrib.pop(attr) for attr in tag.attrib]
            # tag.tag = 'pb'
            # tag.set('n', page_number)
            # tag.text = ''
            new_tag = etree.Element('pb')
            new_tag.set('n', page_number)
            tag.addnext(new_tag)
            parent = tag.getparent()
            text = (tag.tail or '')
            if parent is not None:
                previous = tag.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + text
                else:
                    parent.text = (parent.text or '') + text
                parent.remove(tag)

    # root_str = etree.tostring(root, encoding='unicode').replace('&lt;', '<').replace('&gt;', '>')
    root_str = etree.tostring(root, encoding='unicode')
    print(root[0].tail)
    # root_str = re.sub(r'&lt;([a-zA-Z]+)', '<\1', root_str)
    # root_str = re.sub(r'([a-zA-Z]+)&gt;', '\1>', root_str)

    text = root_str[len('<cont>'):-len('</cont>')]
    return text

    # print(tag.text)
    # print(root.text)
    # print(etree.tostring(root, encoding='unicode').replace('&lt;', '<').replace('&gt;', '>'))
    # print(text)
    pass


def convert_text(text):
    patterns = [
        (
            re.compile(r'<span[^>]*?opnumber[^>]*?>\d+</span>'),
            ''
        ),
        (
            re.compile(r'<span[^>]*?npnumber[^>]*?>(\d+)</span>'),
            r'<pb n="\1"/>'
        ),
        (
            re.compile(r'<span[^>]*?(o|n)pdelimiter[^>]*?>(.*?)</span>'),
            r'\2'
        ),
    ]
    for pattern, replacement in patterns:
        text = pattern.sub(replacement, text)
        # print(text)

    return text


def main():
    # print(convert_text('123') == '123')
    path_to_files = '../../work/slovo_tolstogo/new_2.0/fiction_mixed'
    for filename in os.listdir(path_to_files):
        if not len(filename) > 4 and not filename[-4:] == '.xml':
            continue
        with open(f'{path_to_files}/{filename}') as file:
            # print(filename)
            text = file.read()
            print(text)
            if compare_texts(text, convert_text(text), from_file=False):

                print(filename)
    pass


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
    # s = '''как <tu_as_merde/> запрещение <span class="opdelimiter">людям,<pb/> df</span><span class="opnumber">62</span> must<span class="npnumber">63</span><span class="npdelimiter">которые</span> дерутся за свою жизнь
    # е <span class="opdelimiter">hui <em>wferw</em> werf </span><span class="opnumber">62</span> m34r2 <n type="npnumber">23</n>'''
    # print(s)
    # print()
    # print(convert_text(s))
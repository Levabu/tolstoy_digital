from copy import deepcopy
import os
import re

from lxml import etree

import compare_texts_from_xmls
import replace_old_page_tags
import split_volumes_utils as sp_ut
import utils as ut


def remove_xml_declaration(text: str) -> str:
    start = text.find('<TEI')
    if start == -1:
        print('Error: no TEI tag.')
        exit()
    return text[start:]


def replace_lt_and_gt_with_xml_entities(text: str) -> str:
    """Redundant. Automatically only for cyrillic. Has not effect"""
    text = re.sub(r'<([а-яА-Я]+)', r'&lt;\1', text)
    text = re.sub(r'([а-яА-Я]+)>', r'\1&gt;', text)
    return text


def remove_comments_from_xml(text: str) -> str:
    text = re.sub(r'<!--.*?-->', '', text)
    return text


def remove_extra_text_tag(root):
    text_tags = root.xpath('//ns:text', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if len(text_tags) == 2 and text_tags[1].getparent() is text_tags[0]:
        result_text_tag = deepcopy(text_tags[1])
        parent = text_tags[0].getparent()
        parent.remove(text_tags[0])
        parent.append(result_text_tag)
        # return etree.tostring(root, encoding='unicode')
    return root


def remove_comments_tag(root):
    try:
        comments_tag = root.xpath('//ns:comments', namespaces={'ns': f'{ut.xmlns_namespace}'})[0]
    except IndexError:
        try:
            comments_tag = root.xpath('//comments')[0]
        except IndexError:
            return root
    comments_tag.getparent().remove(comments_tag)
    return root


def remove_extra_page_tag(root):
    """Неправильно попадающий тег перехода на следующую страницу в конце текста."""
    page_tags = root.xpath('//ns:pb', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if not page_tags:
        page_tags = root.xpath('//pb')
    paragraphs = root.xpath('//ns:p', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if not paragraphs:
        paragraphs = root.xpath('//p')
    try:
        last_page_tag = page_tags[-1]
        last_paragraph_tag = paragraphs[-1]
    except IndexError:
        return root
    # for tag in page_tags:
    #     parent_text = ''.join([t for t in tag.getparent().itertext()])

    if last_page_tag.getparent() is last_paragraph_tag:
        parent_text = ''.join([t for t in last_paragraph_tag.itertext()])
        if parent_text.strip() == '':
            last_paragraph_tag.getparent().remove(last_paragraph_tag)
        elif last_page_tag.tail is None or last_page_tag.tail.strip() == '':
            last_paragraph_tag.remove(last_page_tag)
    return root


def fix_notes(root):

    # 1) Преобразовать некоторые теги del в нормальные теги сносок note
    del_tags = root.xpath('//ns:del', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if not del_tags:
        del_tags = root.xpath('//del')
    # del без n не использовался для сносок
    del_tags = list(filter(lambda x: 'n' in x.attrib, del_tags))
    for tag in del_tags:
        try:
            paragraph = deepcopy(tag[-1])
            tag.remove(tag[-1])
            # print(paragraph.text)
        except IndexError:
            continue  # No errors so far though
        tag.tag = 'note'
        new_div = etree.Element('div')
        new_div.set('type', 'section')
        new_div.set('id', tag.get('n'))
        tag.append(new_div)
        new_div.append(paragraph)

    # 2) Убрать ненужный тег head (его нет в новоконвертированном del)
    note_tags = root.xpath('//ns:note', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if not note_tags:
        note_tags = root.xpath('//note')
    for tag in note_tags:
        try:
            should_be_head_tag = tag[0][0]
        except IndexError:
            continue
        if should_be_head_tag.tag == 'head':
            should_be_head_tag.getparent().remove(should_be_head_tag)

    # 3) Добавить префикс к новым дивам
    text = etree.tostring(root, encoding='unicode')
    text = add_xml_prefix_in_div_attrib(text)
    root = etree.fromstring(text)
    return root
    pass


def add_xml_prefix_in_div_attrib(text: str) -> str:
    text = re.sub(
        r'<div type="section" id="n(\d+)">',
        r'<div type="section" xml:id="n\1">',
        text
    )
    return text


def indent_root(root):
    text = etree.tostring(root, encoding='unicode', pretty_print=True)
    text = sp_ut.minimize_text(text)
    root = etree.fromstring(text)
    etree.indent(root)
    return root


def universalize_text(source, from_file=True):
    file_changed = False
    file_text = ut.read_xml(source, 'r') if from_file else source
    # 1) Remove <?xml version='1.0' encoding='UTF-8'?>
    new_text = remove_xml_declaration(file_text)
    if file_text != new_text:
        file_text = new_text
        file_changed = True

    # 2) Replace special characters < and > with xml entities
    # new_text = replace_lt_and_gt_with_xml_entities(file_text)
    # print(file_text == new_text)
    # if file_text != new_text:
    #     file_text = new_text
    #     file_changed = True

    # 2) Replace old page tags with <pb>
    new_text = replace_old_page_tags.convert_text(file_text)
    try:
        if not compare_texts_from_xmls.compare_texts(new_text, file_text, from_file=False):
            print('not_equal!!')
    except etree.XMLSyntaxError as e:
        print('XMLSyntaxError: ', e)
    if file_text != new_text:
        # print(file_text, new_text)
        file_text = new_text
        file_changed = True

    # 3) Remove comments like '<!--<hi rend="opnumber">405</hi>-->'
    new_text = remove_comments_from_xml(file_text)
    if file_text != new_text:
        file_text = new_text
        file_changed = True

    root = etree.fromstring(file_text)
    # 4) Remove duplicated text tag
    new_root = remove_extra_text_tag(root)
    if root != new_root:
        root = new_root
        file_changed = True

    # 5) For 90 volume texts
    new_root = remove_comments_tag(root)
    if root != new_root:
        root = new_root
        file_changed = True

    # 6) Remove extra page tag at the end
    new_root = remove_extra_page_tag(root)
    if root != new_root:
        root = new_root
        file_changed = True

    # 7) Fix notes: a) Remove head in note; b) add div to del with n attr; c) change del with n attr to note
    new_root = fix_notes(root)
    if root != new_root:
        root = new_root
        file_changed = True

    # etree.indent(root)
    # root = indent_root(root)
    return etree.tostring(root, encoding='unicode'), file_changed


def main():
    # path_to_files = '../../work/slovo_tolstogo/new_2.0/fiction_mixed'
    path_to_files = '../../work/slovo_tolstogo/new_2.0/fiction_mixed_inserted_pages_manually_and_from_tim'
    result_path = '../../work/slovo_tolstogo/new_2.0/result'
    for filename in os.listdir(path_to_files):
        if not len(filename) > 4 or not filename[-4:] == '.xml':
            continue
        print(filename)
        text, file_changed = universalize_text(f'{path_to_files}/{filename}', from_file=True)
        # print(text)
        if file_changed:
            with open(f'{result_path}/{filename}', 'w') as file:
                file.write(text)



        # print(file == file_text.encode())
        # print(text)
        # print(file_text[0:file_text.find('\n')+1])


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
    # path_test_file = 'test_file_1.xml'
    # root = etree.fromstring(ut.read_xml(path_test_file, 'rb'))
    # root = remove_extra_text_tag(root)
    # root = remove_extra_page_tag(root)
    # root = fix_notes(root)
    # root = remove_comments_tag(root)
    # etree.indent(root)
    # print(add_xml_prefix_in_div_attrib(etree.tostring(root, encoding='unicode')))
    # with open('test_file_2.xml', 'w') as file:
    #     file.write(etree.tostring(root, encoding='unicode'))
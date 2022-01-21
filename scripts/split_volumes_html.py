import itertools
import os
from pprint import pprint

from lxml import etree
from tqdm import tqdm

import utils as ut
import split_volumes_utils as sp_ut


def split_fiction_0(filename):
    """Old version, works for 38 vol. Parses all divs with id length = 10."""
    html = ut.read_xml(
        filename, 'rb'
    )
    root = etree.fromstring(html)
    volume_number = filename.strip('.html').split()[-1]
    tei_data = {
        'volume': volume_number,
    }

    divs = root.xpath('//ns:div', namespaces={'ns': sp_ut.XHTML_NAMESPACE})
    divs_with_titles = filter(
        lambda x: len(x.attrib['id']) == 10 if 'id' in x.attrib else False,
        divs
    )  # like "h000013026"
    texts = []
    div_with_comments_id = sp_ut.get_div_id_where_comments_start(divs)
    for div in divs_with_titles:
        title = ''.join([t for t in div[0].itertext()]).rstrip('.')
        # title = sp_ut.capitalize_title(title)
        div_id = div.attrib['id']
        if div_id.startswith(div_with_comments_id):
            break
        print(title)
        text_divs = [d for d in divs if 'id' in d.attrib and d.attrib['id'].startswith(div_id)]
        texts.append((title, div_id, text_divs))
        # print(title, id)
    # pprint(texts)
    notes = sp_ut.get_notes_from_html(divs)
    for i in tqdm(range(len(texts))):
        tei_data.update(
            {
                'title': texts[i][0],
                'text': sp_ut.convert_text_divs_to_xml_text(*texts[i], notes)
            }
        )
        to_file = sp_ut.fill_tei_template(tei_data, 'tei_with_short_header.xml')
        with open(f'parse_volume/result/{tei_data["title"]} {tei_data["volume"]}.xml', 'w') as file:
            file.write(to_file)
        xml = ut.read_xml(
            f'parse_volume/result/{tei_data["title"]} {tei_data["volume"]}.xml',
            'rb'
        )
        print(tei_data["title"])

        to_file = sp_ut.indent_xml_string(xml)
        with open(f'parse_volume/result/{tei_data["title"]} {tei_data["volume"]}.xml', 'w') as file:
            file.write(to_file)

        tei_data = {'volume': volume_number}
    for i in texts[0][2]:
        # print([t for t in i.itertext()])
        # print(tree.tostring(i))
        pass
        # print(etree.tostring(i, pretty_print=True, encoding='unicode'))


def split_fiction(filename, item_id_length, edges_div_ids=None, extra_funcs=None,
                  only_divs_with_id=True, split_on_id_length=True):
    """
    Parse html divs, split and convert them into tei xml.

    1) Take divs that are inside ranges specified in edges_div_ids.
    Every range outputs a divs block with divs of the same id length
    as the start value's (and their children).
    If edges_div_ids is None, make one block with all divs
    with specified item_id_length.
    (Otherwise item_id_length is not needed.)
    2) Iterate over blocks and split divs into separate files.
    Every file starts with a div of given id length and continues
    with all its children divs. (Children's ids will be longer.)

    :param filename: path to html file
    :param item_id_length: length of div 'id' attribute, e.g. 'h000013026'
    :param edges_div_ids: list of tuples which contain start and end div ids;
    if end value is None, take all after start.
    :param extra_funcs: to perform on and alter text string
    """
    html = ut.read_xml(
        filename, 'rb'
    )
    root = etree.fromstring(html)
    volume_number = filename.strip('.html').split()[-1]
    tei_data = {
        'volume': volume_number,
    }

    all_divs = root.xpath('//ns:div', namespaces={'ns': sp_ut.XHTML_NAMESPACE})

    if edges_div_ids is None:
        divs_blocks = [(all_divs, item_id_length)]
    else:
        divs_blocks = sp_ut.split_divs_into_blocks_based_on_block_edges(
            all_divs, edges_div_ids
        )

    # [print(etree.tostring(d, encoding='unicode')) for d in divs]
    # pprint(divs_blocks)
    # pprint([etree.tostring(d, encoding='unicode') for divs in divs_blocks for d in divs[0]])
    # pprint([d.attrib['id'] for divs in divs_blocks for d in divs[0] if 'id' in d.attrib])

    notes = sp_ut.get_notes_from_html(all_divs)  # все сноски
    # pprint(divs_blocks)
    for divs, item_id_length in divs_blocks:
        divs_with_titles = list(filter(
            lambda x: len(x.attrib['id']) == item_id_length if 'id' in x.attrib else False,
            divs
        ))  # e.g. for "h000013026" item_id_length is 10
        if not split_on_id_length:
            divs_with_titles = [divs_with_titles[0]]

        texts = []
        div_with_comments_id = sp_ut.get_div_id_where_comments_start(divs)
        for div in divs_with_titles:
            div_id = div.attrib['id']
            if (
                    not div_with_comments_id == '' and
                    div_id.startswith(div_with_comments_id)
            ):
                break
            # print(div.attrib['id'])
            try:
                title = ''.join([t for t in div[0].itertext()]).rstrip('.')
                title = sp_ut.prepare_title(title)
            except IndexError:
                title = 'no_title'
            # print(f"'{title}': '{sp_ut.prepare_title(title)}',")

            if only_divs_with_id:
                text_divs = [d for d in divs if 'id' in d.attrib and d.attrib['id'].startswith(div_id)]
            else:
                text_divs = sp_ut.leave_only_parent_divs(divs)
            # breakpoint()
            texts.append((title, div_id, text_divs))  #

        for i in tqdm(range(len(texts))):
            tei_data.update(
                {
                    'title': texts[i][0],
                    'text': sp_ut.convert_text_divs_to_xml_text(
                        *texts[i], notes, extra_funcs
                    )
                }
            )
            # print('text:', texts[i][0])

            to_file = sp_ut.fill_tei_template(tei_data, 'tei_with_short_header.xml')
            # with open(f'parse_volume/result/{tei_data["title"]} {tei_data["volume"]}.xml', 'w') as file:
            with open(f'parse_volume/result/{tei_data["volume"]} {tei_data["title"]}.xml', 'w') as file:
                file.write(to_file)
            # print(tei_data["title"])

            # Открываю и переписываю xml заново, чтобы:
            # 1) базово провалидировать: невалидный вызовет ошибку,
            # 2) сделать indent
            xml = ut.read_xml(
                # f'parse_volume/result/{tei_data["title"]} {tei_data["volume"]}.xml',
                f'parse_volume/result/{tei_data["volume"]} {tei_data["title"]}.xml',
                'rb'
            )
            to_file = sp_ut.indent_xml_string(xml)
            # with open(f'parse_volume/result/{tei_data["title"]} {tei_data["volume"]}.xml', 'w') as file:
            with open(f'parse_volume/result/{tei_data["volume"]} {tei_data["title"]}.xml', 'w') as file:
                file.write(to_file)

            tei_data = {'volume': volume_number}  # обнуление данных


def search_in_xmls():
    """just for debugging"""
    all_filenames = []
    rends = []
    for path in ut.paths:
        for filename in os.listdir(path):
            all_filenames.append(os.path.join(path, filename))
    # for filename in tqdm(all_filenames):
    for filename in all_filenames:
        file = ut.read_xml(filename, 'rb')
        # soup = BS(file, features='lxml')
        try:
            root = etree.fromstring(file)
            # text_tag = root.xpath('//ns:text', namespaces={'ns': f'{ut.xmlns_namespace}'})[0]
            # idno_tag = root.xpath('//ns:idno', namespaces={'ns': f'{ut.xmlns_namespace}'})[0]
            # title_tag = root.xpath('//ns:title[@level="a"]', namespaces={'ns': f'{ut.xmlns_namespace}'})[0]
            # author_tag1 = root.xpath('//ns:titleStmt/ns:author', namespaces={'ns': f'{ut.xmlns_namespace}'})[0]
            # author_tag2 = root.xpath('//ns:analytic/ns:author', namespaces={'ns': f'{ut.xmlns_namespace}'})[0]
            comments = root.xpath('//ns:comments', namespaces={'ns': f'{ut.xmlns_namespace}'})
            edit_corr = root.xpath('//ns:choice', namespaces={'ns': f'{ut.xmlns_namespace}'})
            divs = root.xpath('//ns:span', namespaces={'ns': f'{ut.xmlns_namespace}'})

            if comments:
                # print(filename)
                pass
            for i in edit_corr:
                if 'original_editorial_correction' in i.attrib:
                    # print(etree.tostring(i, encoding='unicode'))
                    pass
            # print(title_tag.text.strip(' \n'))
            # print(author_tag1.text.strip(' \n'), end=' | ')
            # print(author_tag2.text.strip(' \n'))

            # for i in root.iterchildren():
            for i in divs:
                # print(i.attrib)
                if 'rend' in i.attrib:
                    rends.append(i)

        except Exception as e:
            # print(filename, e)
            pass
    rends = set(rends)
    [print(i.attrib) for i in rends]
    # pprint(rends)


if __name__ == '__main__':
    ut.change_to_project_directory()
    # search_in_xmls()
    volume_file_38 = 'parse_volume/htmls/Полное собрание сочинений. Том 38.html'  # 10
    volume_file_41 = 'parse_volume/htmls/Полное собрание сочинений. Том 41.html'
    volume_file_42 = 'parse_volume/htmls/Полное собрание сочинений. Том 42.html'
    volume_file_43 = 'parse_volume/htmls/Полное собрание сочинений. Том 43.html'
    volume_file_44 = 'parse_volume/htmls/Полное собрание сочинений. Том 44.html'
    volume_file_45 = 'parse_volume/htmls/Полное собрание сочинений. Том 45.html'



    # Если есть третий аргумент, то второй не важен
    # split_fiction(volume_file_38, 10, [('h000011001', None)])
    # split_fiction(
    #     volume_file_43,
    #     7,
    #     [('h000010', 'h000011')],
    #     extra_funcs=[sp_ut.insert_date_tag_for_43_and_44_vol]
    # )
    # split_fiction(
    #     volume_file_44,
    #     7,
    #     [('h000009', None)],
    #     extra_funcs=[sp_ut.insert_date_tag_for_43_and_44_vol]
    # )
    # split_fiction(volume_file_45, 7, [('h000010', 'h000011'), ('h000011002', None)])


    # split_fiction(
    #     volume_file_41,
    #     16,
    #     [
    #         ('h000010', 'h000011'),
    #     ],
    #     extra_funcs=[sp_ut.prepare_v_41_for_xml_conversion],
    #     only_divs_with_id=False
    # )
    #
    # split_fiction(
    #     volume_file_42,
    #     16,
    #     [
    #         ('h000006002', 'h000007')
    #     ],
    #     extra_funcs=[sp_ut.prepare_v_42_for_xml_conversion],
    #     only_divs_with_id=False,
    #     split_on_id_length=False
    # )
    # split_fiction(
    #     volume_file_42,
    #     7,
    #     [
    #         ('h000007', 'h000008')
    #     ],
    #     only_divs_with_id=False,
    # )

    # For testing comparison
    volume_file_27 = 'parse_volume/htmls/Полное собрание сочинений. Том 27.html'
    split_fiction(
        volume_file_27,
        10,
        [
            ('h000012003', 'h000012004')
        ]
    )
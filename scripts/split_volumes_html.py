import os
from pprint import pprint

from lxml import etree
from tqdm import tqdm

import utils as ut
import split_volumes_utils as sp_ut

# xhtml_namespace = 'http://www.w3.org/1999/xhtml'


def split_fiction(filename):
    html = ut.read_xml(
        filename, 'rb'
    )
    root = etree.fromstring(html)
    tree = etree.ElementTree(root)
    # [print(e) for e in root.iter()]
    volume_number = filename.strip('.html').split()[-1]
    tei_data = {
        'volume': volume_number,
    }

    divs = root.xpath('//ns:div', namespaces={'ns': sp_ut.XHTML_NAMESPACE})
    divs_with_titles = filter(
        lambda x: len(x.attrib['id']) == 10 if 'id' in x.attrib else False, divs
    )  # like "h000013026"
    texts = []
    div_with_comments_id = sp_ut.get_div_id_where_comments_start(divs)
    for div in divs_with_titles:
        title = div[0].text.strip(' \n')
        id = div.attrib['id']
        if id.startswith(div_with_comments_id):
            break
        text_divs = [d for d in divs if 'id' in d.attrib and d.attrib['id'].startswith(id)]
        texts.append((title, id, text_divs))
        # print(title, id)
    # pprint(texts)
    for i in range(len(texts)):
        tei_data.update(
            {
                'title': texts[i][0],
                'text': sp_ut.convert_text_divs_to_xml(*texts[i])
            }
        )
        to_file = sp_ut.fill_tei_structure(tei_data, 'tei_with_short_header.xml')
        with open(f'parse_volume/result/test_result_{i}.xml', 'w') as file:
            file.write(to_file)
            # file.write(''.join(
            #     [etree.tostring(t, pretty_print=True, encoding='unicode') for t in texts[i][2]])
            # )
        tei_data = {'volume': volume_number}
    for i in texts[0][2]:
        # print([t for t in i.itertext()])
        # print(tree.tostring(i))
        pass
        # print(etree.tostring(i, pretty_print=True, encoding='unicode'))


def search_in_xmls():
    all_filenames = []
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

            if comments:
                print(filename)
            # print(title_tag.text.strip(' \n'))
            # print(author_tag1.text.strip(' \n'), end=' | ')
            # print(author_tag2.text.strip(' \n'))
        except Exception as e:
            # print(filename, e)
            pass


if __name__ == '__main__':
    ut.change_to_project_directory()
    # search_in_xmls()
    volume_file = 'parse_volume/htmls/Полное собрание сочинений. Том 38.html'
    split_fiction(volume_file)
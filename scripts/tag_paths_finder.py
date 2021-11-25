import os
from pprint import pprint
import csv
import time

from lxml import etree


def read_xml(file, mode):
    with open(file, mode) as file:
        return file.read()


def parse_child(child):
    print(child.tag, child.text, [c.tag for c in child], len(child))


# def is_blank_text(text):
#     return text.count(' ') + text.count('\n') == len(text)


def parse_tei_header(root, xmlns_namespace, columns, file_name):
    tree = etree.ElementTree(root)
    all_elements = [el for el in root.iterdescendants()]
    fields = []
    for e in all_elements:
        # print(e)
        text = e.text if e.text is not None and e.text.strip(' \n') != '' else ''
        attributes = e.attrib
        if text or attributes:
            path = tree.getelementpath(e).replace(f'{{{xmlns_namespace}}}', '')
            result = (path, text, attributes)
            if result[0] not in columns:
                # print(result[0], file_name)
                columns.append(result[0])
            # print(result)
            fields.append(result)
    return fields
    # print(len(fields))


def main():
    xmlns_namespace = 'http://www.tei-c.org/ns/1.0'
    # path = 'TEI-master/letters_and_diaries/letters/letters_with_norm_person'
    paths = [
        'TEI-master/fiction_and_essays',
        'TEI-master/letters_and_diaries/letters/letters_with_norm_person',
        'TEI-master/letters_and_diaries/letters/letters_with_NOTnorm_person',
        'TEI-master/letters_and_diaries/diaries',
    ]
    # paths = [
    #     'untouched_TEI-master/fiction_and_essays',
    #     'untouched_TEI-master/letters_and_diaries/letters/letters_with_norm_person',
    #     'untouched_TEI-master/letters_and_diaries/letters/letters_with_NOTnorm_person',
    #     'untouched_TEI-master/letters_and_diaries/diaries',
    # ]
    columns = []
    for path in paths:
        for file in os.listdir(path):
            # xml_as_bytes = read_xml(os.path.join(path, file), 'rb')
            # print(file)
            # xml_as_bytes = read_xml(f'{path}/{file}', 'rb')

            # try:
            xml_as_bytes = read_xml(os.path.join(path, file), 'rb')
            root = etree.fromstring(xml_as_bytes)
            teiHeader = root.xpath('//ns:teiHeader', namespaces={'ns': f'{xmlns_namespace}'})
            result = parse_tei_header(teiHeader[0], xmlns_namespace, columns, file) if teiHeader else ''
            print(result)

            # except Exception as e:
            #     print(f'{file}\n{e}', end='\n')
            #     print()

    # pprint(columns)
    print(len(columns))
    pass


if __name__ == '__main__':
    time_start = time.time()
    main()

    # xml_as_bytes = read_xml('test_file.xml', 'rb')
    # root = etree.fromstring(xml_as_bytes)

    print(time.time() - time_start)

if __name__ == 'not__main__':
    def whatever():
        xml_as_bytes = read_xml('../test_file.xml', 'rb')
        root = etree.fromstring(xml_as_bytes)
        tree = etree.ElementTree(root)

        # parser = etree.XMLParser(remove_blank_text=True)  # different approach
        # tree = etree.parse('test_file.xml', parser)

        for child in root:
            # print(child.tag, child.text == '\n        ')
            # parse_child(child)
            # print(child.tail.strip() == '')
            # print(child.attrib)
            pass
        # print(root.xpath('string()'), '')
        # print([i.strip() for i in root.xpath('//text()')], '')
        texts = [i for i in root.xpath('//text()') if i.strip() != '']
        attributes = [i for i in root.xpath('//@*')]
        all_elements = [i for i in root.xpath('//*')]
        # print(attributes)
        # texts = [i for i in root.xpath('//text()') if i.strip() == '']
        for t in texts:
            # print(tree.getelementpath(t.getparent()))
            pass
        for e in all_elements[1:]:
            # print(e)
            print(tree.getelementpath(e.getparent()), e.attrib)
            pass

        # print(root.xpath('fileDesc/sourceDesc/biblStruct/monogr/imprint/publisher')[0].text)
        # print(root.xpath('fileDesc/publicationStmt/date')[0].text)

import os
import shutil
from pprint import pprint

from lxml import etree

from scripts import utils as ut


def copy_from_list():
    with open('../temp/incons_files.txt') as file:
        files = [f.strip()for f in file.readlines()]

    for path in ut.paths:
        for file in os.listdir(os.path.join('..', path)):
            if file in files:
                shutil.copy2(f'../{path}/{file}', '../temp/files')


def main(file, letter=False):
    as_bytes = ut.read_xml(f'./files/{file}', 'rb')
    root = etree.fromstring(as_bytes)
    divs = root.xpath('//ns:div', namespaces={'ns': f'{ut.xmlns_namespace}'})
    if not letter:
        ids = [div.attrib.values()[1] for div in divs if 'section' in div.attrib.values()]
        ids = [id for id in ids if id.startswith('h')]
        ids_sorted = sorted(ids)
    else:
        ids = [div.attrib.values()[1] for div in divs if 'n' in div.attrib.keys()]
        ids_sorted = sorted(ids, key=lambda x: int(x.split('_n')[1]))
    pprint(list(zip(ids_sorted, ids)))
    print(ids_sorted == ids)


if __name__ == '__main__':
    # pb\s.*?n="
    file = '58.xml'
    main(file, letter=True)

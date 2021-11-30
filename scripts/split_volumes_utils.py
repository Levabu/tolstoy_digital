import re
import uuid

from lxml import etree

import utils as ut

XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'


def add_uuid_for_paragraphs(matchobj):
    group = matchobj.group(1)
    return r'<p rend{group} id="{id}">'.format(group=group, id=uuid.uuid4())


HTML_TO_XML_PATTERNS = [
    (re.compile(r'<br\s*/>'), r'<lb/>'),
    (
        re.compile(r'<div\s+xmlns="http://www.w3.org/1999/xhtml"\s+class(=".*?")\s+id'),
        r'<div type\1 xml:id'
    ),
    (
        re.compile(r'<p class(.*?)>'),
        # r'<p rend\1 id="{}">'
        add_uuid_for_paragraphs
    )

]


def div_has_comments_beginning(div):
    for tag in div.iterchildren():
        if tag.tag == f"{{{XHTML_NAMESPACE}}}h1":
            for t in tag.iterchildren():
                if t.text == 'КОММЕНТАРИИ':
                    return True
    return False


def get_div_id_where_comments_start(divs):
    id = ""
    for div in divs:
        if div_has_comments_beginning(div):
            id = div.get('id')
    return id


def replace_html_markup_with_xml(text: str) -> str:
    for pattern, replace in HTML_TO_XML_PATTERNS:
        text = re.sub(pattern, replace, text)
    return text


def convert_text_divs_to_xml(title, id, text_divs):
    divs = [etree.tostring(
        t,
        pretty_print=False,
        encoding='unicode'
    ) for t in text_divs]
    text = ''.join(divs)
    text = replace_html_markup_with_xml(text)
    return text


def fill_tei_structure(tei_data, tei_structure_file) -> str:
    tei_data.update(
        {
            'author': 'Толстой Л.Н.',  # for now
            'date': 'fill date later',  # for now
            'date_not_after': 'fill date_not_after later',  # for now
            'date_not_before': 'fill date_not_before later',  # for now
            'setting_time': 'XIX'  # for now
        }
    )
    tei = ut.read_xml(tei_structure_file).format(**tei_data)
    return tei

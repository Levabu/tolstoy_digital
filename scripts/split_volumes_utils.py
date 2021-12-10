import re
import uuid

from lxml import etree
from prereform2modern import Processor

import utils as ut

XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'


def regex_add_uuid_for_paragraphs(matchobj):
    group = matchobj.group(1)
    already_has_id_pattern = r'\s*?id="\w+"'
    group = re.sub(already_has_id_pattern, '', group)
    return r'<p rend{group} id="{id}">'.format(group=group, id=uuid.uuid4())


HTML_TO_XML_PATTERNS = [
    (re.compile(r'<br\s*/>'), r'<lb/>'),
    (
        re.compile(r'<div\s+xmlns="http://www.w3.org/1999/xhtml"\s+class(=".*?")\s+id'),
        r'<div type\1 xml:id'
    ),
    (
        re.compile(r'<div\s+class(.*?)>'),
        r'<div rend\1>'
    ),
    (
        re.compile(r'<p class(.*?)>'),
        regex_add_uuid_for_paragraphs
    ),
    (
        re.compile(r'<em>(.*?)</\s*?em>'),
        r'<hi rend="italic">\1</hi>'
    ),
    (
        re.compile(r'<span\s+?class="\w*?\s*opdelimiter">(.*?)</span>'),
        r'\1'
    ),
    (
        re.compile(r'<span\s+?class="opnumber">.*?</span>'),
        r''
    ),
    (
        re.compile(r'<span\s+?class="npnumber">(.*?)</span>(\s*)(<a.*?/a?>)?'),
        r'<pb n="\1"/>\2'
    ),
    (
        re.compile(r'<span\s+?class="\w*?\s?npdelimiter">(.*?)</span>'),
        r'\1'
    ),
    (
        re.compile(r'<sup>(.*?)</sup>'),
        r'<hi rend="sup">\1</hi>'
    ),
    (
        re.compile(r'<sub>(.*?)</sub>'),
        r'<hi rend="sub">\1</hi>'
    ),
    (
        re.compile(r'<h\d\s+?class(.*?)>(.*?)</h\d>'),
        r'<head rend\1>\2</head>'
    ),
    (
        re.compile(r'<strong>(.*?)</strong>'),
        r'<hi rend="strong">\1</hi>'
    ),
    (
        re.compile(r'<span\s+class(.*?)>(.*?)</span>'),
        r'<hi rend\1>\2</hi>'
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
    div_id = ''
    for div in divs:
        if div_has_comments_beginning(div):
            div_id = div.get('id')
    return div_id


def get_notes_from_html(divs):
    divs_with_notes = list(
        filter(
            lambda x: x.attrib['id'].startswith('n') if 'id' in x.attrib else False,
            divs
        )
    )
    divs_with_notes = [etree.tostring(
        d, encoding='unicode').strip(' \n') for d in divs_with_notes]
    return divs_with_notes


def markup_choices_for_prereform_spelling(text):
    split_pattern = re.compile(r'(<choice.*?>.*?</choice>)')
    tokens = split_pattern.split(text)
    print(tokens)
    for i, token in enumerate(tokens):
        if split_pattern.search(token) is not None:
            corr_pattern = r'<choice(.*?)<corr>(.*?)</corr></choice>'
            matchobj = re.search(corr_pattern, token)
            to_corr = matchobj.group(2)
            text_res, changes, s_json = Processor.process_text(
                text=to_corr,
                show=True,
                delimiters=['<choice><reg>', '</reg><orig>', '</orig></choice>'],
                check_brackets=False
            )
            tokens[i] = f'<choice{matchobj.group(1)}<corr>{text_res}</corr></choice>'
        else:
            text_res, changes, s_json = Processor.process_text(
                text=token,
                show=True,
                delimiters=['<choice><reg>', '</reg><orig>', '</orig></choice>'],
                check_brackets=False
            )
            tokens[i] = text_res
            print(tokens)
    return ''.join(tokens)


def replace_refs_to_notes_with_notes(text, notes):
    pattern_ref = re.compile(r'<a.*?id="backn(\d+)"\s+type="note">.*?</a>')
    pattern_note_contents = re.compile(r'<p(.*?)>(.*?)</p>')
    note_numbers = re.findall(pattern_ref, text)
    for note_number in note_numbers:
        for note in notes:
            if f'"#backn{note_number}"' in note:
                break
        note_matchobj = re.search(pattern_note_contents, note)
        p_tag_contents = note_matchobj.group(1)
        note_text = note_matchobj.group(2)
        note = f"""
        <note n="n{note_number}">
          <div type="section" xml:id="n{note_number}">
            <head>
              <ref target="#backn{note_number}">
                {note_number}
              </ref> 
            </head>
            <p{p_tag_contents}>
              {note_text}
            </p>
          </div>
        </note>
        """
        text = re.sub(
            f'<a.*?id="backn{note_number}"\s+type="note">.*?</a>', note, text
        )
    return text


def replace_html_markup_with_xml(text: str) -> str:
    for pattern, substitute in HTML_TO_XML_PATTERNS:
        text = pattern.sub(substitute, text)
    return text


def markup_choices_for_editorial_corrections(text):
    choice_pattern = re.compile(
        r'(<head.*?>[*, ]*)?(\s*(\w*?(\[(.*?)])\w*)\s*)(?!\">)(</head>)?'
    )
    illegible_pattern = re.compile(  # решить, что с этим делать
        r'(\[\d+.*?не\s*разобр.*?])|'  # [2 неразобр.]
        r'(\w+\[\w+\?])|'  # вл[иянием?]
        r'(\[\?])'  # [?]
    )
    crossed_out_pattern = re.compile(
        r'(<.*?>)?(з|З)ач(е|ё)ркнуто:(<.*?>)?'
    )
    choice_result = re.findall(choice_pattern, text)

    for i in choice_result:
        if (
                i[0] or
                illegible_pattern.search(i[2]) is not None or
                crossed_out_pattern.search(i[2]) is not None
        ):  # if inside head
            continue
        sub_1 = re.sub(r'\[|]', r'', i[2])
        sub_2 = re.sub(r'\[', r'\\[', i[2])
        sub_3 = re.sub(r']', r'\\]', sub_2)
        sub_4 = re.sub('\[.*?]', '', i[2])
        choice_attribute = re.search('<.*?>(.*?)<.*?>', i[2])  # [<hi>хвастовство</hi>]
        if choice_attribute is None:
            choice_attribute = i[2]
        else:
            choice_attribute = choice_attribute.group(1)
        replacement = (f'<choice original_editorial_correction="{choice_attribute}">'
                       f'<sic>{sub_4}</sic><corr>{sub_1}</corr></choice>')
        reg_for_repl = f'(?<!="){sub_3}(?!">)'
        text = re.sub(reg_for_repl, replacement, text)
    return text


def convert_text_divs_to_xml_text(title, id, text_divs, notes):
    divs = [etree.tostring(
        t,
        pretty_print=False,
        encoding='unicode'
    ) for t in text_divs]
    text = ''.join(divs)
    text = replace_refs_to_notes_with_notes(text, notes)
    text = replace_html_markup_with_xml(text)
    text = markup_choices_for_editorial_corrections(text)
    text = markup_choices_for_prereform_spelling(text)
    return text


def fill_tei_template(tei_data, tei_structure_file) -> str:
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


def indent_xml_string(xml_bytes_string):
    root = etree.fromstring(xml_bytes_string)
    etree.indent(root)
    return etree.tostring(root, encoding='unicode')

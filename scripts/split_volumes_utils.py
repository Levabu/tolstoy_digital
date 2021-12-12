import itertools
from pprint import pprint
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


dates = {
    'янв': 1,
    'фев': 2,
    'мар': 3,
    'апр': 4,
    'мая': 5,  # genetiv
    'июн': 6,
    'июл': 7,
    'авг': 8,
    'сен': 9,
    'окт': 10,
    'ноя': 11,
    'дек': 12,
}


def capitalize_title(title):
    """Мб не надо, все равно потом названия руками править"""
    if not title == title.upper():
        return title
    roman_pattern = re.compile(r'^([\[(])([XIVLMxivlm]+)([])]?)$')
    title = title.casefold().capitalize()
    tokens = re.split(r'(\s)', title)
    for i, token in enumerate(tokens):
        mathcobj = roman_pattern.search(token)
        if mathcobj is not None:
            tokens[i] = f'{mathcobj.group(1)}{mathcobj.group(2).upper()}{mathcobj.group(3)}'
    return ''.join(tokens)


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
    divs_with_notes = list(
        map(lambda x: re.sub('\n', '', x), divs_with_notes)
    )
    return divs_with_notes


def markup_choices_for_prereform_spelling(text):
    split_pattern = re.compile(r'(<choice.*?>.*?</choice>)')
    tokens = split_pattern.split(text)
    # print(tokens)
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
            # print(tokens)
    return ''.join(tokens)


def replace_refs_to_notes_with_notes(text, notes):
    # pattern_ref = re.compile(r'<a.*?id="backn(\d+)"\s+type="note">.*?</a>')
    # print(text)
    pattern_ref = re.compile(r'<a[^>]*?id="backn(\d+)"\s+type="note">.*?</a>')
    pattern_note_contents = re.compile(r'<p(.*?)>(.*?)</p>')
    note_numbers = re.findall(pattern_ref, text)
    # print(note_numbers)
    # pprint(notes)
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
            # f'<a.*?id="backn{note_number}"\s+type="note">.*?</a>', note, text
            f'<a[^>]*?id="backn{note_number}"\s+type="note">.*?</a>', note, text
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
                i[0] or  # if inside head
                illegible_pattern.search(i[2]) is not None or
                crossed_out_pattern.search(i[2]) is not None
        ):
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


def minimize_text(text):
    """Delete all '\n'."""
    return re.sub('\n', '', text)


def regex_sub_date(matchobj):
    """For vol. 43 and 44."""
    date = matchobj.group(2)
    day = date.split()[0]
    month = date.split()[1][:3].casefold()
    date_tag = f'<date when="-{dates[month]}-{day}"/>'
    return f'{date_tag}\n{matchobj.group(0)}'


def insert_date_tag_for_43_and_44_vol(text):
    date_pattern = re.compile(r'(<h3 class="center">)(\d{1,2} \w+\.)(</h3>)')
    return date_pattern.sub(regex_sub_date, text)


def convert_text_divs_to_xml_text(title, id, text_divs, notes, extra_funcs):
    divs = [etree.tostring(
        t,
        pretty_print=False,
        encoding='unicode'
    ) for t in text_divs]
    text = ''.join(divs)
    text = minimize_text(text)
    if extra_funcs is not None:
        for func in extra_funcs:
            text = func(text)
    text = replace_refs_to_notes_with_notes(text, notes)
    text = replace_html_markup_with_xml(text)
    text = markup_choices_for_editorial_corrections(text)
    text = markup_choices_for_prereform_spelling(text)  # slow, turn off while debugging
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


def split_divs_into_blocks_based_on_block_edges(divs, edges_div_ids):
    divs_blocks = []
    for i, ids in enumerate(edges_div_ids):
        start_id, end_id = ids
        block = list(itertools.dropwhile(
            lambda x: 'id' not in x.attrib or x.attrib['id'] != start_id,
            divs
        ))
        block = list(itertools.takewhile(
            # lambda x: x.attrib['id'] != end_id if 'id' in x.attrib else True,
            lambda x: 'id' not in x.attrib or x.attrib['id'] != end_id,
            block
        ))
        # print(end_id)
        # pprint([d.attrib['id'] for d in block if 'id' in d.attrib])
        divs_blocks.append((block, len(start_id)))
    return divs_blocks

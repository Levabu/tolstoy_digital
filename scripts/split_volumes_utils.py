import re
import uuid

from lxml import etree

import utils as ut

XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'


def regex_add_uuid_for_paragraphs(matchobj):
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
        regex_add_uuid_for_paragraphs
    ),
    (
        re.compile(r'<em>(.*?)</\s*?em>'),
        r'<hi rend="italic">\1</hi>'
    ),
    (
        re.compile(
            r'<span\s+?class="opdelimiter">(.*?)</span>'
            r'<span\s+?class="opnumber">.*?</span>(.*?)'
            r'<span class="npnumber">(\d+?)</span>(.*?)'
            r'<a.*?/><span\s+?class="npdelimiter">(.*?)</span>'
        ),
        r'\1<pb n="\3"/>\4\5'
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


def replace_ref_to_notes_with_notes(text, notes):
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
        text = re.sub(pattern, substitute, text)
    return text


def correction_tag(string_soup):
    # функция принимает в себя строку. И возвращает строку, с теггами choice, corr и sic. Например строка
    # "Я уставился в р[ек]у Нев[у] и бегу в р[ек]у" станет
    # Я уставился в <choice original_editorial_correction='р[ек]у'><sic>ру</sic><corr>реку</corr></choice> <choice original_editorial_correction='Нев[у]'><sic>Нев</sic><corr>Неву</corr></choice> и бегу в <choice original_editorial_correction='р[ек]у'><sic>ру</sic><corr>реку</corr></choice>
    # Я предполагал использование ее на строке, преобразованной из HTML
    choice_pattern = "\s*([А-Яа-я]*?(\[(.*?)\])[А-Яа-я]*)\s*"

    choice_result = re.findall(choice_pattern, string_soup)

    for i in choice_result:
        sub_1 = re.sub(r"\[|\]", r"", i[0])
        sub_2 = re.sub(r"\[", r"\\[", i[0])
        sub_3 = re.sub(r"\]", r"\\]", sub_2)
        sub_4 = re.sub('\[' + i[2] + "\]", r"", i[0])
        replacement = "<choice" + " original_editorial_correction=" + "\'" + i[0] + "\'" + ">" + "<sic>" + sub_4 + "</sic>" + "<corr>" + sub_1 + "</corr>" + "</choice>"
        reg_for_repl = "(?<!\=\')" + sub_3
        string_soup = re.sub(reg_for_repl,replacement, string_soup)
    return string_soup


def convert_text_divs_to_xml(title, id, text_divs, notes):
    divs = [etree.tostring(
        t,
        pretty_print=False,
        encoding='unicode'
    ) for t in text_divs]
    text = ''.join(divs)
    # with open('parse_volume/note_sample.xml', 'w') as file:
    #     file.write(text)
    text = replace_ref_to_notes_with_notes(text, notes)
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

from copy import deepcopy
import csv
import itertools
from pprint import pprint
import re
from typing import Iterable
import uuid

from lxml import etree
from prereform2modern import Processor

import utils as ut

XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

prepared_titles = {
    'ТРИ ДНЯ В ДЕРЕВНЕ': 'Три дня в деревне',
    'БЛАГОДАРНАЯ ПОЧВА': 'Благодарная почва',
    'СМЕРТНАЯ КАЗНЬ И ХРИСТИАНСТВО': 'Смертная казнь и христианство',
    '[НЕТ ХУДА БЕЗ ДОБРА.]': 'Нет худа без добра.',
    '[О ГОГОЛЕ.]': 'О Гоголе',
    '[ПОМЕТКИ ПРИ ПЕРЕЧИТЫВАНИИ «ВЫБРАННЫХ МЕСТ ИЗ ПЕРЕПИСКИ С ДРУЗЬЯМИ».]': 'Пометки при перечитывании «Выбранных мест из переписки с друзьями»',
    '[ПИСЬМО СТУДЕНТУ О ПРАВЕ.]': 'Письмо студенту о праве',
    'О ВОСПИТАНИИ': 'О воспитании',
    '[ПО ПОВОДУ ПРИЕЗДА СЫНА ГЕНРИ ДЖОРДЖА.]': 'По поводу приезда сына Генри Джорджа.',
    'НЕИЗБЕЖНЫЙ ПЕРЕВОРОТ': 'Неизбежный переворот',
    'ЕДИНАЯ ЗАПОВЕДЬ': 'Единая заповедь',
    '[ДОКЛАД, ПРИГОТОВЛЕННЫЙ ДЛЯ КОНГРЕССА МИРА В СТОКГОЛЬМЕ.]': 'Доклад, приготовленный для конгресса мира в Стокгольме',
    '[ЗАЯВЛЕНИЕ ОБ АРЕСТЕ ГУСЕВА.]': 'Заявление об аресте Гусева.',
    'О НАУКЕ': 'О науке',
    '**** ОТВЕТ ПОЛЬСКОЙ ЖЕНЩИНЕ': 'Ответ польской женщине',
    'В ЧЕМ ГЛАВНАЯ ЗАДАЧА УЧИТЕЛЯ?': 'В чем главная задача учителя?',
    'ПОРА ПОНЯТЬ': 'Пора понять',
    'ЕЩЕ О НАУКЕ': 'Еще о науке',
    'СЛАВЯНСКОМУ СЪЕЗДУ В СОФИИ': 'Славянскому съезду в Софии',
    'НѢТЪ ВЪ МІРѢ ВИНОВАТЫХЪ': 'Нет в мире виноватых',
    'ВАРИАНТЫ РАССКАЗА «НЕТ В МИРЕ ВИНОВАТЫХ» [I]': 'Варианты рассказа «Нет в мире виноватых» [I]',
    'Н[ѢТЪ] В[Ъ] М[ІРѢ] В[ИHОВАТЬІХЪ] (II)': 'Нет в мире в (II)',
    '**[ХОДЫНКА.]': 'Ходынка',
    '** [НЕЧАЯННО.]': 'Нечаянно',
    'ОТЪ НЕЙ ВСѢ КАЧЕСТВА': 'От ней все качества',
    'ВАРИАНТЫ КОМЕДИИ «ОТЪ НЕЙ ВСѢ КАЧЕСТВА»': 'Варианты комедии «От ней все качества»',
    '** ВСѢМЪ РАВНО': 'Всем равно',
    'ВАРИАНТ «ВСЕМ РАВНО»': 'Вариант «Всем равно»',
    '**НѢТЪ ВЪ МІРѢ ВИНОВАТЫХЪ. [III]': 'Нет в мире виноватых [III]',
    'ВАРИАНТЫ «НЕТ В МИРЕ ВИНОВАТЫХ». [III]': 'Варианты «Нет в мире виноватых» [III]',
    'ВАРИАНТЫ СТАТЬИ «СМЕРТНАЯ КАЗНЬ И ХРИСТИАНСТВО»': 'Варианты статьи «Смертная казнь и христианство»',
    'ПИСЬМО РЕВОЛЮЦIОНЕРУ': 'Письмо революционеру',
    'ВАРИАНТЫ «ПИСЬМА РЕВОЛЮЦIОНЕРУ»': 'Варианты «Письма революционеру»',
    'НОМЕРЪ ГАЗЕТЫ': 'Номер газеты',
    'ВАРИАНТЫ СТАТЬИ «О ГОГОЛЕ»': 'Варианты статьи «О Гоголе»',
    'ВАРИАНТЫ «ПИСЬМА СТУДЕНТУ О ПРАВЕ»': 'Варианты «Письма студенту о праве»',
    'ВАРИАНТ СТАТЬИ «О ВОСПИТАНИИ»': 'Вариант статьи «О воспитании»',
    '[О «ВЕХАХ».]': 'О «Вехах»',
    '**, *** [О ГОСУДАРСТВѢ]': 'О государстве',
    'ВАРИАНТЫ СТАТЬИ [«О ГОСУДАРСТВЕ»]': 'Варианты статьи «О государстве»',
    'ВАРИАНТЫ СТАТЬИ «НЕИЗБЕЖНЫЙ ПЕРЕВОРОТ»': 'Варианты статьи «Неизбежный переворот»',
    'ВАРИАНТЫ «ДОКЛАДА, ПРИГОТОВЛЕННОГО ДЛЯ КОНГРЕССА МИРА В СТОКГОЛЬМЕ»': 'Варианты «Доклада, приготовленного для конгресса мира в Стокгольме»',
    '*[ДОКЛАД, ПРИГОТОВЛЕННЫЙ ДЛЯ КОНГРЕССА МИРА НА ФРАНЦУЗСКОМ ЯЗЫКЕ.]': 'Доклад, приготовленный для конгресса мира на французском языке',
    'ВАРИАНТЫ «ЗАЯВЛЕНИЯ ОБ АРЕСТЕ H. Н. ГУСЕВА»': 'Варианты «Заявления об аресте Н. Н. Гусева»',
    'ВАРИАНТЫ СТАТЬИ «О НАУКЕ»': 'Варианты статьи «О науке»',
    'ВАРИАНТЫ «ОТВЕТА ПОЛЬСКОЙ ЖЕНЩИНЕ»': 'Варианты «Ответа польской женщине»',
    '[О РУГАТЕЛЬНЫХЪ ПИСЬМАХЪ.]': 'О ругательных письмах',
    'ВАРИАНТЫ СТАТЬИ [О РУГАТЕЛЬНЫХ ПИСЬМАХ]': 'Варианты статьи «О ругательных письмах»',
    '[ПО ПОВОДУ СТАТЬИ П. СТРУВЕ.]': 'По поводу статьи П. Струве',
    'ВАРИАНТ «ПО ПОВОДУ СТАТЬИ СТРУВЕ»': 'Вариант «По поводу статьи Струве»',
    '*[ПИСЬМО В «РУСЬ» С РУГАТЕЛЬНЫМИ ПИСЬМАМИ.]': 'Письмо в «Русь» с ругательными письмами',
    'ВАРИАНТЫ СТАТЬИ «ПОРА ПОНЯТЬ»': 'Варианты статьи «Пора понять»',
    'ВАРИАНТЫ СТАТЬИ «ЕЩЕ О НАУКЕ»': 'Варианты статьи «Еще о науке»',
    'ВАРИАНТЫ СТАТЬИ «СЛАВЯНСКОМУ СЪЕЗДУ В СОФИИ»': 'Варианты статьи «Славянскому съезду в Софии»',
    '[ПЕРВАЯ РЕДАКЦИЯ СТАТЬИ «БРОДЯЧИЕ ЛЮДИ».]': 'Первая редакция статьи «Бродячие люди»',
    'О БЕЗУМIИ': 'О безумiи',
    'ВАРИАНТЫ СТАТЬИ «О БЕЗУМИИ»': 'Варианты статьи «О безумии»',
    '*[ДОБАВЛЕНИЕ К ДОКЛАДУ НА КОНГРЕССЕ МИРА.]': 'Добавление к докладу на конгрессе мира',
    '[ВОСПОМИНАНИЯ О Н. Я. ГРОТЕ.]': 'Воспоминания о Н. Я. Гроте',
    'О СОЦІАЛИЗМѢ': 'О социализме',
    '* ВАРИАНТЫ «О СОЦИАЛИЗМЕ»': 'Варианты «О социализме»',
    '[ДѢЙСТВИТЕЛЬНОЕ СРЕДСТВО.]': 'Действительное средство',
    'НА КАЖДЫЙ ДЕНЬ (1906—1910) ЧАСТЬ ПЕРВАЯ': 'На каждый день. Часть первая',
    'НА КАЖДЫЙ ДЕНЬ(1906—1910)ЧАСТЬ ВТОРАЯ': 'На каждый день. Часть вторая',
    'ЧЕРНОВЫЕ ВАРИАНТЫ': 'Черновые варианты к «На каждый день»',  # 44 vol.
    'ПУТЬ ЖИЗНИ1910': 'Путь жизни',
    '«ПУТЬ ЖИЗНИ»': 'Варианты к «Пути жизни»'
}


def regex_add_uuid_for_paragraphs(matchobj):
    group = matchobj.group(1)
    already_has_id_pattern = r'\s*?id="\w+"'
    group = re.sub(already_has_id_pattern, '', group)
    return r'<p rend{group} id="{id}">'.format(group=group, id=uuid.uuid4())


HTML_TO_XML_PATTERNS = [
    (re.compile(r'<br\s*/>'), r'<lb/>'),
    (  # New, after v. 42
        re.compile(r'<div(.*?)xmlns="http://www.w3.org/1999/xhtml"(.*?)>'),
        r'<div\1\2>'
    ),
    (
        # re.compile(r'<div\s+xmlns="http://www.w3.org/1999/xhtml"\s+class(=".*?")\s+id'),
        re.compile(r'<div\s+(xmlns="http://www.w3.org/1999/xhtml"\s+)?class(=".*?")\s+id'),
        r'<div type\2 xml:id'
    ),
    (  # New, after v. 41
        re.compile(r'<div\s+(xmlns="http://www.w3.org/1999/xhtml"\s+)?class="(stanza.*?|poem.*?|section.*?)"'),
        r'<div type="\2"'
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
    ),
    (  # New, after v. 41
        re.compile(r'<span\s+class(.*?)>'),
        r'<hi rend\1>'
    ),
    (  # New, after v. 41
        re.compile(r'</span>'),
        r'</hi>'
    ),
    (
        re.compile(r'<span'),
        r'<hi'
    ),
    (  # New, after v. 41. Follows page number
        re.compile(r'<a name="\d+"></a>'),
        ''
    ),
    (  # New, after v. 42
        re.compile(r'<div rend(.*?)xml:id(.*?)>'),
        r'<div type\1xml:id\2>'
    ),
    # (
    #     re.compile(r'<div rend="(.*?)" (((?!xml:).)*)id(.*?)>'),
    #     r'<div type="\1" \2xml:id\4'
    # )
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
    # rus_pattern = re.compile(r'[а-яА-Я\n ]')
    tokens = split_pattern.split(text)
    # print(tokens)
    # print(len(tokens))
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
            in_head_pattern = r'<head[^>].*?>\[.*?\]</head>'  # Иначе странно себя ведет
            if re.search(in_head_pattern, token) is not None:
                continue  # Иначе <head rend="center">[II.]</head> -> <head rend="center"></head>
            text_res, changes, s_json = Processor.process_text(
                text=token,
                show=True,
                delimiters=['<choice><reg>', '</reg><orig>', '</orig></choice>'],
                check_brackets=False
            )
            tokens[i] = text_res
            # print('token', token, '\nresult', text_res)
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
        # print(note_text)
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
        note = re.sub(r'\n|\s{2,}', '', note)  # test for v 41
        # print(note)
        text = re.sub(
            # f'<a.*?id="backn{note_number}"\s+type="note">.*?</a>', note, text
            f'<a[^>]*?id="backn{note_number}"\s+type="note">.*?</a>', note, text
            # f'<a[^>]*?id="backn{note_number}"\s+type="note">.*?</a>', f'\n{note}', text
        )
    # print(text)
    return text


def replace_html_markup_with_xml(text: str) -> str:
    for pattern, substitute in HTML_TO_XML_PATTERNS:
        text = pattern.sub(substitute, text)
    return text


def markup_choices_for_editorial_corrections(text):
    choice_pattern = re.compile(
        # r'(<head.*?>[*, ]*(?!<p))?(\s*(\w*?(\[(.*?)])\w*)\s*)(?!\">)(</head>)?'
        # r'(<head[^>]*?>[*, ]*)?(\s*(\w*?(\[(.*?)])\w*)\s*)(?!\">)(</head>)?'
        # r'(<head[^>]*?>[*, ]*)?(\s*(\w*?(\[(.*?)])\w*)\s*?)(?!\">)(</head>)?'
        r'(<head[^>]*?>[*, IVX.]*)?(\s*(\w*?(\[(.*?)])\w*)\s*?)(?!\">)(</head>)?'
    )
    illegible_pattern = re.compile(  # решить, что с этим делать
        r'(\[\d+.*?не\s*разобр.*?])|'  # [2 неразобр.]
        r'(\w+\[\w+\?])|'  # вл[иянием?]
        r'(\[\?])'  # [?]
    )
    crossed_out_pattern = re.compile(
        # r'(<.*?>)?(з|З)ач(е|ё)ркнуто:(<.*?>)?'
        r'(<[^>]*?>)?(з|З)ач(е|ё)ркнуто:(<[^>]*?>)?'
    )
    choice_result = re.findall(choice_pattern, text)
    # print(choice_result)
    for i in choice_result:
        # print(i)
        if (
                # i[0] or  # if inside head
                (i[0] and i[5]) or  # if inside head
                (i[0] and '<p' in i[0]) or
                illegible_pattern.search(i[2]) is not None or
                crossed_out_pattern.search(i[2]) is not None
        ):
            continue
        sub_1 = re.sub(r'\[|]', r'', i[2])
        sub_2 = re.sub(r'\[', r'\\[', i[2])
        sub_3 = re.sub(r']', r'\\]', sub_2)
        sub_4 = re.sub('\[.*?]', '', i[2])
        # choice_attribute = re.search('<.*?>(.*?)<.*?>', i[2])  # [<hi>хвастовство</hi>]
        choice_attribute = re.search('(<hi.*[^>]>)|(</hi>)', i[2])  # [<hi>хвастовство</hi>]
        left_tag = right_tag = ''
        if choice_attribute is None:
            choice_attribute = i[2]
        else:
            # choice_attribute = choice_attribute.group(1)
            left_tag = choice_attribute.group(1) if choice_attribute.group(1) else ''
            right_tag = choice_attribute.group(2) if choice_attribute.group(2) else ''
            choice_attribute = re.sub(r'(<hi.*[^>]>)|(</hi>)', '', i[2])
            sub_1 = re.sub(r'(<hi.*[^>]>)|(</hi>)', '', sub_1)
        if re.search(r'<lb/>', choice_attribute) is not None:
            choice_attribute = re.sub(r'<(lb/)>', '&lt;\1&gt;', choice_attribute)
        # choice_attribute = choice_attribute.replace('<', '&lt;')  # <> are not allowed inside attribute
        # choice_attribute = choice_attribute.replace('>', '&gt;')  # e.g. "[Составлено H. Н. Гусевым.<lb/>Под редакцией Л. Н. Толстого.]"

        # print(choice_attribute)
        # print(sub_4, sub_1, choice_attribute, sep='\n', end='\n________________\n')
        replacement = (f'{left_tag}<choice original_editorial_correction="{choice_attribute}">'
                       f'<sic>{sub_4}</sic><corr>{sub_1}</corr></choice>{right_tag}')
        sub_3 = re.sub(r'(\(|\))', '\1', sub_3)  # Чтоб скобки не мешали re
        reg_for_repl = f'(?<!="){sub_3}(?!">)'
        # print(reg_for_repl, replacement, text, sep='\n\n')
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
    date_tag = f'<date when="--{dates[month]}-{day}"/>'
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
    # print(text)
    if extra_funcs is not None:
        for func in extra_funcs:
            text = func(text)

    # order matters

    text = replace_refs_to_notes_with_notes(text, notes)
    text = replace_html_markup_with_xml(text)
    text = markup_choices_for_editorial_corrections(text)
    text = markup_choices_for_prereform_spelling(text)  # slow, turn off while debugging
    return text


def fill_tei_template(tei_data: dict, tei_template_file: str) -> str:
    tei_data.update(
        {
            'author': 'Толстой Л.Н.',  # for now
            'date': 'fill date later',  # for now
            'date_not_after': 'fill date_not_after later',  # for now
            'date_not_before': 'fill date_not_before later',  # for now
            'setting_time': 'XIX'  # for now
        }
    )
    tei = ut.read_xml(tei_template_file).format(**tei_data)
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


def prepare_title(default_title):
    if default_title in prepared_titles:
        return prepared_titles[default_title]
    default_title = default_title.strip('*[] ')
    return capitalize_title(default_title)


def leave_only_parent_divs(divs):
    """Filter divs iterable to exclude duplicated children divs."""

    def is_top_div(div) -> bool:
        """Is the div the only `body`'s child which embodies all other divs."""
        # Given that body has only one child and it's a div
        # Which is usually the case
        return div.getparent().tag.split('}')[1] == 'body'

    return [d for d in divs if is_top_div(d.getparent())]


def prepare_v_41_for_xml_conversion(text: str) -> str:
    """To be used as `extra_funcs` argument in main function."""
    """
    for 42 start h000006002
    """

    # def delete_divs_with_duplicated_text(text: str) -> str:
    #     re.sub(
    #         r'<div xmlns="http://www.w3.org/1999/xhtml"((?!id=").)*?>.*?<div xmlns="http://www.w3.org/1999/xhtml">',
    #         '',
    #         text,
    #     )
    #     return text
    # text = delete_divs_with_duplicated_text(text)

    def divide_divs_into_months_groups(start_div_id='h000010002') -> Iterable:
        groups = []
        id_length = len('h000010002')
        prev_div = root.xpath(f'//ns:div[@id="{start_div_id}"]', namespaces={'ns': f'{namespace}'})[0]
        month = [prev_div]
        while True:
            new_div = prev_div.getnext()
            if new_div is None:
                groups.append(month.copy())
                break
            if new_div.get('id') is not None and len(new_div.get('id')) == id_length:
                groups.append(month.copy())
                prev_div = new_div
                month = [prev_div]
                continue
            month.append(new_div)
            prev_div = new_div
        return groups

    def rearrange_group_contents(month):
        def new_day_inside_element(element):
            element_copy = list(element).copy()
            history = []
            while element_copy:
                tag = element_copy.pop(0)
                history.append(tag)
                if len(history) >= 2:
                    if (history[-2].tag.split('}')[1] == 'br'
                            and history[-1].tag.split('}')[1] == 'p'
                            and history[-1].get('class') == 'subtitle centerline'
                            and history[-1][0].tag.split('}')[1] == 'span'
                            and (re.search(r'\d{1,2}-е \w+', history[-1][0].text) is not None
                                 or (re.search(r'\d{1,2}-е', history[-1].text) is not None
                                     and 3 <= len(history[-1][0].text) <= 8
                                     and history[-1][0].text.casefold()[:3] in dates.keys()
                                 )
                            )
                    ):
                        return True
            return False

        def find_start_of_new_day(element):
            """arg: element or list of subelements"""
            element_copy = list(element).copy()
            history = []
            while element_copy:
                tag = element_copy.pop(0)
                history.append(tag)
                if len(history) >= 2:
                    if (history[-2].tag.split('}')[1] == 'br'
                            and history[-1].tag.split('}')[1] == 'p'
                            and history[-1].get('class') == 'subtitle centerline'
                            and history[-1][0].tag.split('}')[1] == 'span'
                            and (re.search(r'\d{1,2}-е \w+', history[-1][0].text) is not None
                                 or (re.search(r'\d{1,2}-е', history[-1].text) is not None
                                     and 3 <= len(history[-1][0].text) <= 8
                                     and history[-1][0].text.casefold()[:3] in dates.keys()
                                 )
                            )
                    ):
                        return len(history) - 2
            return None

        def split_mixed_weekly_and_daily(element):
            days_start = find_start_of_new_day(element)
            week_part = deepcopy(element)
            for child in list(week_part)[days_start:]:
                week_part.remove(child)
            days_part = deepcopy(element)
            for child in list(days_part)[:days_start]:
                days_part.remove(child)
            # pprint(week_part)
            return week_part, days_part

        def rearrange_week(week, last_id):
            """Return arranged element from list of elements"""
            week_div = week[0]
            week_div.set('class', 'weekly')
            week_div_id = last_id[:-3] + '{:03d}'.format(int(last_id[-3:]) + 1)
            week_div.set('id', week_div_id)
            h4_counter = 0
            h5_counter = 0
            for div in week[1:]:
                print(div[0].text)
                if div[0].tag.split('}')[1] == 'h4':
                    h4_counter += 1
                    h5_counter = 0
                    last_h4 = div
                    week_div.append(div)
                    div.set('class', 'weekly section')
                    div.set('id', week_div_id + '{:03d}'.format(h4_counter))
                if div[0].tag.split('}')[1] == 'h5':
                    h5_counter += 1
                    last_h4.append(div)
                    div.set('class', 'section')
                    div.set('id', last_h4.get('id') + '{:03d}'.format(h5_counter))
            last_date = main_div[-1][0].get('when')
            date_element = etree.Element('date')
            date_element.set('when', last_date)
            week_div.insert(0, date_element)

            return deepcopy(week_div)
            pass

        def add_weekly_div_to_main_div(week: list) -> None:
            last_id = main_div[-1].get('id')[:13]
            week = rearrange_week(week, last_id)
            main_div.append(week)
            pass

        def split_days_element_into_days(element):
            # Daily after weekly in the same div continue till the div's end
            tags = list(element).copy()
            days = []
            new_day_start = find_start_of_new_day(tags[2:]) + 2
            while True:
                days.append(tags[0:new_day_start])
                tags = tags[new_day_start:]
                new_day_start = find_start_of_new_day(tags[2:])
                if new_day_start is None:
                    days.append(tags[:])
                    break
                else:
                    new_day_start += 2
            return days
            pass

        def add_days_divs_to_main_div(days) -> None:
            for day in days:
                last_id = main_div[-1].get('id')[:13]
                day_div = etree.SubElement(main_div, 'div')
                day_div.set('class', 'daily')
                day_div.set('id', last_id[:-3] + '{:03d}'.format(int(last_id[-3:]) + 1))
                for tag in day:
                    day_div.append(deepcopy(tag))
                date_text = f'{day[1].text}{day[1][0].text}'
                date = re.search('(\d{1,2})-е (\w+)', date_text)
                date_tag = etree.Element('date')
                day_div.insert(0, date_tag)
                date_tag.set('when', f'--{dates[date.group(2).casefold()[:3]]}-{date.group(1)}')
                print(date.group())
            pass

        # NB: no month starts with a weekly reading
        main_div = month[0]
        div_in_main_with_initial_days = main_div[1]
        # print(list(div_in_main_with_initial_days))
        div_in_main_copy = list(div_in_main_with_initial_days).copy()
        history = []
        days = []
        day = []
        while div_in_main_copy:
            if len(history) >= 2:
                if (history[-2].tag.split('}')[1] == 'br'
                        and history[-1].tag.split('}')[1] == 'p'
                        and history[-1].get('class') == 'subtitle centerline'
                        and history[-1][0].tag.split('}')[1] == 'span'
                        and (re.search(r'\d{1,2}-е \w+', history[-1][0].text) is not None
                             or (re.search(r'\d{1,2}-е', history[-1].text) is not None
                                 and 3 <= len(history[-1][0].text) <= 8
                                 and history[-1][0].text.casefold()[:3] in dates.keys()
                             )
                        )
                ):
                    text = f'{history[-1].text}{history[-1][0].text}'
                    date = re.search('\d{1,2}-е \w+', text).group()
                    # print(date)
                    if len(day) > 2:
                        days.append(day[:-2])
                        day = day[-2:]
            element = div_in_main_copy.pop(0)
            history.append(element)
            day.append(element)
        else:
            if day:
                days.append(day)
        # pprint([etree.tostring(tag, encoding='unicode') for d in days for tag in d])
        pass
        for i, day in enumerate(days):
            day_div = etree.SubElement(main_div, 'div')
            parent_id = day_div.getparent().get('id')
            day_div.set('class', 'daily')
            day_div.set('id', parent_id + '{:03d}'.format(i + 1))
            for tag in day:
                day_div.append(deepcopy(tag))
            date_text = f'{day[1].text}{day[1][0].text}'
            date = re.search('(\d{1,2})-е (\w+)', date_text)
            date_tag = etree.Element('date')
            day_div.insert(0, date_tag)
            date_tag.set('when', f'--{dates[date.group(2).casefold()[:3]]}-{date.group(1)}')
            print(date.group())
        main_div.remove(div_in_main_with_initial_days)
        pass
        # All other divs with weekly and daily in the group
        months_copy = month.copy()[1:]
        history = []
        week = []
        while months_copy:
            element = months_copy.pop(0)
            history.append(element)
            # print(element[0].text)
            # if element[0].text == 'ЯГОДЫ':
            #     print(True)
            #     print(bool(week))
            #     print(element[0].tag.split('}')[1])
            #     print(new_day_inside_element(element))
            if not week and element[0].tag.split('}')[1] == 'h3' and element[0].text == 'НЕДЕЛЬНОЕ ЧТЕНИЕ':
                week.append(element)
                continue
            if week and not new_day_inside_element(element):
                week.append(element)
                # if element[0].text == 'ЯГОДЫ':
                #     print('appended')
                #     print(week[-1][0].text)
            if week and new_day_inside_element(element):
                week_element, days_element = split_mixed_weekly_and_daily(element)
                week.append(week_element)
                add_weekly_div_to_main_div(week)
                week = []
                days = split_days_element_into_days(days_element)
                add_days_divs_to_main_div(days)
                # for not_main_div in month[1:]:
                #     if not_main_div.getparent() is not None:
                #         not_main_div.getparent().remove(not_main_div)

                pass
        else:
            if week:  # After weekly no daily in the month
                add_weekly_div_to_main_div(week)
                pass
            for not_main_div in month[1:]:  # Remove duplicated
                if not_main_div.getparent() is not None:
                    not_main_div.getparent().remove(not_main_div)
        pass

    # `fromstring` method can't start parsing siblings, it needs a single root
    root = etree.fromstring(f'<container>{text}</container>')
    print(root.tag)
    namespace = 'http://www.w3.org/1999/xhtml'
    all_divs = root.xpath('//ns:div', namespaces={'ns': f'{namespace}'})
    parent_divs = [d for d in all_divs if d.getparent().tag == 'container']
    # pprint(all_divs)
    # print(len(all_divs))
    # print(len(parent_divs))

    # Remove first empty div and some other
    root.remove(root.xpath('//ns:div[@id="h000010"]', namespaces={'ns': f'{namespace}'})[0])
    root.remove(root.xpath('//ns:div[@id="h000010003002001002"]', namespaces={'ns': f'{namespace}'})[0])
    # Month is a 'part' (not 'section') and is a parent to its sections
    root.xpath('//ns:div[@id="ref1"]', namespaces={'ns': f'{namespace}'})[0].attrib['id'] = 'h000010001'
    for month_tag in root.xpath(
            '//ns:div[string-length(@id)=10]', namespaces={'ns': f'{namespace}'})[1:]:
        month_tag.attrib['class'] = 'part'
    # Remove empty divs like h000010002002001
    for empty_tag in root.xpath(
            '//ns:div[string-length(@id)=16]', namespaces={'ns': f'{namespace}'}):
        root.remove(empty_tag)
    months = divide_divs_into_months_groups(start_div_id='h000010002')
    for month in months:
        rearrange_group_contents(month)

    text = etree.tostring(root, encoding='unicode')[len('<container>'):-len('</container>')]
    # print(text)
    return text
    pass



def prepare_v_42_for_xml_conversion(text: str) -> str:
    """To be used as `extra_funcs` argument in main function."""
    """
    for 42 start h000006002
    """

    # def delete_divs_with_duplicated_text(text: str) -> str:
    #     re.sub(
    #         r'<div xmlns="http://www.w3.org/1999/xhtml"((?!id=").)*?>.*?<div xmlns="http://www.w3.org/1999/xhtml">',
    #         '',
    #         text,
    #     )
    #     return text
    # text = delete_divs_with_duplicated_text(text)

    def divide_divs_into_months_groups(start_div_id='h000010002') -> Iterable:
        groups = []
        id_length = len(start_div_id)
        # print(root.xpath(f'//ns:div[@id="{start_div_id}"]', namespaces={'ns': f'{namespace}'}))
        print(root.xpath(f'//div'))
        prev_div = root.xpath(f'//ns:div[@id="{start_div_id}"]', namespaces={'ns': f'{namespace}'})[0]
        month = [prev_div]
        while True:
            new_div = prev_div.getnext()
            if new_div is None:
                groups.append(month.copy())
                break
            if new_div.get('id') is not None and len(new_div.get('id')) == id_length:
                groups.append(month.copy())
                prev_div = new_div
                month = [prev_div]
                continue
            month.append(new_div)
            prev_div = new_div
        return groups

    def rearrange_group_contents(month):
        def new_day_inside_element(element):
            element_copy = list(element).copy()
            history = []
            while element_copy:
                tag = element_copy.pop(0)
                history.append(tag)
                if len(history) >= 2:
                    if (history[-2].tag.split('}')[1] == 'br'
                            and history[-1].tag.split('}')[1] == 'p'
                            # and history[-1].get('class') == 'center textindent_38px'
                            # and history[-1][0].tag.split('}')[1] == 'span'
                            and (re.search(
                                r'\d{1,2}-е \w+',
                                ''.join([t for t in history[-1].itertext()])
                            ) is not None
                                 # or (re.search(r'\d{1,2}-е', history[-1].text) is not None
                                 #     and 3 <= len(history[-1][0].text) <= 8
                                 #     and history[-1][0].text.casefold()[:3] in dates.keys()
                                 # )
                            )
                    ):
                        return True
            return False

        def find_start_of_new_day(element):
            """arg: element or list of subelements"""
            element_copy = list(element).copy()
            history = []
            while element_copy:
                tag = element_copy.pop(0)
                history.append(tag)
                if len(history) >= 2:
                    if (history[-2].tag.split('}')[1] == 'br'
                            and history[-1].tag.split('}')[1] == 'p'
                            # and history[-1].get('class') == 'center textindent_38px'
                            # and history[-1][0].tag.split('}')[1] == 'span'
                            and (re.search(
                                r'\d{1,2}-е \w+',
                                ''.join([t for t in history[-1].itertext()])
                            ) is not None
                                 # or (re.search(r'\d{1,2}-е', history[-1].text) is not None
                                 #     and 3 <= len(history[-1][0].text) <= 8
                                 #     and history[-1][0].text.casefold()[:3] in dates.keys()
                                 # )
                            )
                    ):
                        return len(history) - 2
            return None

        def split_mixed_weekly_and_daily(element):
            days_start = find_start_of_new_day(element)
            week_part = deepcopy(element)
            for child in list(week_part)[days_start:]:
                week_part.remove(child)
            days_part = deepcopy(element)
            for child in list(days_part)[:days_start]:
                days_part.remove(child)
            # pprint(week_part)
            return week_part, days_part

        def rearrange_week(week, last_id):
            """Return arranged element from list of elements"""
            week_div = week[0]
            week_div.set('class', 'weekly')
            week_div_id = last_id[:-3] + '{:03d}'.format(int(last_id[-3:]) + 1)
            week_div.set('id', week_div_id)
            h4_counter = 0
            h5_counter = 0
            for div in week[1:]:
                print(div[0].text)
                if div[0].tag.split('}')[1] == 'h4':
                    h4_counter += 1
                    h5_counter = 0
                    last_h4 = div
                    week_div.append(div)
                    div.set('class', 'weekly section')
                    div.set('id', week_div_id + '{:03d}'.format(h4_counter))
                if div[0].tag.split('}')[1] == 'h5':
                    h5_counter += 1
                    last_h4.append(div)
                    div.set('class', 'section')
                    div.set('id', last_h4.get('id') + '{:03d}'.format(h5_counter))
            last_date = main_div[-1][0].get('when')
            date_element = etree.Element('date')
            date_element.set('when', last_date)
            week_div.insert(0, date_element)

            return deepcopy(week_div)
            pass

        def add_weekly_div_to_main_div(week: list) -> None:
            last_id = main_div[-1].get('id')[:13]
            week = rearrange_week(week, last_id)
            main_div.append(week)
            pass

        def split_days_element_into_days(element):
            # Daily after weekly in the same div continue till the div's end
            tags = list(element).copy()
            days = []
            # if element.get('id') == 'h000006002006001012':
            #     breakpoint()
            new_day_start = find_start_of_new_day(tags[2:])
            if new_day_start is None:
                days.append(tags)
                return days
            else:
                new_day_start += 2
            while True:
                days.append(tags[0:new_day_start])
                tags = tags[new_day_start:]
                new_day_start = find_start_of_new_day(tags[2:])
                if new_day_start is None:
                    days.append(tags[:])
                    break
                else:
                    new_day_start += 2
            return days
            pass

        def add_days_divs_to_main_div(days) -> None:
            for day in days:
                last_id = main_div[-1].get('id')[:13]
                print('last_id', last_id)
                day_div = etree.SubElement(main_div, 'div')
                day_div.set('class', 'daily')
                day_div.set('id', last_id[:-3] + '{:03d}'.format(int(last_id[-3:]) + 1))
                for tag in day:
                    day_div.append(deepcopy(tag))
                date_text = ''.join([t for t in day[1].itertext()])
                date = re.search('(\d{1,2})-е (\w+)', date_text)
                date_tag = etree.Element('date')
                day_div.insert(0, date_tag)
                date_tag.set('when', f'--{dates[date.group(2).casefold()[:3]]}-{date.group(1)}')
                print(date.group())
            pass

        # NB: no month starts with a weekly reading
        main_div = month[0]
        print('main_div', main_div[0][0].text)
        div_in_main_with_initial_days = main_div[1]
        # print(list(div_in_main_with_initial_days))
        div_in_main_copy = list(div_in_main_with_initial_days).copy()
        history = []
        days = []
        day = []
        while div_in_main_copy:
            if len(history) >= 2:
                if (history[-2].tag.split('}')[1] == 'br'
                        and history[-1].tag.split('}')[1] == 'p'
                        # and history[-1].get('class') == 'center textindent_38px'
                        # and history[-1][0].tag.split('}')[1] == 'span'
                        and (re.search(
                            r'\d{1,2}-е \w+',
                            ''.join([t for t in history[-1].itertext()])
                        ) is not None
                             # or (re.search(r'\d{1,2}-е', history[-1].text) is not None
                             #     and 3 <= len(history[-1][0].text) <= 8
                             #     and history[-1][0].text.casefold()[:3] in dates.keys()
                             # )
                        )
                ):
                    # text = f'{history[-1].text}{history[-1][0].text}'
                    text = ''.join([t for t in history[-1].itertext()])
                    print('date', text)
                    date = re.search('\d{1,2}-е \w+', text).group()
                    # print(date)
                    if len(day) > 2:
                        days.append(day[:-2])
                        day = day[-2:]
            element = div_in_main_copy.pop(0)
            history.append(element)
            day.append(element)
        else:
            if day:
                days.append(day)
        # pprint([etree.tostring(tag, encoding='unicode') for d in days for tag in d])
        pass
        for i, day in enumerate(days):
            day_div = etree.SubElement(main_div, 'div')
            parent_id = day_div.getparent().get('id')
            day_div.set('class', 'daily')
            day_div.set('id', parent_id + '{:03d}'.format(i + 1))
            for tag in day:
                day_div.append(deepcopy(tag))
            # date_text = f'{day[1].text}{day[1][0].text}'
            date_text = ''.join([t for t in day[1].itertext()])
            date = re.search('(\d{1,2})-е (\w+)', date_text)
            date_tag = etree.Element('date')
            day_div.insert(0, date_tag)
            date_tag.set('when', f'--{dates[date.group(2).casefold()[:3]]}-{date.group(1)}')
            print('in days', date.group())
        main_div.remove(div_in_main_with_initial_days)
        pass
        # All other divs with weekly and daily in the group
        months_copy = month.copy()[1:]
        history = []
        week = []
        while months_copy:
            element = months_copy.pop(0)
            history.append(element)
            # print(element[0].text)
            # if element[0].text == 'ЯГОДЫ':
            #     print(True)
            #     print(bool(week))
            #     print(element[0].tag.split('}')[1])
            #     print(new_day_inside_element(element))
            if not week and element[0].tag.split('}')[1] == 'h3' and element[0].text == 'НЕДЕЛЬНОЕ ЧТЕНИЕ':
                week.append(element)
                continue
            if week and not new_day_inside_element(element):
                week.append(element)
                # if element[0].text == 'ЯГОДЫ':
                #     print('appended')
                #     print(week[-1][0].text)
            if week and new_day_inside_element(element):
                week_element, days_element = split_mixed_weekly_and_daily(element)
                week.append(week_element)
                add_weekly_div_to_main_div(week)
                week = []
                days = split_days_element_into_days(days_element)
                # breakpoint()
                add_days_divs_to_main_div(days)
                # for not_main_div in month[1:]:
                #     if not_main_div.getparent() is not None:
                #         not_main_div.getparent().remove(not_main_div)

                pass
        else:
            if week:  # After weekly no daily in the month
                add_weekly_div_to_main_div(week)
                pass
            for not_main_div in month[1:]:  # Remove duplicated
                if not_main_div.getparent() is not None:
                    not_main_div.getparent().remove(not_main_div)
        pass

    # `fromstring` method can't start parsing siblings, it needs a single root
    root = etree.fromstring(f'<container>{text}</container>')
    print(root.tag)
    namespace = 'http://www.w3.org/1999/xhtml'
    all_divs = root.xpath('//ns:div', namespaces={'ns': f'{namespace}'})
    parent_divs = [d for d in all_divs if d.getparent().tag == 'container']
    # pprint(list(all_divs[1]))
    # pprint(all_divs)
    # print(len(all_divs))
    # print(len(parent_divs))

    # Remove first empty div and some other
    # root.remove(root.xpath('//ns:div[@id="h000010"]', namespaces={'ns': f'{namespace}'})[0])
    # root.remove(root.xpath('//ns:div[@id="h000010003002001002"]', namespaces={'ns': f'{namespace}'})[0])

    # Month is a 'part' (not 'section') and is a parent to its sections
    # root.xpath('//ns:div[@id="ref1"]', namespaces={'ns': f'{namespace}'})[0].attrib['id'] = 'h000010001'  # preface
    for month_tag in root.xpath(
            '//ns:div[string-length(@id)=10]', namespaces={'ns': f'{namespace}'})[1:]:
        month_tag.attrib['class'] = 'part'
    # Remove empty divs like h000010002002001
    # for empty_tag in root.xpath(
    #         '//ns:div[string-length(@id)=16]', namespaces={'ns': f'{namespace}'}):
    #     root.remove(empty_tag)
    months = divide_divs_into_months_groups(start_div_id='h000006002')
    for month in months:
        rearrange_group_contents(month)

    text = etree.tostring(root, encoding='unicode')[len('<container>'):-len('</container>')]
    # print(text)
    return text


def correct_filenames(csv_source) -> dict:
    with open(csv_source, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        return {row[0]: row[1] for row in reader}

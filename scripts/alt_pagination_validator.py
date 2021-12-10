# just for debugging
import os
from pprint import pprint
import re

import utils as ut
import split_volumes_utils as sp_ut

def main():
    # pattern = re.compile('npnumber')
    # pattern = re.compile('<span class="npnumber">441</span>')

    # pattern = re.compile(r'<span\s*?class="npnumber">\s*?(\d*?)\s*?</span>')
    # pattern = re.compile(r'<span\s*?class="opnumber">\s*?(\d*?)\s*?</span>')
    # pattern = re.compile(r'<hi\s*?rend="opnumber">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<hi\s*?style="opnumber">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<hi\s*?style="opnumber.*?">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<hi\s*?style="npnumber.*?">\s*?(\d*?)\s*?</hi>')  # for old pages
    # pattern = re.compile(r'<pb\s*n="(\d*?)"\s*\/>')

    equal = 0
    found = 0
    types_combinations = {}
    for path in ut.paths:
        for file in os.listdir(path):
            # print(file)
            if file in ut.xmls_with_critical_errors:
                continue
            pages, data = ut.get_pages_using_lxml(os.path.join(path, file))
            types = data.get('tag_types')
            if types is not None:
                types = tuple(types)
                if types not in types_combinations:
                    types_combinations[types] = 1
                    # print(types)
                else:
                    types_combinations[types] += 1
            if not pages:
                print(file)
            # pages1 = ut.get_pages_using_re(os.path.join(path, file))
            # print(pages)
            # if pages == pages1:
            #     equal += 1
            # else:
                # print(file)
            # if pages and data.get('tag_types') == {'hi_style_op', 'hi_style_np'}:
            #     print(pages, file)
            #     found += 1
                pass
    print(found, equal)
    pprint(types_combinations)


if __name__ == '__main__':
    ut.change_to_project_directory()
    # main()

    # pages, data = ut.get_pages_using_re('test_file.xml')
    # pages, data = ut.get_pages_using_lxml('test_file.xml')
    # pages, data = ut.get_pages_using_lxml('test_file_1.xml')
    # print(pages, data)
    # fragments = ut.separate_into_consistent_fragments(pages)
    # print(pages)
    # print(fragments)
    # print(data)

    # pages, data = ut.get_pages_using_re('test_file.xml')
    # fragments = ut.separate_into_consistent_fragments(pages)
    # print(fragments)
    # print(ut.extract_gaps_from_fragments(fragments))
    # print(ut.get_pages_using_re('test_file.xml'))

    pass
    # s = "Я уставился в р[ек]у Нев[у] и бегу в р[ек]у"
    # # s = "Председ[ательствующий?]"
    # # s = "[2 не разоб]"
    # s = "то, ч[то] случилось въ его"
    # result = sp_ut.markup_choices_for_editorial_corrections(s)
    # print(s)
    # print(result)
    pass
    # sp_ut.replace_ref_to_notes_with_notes()
    pass
    # for file_name in os.listdir('parse_volume/result'):
    #     if not file_name.startswith('test_result'):
    #         continue
    #     with open(f'parse_volume/result/{file_name}') as file:
    #         text = file.read()
    #     if 'opnumber' in text or 'npnumber' in text or 'delimiter' in text or '<a/' in text:
    #         # print(file_name)
    #         pass
    #     if re.search(r'[=]"\w*?\[\w+]\w*?"', text) is not None:
    #         print(file_name)
    pass
    s = '<p class="left"><span class="npnumber">221</span> <a name="221"></a><span class="Razradka"><span class="npdelimiter">Марфа</span></span>. Что Марфа? Знаю, что Марфа. Ахъ не смотрѣли бы мои глаза, безсовѣстный.</p>'
    s = 'такъ важно б[ыло] то, ч[то] случилось въ его душѣ.<a href="#n18" id="backn18" type="note">[18]</a> А именно вчера послѣ прочтенія книжки, к[отор]ую ему далъ дьяконовъ сынъ'
    s = '<p class="left"><em>[Прохожій.]</em> Извѣстно, что — выпить. Зарекся я. Да зарокъ то мой слабый. А выпью — сейчасъ воровать. Только теперь шабашъ.</p>'
    s = '<h2 class="center">*[ДОКЛАД, ПРИГОТОВЛЕННЫЙ ДЛЯ КОНГРЕССА МИРА <br/>НА ФРАНЦУЗСКОМ ЯЗЫКЕ.]</h2>'
    s = 'у котораго одна горница, гдѣ вся семья, жена, снох[и], дѣвушки, ребята'
    # s = 'ewrkfjn <h2 class="center">* *, *[ДОКЛАД, ПРИГОТОВЛЕННЫЙ ДЛЯ КОНГРЕССА МИРА <br/>НА ФРАНЦУЗСКОМ ЯЗЫКЕ.]</h2>'
    s = 'студентъ [<em>зачеркнуто:</em> «соціалъ революціонеръ»].</p>'
    s = '[<em>хвастовство</em>]'
    s = 'положе[ніе]'
    s = '<hi rend="italic">Зачеркнуто:</hi><choice original_editorial_correction="положе[ніе]"><sic>положе</sic><corr>положеніе</corr></choice></p>'
    s = '<p class="left"> <em>Перед началом следующей реплики зач.:</em> Ba[?]</p>'
    # s = 'у котораго одна горница, гдѣ вся семья, жена, снох[и], дѣвушки, ребята'
    # print(sp_ut.replace_html_markup_with_xml(s))
    s1 = sp_ut.replace_html_markup_with_xml(s)
    print(s1)
    print()
    s2 = sp_ut.markup_choices_for_editorial_corrections(s1)
    print(s2)
    print()
    s3 = sp_ut.markup_choices_for_prereform_spelling(s2)
    print(s3)
    # print(s2 == s3)
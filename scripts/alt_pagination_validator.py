# just for debugging
import os
from pprint import pprint
import re

from lxml import etree

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


def test():

    pass

if __name__ == '__main__':
    ut.change_to_project_directory()
    # main()
    test()
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
    s = '12eiw<h3 class="center">13 ЯНВАРЯ.</h3>cxkdhjn'
    # s = 'у котораго одна горница, гдѣ вся семья, жена, снох[и], дѣвушки, ребята'
    s = '<note n="n19"><div type="section" xml:id="n19"><head><ref target="#backn19">19</ref></head><p class="left">[У вас счастливая pyкa].</p></div></note>'
    s = 'В Т[амбино], отсюда'
    s = '<head rend="center">IV</head><p rend="left" id="34e3551e-f9b8-40f8-b6e1-79c3a62b609a">На масленице шестого года жизни Сергия в затворе из соседнего города, после блинов с вином, собралась веселая компания богатых людей, мужчин и женщин, кататься на тройках. Компания состояла из двух адвокатов, одного богатого помещика, офицера и четырех женщин. Одна была жена офицера, другая — помещика, третья была девица, сестра помещика, и четвертая была разводная жена, красавица, богачка и чудачка, удивлявшая и мутившая город своими выходками.</p><p rend="left" id="eeccc218-c417-4e4d-ae18-c8a0c9185679">Погода была прекрасная, дорога как пол. Проехали верст десять за городом, остановились, и началось совещание, куда ехать: назад или дальше.</p><p rend="left" id="8bcf6699-b978-4a90-8aea-f5fc9134c9e1">— Да куда ведет эта дорога? — спросила Маковкина, разводная жена, красавица.</p><p rend="left" id="7b02b5d4-fe2f-4d51-9242-9645142c5a6d">— В Т[амбино], отсюда двенадцать верст, — сказал адвокат, ухаживавший за Маковкиной.</p><p rend="left" id="0c612ffa-743e-4434-be4b-ea8a081b315a">— Ну, а потом?</p><p rend="left" id="12b1494f-9062-4c27-900d-13361bd078e6">— А потом на Л. через монастырь.</p><p rend="left" id="d02af364-474a-42bd-80a2-a7b04540b168">— Там, где отец Сергий этот живет?</p><p rend="left" id="f35da106-face-4bb8-9f8a-1809243d864a">— Да.</p><p rend="left" id="defe5d49-5fae-405d-aee3-406897b6149f">— Касатский? Этот красавец пустынник?</p><p rend="left" id="97bf22ed-dd22-4b89-a2ec-bdc12240702d">— Да.</p><p rend="left" id="862717a9-0b2e-47f1-a5f8-17606d0f8de9"><pb n="18"/> — Медам! Господа! Едемте к Касатскому. В Т[амбине] отдохнем, закусим.</p><p rend="left" id="54805f7f-17cb-4b01-82f7-afffadde2aaf">— Но мы не поспеем ночевать домой.</p><p rend="left" id="1b8c3730-f87a-479e-8478-9b660202dbdc">— Ничего, ночуем у Касатского.</p><p rend="left" id="2c23f3da-1a20-49cd-a27a-ebe83575a8d1">— Положим, там есть гостиница монастырская, и очень хорошо. Я был, когда защищал Махина.</p><p rend="left" id="e6db9cbb-3a50-40db-89f7-78f92b7804c6">— Нет, я у Касатского буду ночевать.</p><p rend="left" id="1527b3de-ef48-487b-8bac-2f04dbb22b50">— Ну, уж это даже с вашим всемогуществом невозможно.</p><p rend="left" id="178030ca-e6f2-48ca-8a67-880c7b08989c">— Невозможно? Пари.</p><p rend="left" id="e8de4dce-c68d-4c1e-8446-959b603c5793">— Идет. Если вы ночуете у него, то я что хотите.</p><p rend="left" id="33a99187-69d8-4771-9fe1-0b3ed2ef3c48">— A discrétion.<note n="n26"><div type="section" xml:id="n26"><head><ref target="#backn26">26</ref></head><p rend="left" id="1b300392-0eb7-4515-9cb6-29ae161c86d7">'
    s = '<p class="center">[<em>а) Редакция первая.</em>]</p>'
    s = '<p rend="center" id="8c414608-b438-47da-9283-069418e3add0">[Глава XXV,<hi rend="Razradka"> без всякого отделения от XXIV.]</hi></p>'
    s = '<h4 class="center">[II.]</h4>'
    s = '[Составлено H. Н. Гусевым.<br />Под редакцией Л. Н. Толстого.]'

    print('DEBUG')
    # print(sp_ut.replace_html_markup_with_xml(s))
    s1 = sp_ut.replace_html_markup_with_xml(s)
    print(s1)
    print()
    s2 = sp_ut.markup_choices_for_editorial_corrections(s1)
    print(s2)
    print()
    s3 = sp_ut.markup_choices_for_prereform_spelling(s2)
    # s3 = sp_ut.insert_date_tag_for_43_and_44_vol(s)
    print(s3)
    # print(s2 == s3)
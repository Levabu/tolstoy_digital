from lxml import etree

import split_volumes_utils as sp_ut
import utils as ut


header = """<teiHeader>
    <fileDesc>
      <titleStmt>
        <title>
     {title}
    </title>
        <author>
     Толстой Л.Н.
    </author>
        <respStmt>
          <resp>
      подготовка TEI/XML
     </resp>
          <name>
      Мария Картышева, Евгений Можаев, Даниил Скоринкин, Елена Сидорова, Вероника Файнберг, Кирилл Милинцевич
     </name>
        </respStmt>
        <respStmt>
          <name>
      Анастасия Бонч-Осмоловская, Фёкла Толстая, Борис Орехов
     </name>
          <resp>
      Идея, постановка задач, руководство
     </resp>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <idno>
    </idno>
        <publisher>
          <orgName>
      Школа лингвистики НИУ ВШЭ
     </orgName>
        </publisher>
        <availability>
          <p>
      Тексты и метатекстовая разметка доступны для свободного использования и распространения по лицензии Creative Commons Attribution Share-Alike (cc by-sa)
     </p>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <biblStruct>
          <analytic>
            <author>
       Толстой Л.Н.
      </author>
            <title level="a">
       {title}
      </title>
          </analytic>
          <monogr>
            <title level="m">
       Полное собрание сочинений. Том {volume_number}
      </title>
            <imprint>
              <pubPlace>
        Москва
       </pubPlace>
              <publisher>
        Государственное издательство "Художественная литература"
       </publisher>
              <date when="fill date later"/>
            </imprint>
          </monogr>
          <series>
            <title level="s">
       Л.Н. Толстой. Полное собрание сочинений
      </title>
            <biblScope unit="vol">
       {volume_number}
      </biblScope>
          </series>
        </biblStruct>
      </sourceDesc>
    </fileDesc>
    <encodingDesc>
      <classDecl>
        <xi:include href="taxonomy.xml"/>
      </classDecl>
    </encodingDesc>
    <profileDesc>
      <creation>
        <date notAfter="fill date_not_after later" notBefore="fill date_not_before later">
     fill date later
    </date>
        <rs/>
      </creation>
      <textClass>
   </textClass>
      <preparedness>
   </preparedness>
      <settingDesc>
        <time>
     XIX
    </time>
      </settingDesc>
    </profileDesc>
    <xenoData>
      <cyclusName/>
      <p>
    Проект
    <title>
     Толстой.Digital
    </title>
    разрабатывается сотрудниками и студентами
    <orgName>
     Высшей школы экономики
    </orgName>
    в сотрудничестве с
    <orgName>
     Государственным музеем Л.Н. Толстого
    </orgName>
    . Источник текстов –
    <bibl>
     90-томное собрание сочинений Л.Н.Толстого
    </bibl>
    . Разметка основана на стандарте
    <ref target="http://www.tei-c.org">
     TEI (Text Encoding Initiative)
    </ref>
    .
   </p>
      <versionNumber/>
      <isFinished/>
      <isEdited/>
      <fullBibliographicDescription/>
    </xenoData>
  </teiHeader>"""


def split_xml(filename, destination_folder):
    xml = ut.read_xml(
        filename, 'rb'
    )
    volume_number = filename.strip('.xml').split()[-1]
    correct_filenames = sp_ut.correct_filenames('reference/correct_filenames.csv')
    # namespace = 'http://www.w3.org/XML/1998/namespace'  # If you need id
    root = etree.fromstring(xml)
    all_divs = root.xpath(f'//ns:div', namespaces={'ns': f'{ut.xmlns_namespace}'})
    daily_divs = [div for div in all_divs if div.get('type') is not None and div.get('type') == 'daily']
    weekly_divs = [div for div in all_divs if div.get('type') is not None and div.get('type') == 'weekly section']
    items = []
    for div in daily_divs:
        div_type = div.get('type')  # Redundant
        # div.set('type', 'section')
        date = div[0].get('when')
        div.set('when', date)  # Вставляю дату в качестве атрибута дива
        div.remove(div[0])
        title = f'Круг чтения. {date.strip("-")}'
        text = etree.tostring(div, encoding='unicode')
        items.append((div_type, date, title, text))
    for div in weekly_divs:
        div_type = div.get('type').split()[0]  # Redundant
        div.set('type', div_type)
        date = div.getparent()[0].get('when')
        div.set('when', date)
        title = 'Круг чтения. ' + ''.join([i for i in div[0].itertext()]).split('\n')[0].casefold()
        text = etree.tostring(div, encoding='unicode')
        items.append((div_type, date, title, text))

    names = []
    for div_type, date, title, text in items:
        data = {'title': title, 'volume_number': volume_number}
        tei_header = header.format(**data)
        new_filename = f'{title} {volume_number}.xml'
        if new_filename in correct_filenames:
            new_filename = correct_filenames[new_filename]
            new_filename = new_filename.replace('Круг чтения. ', f'Круг чтения. {date.strip("-")} ')
        with open(f'{destination_folder}/{new_filename}', 'w') as file:
            file.write('<TEI xmlns="http://www.tei-c.org/ns/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">\n')
            file.write(tei_header)
            file.write('\n<text>\n')
            file.write(text)
            file.write('</text>\n</TEI>')

        # if div_type != 'daily':
        #     print(new_filename.split('/')[-1])

        # print(new_filename.split('/')[-1])

        # Print sorted
        names.append(new_filename.split('/')[-1])
    names.sort(key=lambda x: [int(i) for i in x.split()[2].split('-')])
    for name in names:
        print(name)


def main():
    ut.change_to_project_directory()
    xml1 = 'parse_volume/result/Круг чтения. Том первый 41.xml'
    xml2 = 'parse_volume/result/Круг чтения. Том второй 42.xml'
    split_xml(xml1, destination_folder='parse_volume/result')
    split_xml(xml2, destination_folder='parse_volume/result')


if __name__ == '__main__':
    main()
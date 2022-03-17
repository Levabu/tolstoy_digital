import csv

from transliterate import translit

import utils as ut


def main():
    with open('reference/for_transliteration.csv') as file:
        reader = csv.reader(file)
        with open('reference/transliterated.csv', 'w') as new_file:
            writer = csv.writer(new_file)
            for line in reader:
                text_id = line[0]
                if text_id == 'N':
                    continue
                start_page, end_page = int(line[5]), int(line[6])
                # volume = int(line[1])
                filename = line[3]
                # if filename[-6:] in ['21.xml', '22.xml', '#N/A', '41.xml', '42.xml']:
                if filename[-6:] in ['21.xml', '22.xml', '#N/A', ]:
                    # print(True)
                    continue
                volume = int(ut.extract_volume_number(filename))
                just_name = filename.rsplit(maxsplit=1)[0]
                just_name = just_name.replace(' . ', '. ')
                just_name = just_name.replace('[', '')
                just_name = just_name.replace(']', '')
                just_name.rstrip('.')
                # if just_name[0] == '[' and just_name[-1] == ']':
                #     just_name = just_name.strip('[]')
                transliterated_name = f'{translit(just_name, "ru", reversed=True)}'
                fin_name = '{:02d}_{:03d}-{:03d}_{}'.format(volume, start_page, end_page, transliterated_name)
                # print(text_id, filename, fin_name)
                print(text_id, '|', fin_name, sep='')
                # if text_id == '869':
                if text_id == '1302':
                # if filename == 'Круг чтения. 12-31 42.xml':
                    break
    pass


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
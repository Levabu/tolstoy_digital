import csv
import re
from string import ascii_letters

import pandas as pd
from transliterate import translit

import utils as ut


def make_id_from_title(title):
    title_id = translit(title, "ru", reversed=True)
    title_id = re.sub('(é|è)', 'e', title_id)
    title_id.replace('\n', ' ')
    title_id = re.sub(r'(\s|-|–|—)', ' ', title_id)
    # title_id = title_id.replace('№', 'No')
    title_id = re.sub('№\s?', 'No ', title_id)
    # for char in title_id:
    #     if not char.isalnum():
    #         print(char)
    title_id = ''.join([c for c in title_id if c.isalnum() or c == ' '])
    title_id = '_'.join(title_id.split())
    return title_id


def main():
    path_to_csv = 'reference/ST_91_titles.csv'
    path_to_xlsx = 'reference/st_91_titles.xlsx'
    non_ascii = set()
    with open(path_to_csv) as file:
        # reader = csv.reader(file)
        # sheet = [line for line in reader]
        df = pd.read_excel(path_to_xlsx)
        print(df.columns)
        # titles = [l[5] for l in sheet][1:]
        # print(len(titles), len(set(titles)))
        print('____________')
        # for line in sheet:
        #     if titles.count(line[5]) > 1:
        #         print(line[8], line[5], sep=' ')
        #     pass
        print('____________')
        # for title in titles:
        # for line in sheet:
        for i, line in df.iterrows():
            # print(line)
            title = line[5]
            title_id = make_id_from_title(title)
            print(int(line[8]), title.replace('\n', ' '), title_id, sep='|')
            # if '\n' in title_id:
            #     exit()
            for char in title_id:
                if char not in non_ascii and char not in ascii_letters:
                    non_ascii.add(char)
        # print(ascii_letters)
        # print(non_ascii)


if __name__ == '__main__':
    ut.change_to_project_directory()
    # main()
    with open('reference/temp.csv', 'r') as file:
        reader = list(csv.reader(file))
        # titles = [line[0].strip('\n') for line in reader]
        # filenames = [line[1].strip('\n') for line in reader]
        for line in reader:
    # non_ascii = set()
    # for title in titles:
            title_id = make_id_from_title(line[0])
            print(line[1], title_id, sep='|')
        # for char in title_id:
        #     if char not in non_ascii and char not in ascii_letters:
        #         non_ascii.add(char)
    # print(non_ascii)
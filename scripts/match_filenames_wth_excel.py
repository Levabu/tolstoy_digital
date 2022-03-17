import csv
import os
from pprint import pprint

from fuzzywuzzy import fuzz

import utils as ut


def similarity(s1, s2) -> float:
    low_s1, low_s2 = s1.casefold(), s2.casefold()
    ratio = fuzz.ratio(low_s1, low_s2)
    partial_ratio = fuzz.partial_ratio(low_s1, low_s2)
    token_sort_ratio = fuzz.token_sort_ratio(low_s1, low_s2)
    token_set_ratio = fuzz.token_set_ratio(low_s1, low_s2)
    average_similarity = (ratio + partial_ratio + token_sort_ratio + token_set_ratio) / 4
    # print(average_similarity)
    return average_similarity


def get_data_rows_from_csv(csv_source) -> dict:
    with open(csv_source) as file:
        reader = csv.reader(file)
        return {int(row[0]): row for row in reader if row[0] and row[0] != 'N'}


def divide_rows_into_volume_groups(rows: dict) -> dict:
    groups = {}
    for row in rows:
        try:
            volume = int(rows[row][1])
        except ValueError:
            # volume = 'no_volume'
            volume = int(rows[row-1][1])
            rows[row][1] = volume
        if volume not in groups:
            groups[volume] = {row: rows[row]}
        else:
            groups[volume].update({row: rows[row]})
        # print(row, rows[row][1])
    # pprint(groups)
    return groups


def get_filenames(folder) -> list:
    filenames = []
    for file in os.listdir(folder):
        if file[-3:] == 'xml':
            filenames.append(file)
    return filenames


def divide_filenames_into_volume_groups(filenames) -> dict:
    groups = {}
    for filename in filenames:
        print(filename)
        volume = int(ut.extract_volume_number(filename))
        if volume not in groups:
            groups[volume] = [filename]
        else:
            groups[volume].append(filename)
    return groups


def match_filenames_and_rows(filenames_groups, rows_groups):
    extra_text_ids = []
    extra_files = []
    ok_names = []
    for volume, rows_group in rows_groups.items():
        # if volume == 'no_volume':
        #     continue
        filenames = filenames_groups[volume]
        for row in rows_group.values():
            text_id = row[0]
            kinda_row_name = f'{row[23].strip()}. {row[25]}'
            try:
                matched_filename = sorted(filenames, key=lambda x: similarity(x, kinda_row_name))[-1]
            except IndexError:
                extra_text_ids.append(text_id)
                continue
            filenames.remove(matched_filename)
            if similarity(matched_filename, kinda_row_name) < 50:
                extra_files.append(matched_filename)
                continue
            ok_names.append((text_id, matched_filename))
            # print(volume, text_id, kinda_row_name, matched_filename, similarity(kinda_row_name, matched_filename), sep='|')
        else:
            if filenames:
                extra_files.extend(filenames)
    return ok_names, extra_files

    pass


def main():
    ut.change_to_project_directory()
    path_to_files = '../../work/tolstoy_digital/new_and_newly_parsed/new_2.0/fiction_mixed'
    filenames = get_filenames(path_to_files)
    filenames_groups = divide_filenames_into_volume_groups(filenames)
    rows = get_data_rows_from_csv('reference/NEW of Metadata Tolstoy 2018 (Ника)  - Works.csv')
    rows_groups = divide_rows_into_volume_groups(rows)
    id_filename_match, extra_files = match_filenames_and_rows(filenames_groups, rows_groups)
    # pprint(id_filename_match)
    # pprint(extra_files)
    with open('reference/filenames_match.csv', 'w') as file:
        writer = csv.writer(file)
        for text_id, filename in id_filename_match:
            try:
                pages, data = ut.get_pages_using_lxml(os.path.join(path_to_files, filename))
            except Exception as e:
                pages, data = ut.get_pages_using_re(os.path.join(path_to_files, filename))
            fragments = ut.separate_into_consistent_fragments(pages)
            writer.writerow([text_id, ut.extract_volume_number(filename), filename, fragments])
            # print([text_id, ut.extract_volume_number(filename), filename, fragments])
        for filename in extra_files:
            try:
                pages, data = ut.get_pages_using_lxml(os.path.join(path_to_files, filename))
            except Exception as e:
                pages, data = ut.get_pages_using_re(os.path.join(path_to_files, filename))
            fragments = ut.separate_into_consistent_fragments(pages)
            writer.writerow([0, ut.extract_volume_number(filename), filename, fragments])
            # print([0, 0, ut.extract_volume_number(filename), filename, fragments])


if __name__ == '__main__':
    main()

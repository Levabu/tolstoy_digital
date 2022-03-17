import csv
import os
import re
from pprint import pprint

from tqdm import tqdm

import utils as ut


def main() -> None:
    all_counter = 0
    empty_pages = 0
    ok_counter = 0
    inconsistent_counter = 0
    error_counter = 0
    all_to_csv = []
    ok_to_csv = []
    empty_to_csv = []
    inconsistent_to_csv = []
    error_to_csv = []
    # used_tags = []
    for path in ut.paths:
    # for path in ut.old_paths:
        for file in tqdm(os.listdir(path)):
            all_counter += 1
            volume = ut.extract_volume_number(file)
            status = 'consistent'
            try:
                pages, data = ut.get_pages_using_lxml(os.path.join(path, file))
            except Exception as e:
                pages, data = ut.get_pages_using_re(os.path.join(path, file))
                data = {'error': e}
                error_counter += 1
                fragments = ut.separate_into_consistent_fragments(pages)
                gaps = ut.extract_gaps_from_fragments(fragments)
                error_to_csv.append((
                    volume,
                    file,
                    e,
                    str(fragments).strip('[]'),
                    gaps
                ))
                print(file, e)
                # print(file, ut.separate_into_consistent_fragments(pages))
            if pages:
                should_be = ut.should_be_pages(pages)
                fragments = ut.separate_into_consistent_fragments(pages)
                tag_types = data.get('tag_types')
                tags_to_write = str(
                    ([ut.real_tags[t] for t in tag_types]
                     if tag_types is not None else [])
                ).strip('[]')
                if ut.is_consistent_pagination(file, pages, should_be):
                    ok_counter += 1
                    ok_to_csv.append((
                        volume,
                        file,
                        tags_to_write,
                        str(fragments).strip('[]'),
                    ))
                else:
                    inconsistent_counter += 1
                    gaps = ut.extract_gaps_from_fragments(fragments)
                    status = 'inconsistent'
                    inconsistent_to_csv.append((
                        volume,
                        file,
                        tags_to_write,
                        str(fragments).strip('[]'),
                        gaps
                    ))
            else:
                empty_pages += 1
                status = 'empty'
                empty_to_csv.append((volume, file))
                fragments = []
            status = f'error, ?{status}?' if data.get('error') is not None else status
            # all_to_csv.append((volume, file, status))
            all_to_csv.append((volume, file, status, fragments))

    print(all_counter, ok_counter, inconsistent_counter, empty_pages, error_counter)
    # breakpoint()
    # pprint(inconsistent_to_csv)

    # print(used_tags)

    # ut.write_to_csv(inconsistent_to_csv, 'test_inconsistent_pages')
    # ut.write_to_csv(empty_to_csv, 'new_empty_pages')
    ut.write_to_csv(all_to_csv, 'new_all_files')
    # ut.write_to_csv(ok_to_csv, 'new_consistent_pages')
    # ut.write_to_csv(error_to_csv, 'new_error_pages')
    pass


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
    # print(ut.get_pages_using_lxml('test_file.xml'))
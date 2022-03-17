import os
import re

import tqdm

import utils as ut


def main():
    illegible_pattern = re.compile(  # решить, что с этим делать
        r'(\[\d+.*?не\s*разобр.*?](?!">))|'  # [2 неразобр.]
        r'(\w+\[\w+\?](?!">))|'  # вл[иянием?]
        r'(\[\?](?!">))|'  # [?]
        r'(\[(<[^>]*?>)?(з|З)ач(е|ё)ркнуто:(<[^>]*?>)?(?!">))'
    )
    illegible_pattern_inside_tags = re.compile(
        r'("\[\d+.*?не\s*разобр.*?]")|'  
        r'("\w+\[\w+\?]")|'  
        r'("\[\?]")|'  # [?]
        r'("\[(<[^>]*?>)?(з|З)ач(е|ё)ркнуто:(<[^>]*?>)?")|'
        # r'("(<head.*?>[*, ]*)?(\s*(\w*?(\[(.*?)])\w*)\s*)(?!\">)(</head>)?")' # normal, for debug
    )
    # crossed_out_pattern = re.compile(
    #     # r'(<.*?>)?(з|З)ач(е|ё)ркнуто:(<.*?>)?'
    #     r'(<[^>]*?>)?(з|З)ач(е|ё)ркнуто:(<[^>]*?>)?'
    # )
    counter = 0
    for path in ut.paths:
        for file in tqdm.tqdm(os.listdir(path)):
        # for file in os.listdir(path):
            text = ut.read_xml(os.path.join(path, file))
            # matchobj = illegible_pattern.search(text)
            matchobj = illegible_pattern_inside_tags.search(text)
            if matchobj and matchobj.group(0) != '':
                print(file)
            # for match in illegible_pattern.finditer(text):
            for match in illegible_pattern_inside_tags.finditer(text):
                result = match.group(0)
                if result != '':
                    print(result)
                    counter += 1
            if matchobj and matchobj.group(0) != '':
                print()
    print(counter)

    pass


if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
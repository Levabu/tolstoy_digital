import utils as ut


def main():
    with open('reference/filenames_from_sheet.txt') as file:
        filenames = [l.strip('\n') for l in file.readlines()]
    with open('reference/pages_after_remove_last_tag.txt') as file:
        lines = [l.strip('\n') for l in file.readlines()]
    new_lines = []
    for line in lines:
        filename = line.split('|')[0]
        # print(filename)
        pages = line.split('|')[1].strip('[]()').split(', ')
        # if len(pages) > 2 and filename in filenames:
        # if len(pages) > 2 and filename in filenames:
        #     print(line)
        start_page = pages[0]
        end_page = pages[-1]
        new_lines.append(f'{line}|{start_page}|{end_page}')
    # print(new_lines)
    with open('reference/filenames_with_edge_pages', 'w') as file:
        for line in new_lines:
            file.write(f'{line}\n')

if __name__ == '__main__':
    ut.change_to_project_directory()
    main()
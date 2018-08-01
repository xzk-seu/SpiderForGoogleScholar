import openpyxl
import os
import scholarly
import Google_complement as gc
from multiprocessing import Process

excel_file = os.path.join(os.getcwd(), 'result.xlsx')

ed = {
    'expert': 'A',
    'affiliation': 'B',
    'interests': 'C',
    'email': 'D',
    'phone': 'E',
    'address': 'F',
    'country': 'G',
    'language': 'H',
    'position': 'I',
    'name': 'J',
    'citedby': 'K',
    'hindex': 'L',
    'hindex5y': 'M',
    'i10index': 'N',
    'i10index5y': 'O',
    'url_picture': 'P',
}


def spider(workbook, line_begin, line_end):
    print(line_begin, line_end)
    sheet = workbook.active
    for i in range(line_begin, line_end + 1):
        i_str = str(i)
        # 获得已有信息
        expert = sheet[ed['expert'] + i_str].value
        affiliation = sheet[ed['affiliation'] + i_str].value if sheet[ed['affiliation'] + str(i)].value is not None else ''
        print('----------------------------------')
        print('|', expert, '|', affiliation, '|')

        # 第一步 在谷歌学术中获得相关信息 --------------------------------

        authors = {a.fill() for a in scholarly.search_author(expert)}
        shooted_words = {'blockchain', 'Blockchain'}
        stauthor = None
        for a in authors:
            if len(shooted_words.intersection(a.interests)) > 0:
                stauthor = a
                break

        if stauthor is not None:
            sheet[ed['affiliation'] + i_str] = affiliation = stauthor.affiliation if stauthor.affiliation else affiliation
            sheet[ed['name'] + i_str] = expert = stauthor.name

            try:
                sheet[ed['citedby'] + i_str] = stauthor.citedby
            except KeyError:
                pass

            try:
                sheet[ed['hindex'] + i_str] = stauthor.hindex
                sheet[ed['hindex5y'] + i_str] = stauthor.hindex5y
                sheet[ed['i10index'] + i_str] = stauthor.i10index
                sheet[ed['i10index5y'] + i_str] = stauthor.i10index5y
            except KeyError:
                pass

            try:
                sheet[ed['url_picture'] + i_str] = stauthor.url_picture
            except KeyError:
                pass

        keywords = expert + ' ' + affiliation
        sheet[ed['email'] + i_str] = gc.get_email(keywords)
        sheet[ed['phone'] + i_str] = gc.get_phone(keywords)
        sheet[ed['address'] + i_str] = gc.get_address(affiliation)
        sheet[ed['country'] + i_str] = gc.get_country(affiliation)
        workbook.save(excel_file)


if __name__ == "__main__":
    counts = 5663
    num_of_process = 6
    quarter = int(counts / num_of_process)

    wb = openpyxl.load_workbook(excel_file)

    arg_list = [
        (wb, 2, quarter),
        (wb, quarter + 1, 2 * quarter),
        (wb, 2 * quarter + 1, 3 * quarter),
        (wb, 3 * quarter + 1, 4 * quarter),
        (wb, 4 * quarter + 1, 5 * quarter),
        (wb, 5 * quarter + 1, counts),
    ]

    for i in range(1, num_of_process + 1):
        p = Process(target=spider, args=arg_list[i-1])
        p.start()


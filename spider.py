import openpyxl
import os
import scholarly
import Google_complement as gc
from multiprocessing import Process
from DBUtils import PooledDB
import pymysql
import time

# connect to mysql
db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '0410',
            'db': 'author',
            'charset': 'utf8'
            }
pool_db = PooledDB.PooledDB(pymysql, mincached=2, maxcached=6, blocking=True, **db_config)


def db_execute(cursor, sql, values):
    cursor.execute(sql, values)
    # try:
    #     cursor.execute(sql, values)
    # except pymysql.err.IntegrityError:
    #     pass
    # except pymysql.err.DataError:
    #     pass
    # except pymysql.err.InternalError:
    #     pass


def db_executemany(cursor, sql, values):
    try:
        cursor.executemany(sql, values)
    except pymysql.err.IntegrityError:
        pass
    except pymysql.err.DataError:
        pass
    except pymysql.err.InternalError:
        pass


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


def spider(sheet, line_begin, line_end):
    print(line_begin, line_end)

    # 获得数据库连接
    conn_db = pool_db.connection()
    cursor = conn_db.cursor()

    for index in range(line_begin, line_end + 1):
        i_str = str(index)
        # 获得已有信息
        expert = sheet[ed['expert'] + i_str].value
        affiliation = sheet[ed['affiliation'] + i_str].value \
            if sheet[ed['affiliation'] + i_str].value is not None else ''
        interests = sheet[ed['interests'] + i_str].value \
            if sheet[ed['interests'] + i_str].value is not None else ''

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

        name = str()
        citedby = -1
        hindex = -1
        hindex5y = -1
        i10index = -1
        i10index5y = -1
        url_picture = str()

        if stauthor is not None:
            affiliation = stauthor.affiliation if stauthor.affiliation else affiliation
            name = stauthor.name

            try:
                citedby = stauthor.citedby
            except KeyError:
                pass

            try:
                sheet[ed['hindex'] + i_str] = stauthor.hindex
                sheet[ed['hindex5y'] + i_str] = stauthor.hindex5y
                sheet[ed['i10index'] + i_str] = stauthor.i10index
                sheet[ed['i10index5y'] + i_str] = stauthor.i10index5y
                hindex = stauthor.hindex
                hindex5y = stauthor.hindex5y
                i10index = stauthor.i10index
                i10index5y = stauthor.i10index5y
            except KeyError:
                pass

            try:
                url_picture = stauthor.url_picture
            except KeyError:
                pass

        keywords = expert + ' ' + affiliation
        email = gc.get_email(keywords)
        phone = gc.get_phone(keywords)
        addresss = gc.get_address(affiliation)
        country = gc.get_country(affiliation)
        language = gc.get_language(country)
        position = gc.get_position(keywords)

        sql_step_1 = ('''insert ignore into `info` (`id`, `expert`, `affiliation`, `interests`, `email`, `phone`, 
        `address`, `country`, `language`, `position`, `name`, `citedby`, `hindex`, `hindex5y`, `i10index`, `i10index5y`,
        `url_picture`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''')

        db_execute(cursor, sql_step_1, (i_str, expert, affiliation, interests, email, phone, addresss,
                                        country, language, position, name, citedby, hindex, hindex5y, i10index, i10index5y, url_picture))
        conn_db.commit()

        # sheet[ed['email'] + i_str] = email
        # sheet[ed['phone'] + i_str] = phone
        # sheet[ed['address'] + i_str] = addresss
        # sheet[ed['country'] + i_str] = country
        # print(expert, email, phone, addresss, country)
    cursor.close()
    conn_db.commit()
    conn_db.close()


if __name__ == "__main__":
    # counts = 5663
    counts = 400
    num_of_process = 6
    quarter = counts // num_of_process
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active

    begin_num = 0

    arg_list = [
        (sheet, 25, quarter),
        (sheet, quarter + 1, 2 * quarter),
        (sheet, 2 * quarter + 1, 3 * quarter),
        (sheet, 3 * quarter + 1, 4 * quarter),
        (sheet, 4 * quarter + 1, 5 * quarter),
        (sheet, 5 * quarter + 1, counts),
    ]

    for i in range(1, num_of_process + 1):
        p = Process(target=spider, args=arg_list[i-1])
        p.start()

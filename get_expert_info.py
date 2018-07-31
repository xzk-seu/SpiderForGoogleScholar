import os
import csv
import scholarly


output_file = os.path.join(os.getcwd(), 'result_blockchain.csv')
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['expert', 'affiliation', 'interests', 'email', 'phone', 'address',
                     'country', 'language', 'position', 'name', 'citedby', 'hindex', 'hindex5y',
                     'i10index', 'i10index5y', 'url_picture'])


keywords = {'blockchain', 'Blockchain'}

input_file = os.path.join(os.getcwd(), 'blockchain_expert.csv')
dict_input = {
    'name': 0,
    'affiliation': 1,
    'interests': 2,
}
with open(input_file, 'r', encoding='ISO-8859-1') as f:
    reader = csv.reader(f)
    # 跳过首行
    next(reader)

    for r in reader:
        name = r[dict_input['name']].strip()

        # 找到所有同名作者
        authors = {a.fill() for a in scholarly.search_author(name)}
        print(name)
        print('Author name', name, 'has', len(authors), 'candidate(s)')

        # 由研究兴趣确定目标学者
        author_shoot = None
        for author in authors:
            if len(keywords.intersection(author.interests)) > 0:
                author_shoot = author
                break

        # 没有找到相关学者，切换到下一个名字
        if author_shoot is None:
            print(name, "no shoot.")
            print("-----------------------------------")
            with open(output_file, 'a', encoding='utf-8', newline='') as f1:
                writer = csv.writer(f1)
                writer.writerow([name, r[dict_input['affiliation']], r[dict_input['interests']], '', '', '',
                                 '', '', '', ''])
            continue
        # 找到目标学者，进行下一步操作
        else:
            print("Shoot author:", author_shoot)
            print("-----------------------------------")

            strInterests = ', '.join(author_shoot.interests)

            with open(output_file, 'a', encoding='utf-8', newline='') as f1:
                writer = csv.writer(f1)
                writer.writerow([name, author_shoot.affiliation, strInterests, author_shoot.email, '', '',
                                 '', '', '', author_shoot.name, author_shoot.citedby, author_shoot.hindex,
                                 author_shoot.hindex5y, author_shoot.i10index, author_shoot.i10index5y,
                                 author_shoot.url_picture])


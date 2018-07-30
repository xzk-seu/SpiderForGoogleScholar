import scholarly
import requests
from PIL import Image
import io
import csv
import os

# write the file head
strFileName = "./export_expert_info.csv"
file = open(strFileName, 'w')
valueStr = "\"expert\",\"citedby\",\"hindex\",\"hindex5y\",\"i10index\",\"i10index5y\",\"name\",\"affiliation\",\"interests\",\"email\"\n"
file.write(valueStr)
file.close()

keywords = ["blockchain", "Blockchain"]

# input the expert name list
filename = os.path.join(os.getcwd(), 'blockchain_expert.csv')
with open(filename, "r", encoding='ISO-8859-1') as f:
    reader = list(csv.reader(f))

names = [n[0].strip() for n in reader][1:]

for name in names:
    # get info from google
    authors = scholarly.search_author(name)
    jsonAuthors = [a.fill() for a in authors]

    strInterest = ""
    Author = None
    for author in jsonAuthors:
        # 研究兴趣
        interestsCount = len(author.interests)
        strInterest = ""
        index = 0
        while index < interestsCount and Author is None:
            interest = author.interests[index]
            if interest in keywords:
                Author = author
            strInterest += "%s" % interest
            if index < interestsCount - 1:
                strInterest += "|"
            index += 1
        print(Author, strInterest)

    if Author is None:
        continue

    print("search the expert: " + name)
    # 输出到文件
    strFileName = "./export_expert_info.csv"
    file = open(strFileName, 'a')
    valueStr = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % (name, Author.citedby, Author.hindex, Author.hindex5y, Author.i10index, Author.i10index5y, Author.name, Author.affiliation,strInterest, Author.email)
    file.write(valueStr)
    file.close()

    iurl = 'https://scholar.google.com/citations?view_op=medium_photo&user=%s' % Author.id
    print(iurl)
    # get the expert' photo
    try:
        req = requests.get(iurl)
        data = req.content
        tmpIm = io.StringIO(data)
        im = Image.open(tmpIm)

        tm = './image/%s.%s' % (name, im.format.lower())
        with open(tm, 'wb') as fp:
            fp.write(data)
    except requests.ConnectionError as e:
        print(e)

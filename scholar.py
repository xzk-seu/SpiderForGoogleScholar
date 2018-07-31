import scholarly
import json

column = ('name',
          'affiliation',
          'citedby',
          'email',
          'phone',
          'address',
          'country',
          'position',
          'language',
          'interessts',
          'googleid',
          'url_picture')

# 返回一个生成器对象
authors = scholarly.search_author("a goriacheva,national research nuclear university mephi")

author_list = [str(a) for a in authors]
print(len(author_list))

for author in author_list:
    print(author)
    au = json.loads(author)
    print(au['name'])




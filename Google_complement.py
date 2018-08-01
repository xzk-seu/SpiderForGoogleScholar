import requests
from bs4 import BeautifulSoup
import re

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-us;q=0.5,en;q=0.3',
    'connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
}

url = 'https://www.google.com/search'
proxies = {"http": "127.0.0.1:1080", "https": "127.0.0.1:1080"}


def get_html(payloads):
    html = requests.get(
        url,
        params=payloads,
        headers=headers,
        proxies=proxies,
    )
    html.encoding = "utf-8"
    return html.text


def get_email(key_words):
    payloads = {
        "q": key_words + ' email',
    }

    soup = BeautifulSoup(get_html(payloads=payloads), 'lxml')
    tag_results = soup.select("span[class='st']")
    results = {str(tr).replace("<em>", '').replace(r"</em>", '') for tr in tag_results}
    emailRegex = re.compile(r"""([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))""", re.VERBOSE)
    emailFilterRegex = re.compile(r"""^[Ee]-?mail""")

    email = str()
    for r in results:
        ems = [emailFilterRegex.sub('', e).strip() for a in emailRegex.findall(r) for e in a]
        for e in ems:
            email = e if len(e) > len(email) else email

    return email


def get_phone(key_words):
    payloads = {
        "q": key_words + ' phone',
    }

    soup = BeautifulSoup(get_html(payloads=payloads), 'lxml')
    tag_results = soup.select("span[class='st']")
    results = {str(tr)
               .replace(r"<em>", '')
               .replace(r"</em>", '')
               .replace(r"<wbr>", '')
               .replace(r"</wbr>", '') for tr in tag_results}

    phoneRegex = re.compile(r"""[Pp]hone[,:]?\s*(\+\s?[\d]+\s?)?(\([\d\-. ]+\)\s{0,2})*(\d+[/.-]?\s?)*""", re.VERBOSE)
    phoneFilterRegex = re.compile(r"""[Pp]hone[,:]?\s*""")

    phone = str()
    # 每一条摘要
    for r in results:
        pho = phoneRegex.search(r)
        pho_no = phoneFilterRegex.sub('', pho.group()).strip() if pho is not None else ''
        # print(r, pho_no)

        phone = pho_no if len(pho_no) > len(phone) else phone
    return phone if len(phone) > 4 else ''


def get_address(affiliation):
    payloads = {
        "q": 'where is ' + affiliation.split(';')[0] + '?',
    }
    soup = BeautifulSoup(get_html(payloads=payloads), 'lxml')
    tag_results = soup.select("div[class='Z0LcW']")
    address = tag_results[0].getText() if len(tag_results) > 0 else ''
    return address


def get_country(affiliation):
    payloads = {
        "q": 'what country is ' + affiliation.split(';')[0] + ' in?',
    }
    soup = BeautifulSoup(get_html(payloads=payloads), 'lxml')
    tag_results = soup.select("div[class='Z0LcW']")
    country = tag_results[0].getText() if len(tag_results) > 0 else ''
    return country


def get_language(country):
    payloads = {
        "q": 'what language do they speak in ' + country + '?',
    }
    soup = BeautifulSoup(get_html(payloads=payloads), 'lxml')
    tag_results = soup.select("div[class='Z0LcW']")
    language = tag_results[0].getText() if len(tag_results) > 0 else ''
    return language


def get_position(key_words):
    payloads = {
        "q": key_words + ' professor or researcher or scientist',
    }

    soup = BeautifulSoup(get_html(payloads=payloads), 'lxml')
    tag_results = soup.select("span[class='st']")
    results = {str(tr)
               .replace(r"<em>", '')
               .replace(r"</em>", '')
               .replace(r"<wbr>", '')
               .replace(r"</wbr>", '') for tr in tag_results}

    associateProfessorRegex = re.compile('''[Aa]ssociate\s+[Pp]rofessor''')
    assistantProfessorRegex = re.compile('''[Aa]ssistant\s+[Pp]rofessor''')
    professorRegex = re.compile('''[Pp]rofessor''')
    researcherRegex = re.compile('''[Rr]esearcher''')
    scientistRegex = re.compile('''[Ss]cientist''')

    # position需要设置优先级
    for r in results:
        if associateProfessorRegex.search(r):
            return 'Associate Professor'

        if assistantProfessorRegex.search(r):
            return 'Assistant Professor'

        if professorRegex.search(r):
            return "Professor"

        if researcherRegex.search(r):
            return 'Researcher'

        if scientistRegex.search(r):
            return 'Scientist'

    return ' '


if __name__ == "__main__":
    get_country('Northy')

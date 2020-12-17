#   Assignment 8 - Finding Word Root (1)
#   
#   Date:           2020/12/03
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
from   bs4 import BeautifulSoup as BS
import json
import requests


class CONST:
    root_url = lambda : 'https://www.etymonline.com'


def queryPage(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        return BS(response.text, "html.parser")
    else:
        print('Failed', response.status_code)
        return None


def findURL(bs4_html):
    first_url = bs4_html.find_all(class_='word__name--TTbAA word_thumbnail__name--1khEg')[0]
    first_url = first_url.get('href')
    return CONST.root_url() + first_url


def findTitle(url):
    bs4_html = queryPage(url)
    first_title = bs4_html.find_all(class_='word__name--TTbAA')[0]
    first_title = first_title.text
    return first_title


def findForeign(url):
    bs4_html = queryPage(url)
    foreign_list = bs4_html.find_all(class_='foreign notranslate')
    foreign_list = [each.text for each in foreign_list]
    return foreign_list


def findRef(url):
    bs4_html = queryPage(url)
    ref_list = bs4_html.find_all(class_="crossreference notranslate")
    ref_list = [each.text for each in ref_list]
    return ref_list


def findText(url):
    bs4_html = queryPage(url)
    text_list = bs4_html.find_all(class_="word__defination--2q7ZH")
    
    whole_text = ''
    for each in text_list:
        whole_text += each.text
    
    return whole_text


if __name__ == '__main__':
    word_list = ['adventure', 'education', 'predict', 'international', 'scholarship']
    
    word_attr = {}
    for word in word_list:
        bs4_html  = queryPage(CONST.root_url() + '/search?q=' + word)
        word_url  = findURL(bs4_html)
        word_attr = {'word':       word,
                     'url':        word_url,
                     'title':      findTitle(word_url),
                     'foreigns':   findForeign(word_url),
                     'references': findRef(word_url),
                     'text':       findText(word_url)}    
        print(json.dumps(word_attr, indent=4))
        print()

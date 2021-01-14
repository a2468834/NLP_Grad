from   bs4 import BeautifulSoup as BS
from   collections import Counter
from   itertools import combinations_with_replacement
import json
import math
import nltk
from   os import path, system
import pickle
import random
import re
import requests
import sys
import threading
import time
import string


def httpGET(url):
    headers  = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return BS(response.text, 'html.parser')
    else:
        print(url)
        print('Failed HTTP GET with error code: {}'.format(response.status_code))
        return None

def getOneAlphabet(alphabet):
    toeic_list = []
    bs4_html = httpGET('https://english.best/vocabulary/toeic/letter-{}/'.format(alphabet))
    bs4_html = bs4_html.find_all(class_='item-title')
    for item in bs4_html:
        item = re.findall(r'[\w|.]+', item.text)[0]
        toeic_list.append(item)
    return toeic_list

toeic_list = []

for alphabet in string.ascii_lowercase:
    toeic_list += getOneAlphabet(alphabet)

with open('TOEIC_vol.txt', 'w') as f:
    for item in toeic_list:
        f.write("{}\n".format(item))
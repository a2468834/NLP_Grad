from   bs4 import BeautifulSoup as BS
from   collections import Counter
from   random import randint
import re
import requests
from   time import sleep, time
from   os import path, system
import pickle
from   itertools import combinations_with_replacement
import nltk


def httpGET(url):
    headers  = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return BS(response.text, 'html.parser')
    else:
        print('Failed HTTP GET with error code: {}'.format(response.status_code))
        return None

def segment(text):
    segment_pos = combinations_with_replacement(list(range(1, len(text))), 2)    
    return [(text[:i], text[i:j], text[j:]) for i, j in segment_pos]


def lemmatize(word):
    #nltk.download('wordnet')
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    lemma = lemmatizer.lemmatize(word, 'v')
    if lemma == word:
        lemma = lemmatizer.lemmatize(word, 'n')
    return lemma

def stemmize(word):
    #nltk.download('wordnet')
    stemmer = nltk.stem.porter.PorterStemmer()
    return stemmer.stem(word)


def googleSearchStats(word):
    url = r'https://www.google.com/search?q=%22{}%22'.format(word)
    print(url)
    bs4_html = httpGET(url)
    bs4_html = bs4_html.find_all(class_='LHJvCe')[0]
    if bs4_html.text:
        search_result_stats = bs4_html.text
        return int(search_result_stats.split()[1].replace(',', ''))
    else:
        return None


def oneGM2Dict():
    with open('1gm-0000', 'r', encoding='utf-8') as f:
        all_lines = f.read().splitlines()
    
    one_gm_dict = Counter()
    for line in all_lines:
        if line:
            tokens = re.findall(r'\w+', line)
            one_gm_dict[tokens[0].lower()] += int(tokens[-1])
    
    with open('1gm-0000.pk', 'wb') as f:
        pickle.dump(one_gm_dict, f)
    
    exit()


if __name__ == '__main__':
    oneGM2Dict()
    nltk.download('wordnet')
    #aa = googleSearchStats('https://www.google.com/search?q=dlkfhskdjfhksdhfshdfh')
    aa = googleSearchStats('i')
    print(aa)
    '''
    #word = 'amendment'
    word = 'going'
        
    nltk.download('wordnet')
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    stemmer = nltk.stem.porter.PorterStemmer()
    
    
    lemma = lemmatizer.lemmatize(word, 'v')
    stemm = stemmer.stem(word)
    print("O: {}".format(word))
    print("L: {}".format(lemma))
    print("S: {}".format(stemm))
    '''

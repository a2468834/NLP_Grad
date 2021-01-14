#   Assignment 10 - Finding Word Root (Final)
#   
#   Date:           2020/12/31
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
from   collections import Counter
from   itertools import combinations_with_replacement, product
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
from   nltk.corpus import wordnet
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


def googleSearchStats(word, stats_dict):
    if word in stats_dict:
        print("##")
        return stats_dict[word]
    else:
        bs4_html = httpGET(r'https://www.google.com/search?q=%22{}%22'.format(word))
        time.sleep(2)
        bs4_html = bs4_html.find_all(class_='LHJvCe')[0]
        
        if bs4_html.text:
            search_result_stats = bs4_html.text
            stats_dict[word] = int(search_result_stats.split()[1].replace(',', ''))
            return int(search_result_stats.split()[1].replace(',', ''))
        else:
            stats_dict[word] = 0
            return 0


def segment(text):
    segment_pos = combinations_with_replacement(list(range(1, len(text))), 2)    
    return [(text[:i], text[i:j], text[j:]) for i, j in segment_pos]


def prob(word_seg, some_fix_ctr):
    some_fix_count_sum = sum(some_fix_ctr.values())
    
    if some_fix_ctr[word_seg] == 0:
        return 1 / ( some_fix_count_sum * 10**len(word_seg) )
    else:
        return some_fix_ctr[word_seg] / some_fix_count_sum


def calcPrefixCounter(word_attr_list, prefix_ctr):
    for each_word_attr in word_attr_list:
        for each_term in (each_word_attr["foreigns"]+each_word_attr["cross-references"]):
            if (each_term == '') or (each_term[0] == '*') or (each_term[0] == '-' and each_term[-1] == '-'):
                continue
            else:
                if (each_term[0] != '-') and (each_term[-1] == '-') and (each_term[1:-1].isalpha() == True):
                    prefix_ctr.update({each_term[:-1] : 1})


def calcAffixCounter(word_attr_list, affix_ctr):
    for each_word_attr in word_attr_list:
        for each_term in (each_word_attr["foreigns"]+each_word_attr["cross-references"]):
            if (each_term == '') or (each_term[0] == '*') or (each_term[0] == '-' and each_term[-1] == '-'):
                continue
            else:
                if (each_term[0] != '-') and (each_term[-1] != '-') and (each_term[1:-1].isalpha() == True):
                    affix_ctr.update({each_term : 1})


def calcSuffixCounter(word_attr_list, suffix_ctr):
    for each_word_attr in word_attr_list:
        for each_term in (each_word_attr["foreigns"]+each_word_attr["cross-references"]):
            if (each_term == '') or (each_term[0] == '*') or (each_term[0] == '-' and each_term[-1] == '-'):
                continue
            else:
                if (each_term[0] == '-') and (each_term[-1] != '-') and (each_term[1:-1].isalpha() == True):
                    suffix_ctr.update({each_term[1:] : 1})


def oldProcessWord(query_word):
    with open('etym.entries.v1.format.json', 'r') as f:
        word_attr_list = json.load(f)["results"]
    
    prefix_ctr, affix_ctr, suffix_ctr = Counter(), Counter(), Counter()
    
    t_prefix = threading.Thread(target=calcPrefixCounter, args =(word_attr_list, prefix_ctr))
    t_affix = threading.Thread(target=calcAffixCounter, args =(word_attr_list, affix_ctr))
    t_suffix = threading.Thread(target=calcSuffixCounter, args =(word_attr_list, suffix_ctr))
    
    t_prefix.start()
    t_affix.start()
    t_suffix.start()
    
    t_prefix.join()
    t_affix.join()
    t_suffix.join()
    
    prob_list = []
    for prefix, affix, suffix in segment(query_word):
        if affix == '':
            p1 = math.log(prob(prefix, prefix_ctr))
            p3 = math.log(prob(suffix, suffix_ctr))
            prob_list.append(((prefix, affix, suffix), p1+p3))
        else:
            p1 = math.log(prob(prefix, prefix_ctr))
            p2 = math.log(prob(affix, affix_ctr))
            p3 = math.log(prob(suffix, suffix_ctr))
            prob_list.append(((prefix, affix, suffix), p1+p2+p3))
    prob_list.sort(key=lambda tup : tup[1], reverse=True)
    
    split_word = ''
    for each_seg, index in zip(prob_list[0][0], range(len(prob_list[0][0]))):
        if index == len(prob_list[0][0])-1:
            break
        else:
            if each_seg:
                split_word += each_seg + ' + '
            else:
                pass
    split_word += prob_list[0][0][-1]
    return split_word


def googleProcessWord(query_word):
    nltk.download('wordnet')
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    stemmer = nltk.stem.porter.PorterStemmer()
    
    counts_list = []
    search_stats_dict = {}
    for prefix, affix, suffix in segment(query_word):
        counts = 0
        print("{}  {}  {}".format(prefix, affix, suffix))
        if affix == '':
            prefix_stem = stemmer.stem(prefix)
            suffix_stem = stemmer.stem(suffix)
            counts += googleSearchStats(prefix, search_stats_dict)
            counts += googleSearchStats(suffix, search_stats_dict)
            counts_list.append((counts, prefix, '', suffix))
        else:
            prefix_stem = stemmer.stem(prefix)
            affix_stem = stemmer.stem(affix)
            suffix_stem = stemmer.stem(suffix)
            counts += googleSearchStats(prefix_stem, search_stats_dict)
            counts += googleSearchStats(affix_stem, search_stats_dict)
            counts += googleSearchStats(suffix_stem, search_stats_dict)
            counts_list.append((counts, prefix, affix, suffix))
        
    counts_list.sort(key=lambda tup : tup[0], reverse=True)
    print(counts_list[0])
    
    return "???"
    
    
    #googleSearchStats('')
    
    '''
    split_word = ''
    for each_seg, index in zip(prob_list[0][0], range(len(prob_list[0][0]))):
        if index == len(prob_list[0][0])-1:
            break
        else:
            split_word += each_seg + ' + '
    split_word += prob_list[0][0][-1]
    return split_word
    '''


def lemmatize(word, pos=None):
    #nltk.download('wordnet')
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    
    if pos is None:
        lemma_v = lemmatizer.lemmatize(word, 'v')
        lemma_n = lemmatizer.lemmatize(word, 'n')
        lemma_a = lemmatizer.lemmatize(word, 'a')
        if lemma_v != word:
            lemma = lemma_v
        elif lemma_n != word:
            lemma = lemma_n
        else:
            lemma = lemma_a
    else:
        lemma = lemmatizer.lemmatize(word, pos)
    return lemma


def stemmize(word):
    #nltk.download('wordnet')
    stemmer = nltk.stem.porter.PorterStemmer()
    return stemmer.stem(word)


def newProcessWord(query_word):
    nltk.download('wordnet')
    
    with open('1gm-0000.pk', 'rb') as f:
        one_gm_dict = pickle.load(f)
    
    word_lemm = lemmatize(query_word)
    word_stem = stemmize(query_word)
    
    for prefix, affix, suffix in segment(query_word):
        if affix == '':
            p1 = math.log(prob(prefix, prefix_ctr))
            p3 = math.log(prob(suffix, suffix_ctr))
            prob_list.append(((prefix, affix, suffix), p1+p3))
        else:
            p1 = math.log(prob(prefix, prefix_ctr))
            p2 = math.log(prob(affix, affix_ctr))
            p3 = math.log(prob(suffix, suffix_ctr))
            prob_list.append(((prefix, affix, suffix), p1+p2+p3))
    
    if word_lemm == word_stem:
        return word_lemm
    else:
        #lemm_stats = googleSearchStats(word_lemm, {})
        #stem_stats = googleSearchStats(word_stem, {})
        lemm_stats = one_gm_dict[word_lemm]
        stem_stats = one_gm_dict[word_stem]
        if lemm_stats > stem_stats:
            return word_lemm
        else:
            return word_stem


def synonymWebster(word):
    url = r'https://www.merriam-webster.com/dictionary/{}'.format(word)
    bs4_html = httpGET(url)
    
    if bs4_html:
        try:
            bs4_html = bs4_html.find(id='synonyms-anchor').find(class_='mw-list').find_all('a')
            synonym_list = [synonym.text for synonym in bs4_html]
        except:
            synonym_list = []
    else:
        # That word does not exist
        synonym_list = []
    return synonym_list


def similarWords(origin_word):
    with open('TOEIC_vol.txt', 'r') as f:
        all_toeic_vol = f.read().splitlines()
    
    orig_word_pos = nltk.pos_tag([origin_word])[0][1]
    if orig_word_pos[0] == 'J':
        orig_word_pos = 'a'
    elif orig_word_pos[0] == 'N':
        orig_word_pos = 'n'
    elif orig_word_pos[0] == 'V':
        orig_word_pos = 'v'
    else:
        orig_word_pos = 'n'
    
    orig_synsets = wordnet.synsets(origin_word, orig_word_pos)
    
    similarity_list = []
    for synonym in synonymWebster(origin_word):
        syno_synsets = wordnet.synsets(synonym, orig_word_pos)
        cartesian_comb = list(product(orig_synsets, syno_synsets))
        
        similarity = 0.0
        for each_comb in cartesian_comb:
            temp_similarity = each_comb[0].path_similarity(each_comb[1])
            if temp_similarity is None:
                temp_similarity = 0.0
            if temp_similarity > similarity: similarity = temp_similarity
        
        similarity_list.append((similarity, synonym))
    
    for toeic_vol in all_toeic_vol:
        toeic_synsets = wordnet.synsets(toeic_vol, orig_word_pos)
        cartesian_comb = list(product(orig_synsets, toeic_synsets))
        
        similarity = 0.0
        for each_comb in cartesian_comb:
            temp_similarity = each_comb[0].path_similarity(each_comb[1])
            if temp_similarity is None:
                temp_similarity = 0.0
            if temp_similarity > similarity: similarity = temp_similarity
        
        similarity_list.append((similarity, toeic_vol))
    
    similarity_list.sort(key=lambda tup : tup[0], reverse=True)
    
    output_str = [similarity_list[0][1], similarity_list[1][1], similarity_list[2][1]] # Return similar words in lexicographical order
    output_str.sort()
    return (output_str[0], output_str[1], output_str[2])


def isTOEICVol(word, toeic_vol):
    with open('TOEIC_vol.txt', 'r') as f:
        all_vol = f.read().splitlines()
    


#['international', 'scholarship', 'university']
#['specially', 'calamity', 'newscast', 'competent']
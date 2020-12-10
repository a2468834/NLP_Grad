#   Assignment 9 - Finding Word Root (2)
#   
#   Date:           2020/12/10
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
from   collections import Counter
from   itertools import combinations_with_replacement
import json
import math
import re


def segment(text):
    segment_pos = combinations_with_replacement(list(range(1, len(text))), 2)    
    return [(text[:i], text[i:j], text[j:]) for i, j in segment_pos]


def prob(word_seg, some_fix_ctr):
    some_fix_count_sum = sum(some_fix_ctr.values())
    
    if some_fix_ctr[word_seg] == 0:
        return 1 / ( some_fix_count_sum * 10**len(word_seg) )
    else:
        return some_fix_ctr[word_seg] / some_fix_count_sum


def calcPrefixCounter(word_attr_list):
    prefix_ctr = Counter()
    
    for each_word_attr in word_attr_list:
        for each_term in (each_word_attr["foreigns"]+each_word_attr["cross-references"]):
            if (each_term == '') or (each_term[0] == '*') or (each_term[0] == '-' and each_term[-1] == '-'):
                continue
            else:
                if (each_term[0] != '-') and (each_term[-1] == '-') and (each_term[1:-1].isalpha() == True):
                    prefix_ctr.update({each_term[:-1] : 1})
    
    return prefix_ctr


def calcAffixCounter(word_attr_list):
    affix_ctr = Counter()
    
    for each_word_attr in word_attr_list:
        for each_term in (each_word_attr["foreigns"]+each_word_attr["cross-references"]):
            if (each_term == '') or (each_term[0] == '*') or (each_term[0] == '-' and each_term[-1] == '-'):
                continue
            else:
                if (each_term[0] != '-') and (each_term[-1] != '-') and (each_term[1:-1].isalpha() == True):
                    affix_ctr.update({each_term : 1})
    
    return affix_ctr


def calcSuffixCounter(word_attr_list):
    suffix_ctr = Counter()
    
    for each_word_attr in word_attr_list:
        for each_term in (each_word_attr["foreigns"]+each_word_attr["cross-references"]):
            if (each_term == '') or (each_term[0] == '*') or (each_term[0] == '-' and each_term[-1] == '-'):
                continue
            else:
                if (each_term[0] == '-') and (each_term[-1] != '-') and (each_term[1:-1].isalpha() == True):
                    suffix_ctr.update({each_term[1:] : 1})
    
    return suffix_ctr


if __name__ == '__main__':
    word_list = ['international', 'scholarship', 'university', 'education', 'programme']
    
    with open('etym.entries.v1.format.json', 'r') as f:
        word_attr_list = json.load(f)["results"]
    
    prefix_ctr = calcPrefixCounter(word_attr_list)
    affix_ctr  = calcAffixCounter(word_attr_list)
    suffix_ctr = calcSuffixCounter(word_attr_list)
    
    for each_word in word_list:
        prob_list = []
        for prefix, affix, suffix in segment(each_word):
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
        
        print(each_word)
        for each_prob, index in zip(prob_list[0:10], list(range(10))):
            print('{}     {:.3f}'.format(each_prob[0], each_prob[1]))
            if index == 9:
                print('\n')

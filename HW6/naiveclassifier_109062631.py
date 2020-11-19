#   Assignment 6 - Naive Bayes Classifier
#   
#   Date:           2020/11/19
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
from   nltk import NaiveBayesClassifier
import nltk.classify
import itertools
import nltk
import numpy
import re
import random
import spacy
import math


class textColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class CONST:
    hi_freq_threshold = lambda : 25000
    train_test_ratio  = lambda : 0.8
    spacy_model       = spacy.load('en_core_web_sm')
    total_word_count  = lambda : 743842922321


def readWordCountDict():
    WC_dict = {}
    
    with open('word.txt', 'r') as f:
        WC_list = f.read().splitlines()
        
        for index in range(len(WC_list)):
            temp = re.findall(r'\w+', WC_list[index])
            WC_list[index] = (temp[0].lower(), int(temp[1]))
    
    WC_list.sort(key=lambda tup : tup[1], reverse=True)
    
    # Output only high freq. words
    for top_index in range(CONST.hi_freq_threshold()):
        WC_dict[WC_list[top_index][0]] = WC_list[top_index][1]
    
    return WC_dict


def readSentTXT():
    good_sent, bad_sent = [], []
    
    with open('sents.cam.txt', 'r', encoding='utf-8') as good_sent_fp, open('sents.bnc.txt', 'r', encoding='utf-8') as bad_sent_fp:
        good_sent = good_sent_fp.read().splitlines()
        bad_sent = bad_sent_fp.read().splitlines()
        
        for index in range(len(good_sent)):
            good_sent[index] = (good_sent[index], 'G')
        
        for index in range(len(bad_sent)):
            bad_sent[index] = (bad_sent[index], 'B')
    
    return good_sent, bad_sent


def calcSentFeatureDict(sent, WC_dict):
    tokenized_sent = re.findall(r'\w+', sent)
    
    # Feature 1 : # of high freq. words in 'snet'
    HF_word_density = 0.0
    for item in tokenized_sent:
        if item in WC_dict:
            HF_word_density += 1.0
    #HF_word_density = HF_word_density / float(len(tokenized_sent))
    
    # Feature 2 : # of specific spaCy part-of-speech tags 
    POS_num = 0
    spacy_doc = CONST.spacy_model(sent)
    for token in spacy_doc:
        if token.pos_ in ['X', 'SYM']:
            POS_num += 1
    
    # Feature 3 : Check whether the first word in 'sent' is uppercase
    if tokenized_sent[0][0].isupper() == True:
        uppercase_head = True
    else:
        uppercase_head = False
    
    # Feature 4 : sentence probability in HW1
    sent_log_prob = 0.0
    for token in tokenized_sent:
        if token in WC_dict:
            sent_log_prob += math.log(float(WC_dict[token]/CONST.total_word_count()), 10)
        else:
            sent_log_prob += math.log(float(1/CONST.total_word_count()), 10)
        
    # Feature 5 : Whether 'sent' contains ';' or not
    if ';' in sent:
        have_semicolon = True
    else:
        have_semicolon = False
    
    have_digit = bool(re.search('\d+', sent))
        
    feature_dict = {}
    feature_dict['HF_density'] = HF_word_density
    #feature_dict['upper_head'] = uppercase_head
    feature_dict['POS_count'] = POS_num
    feature_dict['have_semicolon'] = have_semicolon
    feature_dict['sent_prob'] = sent_log_prob
    feature_dict['have_digit'] = have_digit
    return feature_dict


# Main function
if __name__ == "__main__":
    word_count_dict = readWordCountDict()
    good_sent_set, bad_sent_set = readSentTXT()
    
    total_dataset = good_sent_set + bad_sent_set
    
    feature_set = []
    for item in total_dataset:
        tup_0 = calcSentFeatureDict(item[0], word_count_dict)
        tup_1 = item[1]
        feature_set.append((tup_0, tup_1))
    
    random.shuffle(feature_set)
    train_index = int(len(feature_set)*CONST.train_test_ratio())
    train_set, test_set = feature_set[:train_index], feature_set[train_index:]
    
    '''
    pos_dict = {}
    for i in good_sent_set:
        spacy_parse = CONST.spacy_model(i[0])
        
        for token in spacy_parse:
            if token.pos_ not in pos_dict:
                pos_dict[token.pos_] = 1.0 / len(spacy_parse)
            else:
                pos_dict[token.pos_] += (1.0 - pos_dict[token.pos_]) / len(spacy_parse)
    print(pos_dict)
    
    pos_dict = {}
    for i in bad_sent_set:
        spacy_parse = CONST.spacy_model(i[0])
        
        for token in spacy_parse:
            if token.pos_ not in pos_dict:
                pos_dict[token.pos_] = 1.0 / len(spacy_parse)
            else:
                pos_dict[token.pos_] += (1.0 - pos_dict[token.pos_]) / len(spacy_parse)
    print(pos_dict)
    exit()
    '''
    
    NB_classifier = nltk.NaiveBayesClassifier.train(train_set)
    print("Accuracy: %.4f"%nltk.classify.accuracy(NB_classifier, test_set))
    
    
    
    
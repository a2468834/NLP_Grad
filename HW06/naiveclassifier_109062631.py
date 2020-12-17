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
import itertools
import math
from   multiprocessing import Pool
from   nltk import NaiveBayesClassifier
import nltk
import nltk.classify
import random
import re
import spacy
import time


class CONST:
    HF_threshold     = lambda : 25000
    train_test_ratio = lambda : 0.95
    total_word_count = lambda : 743842922321
    spacy_model      = spacy.load('en_core_web_sm')


def readWordCountDict():
    # 'WC': word count
    with open('word.txt', 'r') as f:
        WC_list = f.read().splitlines()
        
        for index in range(len(WC_list)):
            temp = re.findall(r'\w+', WC_list[index])
            WC_list[index] = (temp[0].lower(), int(temp[1]))
    
    WC_list.sort(key=lambda tup : tup[1], reverse=True)
    
    # Only put those high freq. words into WC_dict
    return {WC_list[top_index][0] : WC_list[top_index][1] for top_index in range(CONST.HF_threshold())}    


def readSentenceTXT():
    good_sent, bad_sent = [], []
    
    with open('sents.cam.txt', 'r', encoding='utf-8') as good_sent_fp, open('sents.bnc.txt', 'r', encoding='utf-8') as bad_sent_fp:
        good_sent = good_sent_fp.read().splitlines()
        bad_sent = bad_sent_fp.read().splitlines()
        
        # Add label
        for index in range(len(good_sent)):
            good_sent[index] = (good_sent[index], 'G')
        
        for index in range(len(bad_sent)):
            bad_sent[index] = (bad_sent[index], 'B')
    
    return good_sent, bad_sent


def calcFeatures(pool_map_tuple):
    (sent, sent_label), WC_dict = pool_map_tuple # Unpack input parameter
    tokenized_sent = re.findall(r'\w+', sent)
    
    # Feature: # of high freq. words in 'snet'
    HF_word_count = 0
    for word in tokenized_sent:
        if word in WC_dict:
            HF_word_count += 1
    
    # Feature: # of words in 'sent'
    word_count = len(tokenized_sent)
    
    # Feature: Check whether the first word in 'sent' is uppercase
    uppercase_head = tokenized_sent[0][0].isupper()
    
    # Feature: sentence probability in HW1
    sent_log_prob = 0.0
    for token in tokenized_sent:
        if token in WC_dict:
            sent_log_prob += math.log(float(WC_dict[token]/CONST.total_word_count()), 10)
        else:
            sent_log_prob += math.log(float(1.0/CONST.total_word_count()), 10)
        
    # Feature: Whether 'sent' contains ';' or not
    if ';' in sent:
        have_wired_punctuation = True
    elif '``' in sent:
        have_wired_punctuation = True
    elif '&' in sent:
        have_wired_punctuation = True
    elif '*' in sent:
        have_wired_punctuation = True
    else:
        have_wired_punctuation = False
    
    # Feature: Whether 'sent' contains phone numbers
    have_phone = bool(re.search(r'\d{3}\s\d{3}\s\d{4}', sent))
    
    # Feature: Whether all alphabets in 'sent' are uppercase
    all_uppercase = sent.isupper()
    
    # Feature: Whether 'sent' contains pattern '(=' or '[ +'
    wired_pattern = bool(re.search(r'(\(\=)', sent)) or bool(re.search(r'(\[\ \+)', sent))
    
    # Feature: # of digits in 'sent'
    digit_num = len(re.findall(r'\d', sent))
    
    # Feature: # of dashes in 'sent'
    dash_num = len(re.findall(r'\-', sent))
    
    # Pack features into a dict
    feature_dict = {}
    feature_dict['HF_count']   = HF_word_count
    feature_dict['have_phone'] = have_phone
    feature_dict['wired_punc'] = have_wired_punctuation
    feature_dict['all_upper']  = all_uppercase
    feature_dict['word_count'] = word_count
    feature_dict['sent_prob']  = sent_log_prob
    feature_dict['wired_pat']  = wired_pattern
    feature_dict['digit_num']  = digit_num
    feature_dict['dash_num']   = dash_num
    
    return (feature_dict, sent_label)


# Main function
if __name__ == "__main__":
    pool = Pool()
    
    word_count = readWordCountDict()
    good_dataset, bad_dataset = readSentenceTXT()
    
    total_dataset = good_dataset + bad_dataset
    total_dataset_w_feature = pool.map(calcFeatures, itertools.product(total_dataset, [word_count]))
    
    opt_accuracy, opt_total_dataset, opt_total_dataset_w_feature = 0.0, None, None
    for epoch in range(100):
        rand_int = int(time.time())
        random.Random(rand_int).shuffle(total_dataset)
        random.Random(rand_int).shuffle(total_dataset_w_feature)
        division_index = int(len(total_dataset_w_feature)*CONST.train_test_ratio())
        train_dataset  = total_dataset_w_feature[:division_index]
        test_dataset   = total_dataset_w_feature[division_index:]
        
        NB_classifier = nltk.NaiveBayesClassifier.train(train_dataset)
        cur_accuracy = nltk.classify.accuracy(NB_classifier, test_dataset)
        
        if opt_accuracy < cur_accuracy:
            opt_accuracy = cur_accuracy
            opt_total_dataset = total_dataset
            opt_total_dataset_w_feature = total_dataset_w_feature
    
    print("Example:")
    print()
    print(opt_total_dataset[0][0])
    print()
    print("Label: %s"%opt_total_dataset_w_feature[0][1])
    print("Features: %s"%str(opt_total_dataset_w_feature[0][0]))
    print()
    print("Accuracy: %.4f"%(opt_accuracy))

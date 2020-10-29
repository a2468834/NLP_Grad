#   Assignment 4 - Miscollocation
#   
#   Date:           2020/10/29
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   SW Environment: Python 3.8.5 [GCC 9.3.0] on Ubuntu 20.04.1 LTS
#   HW Environment: AMD Ryzen 5 3400G w/ 32GB ram w/o discrete GPU
import spacy
from nltk.corpus import wordnet as wn
import nltk
nltk.download('wordnet')
from transformers import *
import numpy
import re
import itertools


# 步驟 1: OK
def check_sentence_vn(doc):
    result = []
    # Find all dep_=='dobj'
    dobj_list = [(index, doc[index]) for index in range(len(doc)) if doc[index].dep_=='dobj']
    
    for each_dobj in dobj_list:
        for index in range(len(doc)):
            if doc[index].text==str(each_dobj[1].head): each_dobj_head = (index, doc[index])
        result.append([(each_dobj_head[1].text, each_dobj_head[0]), (each_dobj[1].text, each_dobj[0])])
    
    return result


model = "bert-large-uncased"
p = pipeline("fill-mask", model=model, topk=100)


# 步驟 2: OK
def mask_cand(sentence, verb_index):
    sentence_tokens = re.findall(r'\w+|[,.?]', sentence)
    sentence_tokens[verb_index] = "[MASK]"
    return p(list2Sent(sentence_tokens))


def list2Sent(input_list):
    output_sentence = ""
    for index in range(len(input_list)):
        if input_list[index] == '':
            pass
        elif input_list[index] == '.':
            output_sentence = output_sentence[0:-1] + input_list[index] + ' '
        else:
            output_sentence = output_sentence + input_list[index] + ' '
    # Remove the last character ' ' in the string
    return output_sentence[0:-1]


# 步驟 3
def similarity(miscollocations, sentence):
    for i in range(5): print()
    
    for each_collocation in miscollocations:
        total_result = []
        origin_synsets = wn.synsets(each_collocation[0][0], 'v')
        mask_list = mask_cand(sentence, each_collocation[0][1])
        
        for each_mask in mask_list:
            candid_synsets =  wn.synsets(each_mask['token_str'], 'v')
            
            all_combination = list(itertools.product(origin_synsets, candid_synsets))
            
            similarity = 0
            for comb in all_combination:
                temp = comb[0].path_similarity(comb[1])
                if temp > similarity: similarity = temp
            
            if (similarity >= 0.4) and (each_mask['token_str'] != each_collocation[0][0]):
                total_result.append((each_mask['token_str'], each_collocation[1][0], similarity, each_mask['score']))
        total_result = sorted(total_result, key=lambda tup : tup[2], reverse=True)
        total_result = sorted(total_result, key=lambda tup : tup[3], reverse=True)
        print(sentence)
        for item in total_result: print(item)
        print()
        print()


nlp = spacy.load('en_core_web_sm')

# Test 1
doc, sentence = nlp("They all have the mistake."), "They all have the mistake."
miscollocations = check_sentence_vn(doc)
similarity(miscollocations, sentence)

# Test 2
doc, sentence = nlp("I reach the dream as a teacher now."), "I reach the dream as a teacher now."
miscollocations = check_sentence_vn(doc)
similarity(miscollocations, sentence)

# Test 3
doc, sentence = nlp("This does not entail that we never learn knowledge."), "This does not entail that we never learn knowledge."
miscollocations = check_sentence_vn(doc)
similarity(miscollocations, sentence)

# Test 4
doc, sentence = nlp("Just as we must identify all the outputs necessary to reach the purpose."), "Just as we must identify all the outputs necessary to reach the purpose."
miscollocations = check_sentence_vn(doc)
similarity(miscollocations, sentence)

#   Assignment 4 - Miscollocation
#   
#   Date:           2020/10/29
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
from nltk.corpus import wordnet
from transformers import pipeline
import itertools
import nltk
import numpy
import re
import spacy


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


def check_sentence_vn(spacy_doc):
    result = []
    
    for spacy_token in spacy_doc:
        # The '.head' of spacy-dobj token must be a verb or auxiliary verb.
        if spacy_token.dep_ == 'dobj':
            collocation_1st_part = (spacy_token.head.text, spacy_token.head.i)
            collocation_2nd_part = (spacy_token.text, spacy_token.i)
            result.append([collocation_1st_part, collocation_2nd_part])
    
    return result


def mask_cand(sentence, verb_index, tfs_model):
    sentence_tokenized = re.findall(r'\w+|[,.?]', sentence)
    sentence_tokenized[verb_index] = "[MASK]"
    return tfs_model(list2StrSent(sentence_tokenized))


def replaceWithMASK(sentence, replace_index):
    tokenization                = re.findall(r'\w+|[,.?]', sentence)
    tokenization[replace_index] = "[MASK]"
    return list2StrSent(tokenization)


def list2StrSent(input_list):
    output_sentence = ""
    
    for item in input_list:
        if item == '':
            pass
        elif item == '.':
            output_sentence = output_sentence[0:-1] + item + ' '
        else:
            output_sentence = output_sentence + item + ' '
    
    # Remove the last character ' ' in the string sentence.
    return output_sentence[0:-1]


# collocations = [[collocation_1st_part, collocation_2nd_part], [...], ...]
# E.g., [[('identify', 4), ('output', 7)], [('reach', 10), ('purpose', 12)]]
# See check_sentence_vn() to find more details about collocation_1st_part & collocation_2nd_part
def similarity(collocations, sentence, tfs_model):
    for each_collocation in collocations:
        total_result = []
        orig_synsets = wordnet.synsets(each_collocation[0][0], 'v')
        mask_list    = mask_cand(sentence, each_collocation[0][1], tfs_model) # a list of dicts
        
        for mask_outcome in mask_list:
            cand_synsets   =  wordnet.synsets(mask_outcome['token_str'], 'v')
            cartesian_comb = list(itertools.product(orig_synsets, cand_synsets))
            
            similarity = 0.0
            for each_comb in cartesian_comb:
                temp_similarity = each_comb[0].path_similarity(each_comb[1]) # calculate WordNet similarity between two WordNet synsets.
                if temp_similarity > similarity: similarity = temp_similarity
            
            if (similarity > 0.4) and (mask_outcome['token_str'] != each_collocation[0][0]):
                total_result.append((mask_outcome['token_str'], each_collocation[1][0], similarity, mask_outcome['score']))
        
        # Sort total_result by 'similarity' (1st pri) and 'mask_outcome['score']'
        total_result = sorted(total_result, key=lambda tup : (tup[2], tup[3]), reverse=True)
        
        # Print out results
        print(replaceWithMASK(sentence, each_collocation[0][1]))
        print_template = "({0:16} | {1:16} | {2:.2f} | {3:.5f})"
        for item in total_result:
            print(print_template.format(*item))
        print("\n\n")


# Main function
if __name__ == "__main__":
    # About pretrained models of 'transformers': https://huggingface.co/transformers/pretrained_models.html
    print(f"{textColor.OKGREEN}Loading transformers model.{textColor.ENDC}")
    tfs_model = pipeline("fill-mask", model="bert-large-uncased", topk=100)
    print(f"{textColor.OKGREEN}Load-in completed.\n\n\n{textColor.ENDC}")
    
    # Dependency parser of spaCy
    spacy_model = spacy.load('en_core_web_sm')
    
    # Test case 1
    sentence = "They all have the mistake."
    collocations = check_sentence_vn(spacy_model(sentence))
    similarity(collocations, sentence, tfs_model)
    print("\n\n")
    
    # Test case 2
    sentence = "I reach the dream as a teacher now."
    collocations = check_sentence_vn(spacy_model(sentence))
    similarity(collocations, sentence, tfs_model)
    print("\n\n")
    
    # Test case 3
    sentence = "This does not entail that we never learn knowledge."
    collocations = check_sentence_vn(spacy_model(sentence))
    similarity(collocations, sentence, tfs_model)
    print("\n\n")
    
    # Test case 4
    sentence = "Just as we must identify all the outputs necessary to reach the purpose."
    collocations = check_sentence_vn(spacy_model(sentence))
    similarity(collocations, sentence, tfs_model)

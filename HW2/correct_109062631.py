#   Assignment 2 - Noisy Channel Model
#    
#   Date:        2020/10/15
#   CourseID:    10910ISA 562100
#   Course:      Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:   109062631
#   Writer_Name: Wang, Chuan-Chun
#   Environment: Python 3.8.5 on Windows 10(1916) with Intel Core i7-10510U
from collections import Counter, defaultdict
import itertools
import kenlm
import math
import operator
import re
import time


# Global variables
uniGramTokenize = lambda text : re.findall(r'\w+|[,.?]', text.lower())
model = kenlm.Model('bnc.prune.arpa')                                            # Load pre-trained language model (BNC dataset), provided by TA
uni_gram_count = Counter(uniGramTokenize(open('big.txt').read()))                # A python-LIST of 1-gram words' counts
dets = {"", "the", "a", "an"}                                                    # All available determiners
preps = {"", "about", "at", "by", "for", "from", "in", "of", "on", "to", "with"} # All available prepositions


class TAProvided:
    # Return the probability of 'word'.
    def P(word, N=sum(uni_gram_count.values())):
        return float(uni_gram_count[word] / N)
    
    # The subset of 'words' that appears in the dictionary of 'uni_gram_count'.
    def known(words): 
        return set(w for w in words if w in uni_gram_count)
    
    # All edits that are one-edit away from 'word'.
    def edits1(word):
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)
    
    # All edits that are two-edit away from 'word'.
    def edits2(word):
        return (e2 for e1 in TAProvided.edits1(word) for e2 in TAProvided.edits1(e1))
    
    # Return a python-list of top 5 of words (by prob. in 'uni_gram_count')
    # Note: if the input parameter 'word' is correct, the first element (top-1 prob.) of list is 'word' itself.
    def suggest(word):
        suggest_P = {}
        edits_set = TAProvided.edits1(word).union(set(TAProvided.edits2(word)))
        for candidate in TAProvided.known(edits_set):
            suggest_P[candidate] = TAProvided.P(candidate)
        if word in uni_gram_count:
            suggest_P[word] = 1
        suggest_can = sorted(suggest_P, key=suggest_P.get, reverse=True)[:5]
        return suggest_can


# Convert a python-list into several words with whitespaces (i.e., a sentence).
def list2Sent(input_list):
    output_sentence = ""
    for index in range(0, len(input_list)):
        if input_list[index] == '':
            pass
        else:
            output_sentence = output_sentence + input_list[index] + ' '
    # Remove the last character ' ' in the string
    return output_sentence[0:-1]


# Generate all combinations (in the order of dict.key) of a python-dictionary
# Input:  dict of lists e.g., {1 : [aaa, @@@], 2 : [bbb, %%%]}
# Output: list of tuples e.g.., [(aaa, bbb), (aaa, %%%), (@@@, bbb), (@@@, %%%)]
def combinationOfDict(input_dict):
    return list(itertools.product(*(input_dict[key] for key in sorted(input_dict))))


def tokens_check(sentence):
    sentence_tokenized = uniGramTokenize(sentence.lower())
    
    # If a piece of tokenized sentence is not contained in 'uni_gram_count', it must be a tpoy.
    typo_index = [i for i in range(0, len(sentence_tokenized)) if uni_gram_count[sentence_tokenized[i]] == 0]
    
    typo_candidate = {i : TAProvided.suggest(sentence_tokenized[i]) for i in typo_index}
    
    possible_sentence = []
    for each_comb in combinationOfDict(typo_candidate):
        correct_sent = sentence_tokenized
        for i in range(0, len(each_comb)): correct_sent[typo_index[i]] = each_comb[i]
        possible_sentence.append(list2Sent(correct_sent))
    
    max_score = -float("inf")
    max_score_index = 0
    for i in range(0, len(possible_sentence)):
        temp_score = model.score(possible_sentence[i], bos=True, eos=True) / len(uniGramTokenize(possible_sentence[i]))
        if max_score < temp_score:
            max_score, max_score_index = temp_score, i
    return possible_sentence[max_score_index]


# Generate all combinations of determiners and prepositions to original sentence
def generate_candidates(tokens):
    # Find all of determiners and prepositions' indices in 'tokens'
    tokens_dets_index = [i for i in range(0, len(tokens)) if tokens[i] in set(dets)]
    tokens_preps_index = [i for i in range(0, len(tokens)) if tokens[i] in set(preps)]
    
    # Code Review Here
    dets_preps_dict = {}
    for i in tokens_dets_index:
        dets_preps_dict[i] = list(dets)
    for i in tokens_preps_index:
        dets_preps_dict[i] = list(preps)
    
    all_keys = sorted(dets_preps_dict)
    combinaitons = list(itertools.product(*(dets_preps_dict[Name] for Name in all_keys)))
    
    result = []
    for one_comb in combinaitons:
        temp = tokens
        for i in range(0, len(one_comb)):
            temp[all_keys[i]] = one_comb[i]
        result.append(list2Sent(temp))
    return result


def process_sent(sentence):
    correct_sent = tokens_check(sentence)
    all_candi = generate_candidates(uniGramTokenize(correct_sent))
    
    max_score = -99999.99999
    max_score_index = 0
    for i in range(0, len(all_candi)):
        tmp = model.score(all_candi[i], bos=True, eos=True) / len(uniGramTokenize(all_candi[i]))
        if max_score < tmp:
            max_score = tmp
            max_score_index = i
    return all_candi[max_score_index]


if __name__ == "__main__":
    print("\n")
    task_1_text = 'he sold everythin except the housee'
    task_2_text = 'we discuss a possible meaning by it .'

    print("###### Task1 ######")
    print("Before: %s"%task_1_text)
    print("After:  %s"%tokens_check(task_1_text))
    exit()
    print("\n")
    
    print("###### Task2 ######")
    print("Before: %s"%task_2_text)
    print("After:  %s"%process_sent(task_2_text))

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
import math, re
import kenlm
import operator
import itertools

model = kenlm.Model('bnc.prune.arpa')

# ---------- Spelling Check ----------

def words(text): return re.findall(r'\w+|[,.?]', text.lower())


WORDS = Counter(words(open('big.txt').read()))


def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return float(WORDS[word] / N)


def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)


def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def suggest(word):
    '''return top 5 words as suggestion, original_word as top1 when original_word is correct'''
    suggest_P = {}
    edits_set = edits1(word).union(set(edits2(word)))
    for candidate in known(edits_set):
        suggest_P[candidate] = P(candidate)
    if word in WORDS:
        suggest_P[word] = 1
    suggest_can = sorted(suggest_P, key=suggest_P.get, reverse=True)[:5]
    
    return suggest_can

# ---------- Spelling Check ----------

###### Task1 ######
def tokens_check(sentence):
    sent_tokenized = words(sentence.lower())
    
    # Task 1.1
    wrong_word_index = []
    for i in range(0, len(sent_tokenized)):
        # Cannot find 'i' in WRDS means 'i' is a worong words.
        if WORDS[sent_tokenized[i]] == 0:
            wrong_word_index.append(i)
    
    candidate_dict = {}
    for i in wrong_word_index:
        wrong_word = sent_tokenized[i]
        candidate_dict[i] = suggest(wrong_word)
    
    # Task 1.2
    all_keys = sorted(candidate_dict)
    combinaitons = list(itertools.product(*(candidate_dict[Name] for Name in all_keys)))
    
    possible_sentence = []
    for one_comb in combinaitons:
        temp = sent_tokenized
        for i in range(0, len(one_comb)):
            temp[wrong_word_index[i]] = one_comb[i]
        possible_sentence.append(listToString(temp))
    
    max_score = -99999.99999
    max_score_index = 0
    for i in range(0, len(possible_sentence)):
        tmp = model.score(possible_sentence[i], bos=True, eos=True) / len(words(possible_sentence[i]))
        if max_score < tmp:
            max_score = tmp
            max_score_index = i
    return possible_sentence[max_score_index]

    
def listToString(in_list):      
    str1 = ""
    for index in range(0, len(in_list)-1):
        if in_list[index] == '':
            pass
        else:
            str1 = str1 + in_list[index] + ' '
    str1 = str1 + in_list[-1]
    return str1
    
###### Task2 ######
dets = {"", "the", "a", "an"}
preps = {"", "about", "at", "by", "for", "from", "in", "of", "on", "to", "with"}

def generate_candidates(tokens):
    tokens_dets_index = []
    for i in range(0, len(tokens)):
        if tokens[i] in set(dets):
            tokens_dets_index.append(i)
    tokens_preps_index = []
    for i in range(0, len(tokens)):
        if tokens[i] in set(preps):
            tokens_preps_index.append(i)
    
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
        result.append(listToString(temp))
    return result


def process_sent(sentence):
    correct_sent = tokens_check(sentence)
    all_candi = generate_candidates(words(correct_sent))
    
    max_score = -99999.99999
    max_score_index = 0
    for i in range(0, len(all_candi)):
        tmp = model.score(all_candi[i], bos=True, eos=True) / len(words(all_candi[i]))
        if max_score < tmp:
            max_score = tmp
            max_score_index = i
    return all_candi[max_score_index]

print("\n")
text_task_1 = 'he sold everythin except the housee'
text_task_2 = 'we discuss a possible meaning by it .'

print("###### Task1 ######")
print("Before: %s"%text_task_1)
print("After:  %s"%tokens_check(text_task_1))

print("\n")

print("###### Task2 ######")
print("Before: %s"%text_task_2)
print("After:  %s"%process_sent(text_task_2))

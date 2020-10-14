#   Assignment 1 - Language Model
#    
#   Date:        2020/10/08
#   CourseID:    10910ISA 562100
#   Course:      Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:   109062631
#   Writer_Name: Wang, Chuan-Chun
#   Environment: Python 3.8.5 on Windows 10(1916) with Intel Core i7-10510U
from collections import Counter
import math
import re
#from nltk.util import ngrams


# Memoization class
class memoize:
    def __init__(self, func):
        self.func = func
        self.memo_dict = {}
    def __call__(self, *args):
        if args not in self.memo_dict:
            self.memo_dict[args] = self.func(*args)
        # Warning: You may wish to do a deepcopy here if returning objects
        return self.memo_dict[args]


# Tokenize text and get a python-LIST of tokenize
# 'lower()' method returns a string where all characters are lower case.
@memoize
def uniGramTokenize(text):
    return re.findall(r'\w+', text.lower())


# Get all 2-grams
@memoize
def biGramTokenize(text):
    uni_gram_list = uniGramTokenize(text)
    return list(((uni_gram_list[i], uni_gram_list[i+1])) for i in range(len(uni_gram_list)-1))


# Equivalent code
# 
# def Tokenize(text, ngram_deg):
#     return list(ngrams(re.findall(r'\w+', text.lower()), ngram_deg))


# ==Format==
# Call add1Smooth(("He", "is")), then retrun 1.306 (probability with add one smooth)
# 'bi_gram' is a tuple of two strings.
def add1Smooth(bi_gram):
    V = len(list(uni_count.keys()))
    return (bi_count[bi_gram] + 1) / (uni_count[bi_gram[0]] + V)
    

# ==Format==
# call sentenceProb("He is looking a new job.")
# retrun -33.306 (sentence probability)
def sentenceProb(sentence):
    bi_gram = biGramTokenize(sentence)
    sent_prob = 0.0
    for i in bi_gram:
        sent_prob = sent_prob + math.log(add1Smooth(i), 10)
    return sent_prob


# The correct answer is P(sent1) < P(sent2) and P(sent3) < P(sent4)
if __name__ == "__main__":
    # Count the number of times which 1-grams(unigram) and 2-grams(bigram) appeared
    with open('big.txt', 'r') as infp:
        full_text = infp.read()
        uni_count = Counter(uniGramTokenize(full_text))
        bi_count  = Counter(biGramTokenize(full_text))
    
    sent1 = "Are you interested about your offer for Marketing Assistant."
    sent2 = "Are you interested in your offer for Marketing Assistant."
    sent3 = "He is looking to a new job."
    sent4 = "He is looking for a new job."
    
    print("\nAll the probabilities are base on 10.\n")
    print("%s (%.3f)"%(sent1, sentenceProb(sent1)))
    print("%s (%.3f)"%(sent2, sentenceProb(sent2)))
    print("%s (%.3f)"%(sent3, sentenceProb(sent3)))
    print("%s (%.3f)"%(sent4, sentenceProb(sent4)))

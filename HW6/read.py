import spacy
import re

if __name__ == "__main__":
    punc_set = set()
    spacy_model = spacy.load('en_core_web_sm')
    
    with open('word.txt', 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    
    temp = 0
    for line in lines:
        temp += int(re.findall(r'\w+', line)[1])
    
    print(temp)
            
#   Assignment 3 - Skip-gram and MapReduce
#   
#   Date:        2020/10/22
#   CourseID:    10910ISA 562100
#   Course:      Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:   109062631
#   Writer_Name: Wang, Chuan-Chun
#   Environment: Python 3.8.5 on Windows 10(1916) with Intel Core i7-10510U
from collections     import Counter
from multiprocessing import Pool
import gc
import re


# '$' represents empty character.
def mapper(row):
    tokens = re.findall(r'\w+', row)
    try:
        skip_gram          = tokens[0] + ' ' + tokens[-2] # include testing uni-gram case
        skip_gram_distance = len(tokens)-2
        skip_gram_count    = int(tokens[-1])
    except:
        skip_gram          = '$'
        skip_gram_distance = 0
        skip_gram_count    = None
    del row
    del tokens
    return ((skip_gram, skip_gram_distance), skip_gram_count)


def reducer(data):
    total_dict = {}
    
    # tup    : ((skip_gram, skip_gram_distance), skip_gram_count)
    # tup[0] : (skip_gram, skip_gram_distance)
    # tup[1] : skip_gram_count
    for tup in data:
        if tup[0] not in total_dict:
            total_dict[tup[0]] = (-1 if tup[0][0] == '$' else tup[1])
        else:
            total_dict[tup[0]] = (-1 if tup[0][0] == '$' else total_dict[tup[0]] + tup[1])
    
    # Turn python-dict into a sorted python-list
    total_dict = sorted(total_dict.items(), key=lambda x : x[1], reverse=True)
    
    # Output TOP200 of most frequent skip-grams
    with open("HW3_109062631.out", "w") as fptr:
        for index in range(200):
            fptr.write(str(total_dict[index][0]))
            fptr.write("\t")
            fptr.write(str(total_dict[index][1]))
            fptr.write("\n")


if __name__ == "__main__":
    # Create multiprocessing pool
    pool = Pool()
    
    # Map
    print("Map Stage...")
    with open("web1t.baby") as f:
        baby1t = f.read().splitlines()
    
    skipgram_count = [row for row in pool.map(mapper, baby1t) if row]
    skipgram_count.sort(key=lambda x : x[0])
    del baby1t
    
    # Reduce
    print("Reduce Stage...")
    reducer(skipgram_count)

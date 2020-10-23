#   Assignment 3 - Skip-gram and MapReduce
#   
#   Date:        2020/10/22
#   CourseID:    10910ISA 562100
#   Course:      Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:   109062631
#   Writer_Name: Wang, Chuan-Chun
#   Environment: Python 3.8.5 on Windows 10(1916) with Intel Core i7-10510U
import fileinput
from tqdm import tqdm
from collections import Counter
from multiprocessing import Pool
import re
import pickle
import gc


uniGramTokenize = lambda text : re.findall(r'\w+', text.lower())


 # '$' represents empty character.
def mapper(row):
    tokens = uniGramTokenize(row)
    
    try:
        skip_gram          = tokens[0] + ' ' + tokens[-2]
        skip_gram_distance = (len(tokens)-1)-1
        skip_gram_count    = int(tokens[-1])
    except:
        skip_gram          = '$'
        skip_gram_distance = 0
        skip_gram_count    = None
    
    return ((skip_gram, skip_gram_distance), skip_gram_count)


def reducer(data):
    total_dict = {}
    
    for tup in data: # tup = ((skip_gram, skip_gram_distance), skip_gram_count)
        if tup[0] not in total_dict:
            total_dict[tup[0]] = tup[1]
        else:
            total_dict[tup[0]] = total_dict[tup[0]] + tup[1]
    
    return total_dict


if __name__ == "__main__":
    skipgram_count = []
    
    # Create multiprocessing pool
    #pool = Pool()
    
    # Map
    print("Map Stage...")
    '''
    with open("web1t.baby", encoding="utf-8") as f:
        baby1t = f.read().splitlines()
    
    index = 0
    with open("PkDump.pk", "wb") as write_fp:
        for row in baby1t:
            if row:
                #skipgram_count.append(mapper(row))
                pickle.dump([mapper(row)], write_fp)
                index += 1
            if (index%100000) == 0 : print(index)
    '''
    index = 0
    with open("PkDump.pk", "rb") as read_fp:
        while True:
            print(index)
            index += 1
            try:
                skipgram_count.append(pickle.load(read_fp))
            except EOFError:
                break
    print("Finish reading.")
    #skipgram_count = [row for row in pool.map(mapper, baby1t) if row]
    skipgram_count.sort(key=lambda x : x[0])
    print("Finish sorting.")
    # skipgram_count:
    # [
    #   ... ,
    #   (('of the', 1), 12345678),
    #   (('of the', 1), 123),
    #   (('at the', 2), 456),
    #   ...
    # ]

    # Reduce
    print("Reduce Stage...")
    result = reducer(skipgram_count)
    result = sorted(result.items(), key=lambda x : x[1])
    
    with open("output.txt", "w") as fptr:
        i = 1
        for key, value in result.items():
            if i > 30: break
            else:
                fptr.write(key)
                fptr.write("    ")
                fptr.write(value)
                fptr.write("\n")
                i += 1

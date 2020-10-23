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
from tqdm            import tqdm
import fileinput
import gc
import re


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
            if tup[1] == None:
                total_dict[tup[0]] = -1
            else:
                total_dict[tup[0]] = tup[1]
        else:
            if tup[1] == None:
                total_dict[tup[0]] = -1
            else:
                total_dict[tup[0]] = total_dict[tup[0]] + tup[1]
        
    # Turn python-dict into a sorted python-list
    total_dict = sorted(total_dict.items(), key=lambda x : x[1], reverse=True)
    
    with open("output.txt", "w") as fptr:
        for index in range(35):
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
    print("Finish reading web1t.baby.")
    skipgram_count = [row for row in pool.map(mapper, baby1t) if row]
    del baby1t
    print("Finish mapping.")
    skipgram_count.sort(key=lambda x : x[0])
    print("Finish sorting.")
    
    # Reduce
    print("Reduce Stage...")
    reducer(skipgram_count)

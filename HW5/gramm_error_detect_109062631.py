#   Assignment 5 - Grammatical Error Detection
#   
#   Date:           2020/11/05
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
from   linggle import Linggle
import os
import pathlib
import re
import requests

class FUNC:
    tokenize = lambda text : re.findall(r'\w+|[,.?]', text.lower())


class CONST:
    file_name = lambda : 'sentences-test.tsv'
    #file_name = lambda : 'sentences.tsv'
    OKGREEN   = lambda : '\033[92m'
    ENDC      = lambda : '\033[0m'
    


def get_sbg_stat(sbg):
    '''
    1.  Example usage of get_sbg_stat()
        > $ get_sbg_stat('affected our')
        > {'1': 45440, '2': 29769, '3': 3005, '4': 4111}
    2.  Query example url
        http://thor.nlplab.cc:5566/search?q={skip_bigram}
    '''
    response = requests.get('http://thor.nlplab.cc:5566/search?q=' + sbg.lower())
    return response.json()


# Return a list of lists: [[sentence_0], [sentence_1],...], where sentence_0 = [(word_0, 'c/i'), (word_1, 'c/i'),...]
def readTSV():
    working_dir   = pathlib.Path().absolute()
    tsv_file_path = os.path.join(working_dir, CONST.file_name())
    
    result = []
    
    with open(tsv_file_path, 'r') as fp:
        whole_file = fp.readlines()
    
    one_sent = []
    for index in range(len(whole_file)):
        if (whole_file[index] == "\n"):
            result.append(one_sent)
            one_sent = []
        elif (index == len(whole_file)-1):
            # Append the last line of input file
            temp = FUNC.tokenize(whole_file[index])
            one_sent.append((temp[0], temp[1]))
            result.append(one_sent)
            one_sent = []
        else:
            temp = FUNC.tokenize(whole_file[index])
            one_sent.append((temp[0], temp[1]))
    
    return result


# Assume incorrect word is 'to', D-3-gram is 'affected to our', and I-3-gram is 'to our life'
# del_cands = [('affected our', skipgram distance of prev. string)]
# ins_cands = [('to our', skipgram dist.), ('to life', skipram dist.)]
def makeCandidates(query_sent):
    del_cands, ins_cands, incorrect_word = [], [], ""
    
    for index in range(len(query_sent)):
        if query_sent[index][1] == 'c':
            pass
        else: #query_sent[index][1] == 'i'
            incorrect_word = query_sent[index][0]
            
            # Deletion candidates
            del_cands.append((query_sent[index-1][0] + ' ' + query_sent[index+1][0], 2))
            
            # Insertion candidates
            ins_cands.append((query_sent[index][0] + ' ' + query_sent[index+1][0], 1))
            ins_cands.append((query_sent[index][0] + ' ' + query_sent[index+2][0], 2))
            
    return del_cands, ins_cands, incorrect_word


def calcDistPercent(cand_str):
    dist_dict = get_sbg_stat(cand_str)
    
    total_num = sum(dist_dict.values())
    dist_dict = { key : round(dist_dict[key] / total_num * 100.0, 4) for key in dist_dict}
    
    return dist_dict


def list2StrSent(sent_list):
    output_sentence = ""
    for index in range(len(sent_list)):
        if sent_list[index] == '':
            pass
        elif sent_list[index] in ['.', '?']:
            output_sentence = output_sentence[0:-1] + sent_list[index] + ' '
        else:
            output_sentence = output_sentence + sent_list[index] + ' '
    # Remove the last character ' ' in the string
    return output_sentence[0:-1]


def printResult(print_sent_list, incorrect_word, mode):
    print_sent_list = [itr[0] for itr in print_sent_list]
    
    try:
        index = print_sent_list.index(incorrect_word)
    except:
        print("Cannot find incorrect word in the query sentence.")
        exit()
    
    if mode == "DEL":
        print_sent_list[index] = '?' + print_sent_list[index]
        print(f"{CONST.OKGREEN()}%s{CONST.ENDC()}"%list2StrSent(print_sent_list))
    elif mode == "INS0":
        print_sent_list[index] = '_ ' + print_sent_list[index]
        print(f"{CONST.OKGREEN()}%s{CONST.ENDC()}"%list2StrSent(print_sent_list))
    elif mode == "INS1":
        print_sent_list[index] = print_sent_list[index] + ' _'
        print(f"{CONST.OKGREEN()}%s{CONST.ENDC()}"%list2StrSent(print_sent_list))
    elif mode == "ORIGIN":
        print("Sentence: %s"%list2StrSent(print_sent_list))
    else:
        print("Wrong mode at list2StrSent.")
        exit()


# Main function
if __name__ == "__main__":
    query_sent_list = readTSV()
    
    for query_sent in query_sent_list:
        del_cands, ins_cands, incorrect_word = makeCandidates(query_sent)
        
        del_dist_dict_0 = calcDistPercent(del_cands[0][0])
        ins_dist_dict_0 = calcDistPercent(ins_cands[0][0])
        ins_dist_dict_1 = calcDistPercent(ins_cands[1][0])
        
        del_score = del_dist_dict_0['1']
        ins_score = (ins_dist_dict_0['2'] + ins_dist_dict_1['3']) / 2.0
        
        if del_score > ins_score:
            printResult(query_sent, incorrect_word, "ORIGIN")
            print(f"{CONST.OKGREEN()}Answer: Delete{CONST.ENDC()}")
            printResult(query_sent, incorrect_word, "DEL")
        else:
            printResult(query_sent, incorrect_word, "ORIGIN")
            print(f"{CONST.OKGREEN()}Answer: Insert{CONST.ENDC()}")
            printResult(query_sent, incorrect_word, "INS0")
            printResult(query_sent, incorrect_word, "INS1")
        print("\n\n")
 
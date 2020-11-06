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
import ast
from   linggle import Linggle
from   multiprocessing import Pool
import os
import pathlib
import pickle
import re
import requests
import sys
import zlib

# The abbreviation "IW" means "incorrect word".

class FUNC:
    tokenize = lambda text : re.findall(r'\w+|[,.?]', text.lower())
    
    def zlib_comp(uncompression): # Use highest level of compression
        return zlib.compress(pickle.dumps(uncompression), level=9)
    
    def zlib_decomp(compression):
        return pickle.loads(zlib.decompress(compression))


class CONST:
    file_name    = lambda : 'sentences-test.tsv'
    DB_file_name = lambda : "sb.dist.tsv"
    #file_name   = lambda : 'sentences.tsv'
    OKGREEN      = lambda : '\033[92m'
    ENDC         = lambda : '\033[0m'
    

def get_sbg_stat(mode, sbg, sbg_DB=None):
    ''' Usage of mode == 'NETWORK'
    1.  Example usage of get_sbg_stat()
        > $ get_sbg_stat('affected our')
        > {'1': 45440, '2': 29769, '3': 3005, '4': 4111}
    2.  Query example url
        http://thor.nlplab.cc:5566/search?q={skip_bigram}
    '''
    if mode == 'NETWORK':
        response = requests.get('http://thor.nlplab.cc:5566/search?q=' + sbg.lower())
        response = response.json()
    elif mode == 'LOCAL':
        try:
            response = FUNC.zlib_decomp(sbg_DB[sbg.lower()])
        except:
            print("Error when accessing sbg_DB.")
            exit()
        response = {str(tuple0): tuple1 for tuple0, tuple1 in response}
    else:
        print("Error mode of get_sbg_stat().")
        exit()
    
    return response


# Return a list of dicts: [{'token' : token_sentence, 'IW_index' : IW_index),...], 
# where token_sentence = ['word_0', 'word_1',...]
def readTSV():
    working_dir   = pathlib.Path().absolute()
    tsv_file_path = os.path.join(working_dir, CONST.file_name())
        
    with open(tsv_file_path, 'r') as fp: whole_file = fp.readlines()
    
    one_sent, result = [], []
    IW_index, prev_sent_index = 0, 0
    for itr in range(len(whole_file)):
        if (whole_file[itr] == "\n"):
            # Append a complete info. of a single sentence into return list
            result.append({'token': one_sent, 'IW_index': IW_index - prev_sent_index})
            one_sent, IW_index = [], 0
            prev_sent_index = itr + 1
        elif (itr == len(whole_file)-1):
            temp = FUNC.tokenize(whole_file[itr])
            one_sent.append(temp[0])
            IW_index = itr if (temp[1] == 'i') else IW_index
            
            # Append a complete info. of a single sentence into return list
            result.append({'token': one_sent, 'IW_index': IW_index - prev_sent_index})
            one_sent, IW_index = [], 0
            prev_sent_index = itr + 1
        else:
            temp = FUNC.tokenize(whole_file[itr])
            one_sent.append(temp[0])
            IW_index = itr if (temp[1] == 'i') else IW_index
    
    return result


# Assume incorrect word is 'to', D-3-gram is 'affected to our', and I-3-gram is 'to our life'
# del_cands = [('affected our', skipgram distance of prev. string)]
# ins_cands = [('to our', skipgram dist.), ('to life', skipram dist.)]
def makeCandidates(query_sent):
    del_cands, ins_cands = [], []
    IW_index = query_sent['IW_index']
    
    # Deletion candidates
    del_cands.append((query_sent['token'][IW_index-1] + ' ' + query_sent['token'][IW_index+1], 2))
    
    # Insertion candidates
    ins_cands.append((query_sent['token'][IW_index] + ' ' + query_sent['token'][IW_index+1], 1))
    ins_cands.append((query_sent['token'][IW_index] + ' ' + query_sent['token'][IW_index+2], 2))
            
    return del_cands, ins_cands


def calcDistPercent(cand_str, sbg_DB=None):
    dist_dict = get_sbg_stat('LOCAL', cand_str, sbg_DB=sbg_DB)
    
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


def printResult(query_sent, mode, IW_index=None):
    print_sent_list = query_sent['token'].copy() # Make sure the assignment id a pass-by-value copy.
    
    if mode == "DEL":
        print_sent_list[IW_index] = '?' + print_sent_list[IW_index]
        print(f"{CONST.OKGREEN()}%s{CONST.ENDC()}"%list2StrSent(print_sent_list))
    elif mode == "INS0":
        print_sent_list[IW_index] = '_ ' + print_sent_list[IW_index]
        print(f"{CONST.OKGREEN()}%s{CONST.ENDC()}"%list2StrSent(print_sent_list))
    elif mode == "INS1":
        print_sent_list[IW_index] = print_sent_list[IW_index] + ' _'
        print(f"{CONST.OKGREEN()}%s{CONST.ENDC()}"%list2StrSent(print_sent_list))
    elif mode == "ORIGIN":
        print("Sentence: %s"%list2StrSent(print_sent_list))
    else:
        print("Wrong mode at list2StrSent.")
        exit()


# Read data using multiprocessing Pool
def readDataTSVParallel():
    pool = Pool()
    
    working_dir   = pathlib.Path().absolute()
    tsv_file_path = os.path.join(working_dir, CONST.DB_file_name())
    
    print("Open data tsv file.")
    with open(tsv_file_path) as fp:
        input_data = fp.read().splitlines()
    
    print("Start parallel computing.")
    return {key_value[0]: key_value[1] for key_value in pool.map(mapper, input_data)}


def mapper(each_line):
    temp  = re.split(r'\t+', each_line)
    key   = temp[0]
    value = list(ast.literal_eval(temp[1]))
    value = FUNC.zlib_comp(value)
    return (key, value)


# Main function
if __name__ == "__main__":
    query_sent_list = readTSV()
    sbg_DB = readDataTSVParallel()
    
    for query_sent in query_sent_list:
        del_cands, ins_cands = makeCandidates(query_sent)
        
        del_dist_dict_0 = calcDistPercent(del_cands[0][0], sbg_DB=sbg_DB)
        ins_dist_dict_0 = calcDistPercent(ins_cands[0][0], sbg_DB=sbg_DB)
        ins_dist_dict_1 = calcDistPercent(ins_cands[1][0], sbg_DB=sbg_DB)
        
        del_score = del_dist_dict_0['1']
        ins_score = (ins_dist_dict_0['2'] + ins_dist_dict_1['3']) / 2.0
        
        if del_score > ins_score:
            printResult(query_sent, "ORIGIN", query_sent['IW_index'])
            print(f"{CONST.OKGREEN()}Answer: Delete{CONST.ENDC()}")
            printResult(query_sent, "DEL", query_sent['IW_index'])
        else:
            printResult(query_sent, "ORIGIN", query_sent['IW_index'])
            print(f"{CONST.OKGREEN()}Answer: Insert{CONST.ENDC()}")
            printResult(query_sent, "INS0", query_sent['IW_index'])
            printResult(query_sent, "INS1", query_sent['IW_index'])
        print("\n\n")

'''
linggle = Linggle()

linggle.query('am replying your _ letter')
# []

linggle.query('am replying _ your letter')
# [['am replying to your letter', 245]]

'''

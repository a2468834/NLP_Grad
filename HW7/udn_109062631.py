#   Assignment 7 - Using Church-Gale algorithm to build an ERRANT for Mandarin
#   
#   Date:           2020/11/26
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
import nltk
import monpa
import numpy

# [Step 1] 加入詞性參考 by ckip
'''
text = '這也間接突顯出鴻海'
text = '也直接透露出鴻海'

Print Result:

[('這', 'Nep'), ('也', 'D'), ('間接', 'D'), ('突顯出', 'VJ'), ('鴻海', 'Nb')]
[('也', 'D'), ('直接', 'VH'), ('透露出', 'VK'), ('鴻海', 'Nb')]
'''


def seg_pos(sent):
    return monpa.pseg(sent)


text1 = '這也間接突顯出鴻海'
text2 = '也直接透露出鴻海'


def printMatrix(matrix, matrix_name):
    print()
    print(matrix_name)
    for row in matrix:
        print('[', end="")
        for item in row:
            if len(str(item))>=3:
                print(" '" + str(item) + "' ", end='')
            else:
                print("  '" + str(item) + "'  ", end='')
        print(']', end="\n")
    print()


# [Strp 2] 計算 edit cost 返回cost_matrix, op_matrix
#Hint:[Strp 2]會呼叫[Strp 3]的方法，Cost可以自己調整

'''
M是Match
I是insert cost
D是delete cost
R是replace cost
I/D是insert和delete相加的cost
'''

'''
輸入：
orig = [('這', 'Nep'), ('也', 'D'), ('間接', 'D'), ('突顯出', 'VJ'), ('鴻海', 'Nb')]
cor = [('也', 'D'), ('直接', 'VH'), ('透露出', 'VK'), ('鴻海', 'Nb')]
cost_matrix, op_matrix = calculate_edit_cost(orig, cor)
'''

'''
輸出：
cost_matrix = 
 [[0, 2, 4, 5, 4],
  [4, 6, 8, 9, 8],
  [2, 0, 6, 7, 6],
  [3, 5, 5, 8, 7],
  [5, 7, 8, 5, 8],
  [4, 6, 8, 9, 0]]
 
op_matrix =
 [['O', 'I', 'I', 'I', 'I'],
  ['D', 'I/D', 'I/D', 'I/D', 'I/D'],
  ['D', 'M', 'I/D', 'I/D', 'I/D'],
  ['D', 'I/D', 'R', 'I/D', 'I/D'],
  ['D', 'I/D', 'R', 'R', 'R'],
  ['D', 'I/D', 'I/D', 'I/D', 'M']]
'''


def get_sub_cost(orig, cor):
    cost = 0
    if orig == cor:
        return cost
    else:
        cost += nltk.edit_distance(orig[0], cor[0])*2
        cost += nltk.edit_distance(orig[1], cor[1])
        return cost


def calculate_edit_cost(orig, cor):
    # Create the cost_matrix and the op_matrix
    cost_matrix = [[0 for j in range(len(cor)+1)] for i in range(len(orig)+1)] # (len(orig)+1)-by-(len(cor)+1)
    op_matrix   = [["O" for j in range(len(cor)+1)] for i in range(len(orig)+1)] # (len(orig)+1)-by-(len(cor)+1)
    
    # Fill in the edges
    for i in range(1, len(orig)+1):
        cost_matrix[i][0] = nltk.edit_distance(orig[i-1][1]+orig[i-1][0], '')
        op_matrix[i][0] = "D"
    for j in range(1, len(cor)+1):
        cost_matrix[0][j] = nltk.edit_distance('', cor[j-1][1]+cor[j-1][0])
        op_matrix[0][j] = "I"
    
    # Loop through the cost_matrix
    for i in range(len(orig)):
        for j in range(len(cor)):
            rep_cost = get_sub_cost(orig[i], cor[j]) + abs(i-j)
            del_cost = nltk.edit_distance(orig[i][0]+orig[i][1], '')
            ins_cost = nltk.edit_distance(cor[j][0]+cor[j][1], '')
                    
            if orig[i] == cor[j]:
                cost_matrix[i+1][j+1] = 0
                op_matrix[i+1][j+1] = "M"
            else: # orig[i] != cor[j]
                # Case: Insert or delete
                if nltk.edit_distance(orig[i][0]+orig[i][1], cor[j][0]+cor[j][1]) == 1:
                    if len(orig[i][0]) > len(cor[j][0]): # Delete
                        cost_matrix[i+1][j+1] = del_cost
                        op_matrix[i+1][j+1] = "D"
                    else: # Insert
                        cost_matrix[i+1][j+1] = ins_cost
                        op_matrix[i+1][j+1] = "I"
                # Case: I/D or Replace
                else:
                    if rep_cost < float(ins_cost+del_cost):
                        cost_matrix[i+1][j+1] = int(rep_cost)
                        op_matrix[i+1][j+1] = "R"
                    else:
                        cost_matrix[i+1][j+1] = ins_cost+del_cost
                        op_matrix[i+1][j+1] = "I/D"
    return cost_matrix, op_matrix


# tuple = ('chinese_word', 'POS')
orig = [('這', 'Nep'), ('也', 'D'), ('間接', 'D'), ('突顯出', 'VJ'), ('鴻海', 'Nb')]
cor = [('也', 'D'), ('直接', 'VH'), ('透露出', 'VK'), ('鴻海', 'Nb')]
cost_matrix, op_matrix = calculate_edit_cost(orig, cor)
printMatrix(cost_matrix, 'cost_matrix')
printMatrix(op_matrix, 'op_matrix')


"""# [Strp 3] 計算Replace的cost
嘗試找出可能可以計算cost的方式，例如檢查詞性、詞的長度或詞的差異等，最後將所有的cost相加回傳。

`Hint 要給多少Cost可以自己設定`

input
``` Python
orig = ('突顯出', 'VJ')
cor = ('透露出', 'VK')

```
return cost
"""

sent_orig = seg_pos('這也間接突顯出鴻海')
sent_correct = seg_pos('也直接透露出鴻海')

calculate_edit_cost(sent_orig, sent_correct)




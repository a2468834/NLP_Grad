#   Assignment 10 - Finding Word Root (Final)
#   
#   Date:           2020/12/31
#   CourseID:       10910ISA 562100
#   Course:         Natural Language Processing Lab (Graduated)
#   
#   Writer_ID:      109062631
#   Writer_Name:    Wang, Chuan-Chun
#   
#   Environment:    
#      Software:    Python 3.8.5 on 64-bit Windows 10 Pro v2004
#      Hardware:    Intel i7-10510U, 16GB DDR4 non-ECC ram, and no discrete GPU
from   finding_roots import *
from   flask import Flask, render_template, request


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/handle_data', methods=['POST'])
def handle_data():
    query_word = request.form['query']
    query_word = query_word.lower()
    data = {'origin_word': query_word, 'split_word_old': oldProcessWord(query_word), 'similar_words':similarWords(query_word)}
    return render_template('result.html', data=data)


app.run(debug=True)

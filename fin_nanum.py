import pandas as pd
import numpy as np
import pickle
import json
import pymysql
import gensim
from gensim.models.fasttext import FastText
from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import datapath
from flask import Flask, request, jsonify, make_response, render_template
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

model = KeyedVectors.load_word2vec_format('.\models\wiki.ko.vec', binary=False)

# load vectorized dataset
# 벡터화된 데이터셋을 불러옵니다
with open('fin_nanum_vec_03.pkl', 'rb') as f:
    df = pickle.load(f)

okt = Okt()

# define a fuction calculating the mean of vectors
# 모델과 토큰화된 문자열이 포함된 리스트가 주어졌을 때 리스트의 문자열들의 평균 벡터값을 계산하는 함수를 정의합니다.
def get_mean_vector(model, words):
    # remove out-of-vocabulary words
    # 모델에 저장되어 있지 않은 토큰이 포함되어 있는 경우 제거합니다.
    words = [word for word in words if word in model.vocab]

    # calculate the mean of vector(s) only if the length of the list is not zero
    # 제거 후 길이가 리스트의 길이가 1 이상인 경우 평균값을 계산하고 그렇지 않은 경우 빈 리스트를 반환합니다.
    if len(words) >= 1:
        return np.mean(model[words], axis=0)
    else:
        return []

@app.route('/result', methods=['GET', 'POST'])
def output_question():
    # get input data
    # 입력값을 가져옵니다.
    s_input = str(request.args.get('s_ask'))
    # extract only nouns from input string and get the mean of vectors
    # 입력 받은 문자열에서 명사만을 추출한 후 평균 벡터값을 도출합니다.
    v_input = get_mean_vector(model, okt.nouns(s_input))
    # get five most similar questions from DB using cosine similarity
    # DB에서 코사인 유사도가 가장 높은 상위 다섯 개 항목을 출력합니다.
    d_result = dict(pd.Series([cosine_similarity([vec], [v_input])[0][0] for vec in df['question_vec'] if len(vec) > 0]).sort_values(ascending=False)[:5])
    result = {round(v, 5): [df.iloc[k, 0], df.iloc[k, 1], df.iloc[k, 4]] for k, v in d_result.items()}

    return result

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

#!/usr/bin/env python
# coding: utf-8

# Importing Libraries

import sys
import gc
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb
import pickle

input_val = []

def extract_feature(test_text):
 # load tfidf features
    tf1 = pickle.load(open("feature.pkl",'rb'))
    test_word_features = tf1.transform(test_text)
    test_features = hstack([test_word_features])
    return test_features
		
def predict_lgb(test_features):
    #current labels
    class_names = ['hindi', 'tamil','english']
    for class_name in class_names:
        sfm = pickle.load(open("sfm"+class_name+".pkl",'rb'))
        test_sparse_matrix = sfm.transform(test_features)
        joblib_file = 'lang_detect_lgbmodel_'+class_name+'.txt'
        model = lgb.Booster(model_file='{}'.format(joblib_file))
        submission[class_name] = model.predict(
		    test_sparse_matrix,
			predict_disable_shape_check=True
        )
    return submission
if __name__ == "__main__" :
    #print("Argument length",len(sys.argv))
    input_val = str(sys.argv[1])
    print("input text:.............>>>>",input_val) 
    list_val = [input_val]
    test = pd.DataFrame(list_val , columns= ['text'])
    test_text = test['text']
    test_features = extract_feature(test_text)
    #final result df
    submission = pd.DataFrame.from_dict({'text': test['text']})
    #prediction
    submission = predict_lgb(test_features)
    print(submission.head())
    #max column name & it's label encode
    submission['lang_detected'] = submission[['hindi','tamil','english']].idxmax(axis=1)
    print("Language detected is .........>>>>",submission['lang_detected']) 
	
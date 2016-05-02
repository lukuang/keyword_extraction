"""
use cross validation to preport results
"""

import os
import json
import sys
import re
import argparse
from sklearn import cross_validation
from sklearn import metrics

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]


def load_data_set(data_dir):
    features = json.load(open(os.path.join(data_dir,"feature_vector")))
    judgements = json.load(open(os.path.join(data_dir,"judgement_vector")))
    entities = json.load(open(os.path.join(data_dir,"all_entities")))

    return features,judgements,entities





def get_classifier(method):
    if method == 0:
        from sklearn import svm
        classifier = svm.LinearSVC()
    elif method == 1:
        from sklearn import linear_model
        classifier = linear_model.LogisticRegression(C=1e5)
    elif method == 2:
        from sklearn.naive_bayes import GaussianNB
        classifier = GaussianNB()
    else: 
        from sklearn import tree
        classifier = tree.DecisionTreeClassifier()

    return classifier

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir","-tr",default = "/home/1546/code/keyword_extraction/stanford_parser/no_location_features")
    parser.add_argument('--method','-m',type=int,default=0,choices=range(4),
        help=
        """chose mthods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
                3:decision  tree
        """)
    args=parser.parse_args()
    X,y,entities = load_data_set(args.data_dir)
    classifier = get_classifier(args.method)
    predicted = cross_validation.cross_val_predict(clf,X,y,cv=5)
    accuracy = metrics.accuracy_score(y,predicted)
    f1 = metrics.f1_score(y,predicted)
    print "performance:"
    print "accuracy: %f, f1: %f" %(accuracy,f1)

if __name__=="__main__":
    main()


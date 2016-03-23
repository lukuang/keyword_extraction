"""
predict test set's entity category
"""

import os
import json
import sys
import re
import argparse

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]


def load_training_set(training_dir):
    features = json.load(open(os.path.join(training_dir,"feature_vector")))
    judgements = json.load(open(os.path.join(training_dir,"judgement_vector")))

    return features,judgements


def load_test_set(test_dir):
    entities = json.load(open(os.path.join(test_dir,"test_candidates")))
    test_set = json.load(open(os.path.join(test_dir,"test_vector")))

    return entities,test_set


def get_classifier(method,X,y):
    if method == 0:
        from sklearn import svm
        classifier = svm.LinearSVC()
    elif method == 1:
        from sklearn import linear_model
        classifier = linear_model.LogisticRegression(C=1e5)
    else:
        from sklearn.naive_bayes import GaussianNB
        classifier = GaussianNB()

    return classifier.fit(X,y)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test_dir","-te",default = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/testing/ORGANIZATION")
    parser.add_argument("--training_dir","-tr",default = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/training/ORGANIZATION")
    parser.add_argument('--method','-m',type=int,default=0,choices=range(3),
        help=
        """chose mthods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
        """)
    args=parser.parse_args()
    X,y = load_training_set(args.training_dir)
    entities,test_set = load_test_set(args.test_dir) 
    classifier = get_classifier(args.method,X,y)
    prediction = classifier.predict(test_set)
    print "prediction:"
    for i in range(len(entity)):
        print "\t%s: %f" %(entity[i],prediction[i])

if __name__=="__main__":
    main()


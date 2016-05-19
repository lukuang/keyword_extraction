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
from collections import Counter,namedtuple

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]


def load_data_set(data_dir):
    features = json.load(open(os.path.join(data_dir,"feature_vector")))
    judgements = json.load(open(os.path.join(data_dir,"judgement_vector")))
    entity_info = json.load(open(os.path.join(data_dir,"entity_info")))

    return features,judgements,entity_info





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


def get_top_entities(all_entities,predicted,top_size,need_positive):
    
    if need_positive:
        label = 1
    else:
        label = 0

    needed_entities = {}
    for i in range(len(predicted)):
        if predicted[i] == label:
            entity = all_entities[i]
            if entity not in needed_entities:
                needed_entities[entity] = 0
            needed_entities[entity] += 1

    sorted_entities = sorted(needed_entities.items(),key=lambda x:x[1],reverse=True)

    print "top %d entities:" %(top_size)
    for i in range(top_size):
        print "\t%s: %d" %(sorted_entities[i][0],sorted_entities[i][1])


def show_performance_on_entity_types(y,predicted,entity_info):
    Size = namedtuple('Size', ['pos', 'neg'])
    type_size = Size(pos=Counter(),neg=Counter())
    correct_predicted = Size(pos=Counter(),neg=Counter())
    for i in range(len(entity_info)):
        entity_type_list = entity_info[i]["type"]
        if y[i] == 1:
            type_size.pos.update(entity_type_list)
            if predicted[i] == 1:
                correct_predicted.pos.update(entity_type_list)

        else:
            type_size.neg.update(entity_type_list)
            if predicted[i] == 0:
                correct_predicted.neg.update(entity_type_list)

    print "show performance in terms of entity types:"
    print "There are %d entities" %(len(y))
    print "In positive example:"
    for k in type_size.pos.keys():
        print "\tThere are %d %s entities, %d are predicted correctly"\
             %(type_size.pos[k],k,correct_predicted.pos[k])
    print "In negative example:"
    for k in type_size.neg.keys():
        print "\tThere are %d %s entities, %d are predicted correctly"\
             %(type_size.neg[k],k,correct_predicted.neg[k])




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir","-dr",default = "/home/1546/code/keyword_extraction/stanford_parser/no_location_features")
    parser.add_argument('--method','-m',type=int,default=0,choices=range(4),
        help=
        """chose mthods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
                3:decision  tree
        """)
    parser.add_argument("--top_size","-ts",type=int,default = 20)
    parser.add_argument("--need_positive","-np",action='store_true')

    args=parser.parse_args()
    X,y,entity_info = load_data_set(args.data_dir)
    clf = get_classifier(args.method)
    predicted = cross_validation.cross_val_predict(clf,X,y,cv=5)
    accuracy = metrics.accuracy_score(y,predicted)
    f1 = metrics.f1_score(y,predicted)

    print "performance:"
    print "accuracy: %f, f1: %f" %(accuracy,f1)
    show_performance_on_entity_types(y,predicted,entity_info)
    #get_top_entities(all_entities,predicted,args.top_size,args.need_positive)

if __name__=="__main__":
    main()


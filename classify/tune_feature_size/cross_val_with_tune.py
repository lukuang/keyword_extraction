"""
use cross validation to preport results
"""

import os
import json
import sys
import re
import argparse
from sklearn import cross_validation
from sklearn.metrics import classification_report
from sklearn import metrics
from collections import Counter,namedtuple

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]


def load_data_set(data_dir):
    feature_data = json.load(open(os.path.join(data_dir,"feature_data")))

    return features,judgements,feature_data





def get_classifier(method):
    if method == 0:
        from sklearn.svm import SVC
        classifier = SVC(kernel="linear",C=1)
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

def get_limit(negative_frequency,positive_frequency):
    size1 = len(negative_frequency)
    size2 = len(positive_frequency)
    max_size = max(size1,size2)
    
    mode = max_size//10
    limit = mode*10
    if limit - max_size < 0:
        limit +=  10
    
    return limit


def prepare_data(train_data,what_to_tune):
    negative_feature_frequency = {}
    positive_feature_frequency = {}
    negative_category_frequency = {}
    positive_category_frequency = {}

    for single_data in train_data:
        if single_data["judgement"] == 0:
                for w in single_data["word_features"]: 
                    if w not in negative_feature_frequency:
                        negative_feature_frequency[w] = 0
                    negative_feature_frequency[w] += 1

                if not single_data["category"]:
                    continue

                for c in single_data["category"]:
                    if c not in negative_category_frequency:
                        negative_category_frequency[c] = 0
                    negative_category_frequency[c] += 1


            else:
                for w in single_data["word_features"]: 
                    if w not in positive_feature_frequency:
                        positive_feature_frequency[w] = 0
                    positive_feature_frequency[w] += 1

                if not single_data["category"]:
                    continue

                for c in single_data["category"]:
                    if c not in positive_category_frequency:
                        positive_category_frequency[c] = 0
                    positive_category_frequency[c] += 1

    ws_limit = get_limit(negative_feature_frequency,positive_feature_frequency)
    cs_limit = get_limit(negative_category_frequency,positive_category_frequency)

    sorted_negative_feature_frequency = sorted(negative_feature_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_positive_feature_frequency = sorted(positive_feature_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_negative_category_frequency = sorted(negative_category_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_positive_category_frequency = sorted(positive_category_frequency.items(),key = lambda x:x[1],reverse=True)

    para_set = []
    if what_to_tune == 0:
        for ws_input in range(10,ws_limit*10+10):
            para_set.append([ws_input,0])
    elif what_to_tune == 1:
        for cs_input in range(10,cs_input*10+10):
            para_set.append([0,cs_input])

    else:
        for ws_input in range(10,ws_limit*10+10):
            for cs_input in range(10,cs_input*10+10):
                para_set.append([ws_input,cs_input])

    return para_set,
           sorted_negative_feature_frequency,sorted_positive_feature_frequency,
           sorted_negative_category_frequency,sorted_positive_category_frequency


def get_top_features(sorted_features,feature_size):
    top_features = []
    i = 0
    for (feature,v) in sorted_features:
        if i==feature_size:
            break
        i += 1
        top_features.append(feature)
        
    return top_features


def get_top_common_feature(sorted_positive_feature, sorted_negative_feature,feature_size):
    top_features = get_top_features(sorted_positive_feature,feature_size)
    top_features += get_top_features(sorted_negative_feature,feature_size)

    return list(set(top_features))


def tune(train_data,test_data,what_to_tune):
    para_set,\
    sorted_negative_feature_frequency,sorted_positive_feature_frequency,\
    sorted_negative_category_frequency,sorted_positive_category_frequency\
        = prepare_data(train_data,what_to_tune)

    for ws_input, cs_input in para_set:
        top_context_feature = get_top_common_feature(sorted_negative_feature_frequency,sorted_positive_feature_frequency,ws_input)
        top_category_feature = get_top_common_feature(sorted_negative_category_frequency,sorted_positive_category_frequency,cs_input)
        ws_real = len(top_context_feature)
        cs_real = len(top_category_feature)

        train_feature_vector = []
        train_judgement_vector = []
        test_feature_vector = []
        test_judgement_vector = []

        


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir","-dr",default = "/home/1546/code/keyword_extraction/stanford_parser/no_location_features")
    parser.add_argument('--method','-m',type=int,default=0,choices=range(4),
        help=
        """choose methods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
                3:decision  tree
        """)
    parser.add_argument("--what_to_tune","-w",type=int,default=0,choices=range(3),
        help=
        """choose what to tune:
                0: context only 
                1: category only
                2: both
        """)

    args=parser.parse_args()

    feature_data = load_data_set(args.data_dir)
    clf = get_classifier(args.method)
    label = []
    for single_data in feature_data:
        label.append(single_data["judgement"])

    skf = cross_validation.StratifiedKFold(label,5)

    predicted = [0]*len(label)

    run_index = 0
    for train_index, test_index in skf:
        run_index += 1
        print "Start run %d" % run_index
        #split the data
        train_index = train_index.tolist()
        test_index = test_index.tolist()
        train_data = []
        test_data = []

        for i in train_index:
            train_data.append(feature_data[ i ])

        for i in test_index:
            test_data.append(feature_data[ i ])

        sub_predicted_y,ws_input,cs_input, ws_real, cs_real
                = tune(train_data,test_data,args.what_to_tune)

        print "ws_input:%d, cs_input:%d, ws_real:%d, cs_real:%d"\
            %(ws_input,cs_input, ws_real, cs_real)

        for i in range(len(test_index)):
            predicted[ test_index[i] ] = sub_predicted_y[i]



    #accuracy = metrics.accuracy_score(y,predicted)
    #f1 = metrics.f1_score(y,predicted)

    #print "performance:"
    #print "accuracy: %f, f1: %f" %(accuracy,f1)
    
    y = label
    show_performance_on_entity_types(y,predicted,feature_data)
    print classification_report(y, predicted)
    #get_top_entities(all_entities,predicted,args.top_size,args.need_positive)

if __name__=="__main__":
    main()


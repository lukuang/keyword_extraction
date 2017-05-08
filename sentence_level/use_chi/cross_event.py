"""
report cross event performance
"""

import os
import json
import sys
import re
import argparse
from sklearn import cross_validation
from sklearn.metrics import f1_score 
from sklearn.feature_selection import SelectKBest
from sklearn.cross_validation import StratifiedKFold
import sklearn.metrics
from sklearn.metrics import classification_report
from sklearn import metrics
from sklearn.feature_selection import chi2
from collections import Counter,namedtuple
import cPickle
import numpy as np

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]

def get_event_name(feature_data_dir):
    abs_path = os.path.abspath(feature_data_dir)
    return os.path.basename(abs_path)

def load_data_set(event1_feature_data_dir,event2_feature_data_dir,event1_name,event2_name):
    feature_data = {}

    # event1_name = get_event_name(event1_feature_data_dir)
    feature_data[event1_name] = load_data_set_from_single_dir(event1_feature_data_dir)

    # event2_name = get_event_name(event2_feature_data_dir)
    feature_data[event2_name] = load_data_set_from_single_dir(event2_feature_data_dir)


    return feature_data

def load_data_set_from_single_dir(feature_data_dir):
    feature_data = []
    for instance in os.walk(feature_data_dir).next()[2]:
        feature_data_file = os.path.join(feature_data_dir,instance)
        instance_feature_data = load_data_set_from_single_file(feature_data_file)
        feature_data += instance_feature_data

    return feature_data

def load_data_set_from_single_file(feature_data_file):
    feature_data = json.load(open(feature_data_file))
    return feature_data



def get_classifier(method):
    if method == 0:
        from sklearn.svm import SVC
        classifier = SVC(kernel="rbf",C=1)
    elif method == 1:
        from sklearn import linear_model
        classifier = linear_model.LogisticRegression(C=1e5)
    elif method == 2:
        from sklearn.naive_bayes import GaussianNB
        classifier = GaussianNB()
    elif method == 3: 
        from sklearn import tree
        classifier = tree.DecisionTreeClassifier()
    else:
        from sklearn.ensemble import RandomForestClassifier
        classifier = RandomForestClassifier()

    return classifier





def prepare_data(feature_data):
    label = []
    words = set()
    categories = set()
    for single_data in feature_data:
        label.append(single_data["judgement"])
        for w in single_data["word_features"]:
            words.add(w)
        if single_data["category"]:
            for c in single_data["category"]:
                categories.add(c)

    word_vector = []

    for single_data in feature_data:
        single_word_vector = []
        for w in words:
            if w in single_data["word_features"]:
                single_word_vector.append(single_data["word_features"][w])
            else:
                single_word_vector.append(0)
        word_vector.append(single_word_vector)

    

    word_indecies = {}
    i = 0
    for w in words: 
        word_indecies[i] = w
        i += 1

    return label,word_indecies, categories, word_vector



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event1_feature_data_dir")
    parser.add_argument("event1_name")
    parser.add_argument("event2_feature_data_dir")
    parser.add_argument("event2_name")
    parser.add_argument('--method','-m',type=int,default=1,choices=range(5),
        help=
        """choose methods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
                3:decision  tree
                4:random forest
        """)
    parser.add_argument("--use_stanford_type","-us",action='store_true',
        help = 
        """When specified, the type information of Stanford NER
        is used as features
        """
    )
    parser.add_argument("--use_category","-uc",action='store_true',
        help = 
        """When specified, the category information from wikidata
        is used as features
        """
    )
    parser.add_argument("--no_words","-nw",action='store_true',
        help = 
        """When specified, no word features will be used
        """
    )
    parser.add_argument("--set_feature_size","-sf",type=int)
    args=parser.parse_args()

    feature_data = load_data_set(args.event1_feature_data_dir,args.event2_feature_data_dir,args.event1_name,args.event2_name)
    
    # chi2_values, pval = chi2(word_vector,label)
    # # print "There are %d chi values" %(len(chi2_values))
    # feature_value_id_map = {}
    # for i in range(len(chi2_values)):
    #     feature_value_id_map[ i] = chi2_values[i]

    # sorted_features = sorted(feature_value_id_map.items(),key=lambda x:x[1],reverse=True)
    # print "There are %d sorted_features" %(len(sorted_features))
    # print sorted_features
    if args.set_feature_size is not None:
        feature_size_vector = [args.set_feature_size]
    else: 
        feature_size_vector = [i*100 for i in range(1,40)]

    best_f1 = -1
    best_size = 0
    recall_atm = 0
    precision_atm = 0

    


    clf = get_classifier(args.method)

    for feature_size in feature_size_vector:
        print "For size %d" %(feature_size)
        f1_vector = []

        for event in feature_data:
            train_feature_data = []
            test_feature_data = []
            for other_event in feature_data:
                if other_event != event:
                    train_feature_data += feature_data[other_event]
            test_feature_data = feature_data[event]

            test_X = []
            test_y = []
            #select word features
                    

            train_y,sub_word_indecies, sub_categories,sub_word_vector = prepare_data(train_feature_data)

                

            chi2_values, pval = chi2(sub_word_vector,train_y)
            feature_value_id_map = {}
            for i in range(len(chi2_values)):
                feature_value_id_map[ sub_word_indecies[i] ] = chi2_values[i]

            sorted_features = sorted(feature_value_id_map.items(),key=lambda x:x[1],reverse=True)
            chosen_words = []
            for i in range(feature_size):
                if i >= len(sorted_features):
                    continue
                chosen_words.append( sorted_features[i][0] )

            X_new = []
            train_y = []

            # add category and type features if needed
            for single_data in train_feature_data:
                single_x = []
                if not args.no_words:
                    for w in chosen_words:
                        if w in single_data["word_features"]:
                            single_x.append(single_data["word_features"][w])
                        else:
                            single_x.append(0)
                
                if args.use_category:
                    if single_data["category"]:
                        for c in sub_categories:
                            if c in single_data["category"]:
                                single_x.append(1)
                            else:
                                single_x.append(0)
                    else:
                        single_x += [0]*len(sub_categories)

                if args.use_stanford_type:
                    if "ORGANIZATION" in single_data["type"]:
                        single_x.append(1)
                    else:
                        single_x.append(0)
                    if "LOCATION" in single_data["type"]:
                        single_x.append(1)
                    else:
                        single_x.append(0)
                X_new.append(single_x)
                train_y.append(single_data["judgement"])

            for single_data in test_feature_data:
                single_x = []
                if not args.no_words:
                    for w in chosen_words:
                        if w in single_data["word_features"]:
                            single_x.append(single_data["word_features"][w])
                        else:
                            single_x.append(0)
                if args.use_category:
                    if single_data["category"]:
                        for c in sub_categories:
                            if c in single_data["category"]:
                                single_x.append(1)
                            else:
                                single_x.append(0)
                    else:
                        single_x += [0]*len(sub_categories)

                if args.use_stanford_type:
                    if "ORGANIZATION" in single_data["type"]:
                        single_x.append(1)
                    else:
                        single_x.append(0)
                    if "LOCATION" in single_data["type"]:
                        single_x.append(1)
                    else:
                        single_x.append(0)
                test_X.append(single_x)
                test_y.append(single_data["judgement"])
                
            clf.fit(X_new,train_y)
            predicted_y = clf.predict(test_X)
            event_f1 = f1_score(test_y,predicted_y)
            f1_vector.append(event_f1)
            print "\tFor event %s, f1 is %f" %(event,event_f1)



        average_f1 = sum(f1_vector)/(1.0*len(f1_vector))
        print "Average %f" %(average_f1)
        if average_f1 > best_f1:
            best_f1 = average_f1
            best_size = feature_size
                
        print "-"*20

    print "best f1 is %f achieved by size %d" %(best_f1,best_size)

    

   

if __name__=="__main__":
    main()


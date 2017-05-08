"""
report cross instance performance
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
from sklearn.feature_selection import chi2,f_classif,mutual_info_classif
from enum import IntEnum
from collections import Counter,namedtuple
import cPickle
import numpy as np

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]

class SelectionMeasure(IntEnum):
    chi_2 = 0
    f = 1
    mutual_info = 2

def load_data_set(feature_data_dir):
    feature_data = {}
    for instance in os.walk(feature_data_dir).next()[2]:
        feature_data_file = os.path.join(feature_data_dir,instance)
        instance_feature_data = load_data_set_from_single_file(feature_data_file)
        feature_data[instance]= instance_feature_data

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

    category_vector = []
    category_indecies = {}
    for single_data in feature_data:
        single_category_vector = []
        if single_data["category"]:
            for c in categories:
                if c in single_data["category"]:
                    single_category_vector.append(1)
                else:
                    single_category_vector.append(0)
        else:
            single_category_vector = [0]*len(categories)
        category_vector.append(single_category_vector)

    j = 0
    for c in categories:
        category_indecies[j] = c
        j += 1

    word_indecies = {}
    i = 0
    for w in words: 
        word_indecies[i] = w
        i += 1

    return label,word_indecies, categories, word_vector,category_vector,category_indecies

def select_sized_features(feature_size,fearure_vecotr,feature_indecies,y,feature_selection_measure):
    if feature_selection_measure == SelectionMeasure.chi_2:
        feature_values,p_value = chi2(fearure_vecotr,y)
    elif feature_selection_measure == SelectionMeasure.f:
        feature_values,p_value = f_classif(fearure_vecotr,y)
    else:
    # elif feature_selection_measure == SelectionMeasure.mutual_info:
        feature_values = mutual_info_classif(fearure_vecotr,y)

    feature_value_id_map = {}
    for i in range(len(feature_values)):
        feature_value_id_map[ feature_indecies[i] ] = feature_values[i]

    sorted_features = sorted(feature_value_id_map.items(),key=lambda x:x[1],reverse=True)
    selected_features = []
    for i in range(feature_size):
        if i >= len(sorted_features):
            continue
        selected_features.append( sorted_features[i][0] )

    return selected_features

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_data_dir")
    parser.add_argument('--method','-m',type=int,default=1,choices=range(5),
        help=
        """choose methods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
                3:decision  tree
                4:random forest
        """)
    parser.add_argument('--feature_selection_measure','-fm',type=int,default=0,choices=list(map(int, SelectionMeasure)),
        help=
        """choose feature selection measure from:
                0:chi2
                1:f_classif
                2:mutual_info_classif
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
    parser.add_argument("--set_category_size","-cs",type=int,default=50)
    args=parser.parse_args()

    feature_data = load_data_set(args.feature_data_dir)
    
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
        feature_size_vector = [i*10 for i in range(1,40)]

    best_f1 = -1
    best_size = 0
    recall_atm = 0
    precision_atm = 0

    
    args.feature_selection_measure = SelectionMeasure(args.feature_selection_measure)

    


    for feature_size in feature_size_vector:
        print "For size %d" %(feature_size)
        f1_vector = []

        for instance in feature_data:
            train_feature_data = []
            test_feature_data = []
            for other_instance in feature_data:
                if other_instance != instance:
                    train_feature_data += feature_data[other_instance]
            test_feature_data = feature_data[instance]

            test_X = []
            test_y = []
            #select word features
                    

            train_y,sub_word_indecies, sub_categories,sub_word_vector,sub_category_vector,sub_category_indecies = prepare_data(train_feature_data)

                
            # print "\tThere are %d categories" %(len(sub_categories))
            # chi2_values, pval = chi2(sub_word_vector,train_y)
            # feature_value_id_map = {}
            # for i in range(len(chi2_values)):
            #     feature_value_id_map[ sub_word_indecies[i] ] = chi2_values[i]

            # sorted_features = sorted(feature_value_id_map.items(),key=lambda x:x[1],reverse=True)
            # selected_words = []
            # for i in range(feature_size):
            #     if i >= len(sorted_features):
            #         continue
            #     selected_words.append( sorted_features[i][0] )
            
            selected_categories = select_sized_features(args.set_category_size,sub_category_vector,sub_category_indecies,train_y,args.feature_selection_measure)
            selected_words = select_sized_features(feature_size,sub_word_vector,sub_word_indecies,train_y,args.feature_selection_measure)

            X_new = []



            # add category and type features if needed
            for single_data in train_feature_data:
                single_x = []
                if not args.no_words:
                    for w in selected_words:
                        if w in single_data["word_features"]:
                            single_x.append(single_data["word_features"][w])
                        else:
                            single_x.append(0)
                if args.use_category:
                    if single_data["category"]:
                        for c in selected_categories:
                            if c in single_data["category"]:
                                single_x.append(1)
                            else:
                                single_x.append(0)
                    else:
                        single_x += [0]*len(selected_categories)

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

            for single_data in test_feature_data:
                single_x = []
                if not args.no_words:
                    for w in selected_words:
                        if w in single_data["word_features"]:
                            single_x.append(single_data["word_features"][w])
                        else:
                            single_x.append(0)
                if args.use_category:
                    if single_data["category"]:
                        for c in selected_categories:
                            if c in single_data["category"]:
                                single_x.append(1)
                            else:
                                single_x.append(0)
                    else:
                        single_x += [0]*len(selected_categories)

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
                
            clf = get_classifier(args.method)
            clf.fit(X_new,train_y)
            predicted_y = clf.predict(test_X)
            instance_f1 = f1_score(test_y,predicted_y)
            f1_vector.append(instance_f1)
            print "\tFor instance %s, total feature size %d, f1 is %f" %(instance,len(test_X[0]),instance_f1)



        average_f1 = sum(f1_vector)/(1.0*len(f1_vector))
        print "Average %f" %(average_f1)
        if average_f1 > best_f1:
            best_f1 = average_f1
            best_size = feature_size
                
        print "-"*20

    print "best f1 is %f achieved by size %d" %(best_f1,best_size)

    

   

if __name__=="__main__":
    main()


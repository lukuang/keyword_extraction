"""
use one year data as test set and other years' as trainning set to report result
"""

import os
import json
import sys
import re
import argparse
import codecs
from collections import namedtuple
from sklearn.metrics import classification_report
from sklearn import svm


Sub_data = namedtuple("Sub_data",["features","judgements","entity_info"])


def load_data_set(data_dir):
    features = json.load(open(os.path.join(data_dir,"feature_vector")))
    judgements = json.load(open(os.path.join(data_dir,"judgement_vector")))
    entity_info = json.load(open(os.path.join(data_dir,"entity_info")))

    return features,judgements,all_entities,entity_info


def group_with_years(features,judgements,entity_info):
    grouped_data = {}
    for i in range(len(entity_info)):
        year = entity_info[i][year]
        if year not in grouped_data
            grouped_data[year] = Sub_data._make([[],[],[]])
        grouped_data[year].features.append( features[i] )
        grouped_data[year].judgements.append( judgements[i] )
        grouped_data[year].entity_info.append( entity_info[i] )
    return grouped_data


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
    parser.add_argument("")
    args=parser.parse_args()

    X,y,entity_info = load_data_set(args.data_dir)
    grouped_data = group_with_years(X,y,entity_info)
    for year in grouped_data:
        X_train, y_train, X_test, y_test = /
            split_data_for_year(grouped_data,year)
        clf = svm.SVC(kernel='linear', C=100).fit(X_train, y_train)
        y_true, y_pred = y_test, clf.predict(X_test)
        print "For year %s:" %(year)
        print classification_report(y_true, y_pred)
        print "-"*20



if __name__=="__main__":
    main()


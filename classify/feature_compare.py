"""
Select features with SelectFromModel and print the comparison
of features
"""

import os
import json
import sys
import re
import argparse
import codecs
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel


def load_required_data_from_dir(feature_dir):
    X = load_data_from_json(os.path.join(feature_dir,"feature_vector"))
    y = load_data_from_json(os.path.join(feature_dir,"judgement_vector"))
    all_features = load_data_from_json(os.path.join(feature_dir,"all_word_features"))
    all_features += load_data_from_json(os.path.join(feature_dir,"all_cates"))
    
    return X,y,all_features


def load_data_from_json(file_path):
    return json.load(open(file_path))



def get_support(X,y,C):
    lsvc = LinearSVC(C=C, penalty="l1", dual=False).fit(X, y)
    model = SelectFromModel(lsvc, prefit=True)
    X_support = model.get_support()
    return X_support


def select_feature_from_support(all_features,X_support):
    selected_features = []

    for i in range(X_support.shape[0]):
        if X_support[i]:
            selected_features.append(all_features[i])

    return selected_features


def select_features(feature_dir,C):
    
    X,y,all_features = load_required_data_from_dir(feature_dir)

    X_support = get_support(X,y,C)

    
    selected_features = select_feature_from_support(all_features,X_support)

    return selected_features


def compare_features(features1,features2,feature_dir1,feature_dir2):
    common = set()
    unique1 = set()
    unique2 = set()

    print features1
    print features2
    for f in features1:
        if f in features2:
            common.add(f)
        else:
            unique1.add(f)

    for f in features2:
        if f not in features1:
            unique2.add(f)

    print "comparison result:"
    print "there are %d features in %s and %d features in %s"\
            %(len(features1),os.path.basename(feature_dir1),\
                len(features2),os.path.basename(feature_dir2))

    print "%d common features" %(len(common))
    print common
    print "%d unique features in %s" %(len(unique1),os.path.basename(feature_dir1))
    print unique1
    print "%d unique features in %s" %(len(unique2),os.path.basename(feature_dir2))
    print unique2
    print "-"*20


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_dir1")
    parser.add_argument("feature_dir2")
    parser.add_argument("--C",'-C',type=float,default=0.1)
    args=parser.parse_args()

    features1 = select_features(args.feature_dir1,args.C)
    features2 = select_features(args.feature_dir2,args.C)
    compare_features(features1,features2,args.feature_dir1,args.feature_dir2)

if __name__=="__main__":
    main()


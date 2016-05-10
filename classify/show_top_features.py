"""
show top features given feature dir
"""

import os
import json
import sys
import re
import argparse
import codecs
from collections import Counter

def load_required_data_from_dir(feature_dir):
    X = load_data_from_json(os.path.join(feature_dir,"feature_vector"))
    y = load_data_from_json(os.path.join(feature_dir,"judgement_vector"))
    all_features = load_data_from_json(os.path.join(feature_dir,"all_word_features"))
    all_features += load_data_from_json(os.path.join(feature_dir,"all_cates"))
    
    return X,y,all_features


def load_data_from_json(file_path):
    return json.load(open(file_path))

def get_top_features(X,y,all_features,top_size):
    positive_features = Counter()
    negative_features = Counter()

    for i in range(len(y)):
        if y[i] == 0:
            negative_features.update(dict( zip(all_features,X[i]) ) )
        else:
            positive_features.update(dict( zip(all_features,X[i]) ) )


    return positive_features.most_common(top_size),\
        negative_features.most_common(top_size)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("featuer_dir")
    parser.add_argument("--top_size",'-ts',type=int,default=100)
    args=parser.parse_args()
    X,y,all_features = load_required_data_from_dir(args.featuer_dir)

    top_positive_features,top_negative_features = get_top_features(X,y,all_features,\
            args.top_size)

    print "top positive features:"
    print top_positive_features
    print "top negative features:"
    print top_negative_features
    

if __name__=="__main__":
    main()


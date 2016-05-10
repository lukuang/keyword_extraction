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
    all_word_features = load_data_from_json(os.path.join(feature_dir,"all_word_features"))
    all_features = all_word_features[:]
    all_cates = load_data_from_json(os.path.join(feature_dir,"all_cates"))
    all_features += all_cates
    
    return X,y,all_features,all_word_features,all_cates


def load_data_from_json(file_path):
    return json.load(open(file_path))


def print_single_type_features(features):
    for(k,v) in features:
        print "\t%s: %f" %(k,v)



def print_all_features(top_word_features,top_cates):
    print "word features:"
    print_single_type_features(top_word_features)
    print "category feautres:"
    print_single_type_features(top_cates)


def show_top_features(X,y,all_features,\
        all_word_features,all_cates,\
        top_word_size,top_category_size):

    positive_word_features = Counter()
    positive_cate_features = Counter()

    negative_word_features = Counter()
    negative_cate_features = Counter()

    for i in range(len(y)):
        temp_dict = dict( zip(all_features,X[i]) )
        print temp_dict
        if y[i] == 0:
            negative_word_features.update({ k:v for (k,v) in temp_dict if k in all_word_features })
            negative_cate_features.update({ k:v for (k,v) in temp_dict if k in all_cates })
        else:
            positive_word_features.update({ k:v for (k,v) in temp_dict if k in all_word_features })
            positive_cate_features.update({ k:v for (k,v) in temp_dict if k in all_cates })

    print "top positive features:"
    print_all_features(positive_word_features.most_common(top_word_size),\
                positive_cate_features.most_common(top_category_size))

    print "top negative features:"
    print_all_features(negative_word_features.most_common(top_word_size),\
                negative_cate_features.most_common(top_category_size))

    #return positive_features.most_common(top_size),\
    #    negative_features.most_common(top_size)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("featuer_dir")
    parser.add_argument("--top_word_size",'-ws',type=int,default=50)
    parser.add_argument("--top_category_size",'-cs',type=int,default=30)
    args=parser.parse_args()
    X,y,all_features,all_word_features, all_cates = load_required_data_from_dir(args.featuer_dir)

    show_top_features(X,y,all_features,\
        all_word_features,all_cates,\
        args.top_word_size,args.top_category_size)

    
    

if __name__=="__main__":
    main()


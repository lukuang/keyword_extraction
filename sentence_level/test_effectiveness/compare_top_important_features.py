"""
compare top features accross instance in terms of feature weights
"""

import os
import json
import sys
import re
import argparse
import codecs
import cPickle
from collections import Counter

def load_top_features(feature_data_dir,dir_name,feature_size):
    top_features = {}
    for instance in os.walk(feature_data_dir).next()[1]:
        instance_feature_data_dir = os.path.join(feature_data_dir,instance,dir_name)
        word_feature_file = os.path.join(instance_feature_data_dir,"word_feature")
        classifier_file = os.path.join(instance_feature_data_dir,"clf")
        
        word_features = json.load(open(word_feature_file))
        clf = cPickle.load(open(classifier_file))
        coeff = map(abs,clf.coef_[0])

        lst = zip(word_features,coeff)
        sorted_features = sorted(lst, key = lambda x:x[1])
        top_features[instance] = []
        for i in range( min(feature_size,len(sorted_features)) ):
            top_features[instance].append(sorted_features[i][0])

    return top_features


def show_unique_top_features(top_features):
    strict_unique = {}
    unstrict_unique = {}
    feature_counter = Counter()
    feature_instance_map = {}
    for instance in top_features:
        strict_unique[instance] = []
        unstrict_unique[instance] = []
        for w in top_features[instance]:
            feature_counter[w] += 1
            if w not in feature_instance_map:
                feature_instance_map[w] = []
            feature_instance_map[w].append(instance)

    
    instance_size = len(top_features)
    for w in feature_counter:
        if feature_counter[w]!= instance_size:
            if feature_counter[w] == 1:
                instance_name = feature_instance_map[w][0]
                strict_unique[instance_name].append(w)
            else:
                for instance_name in feature_instance_map[w]:
                    unstrict_unique[instance_name].append(w)

    print "Strict features:"
    for instance in strict_unique:
        print "%s:" %(instance)
        feature_string = " ".join(strict_unique[instance])
        print "\t%s" %(feature_string)
    
    print '-'*20
    print "Unstrict features:"
    for instance in unstrict_unique:
        print "%s:" %(instance)
        feature_string = " ".join(unstrict_unique[instance])
        print "\t%s" %(feature_string)
        

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature_data_dir","-fd",default="/home/1546/code/keyword_extraction/sentence_level/data/eval/intra")
    parser.add_argument("dir_name")
    parser.add_argument("--feature_size","-fz",type=int,default=10)
    args=parser.parse_args()


    top_features = load_top_features(args.feature_data_dir,args.dir_name,
                                     args.feature_size)

    show_unique_top_features(top_features)

if __name__=="__main__":
    main()


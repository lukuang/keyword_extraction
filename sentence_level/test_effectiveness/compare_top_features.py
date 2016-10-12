"""
compare top features accross instance
"""

import os
import json
import sys
import re
import argparse
import codecs
from collections import Counter


def load_data_set(feature_data_dir):
    all_data = {}
    for instance in os.walk(feature_data_dir).next()[2]:
        feature_data_file = os.path.join(feature_data_dir,instance)
        instance_feature_data = load_data_set_from_single_file(feature_data_file)
        all_data[instance]= instance_feature_data

    return all_data

def load_data_set_from_single_file(feature_data_file):
    feature_data = json.load(open(feature_data_file))
    
    return feature_data
    


def get_single_top_features(sorted_features,feature_size):
    top_features = []
    i = 0
    for (feature,v) in sorted_features:
        if i==feature_size:
            break
        i += 1
        top_features.append(feature)
        
    return top_features

def get_single_top_common_feature(sorted_positive_feature, sorted_negative_feature,feature_size):
    top_features = get_single_top_features(sorted_positive_feature,feature_size)
    top_features += get_single_top_features(sorted_negative_feature,feature_size)

    return list(set(top_features))


def get_top_features(feature_data,feature_size):
    negative_feature_frequency = {}
    positive_feature_frequency = {}



    for single_data in feature_data:
        if single_data["judgement"] == 0:
            for w in single_data["word_features"]: 
                if w not in negative_feature_frequency:
                    negative_feature_frequency[w] = 0
                negative_feature_frequency[w] += 1

           


        else:
            for w in single_data["word_features"]: 
                if w not in positive_feature_frequency:
                    positive_feature_frequency[w] = 0
                positive_feature_frequency[w] += 1



    sorted_negative_feature_frequency = sorted(negative_feature_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_positive_feature_frequency = sorted(positive_feature_frequency.items(),key = lambda x:x[1],reverse=True)

    single_top_features = get_single_top_common_feature(sorted_positive_feature_frequency, sorted_negative_feature_frequency,feature_size)


    return single_top_features


def get_all_top_feature_for_sall_data(all_data,feature_size):
    top_features = {}
    for instance in all_data:
        top_features[instance] = get_top_features(all_data[instance],feature_size)

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
        for w in strict_unique[instance]:
            print " %s" %(w)
    
    print '-'*20
    print "Unstrict features:"
    for instance in unstrict_unique:
        print "%s:" %(instance)
        for w in unstrict_unique[instance]:
            print " %s" %(w)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_data_dir")
    parser.add_argument("--feature_size","-fz",type=int,default=10)
    args=parser.parse_args()

    all_data = load_data_set(args.feature_data_dir)

    top_features = get_all_top_feature_for_sall_data(all_data,args.feature_size)

    show_unique_top_features(top_features)



if __name__=="__main__":
    main()


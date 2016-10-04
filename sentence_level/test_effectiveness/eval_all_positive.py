"""
give the evaluation for labeling all samples possitive
"""

import os
import json
import sys
import re
import argparse
import codecs
from sklearn.metrics import classification_report

def load_data_set(feature_data_dir,split_data):
    feature_data = []
    for instance in os.walk(feature_data_dir).next()[2]:
        feature_data_file = os.path.join(feature_data_dir,instance)
        instance_feature_data = load_data_set_from_single_file(feature_data_file,split_data)
        feature_data += instance_feature_data

    return feature_data

def load_data_set_from_single_file(feature_data_file,split_data):
    feature_data = json.load(open(feature_data_file))
    if split_data == 0:
        return feature_data
    elif split_data == 1:
        location_only = []
        for single_data in feature_data:
            if "LOCATION" in single_data["type"]:
                location_only.append(single_data)
        return location_only
    elif split_data == 2:
        organization_only = []
        for single_data in feature_data:
            if "ORGANIZATION" in single_data["type"]:
                organization_only.append(single_data)
        return organization_only

    else:
        raise NotImplementedError("no split method %d is implemented" %(split_data))


def get_test_judgement(test_data):
    test_judgement_vector = []

    for single_data in test_data:
        if single_data["judgement"] == 0:
            test_judgement_vector.append(0)
        else:
            test_judgement_vector.append(1)


    return test_judgement_vector



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature_data_file","-f")
    parser.add_argument("--feature_data_dir","-d")
    parser.add_argument("--split_data","-sd",type=int,default=0,choices=range(3),
        help=
        """choose to split data on stanford types or not:
                0: no split 
                1: LOCATION only
                2: ORGANIZATION only
        """)
    args=parser.parse_args()

    if not (args.feature_data_file or args.feature_data_dir):
        print "at least specify a file or a directory"
        sys.exit(-1)
    elif args.feature_data_file and args.feature_data_dir:
        print "can only specify one of them: a file or a directory"
        sys.exit(-1)
    elif args.feature_data_file:
        feature_data = load_data_set_from_single_file(args.feature_data_file,args.split_data)
    else:
        feature_data = load_data_set(args.feature_data_dir,args.split_data)

    predicted = [1]*len(feature_data)
    y = get_test_judgement(feature_data)

    print classification_report(y, predicted)

if __name__=="__main__":
    main()


"""
compare my judgement to the automatic one
"""

import os
import json
import sys
import re
import argparse
import codecs
from sklearn.metrics import classification_report


def load_json(json_file):
    return json.load(open(json_file))


def get_entities(candidate_dir):
    positive = load_json(os.path.join(candidate_dir,"positive"))
    negative = load_json(os.path.join(candidate_dir,"negative_no_location"))
    return positive, negative



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual_candidate_dir","-md",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/candidiates/new_tornado/")
    parser.add_argument("--auto_candidate_dir","-ad",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/candidiates/new_tornado/auto")
    args=parser.parse_args()

    manual_positive, manual_negative = get_entities(args.manual_candidate_dir)
    auto_positive, auto_negative = get_entities(args.auto_candidate_dir)

    auto = []
    manual = []
    false_positive = {}
    false_negative = {}
    for q in auto_positive:
        for e in auto_positive[q]:
            auto.append(1)
            if e in manual_positive[q]:
                manual.append(1)
            else:
                if q not in false_positive:
                    false_positive[q] = []
                false_positive[q].append(e)
                manual.append(0)

    for q in auto_negative:
        
        for e in auto_negative[q]:
            auto.append(0)
            if e in manual_positive[q]:
                if q not in false_negative:
                    false_negative[q] = []
                false_negative[q].append(e)
                manual.append(1)
            else:
                manual.append(0)

    y_true , y_pred = manual, auto

    print "false positive:"
    print false_positive
    print "-"*20
    print "false negative:"
    print false_negative
    print "-"*20
    

    print classification_report(y_true, y_pred)
    print "-"*20


if __name__=="__main__":
    main()


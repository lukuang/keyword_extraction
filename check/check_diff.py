"""
check the difference between auto and manual
"""

import os
import json
import sys
import re
import argparse
import codecs

def load(data_dir):
    positive_f = os.path.join(data_dir,"positive")
    negative_f = os.path.join(data_dir,"negative_no_location")
    positive = json.load(open(positive_f))
    negative = json.load(open(negative_f))
    data = []
    for q in positive:
        data[q] = []
        for e in positive[q]:
            if e not in data[q]:
                data[q].append[e]
        for e in negative:
            if e not in data[q]:
                data[q].append[e]
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manual_dir")
    parser.add_argument("new_dir")
    parser.add_argument("--dest","-d",default="diff.json")
    args=parser.parse_args()
    diff = {}
    manual = load(args.manual_dir)
    new = load(args.new_dir)
    c = 0 
    for q in new:
        diff[q] = []
        for e in new[q]:
            if e not in manual:
                if e not in diff[q]:
                    diff[q].append(e)  
                    c += 1
    print "There are %d new entities" %c

    with open(args.dest,'w') as f:
        f.write(json.dumps(diff))

if __name__=="__main__":
    main()


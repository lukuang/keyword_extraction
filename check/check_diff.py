"""
check the difference between negative_no_location
"""

import os
import json
import sys
import re
import argparse
import codecs

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manul")
    parser.add_argument("new")
    parser.add_argument("--dest","-d",default="diff.json")
    args=parser.parse_args()
    diff = {}
    manul = json.load(open(args.manul))
    new = json.load(open(args.new))
    c = 0 
    for q in new:
        diff[q] = []
        for e in new[q]:
            if e not in manul:
                if e not in diff[q]:
                    diff[q].append(e)  
                    c += 1
    print "There are %d new entities" %c

    with open(args.dest,'w') as f:
        f.write(json.dumps(diff))

if __name__=="__main__":
    main()


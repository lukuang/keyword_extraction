"""
show top verbs for positive/negative result tuples
"""

import os
import json
import sys
import re
import argparse


def get_verbs(tuple_file):
    tuples = json.load(open(tuple_file))
    verbs = {}
    for line_index in tuples:
        sub_tuples = tuples[line_index]["result_tuples"]
        for sinlge_tuple in sub_tuples:
            verb = sinlge_tuple["verb"]
            if verb not in verbs: 
                verbs[verb] = 0
            verbs[verb] += 1
    return verbs

def show_top(verbs,top):
    sorted_verbs =  sorted(verbs.items(),key = lambda x:x[1],reverse=True)
    i = 0
    for (k,v) in sorted_verbs:
        print "\t%s: %d" %(k,v)
        i += 1
        if i==top:
            print "-"*20
            break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive_file","-pf",default="positive_result_tuples")
    parser.add_argument("--negative_file","-nf",default="negative_result_tuples")
    parser.add_argument("--top","-t",type=int,default=20)
    args=parser.parse_args()

    print "negative:"
    negative_verbs = get_verbs(args.negative_file)
    show_top(negative_verbs,args.top)
    print "positive"
    positive_verbs = get_verbs(args.positive_file)
    show_top(positive_verbs,args.top)


if __name__=="__main__":
    main()


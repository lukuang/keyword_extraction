"""
show top verbs for positive/negative result tuples
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import  Model

NO_NEED = ['were','was','is','has','are','have','had','been','be']

def remap_tuples(tuple_file):
    tuples = json.load(open(tuple_file))
    remaped_tuples = {}
    for line_index in tuples:
        instance = tuples[line_index]["instance"]
        entity =  tuples[line_index]["entity"]
        identifier = instance+"/"+entity
        if identifier not in remaped_tuples:
            remaped_tuples[identifier] = []
        remaped_tuples[identifier] +=  tuples[line_index]["result_tuples"]

    return remaped_tuples


def get_verbs(tuple_result):
    verbs = {}
    for identifier in tuple_result:
        verb_model = Model(True)
        for single_tuple in tuple_result[identifier]:
            verb = single_tuple['verb']
            if verb not in NO_NEED:
                verb_model.update(text_list=[verb])
        verb_model.normalize()
        for verb in verb_model.model:
            if verb not in verbs:
                verbs[verb] = 0
            verbs[verb] += verb_model.model[verb]
    return verbs


def get_all_words(tuple_results):
    words = {}
    for identifier in tuple_result:
        word_model = Model(True)
        for single_tuple in tuple_result[identifier]:
            word_model += Sentence(single_tuple['sentence'],remove_stopwords=True).stemmed_model

        word_model.normalize()
        for word in word_model.model:
            if word not in words:
                words[word] = 0
            words[word] += word_model.model[word]
    return words

def show_top(verbs,top):
    sorted_verbs =  sorted(verbs.items(),key = lambda x:x[1],reverse=True)
    i = 0
    for (k,v) in sorted_verbs:
        print "\t%s: %f" %(k,v)
        i += 1
        if i==top:
            print "-"*20
            break




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive_temp","-pt",default="positive_temp_results")
    parser.add_argument("--negative_temp","-nt",default="negative_temp_results")
    parser.add_argument("--positive_file","-pf",default="positive_result_tuples")
    parser.add_argument("--negative_file","-nf",default="negative_result_tuples")
    parser.add_argument("--top","-t",type=int,default=20)
    parser.add_argument("--all_word","-a",action='store_true')
    args=parser.parse_args()

    print "negative:"
    if not os.path.exists(args.negative_file):
        negative_remap_tuples = remap_tuples(args.negative_temp)
        with codecs.open(args.negative_file,'w','utf-8') as f:
            f.write(json.dumps(negative_remap_tuples))
    else:
        negative_remap_tuples = json.load(open(args.negative_file))
    if(args.all_word):
        negative_words = get_all_words(negative_remap_tuples)
        show_top(negative_words,args.top)
    else:
        negative_verbs = get_verbs(negative_remap_tuples)
        show_top(negative_verbs,args.top)


    print "positive"
    if not os.path.exists(args.positive_file):
        positive_remap_tuples = remap_tuples(args.positive_temp)
        with codecs.open(args.positive_file,'w','utf-8') as f:
            f.write(json.dumps(positive_remap_tuples))
    else:
        positive_remap_tuples = json.load(open(args.positive_file))
    if (args.all_word):
        positive_words = get_all_words(positive_remap_tuples)
        show_top(positive_words,args.top)
    else:
        positive_verbs = get_verbs(positive_remap_tuples)
        show_top(positive_verbs,args.top)


if __name__=="__main__":
    main()


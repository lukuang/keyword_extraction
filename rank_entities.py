"""
rank entities of new instance basd on their type and sentence context
"""

import os
import json
import sys
import re
import argparse
from myUtility.corpus import *

TYPES = {
    'LOCATION':[
        "LOCATION",
        "FACILITY"
    ],
    'ORGANIZATION':[
        "ORGANIZATION"
    ]
}

def get_sentence_window(words,sentence,windows):
    """
    Use the whole sentence as the context
    """
    #print sentence
    for w in words:
        
        if sentence.find(w) != -1:
            temp_sentence = sentence
            #print "found sentence %s" %temp_sentence
            for t in words:
                if temp_sentence.find(t) != -1:
                    temp_sentence = temp_sentence.replace(t,"")
            #print "after process %s" %temp_sentence
            if w not in windows:
                windows[w] = Sentence(temp_sentence,remove_stopwords=True).stemmed_model
            else:
                windows[w] += Sentence(temp_sentence,remove_stopwords=True).stemmed_model


def get_type_model(type_model_file):
    """
    get models for each type of entities    
    """

    data = {}
    tag = ""
    with open(type_model_file,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\t(.+?):(.+)$",line)
                if m is not None:
                    data[tag][m.group(1)] = float(m.group(2))
                    
                else:
                    print "line did not match:"
                    print line
    for tag in data:
        data[tag] = Model(True,text_dict=data[tag], need_stem = True, input_stemmed = True)
    return data


def get_files(article_dir):
    all_files = []
    sub_dirs = os.walk(article_dir).next()[1]
    for d in sub_dirs:
        d = os.path.join(article_dir,d)
        all_files += [os.path.join(d,f) for f in os.walk(d).next()[2]]
    return all_files


def get_all_sentence_windows(documents,entity_candidates):
    windows = {}
    
    words = []
    for entity_type in entity_candidates:
        words += entity_candidates[entity_type]
        if entity_type not in windows:
            windows[entity_type] = {}
    #print "there are %d words" %(len(words))
    temp_windows = {}
    for single_file in documents:
        #if single_file!='clean_text/Oklahoma/2013-05-21/41-0':
        #    continue
        print "process file %s" %single_file
        for sentence in documents[single_file].sentences:

            get_sentence_window(words,sentence.text,temp_windows)
    #print "there are %d words in temp_windows" %(len(temp_windows))
    for w in temp_windows:
        for entity_type in entity_candidates:
            if w in entity_candidates[entity_type]:
                windows[entity_type][w] = temp_windows[w]
                break
    for t in windows:
        print "there are %d words" %(len(windows[t]))
    return windows


def get_candidate_models(entity_candidates,article_dir):


    all_files = get_files(article_dir)
    documents = {}
    for single_file in all_files:
        documents[single_file] = Document(single_file,file_path = single_file)
    
    windows = get_all_sentence_windows(documents,entity_candidates)
    return windows



def get_candidates(candiate_file,candiate_top):
    """
    get top ranked entity candidates for
    an event    
    """

    data = {}
    tag = ""
    with open(candiate_file,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\t(.+?):(.+)$",line)
                if m is not None:
                    data[tag][m.group(1)] = float(m.group(2))
                    
                else:
                    print "line did not match:"
                    print line
    for k in data.keys():
        if k not in TYPES:
            data.pop(k,None)
        else:
            #print "for type %s" %k
            sorted_sub = sorted(data[k].items(),key = lambda x:x[1], reverse=True)
            data[k] = {}
            i = 0
            for (key,value) in sorted_sub:
                #print "add %s with value %f" %(key,value)
                data[k][key] = value
                i += 1
                if i>=candiate_top:
                    break

    return data


def rank_entities(candidate_models,type_models,output_top):
    output = {}
    for entity_type in candidate_models:
        for annotated_type in TYPES[entity_type]:
            print "for %s:" %annotated_type
            output[annotated_type] = {}
            temp = {}
            for entity in candidate_models[entity_type]:
                sim = type_models[annotated_type].cosine_sim(candidate_models[entity_type][entity])
                temp[entity] = sim
            sorted_candidates = sorted(temp.items(), key = lambda x:x[1],reverse=True)
            i = 0
            for (k,v) in sorted_candidates:
                print "\t%s %f" %(k,v)
                output[annotated_type][k] = v
                i+=1
                if i >= output_top:
                    break
            print "-"*20


    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candiate_file")
    parser.add_argument("article_dir")
    parser.add_argument("dest")
    parser.add_argument("type_model_file")
    parser.add_argument("--candiate_top",'-ct',type=int,default=20)
    parser.add_argument("--output_top",'-ot',type=int,default=20)

    args=parser.parse_args()

    entity_candidates = get_candidates(args.candiate_file,args.candiate_top)
    candidate_models = get_candidate_models(entity_candidates,args.article_dir)
    
    type_models = get_type_model(args.type_model_file)

    output = rank_entities(candidate_models,type_models,args.output_top)
    #print json.dumps(output,indent=4)



if __name__=="__main__":
    main()


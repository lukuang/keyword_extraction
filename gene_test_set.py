"""
generate feature vector for testing
"""

import os
import json
import sys
import re
import argparse
from myUtility.corpus import *
import copy
from get_entity_cate import get_cate_for_entity_list
import codecs

TYPES = {
    'LOCATION':[
        "LOCATION",
        "FACILITY"
    ],
    'ORGANIZATION':[
        "ORGANIZATION"
    ]
}

def get_sentence_window(entity_map,sentence,windows):
    """
    Use the whole sentence as the context
    """
    #print sentence
    for w in entity_map:
        
        if sentence.find(w) != -1:
            temp_sentence = sentence
            #print "found sentence %s" %temp_sentence
            for t in entity_map:
                if entity_map[t]:
                    temp_sentence = temp_sentence.replace(entity_map[t],"")
                elif temp_sentence.find(t) != -1:
                    temp_sentence = temp_sentence.replace(t,"")
            #print "after process %s" %temp_sentence
            if entity_map[w]:
                w = entity_map[w]
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


def get_entity_map(words):
    entity_map = {}
    multiple = []
    for w in words:
        entity_map[w] = None
        for e in words:
            if w != e:
                if e.find(w)!=-1:
                    if entity_map[w] != None:
                        if entity_map[w].find(e) != -1:
                            pass
                        elif  e.find(entity_map[w]) != -1:
                            entity_map[w] = e
                        else:
                            multiple.append(w)
                            #print "For %s, there are two none substring candidates: %s %s" %(w, e,entity_map[w] )
                            #sys.exit(-1)
                    else:
                        entity_map[w] = e
    # delete the ones that have multiple possibilities
    for w in multiple:
        entity_map.pop(w, None)

    #print json.dumps(entity_map)
    #sys.exit(-1)
    return entity_map                        



def get_all_sentence_windows(documents,entity_candidates,requried_type):
    windows = {}
    

    words = entity_candidates[requried_type]
    print "there are %d words" %(len(words))


    entity_map = get_entity_map(words)

    for single_file in documents:
        #if single_file!='clean_text/Oklahoma/2013-05-21/41-0':
        #    continue
        print "process file %s" %single_file
        for sentence in documents[single_file].sentences:
            get_sentence_window(entity_map,sentence.text,windows)

    print "there are %d words in windows" %(len(windows))

    return windows


def get_candidate_models(entity_candidates,article_dir,requried_type):


    all_files = get_files(article_dir)
    documents = {}
    for single_file in all_files:
        documents[single_file] = Document(single_file,file_path = single_file)
    
    windows = get_all_sentence_windows(documents,entity_candidates,requried_type)
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
                    frequency = float(m.group(2))
                    #if frequency <= 1.0:
                    #    continue
                    #else:
                    data[tag][m.group(1)] = frequency
                    
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

def get_feature_vector(all_words,all_cates,model,single_cate_info):
    feature_vector = []
    for w in all_words:
        if w in model:
            feature_vector.append(model[w])
        else:
            feature_vector.append(0)
    if single_cate_info:
        for cate in all_cates:
            if cate in  single_cate_info:
                feature_vector.append(1)
            else:
                feature_vector.append(0)
    else:
        feature_vector += [0]*len(all_cates)

    return feature_vector


def main():
    reload(sys)
    sys.setdefaultencoding('UTF8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candiate_file")
    parser.add_argument("article_dir")
    parser.add_argument("feature_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("--candiate_top",'-ct',type=int,default=20)
    parser.add_argument("--type",'-t',default="ORGANIZATION")

    args=parser.parse_args()

    entity_candidates = get_candidates(args.candiate_file,args.candiate_top)
    candidate_models = get_candidate_models(entity_candidates,args.article_dir,args.type)
    
    all_words = json.load(open(os.path.join(args.feature_dir,"all_words")))
    all_cates = json.load(open(os.path.join(args.feature_dir,"all_cates")))

    cate_info = get_cate_for_entity_list(candidate_models.keys())

    test_candidates = []
    test_vector = []
    for entity in candidate_models:
        candidate_models[entity].normalize()
        test_candidates.append(entity)
        feature_vector = get_feature_vector(all_words,all_cates,candidate_models[entity].model,cate_info[entity])
        test_vector.append(feature_vector)

    with codecs.open(os.path.join(args.dest_dir,"test_vector"),"w",'utf-8') as f:
        f.write(json.dumps(test_vector))
    with codecs.open(os.path.join(args.dest_dir,"test_candidates"),"w",'utf-8') as f:
        f.write(json.dumps(test_candidates))

    #print json.dumps(output,indent=4)



if __name__=="__main__":
    main()


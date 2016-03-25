"""
rank entities of new instance basd on their type and sentence context
"""

import os
import json
import sys
import re
import argparse
from myUtility.corpus import *
import copy




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



def get_all_sentence_windows(documents,entity_candidates):
    windows = {}
    
    words = []
    for entity_type in entity_candidates:
        words += entity_candidates[entity_type]
        if entity_type not in windows:
            windows[entity_type] = {}
    print "there are %d words" %(len(words))


    entity_map = get_entity_map(words)
    temp_windows = {}
    for single_file in documents:
        #if single_file!='clean_text/Oklahoma/2013-05-21/41-0':
        #    continue
        print "process file %s" %single_file
        for sentence in documents[single_file].sentences:

            get_sentence_window(entity_map,sentence.text,temp_windows)
    print "there are %d words in temp_windows" %(len(temp_windows))
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

def get_sub_features(type_model_file,size):
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
                i = 0
            else:
                m = re.search("^\t(.+?):(.+)$",line)
                if i>=size:
                    continue
                if m is not None:
                    data[tag][m.group(1)] = float(m.group(2))
                    i += 1

                    
                else:
                    print "line did not match:"
                    print line
    return data





def dict_check(original, type_model):
    for w in original.model:
        if w not in type_model.model:
            print "MISSING %s" %w
            sys.exit(-1)
        else:
            if original.model[w] != type_model.model[w]:
                print "value difference!"
                print "for %s: %f and %f" %(w,original.model[w],type_model.model[w])
                sys.exit(-1)

def rank_entities(candidate_models,positive_models,negative_models,output_top,alpha):
    output = {}
    #for tag in type_models:
    #    type_models[tag].normalize()
    #original = copy.deepcopy(type_models)
    for entity_type in candidate_models:
        for annotated_type in TYPES[entity_type]:
            print "for %s:" %annotated_type
            output[annotated_type] = {}
            temp = {}
            for entity in candidate_models[entity_type]:
                sim = alpha*candidate_models[entity_type][entity].cosine_sim(positive_models[annotated_type])
                sim -= (1-alpha)*candidate_models[entity_type][entity].cosine_sim(negative_models[annotated_type])
                temp[entity] = sim
                #dict_check(original[annotated_type], type_models[annotated_type])
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
    reload(sys)
    sys.setdefaultencoding('UTF8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candiate_file")
    parser.add_argument("article_dir")
    parser.add_argument("positive_model_file")
    parser.add_argument("negative_model_file")
    parser.add_argument("alpha",type=int)
    parser.add_argument("--candiate_top",'-ct',type=int,default=20)
    parser.add_argument("--output_top",'-ot',type=int,default=20)
    parser.add_argument("--size","-t",type=int,default=20,
        help="the number of top terms in positive/negative models that will be used")

    args=parser.parse_args()

    alpha = 0.1*args.alpha
    entity_candidates = get_candidates(args.candiate_file,args.candiate_top)
    candidate_models = get_candidate_models(entity_candidates,args.article_dir)
    

    positive_models = get_sub_features(args.positive_model_file,args.size)
    negative_models = get_sub_features(args.negative_model_file,args.size)

    output = rank_entities(candidate_models,positive_models,negative_models,args.output_top,alpha)
    #print json.dumps(output,indent=4)



if __name__=="__main__":
    main()


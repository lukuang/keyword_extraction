"""
get the feature vectors of entities
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Document, Sentence
from get_entity_cate import get_cate_for_entity_list

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






def get_text_window(words,document,windows,window_size):
    """
    Use a window as the context
    """
    spaces = [m.start() for m in re.finditer(' ', document)]
    for w in words:
        w_size = w.count(" ")+1
        if w not in windows: 
            windows[w] = []
        for m in re.finditer(w,document):
            start = m.start()-1
            if start in spaces:
                w_start = max(0,spaces.index(start)-window_size)
                w_end = min(len(spaces)-1,spaces.index(start)+window_size+w_size)
                #window_string = document[spaces[w_start]:spaces[w_end]]
                window_string = document[spaces[w_start]:m.start()-1] +" "+ document[m.end()+1:spaces[w_end]]
            else:
                w_end = min(len(spaces)-1,window_size+w_size-1)
                #window_string = document[0:spaces[w_end]]
                window_string = document[m.end()+1:spaces[w_end]]
            windows[w].append(Sentence(window_string,remove_stopwords=True).stemmed_text)




def get_files(a_dir):
    all_files = os.walk(a_dir).next()[2]
    files = []
    for f in all_files:
        files.append( f )
    return files

def show_documents(documents):
    for instance in documents:
        print "%s:" %instance
        for single_file in documents[instance]:
            for sentence in documents[instance][single_file].sentences:
                print "%s:%s" %(single_file,sentence.text)
            print "-"*20
    

def get_all_sentence_windows(documents,entities_judgement,negative_candidates,required_type):
    windows = {}
    for instance in documents:
        print "%s:" %instance
        words = []
        words += negative_candidates[instance][required_type]
        words += entities_judgement[instance][required_type]
        windows[instance] = {}

        temp_windows = {}
        for single_file in documents[instance]:
            print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_sentence_window(words,sentence.text,temp_windows)

        windows[instance] = temp_windows
        # for w in temp_windows:
        #     for entity_type in entities_judgement[instance]:
        #         if w in entities_judgement[instance][entity_type]:
        #             windows[entity_type][w] = temp_windows[w]
        #             break
        #     for entity_type in negative_candidates[instance]:
        #         if w in negative_candidates[instance][entity_type]:
        #             windows[entity_type][w] = temp_windows[w]
        #             break
    return windows


def get_documents(instance_names,top_dir,disaster_name):
    documents = {}
    for instance in instance_names:
        print "for %s" %instance
        source_dir = os.path.join(top_dir,"clean_text",disaster_name,instance)
        
        sub_dirs = os.walk(source_dir).next()[1]
        documents[instance] = {}
        for a_dir in sub_dirs:
            date_dir = os.path.join(source_dir,a_dir)
            for single_file in get_files(date_dir):
                #print "open file %s" %os.path.join(date_dir,single_file)
                single_file = os.path.join(date_dir,single_file)
                documents[instance][single_file] = Document(single_file,file_path = single_file)
    return documents


def get_json(source,required_type,positive_entities):
    data = {}
    tag = ""
    with open(source,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\t(.+?):(.+)$",line)
                if m is not None:
                    entity = m.group(1)
                    if entity not in positive_entities:
                        data[tag][entity] = float(m.group(2))
                else:
                    print "line did not match:"
                    print line

    
    return data[required_type]



def get_negative_candidates(instance_names,entity_dir,required_type,entities_judgement):
    negative_candidates = {}
    for instance in instance_names:
        negative_candidates[instance] = {}
        entity_file = os.path.join(entity_dir,instance,"df")
        negative_candidates[instance][required_type] = get_json(entity_file,required_type
                            ,entities_judgement[instance][required_type])
    return negative_candidates



def get_entities_judgement(entity_judgement_file,required_type,small):
    data = ""
    with open(entity_judgement_file) as f:
        data = f.read()

    entities_judgement_data = json.loads(data)
    entities_judgement = {}
    for single in entities_judgement_data:
        if small and len(single[required_type]) == 0:
            continue    
        q = single["query_string"]
        entities_judgement[q] = {required_type:single[required_type]}
    return entities_judgement


def get_sub_features(type_model_file,size,required_type):
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
                if m is not None and i<size:
                    data[tag][m.group(1)] = float(m.group(2))
                    i += 1

                    
                else:
                    print "line did not match:"
                    print line
    return data[required_type]

def get_all_words(positive_file,negative_file,size,required_type):
    words = get_sub_features(positive_file,size,required_type)
    words.update(get_sub_features(negative_file,size,required_type) )
    return words.keys()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("--top_dir",'-tp',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data')
    parser.add_argument("--negative_file",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/models/negative_entities/')
    parser.add_argument("--positive_file",'-pf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/models/entity_type_models')
    parser.add_argument("--size",'-si',type=int,default=20)
    parser.add_argument("dest_dir")
    parser.add_argument("--type",'-t',default="ORGANIZATION")
    parser.add_argument("--normalize",'-n',action="store_true")
    parser.add_argument("--small",'-s',action="store_true")
    parser.add_argument("--entity_judgement_file","-e",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/entities_judgement.json")
    args=parser.parse_args()
    
    

    entities_judgement = get_entities_judgement(args.entity_judgement_file,args.type,args.small)

    args.top_dir = os.path.abspath(args.top_dir)
    instance_names = entities_judgement.keys()
    documents = get_documents(instance_names,args.top_dir,args.disaster_name)

    entity_dir = os.path.join(args.top_dir,"entity",args.disaster_name)
    negative_candidates = get_negative_candidates(instance_names,entity_dir,args.type,entities_judgement)   



    windows = get_all_sentence_windows(documents,entities_judgement,negative_candidates, args.type)
  
    all_entities = []
    pure_entities = set()
    for instance in windows:
        for entity in windows[instance]:
            pure_entities.add(entity)

    all_words = get_all_words(args.positive_file,args.negative_file,args.size,args.type)
    all_features = all_words

    cate_info = get_cate_for_entity_list(list(pure_entities) )
    all_cates = []
    for entity in cate_info:
        if cate_info[entity]:
            for cate in cate_info[entity]:
                if cate not in all_cates:
                    all_cates.append(cate)

    all_features += all_cates
   

    judgement_vector = []
    feature_vector = []



    for instance in entities_judgement:
        for entity in negative_candidates[instance][args.type]:
            all_entities.append(instance+"/"+entity)
            judgement_vector.append(-1)
            single_feature_vectore = []
            if args.normalize:
                windows[instance][entity].normalize()
            for w in all_words:
                if w in windows[instance][entity].model:
                    single_feature_vectore.append(windows[instance][entity].model[w])
                else:
                    single_feature_vectore.append(0)

            if cate_info[entity]:
                for cate in all_cates:
                    if cate not in cate_info[entity]:
                        single_feature_vectore.append(0)
                    else:
                        single_feature_vectore.append(1)
            else:
                single_feature_vectore += [0]*len(all_cates)
            feature_vector.append(single_feature_vectore)


        for entity in entities_judgement[instance][args.type]:
            all_entities.append(instance+"/"+entity)
            judgement_vector.append(1)
            single_feature_vectore = []
            if args.normalize:
                windows[instance][entity].normalize()
            for w in all_words:

                if w in windows[instance][entity].model:
                    single_feature_vectore.append(windows[instance][entity].model[w])
                else:
                    single_feature_vectore.append(0)

            if cate_info[entity]:
                for cate in all_cates:
                    if cate not in cate_info[entity]:
                        single_feature_vectore.append(0)
                    else:
                        single_feature_vectore.append(1)
            else:
                single_feature_vectore += [0]*len(all_cates)
            feature_vector.append(single_feature_vectore)

     



    with codecs.open(os.path.join(args.dest_dir,"feature_vector"),"w","utf-8") as f:
        f.write(json.dumps(feature_vector))
    #print json.dumps(windows,indent=4)
    with codecs.open(os.path.join(args.dest_dir,"judgement_vector"),"w","utf-8") as f:
        f.write(json.dumps(judgement_vector))
    with codecs.open(os.path.join(args.dest_dir,"all_entities"),"w","utf-8") as f:
        f.write(json.dumps(all_entities))
    with codecs.open(os.path.join(args.dest_dir,"all_words"),"w","utf-8") as f:
        f.write(json.dumps(all_words))
    with codecs.open(os.path.join(args.dest_dir,"all_cates"),"w","utf-8") as f:
        f.write(json.dumps(all_cates))
    print "finished"

if __name__=="__main__":
    main()


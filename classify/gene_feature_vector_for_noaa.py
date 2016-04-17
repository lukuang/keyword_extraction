"""
get the feature vectors of entities
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Document, Sentence, Model
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
    

def get_all_sentence_windows(documents,positive_candidates,negative_candidates):
    windows = {}
    for instance in documents:
        print "%s:" %instance
        if instance not in negative_candidates:
            continue
        words = []
        words += negative_candidates[instance]
        words += positive_candidates[instance]
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
                m = re.search("^\t(.+?):(\d+(\.\d+)?)$",line)
                if m is not None:
                    entity = m.group(1)
                    if entity not in positive_entities:
                        data[tag][entity] = float(m.group(2))
                else:
                    print "line did not match:"
                    print line

    
    return data[required_type]


def get_single_model(candidate_dir):
    candidate_models = {}
    files = os.walk(candidate_dir).next()[2]
    for a_file in files:
        candidate_models[a_file] = {}
        temp_model = json.load(open(os.path.join(candidate_dir,a_file)))
        for w in temp_model:
            if w not in candidate_models:
                temp = Model(True,text_dict=temp_model[w], need_stem = True, input_stemmed = True)
                temp.normalize()
                candidate_models[a_file][w] = temp

    return candidate_models


def get_model(positive_dir, negative_dir):
    positive_model = get_single_model(positive_dir)
    negative_model = get_single_model(negative_dir)
    return positive_model, negative_model





def get_sub_features(model,size):
    """
    get top terms as features   
    """

    data = Model(True, need_stem = True, input_stemmed = True)
    for instance in model:
        for w in model[instance]:
            data += model[instance][w]
    data.normalize()
    terms = data.model
    sorted_terms = sorted(terms.items(),key = lambda x:x[1],reverse=True)
    i = 0
    features = {}
    for (w,v) in sorted_terms:
        features[w] = v
        i += 1
        if i == size:
            break
    return features


def get_cate_info(pure_entities,cate_info_file):
    if os.path.exists(cate_info_file):
        cate_info = json.load(open(cate_info_file))
    else:
        cate_info = get_cate_for_entity_list(list(pure_entities) )
        with codecs.open(cate_info_file,'w','utf-8') as f:
            f.write(json.dumps(cate_info)) 
    return cate_info


def get_all_word_features(positive_model,negative_model,size):
    words = get_sub_features(positive_model,size)
    words.update(get_sub_features(negative_model,size) )
    return words.keys()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative_dir",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/model/negative')
    parser.add_argument("--cate_info_file",'-cf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/model/cate_info_file')
    parser.add_argument("--positive_dir",'-pf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/model/positive')
    parser.add_argument("--size",'-si',type=int,default=20)
    parser.add_argument("dest_dir")
    args=parser.parse_args()
    
    

    positive_model,negative_model = get_model(args.positive_dir,args.negative_dir)



  
    
    pure_entities = set()
    for instance in positive_model:
        for entity in positive_model[instance]:
            pure_entities.add(entity)
        for entity in negative_model[instance]:
            pure_entities.add(entity)


    all_word_features = get_all_word_features(positive_model,negative_model,args.size)
    all_features = all_word_features


    cate_info = get_cate_info(pure_entities,args.cate_info_file)
    
    all_cates = []
    for entity in cate_info:
        if cate_info[entity]:
            for cate in cate_info[entity]:
                if cate not in all_cates:
                    all_cates.append(cate)

    all_features += all_cates
   

    judgement_vector = []
    feature_vector = []

    all_entities = []

    for instance in positive_model:
        for entity in negative_model[instance]:
            all_entities.append(instance+"/"+entity)
            judgement_vector.append(-1)
            single_feature_vectore = []
            
            for w in all_word_features:
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


        for entity in positive_model[instance]:
            all_entities.append(instance+"/"+entity)
            judgement_vector.append(1)
            single_feature_vectore = []
            if args.normalize:
                windows[instance][entity].normalize()
            for w in all_word_features:

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
    with codecs.open(os.path.join(args.dest_dir,"all_word_features"),"w","utf-8") as f:
        f.write(json.dumps(all_word_features))
    with codecs.open(os.path.join(args.dest_dir,"all_cates"),"w","utf-8") as f:
        f.write(json.dumps(all_cates))
    print "finished"

if __name__=="__main__":
    main()


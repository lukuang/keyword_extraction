"""
use words of whole sentence as features
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Sentence, Document, Model
from get_entity_cate import get_cate_for_entity_list

def read_single_file(file_path, required_entity_types):
    data = {}
    with open(file_path,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = []
            else:
                m = re.search("^\t(.+?):(\d+(\.\d+)?)$",line)
                if m is not None:
                    data[tag].append(m.group(1))

    single_type_mapping = {}
    for tag in required_entity_types:
        try:
            for entity in data[tag]:
                if entity not in single_type_mapping:
                    single_type_mapping[entity] = []
                single_type_mapping[entity].append(tag)
        except KeyError:
            pass

    return single_type_mapping

def get_entity_type_mapping(news_entity_dir,required_entity_types,required_file_name):
    entity_type_mapping = {}
    eids = os.walk(news_entity_dir).next()[1]
    #original_entities.keys()
    for eid in eids:
        entity_file = os.path.join(news_entity_dir,eid,required_file_name)
        entity_type_mapping[eid] = read_single_file(entity_file, required_entity_types)
    return entity_type_mapping




def get_candidates(candidate_file):
    candidates = json.load(open(candidate_file))
    return candidates


def get_files(a_dir):
    all_files = os.walk(a_dir).next()[2]
    files = []
    for f in all_files:
        files.append( f )
    return files


def get_documents(instance_names,text_dir):
    documents = {}
    for instance in instance_names:
        print "for %s" %instance
        source_dir = os.path.join(text_dir,instance)
        
        sub_dirs = os.walk(source_dir).next()[1]
        documents[instance] = {}
        for a_dir in sub_dirs:
            date_dir = os.path.join(source_dir,a_dir)
            for single_file in get_files(date_dir):
                #print "open file %s" %os.path.join(date_dir,single_file)
                single_file = os.path.join(date_dir,single_file)
                documents[instance][single_file] = Document(single_file,file_path = single_file)
    return documents



def get_sentence_window(entity_map,sentence,windows):
    """
    Use the whole sentence as the context
    """
    #print sentence
    for w in entity_map:
        # if w != u'Jefferson County':
        #     continue
        # else:
        #     pass
        #     print "YES!"
        if sentence.find(w) != -1:
            #print "found sentence %s" %sentence
            if entity_map[w]:
                w = entity_map[w]
            if w not in windows:
                windows[w] = Model(True,need_stem=True)
            
            windows[w] += Sentence(re.sub("\n"," ",sentence),remove_stopwords=True).stemmed_model




def get_nochange_map(words):
    entity_map = {}
    for w in words:
        entity_map[w] = w
    #print json.dumps(entity_map)
    return entity_map



def get_all_sentence_windows(documents,candidates,word_feature_size,entity_type_mapping):
    all_word_features = {}
    entities = set()
    feature_data = {}
    one_type_mapping = []
    for instance in documents:
        print "%s:" %instance
        # if instance!='59890':
        #     continue
        words = set()

        words.update(candidates[instance])

        #words += entities_judgement[instance][required_type]
        entity_map = get_nochange_map(words)

        temp_windows = {}
        for single_file in documents[instance]:
            print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_sentence_window(entity_map,sentence.text,temp_windows)


        for entity in candidates[instance]:
            try:
                temp_windows[entity].normalize()
                identifier = instance+"/"+entity
                feature_data[identifier] = {
                    "entity": entity,
                    "word_features": temp_windows[entity].model

                }
                for w in temp_windows[entity].model:
                    if w not in all_word_features:
                        all_word_features[w] = 0
                    all_word_features[w] += temp_windows[entity].model[w]

                entities.add(entity)
                one_type_mapping.append(entity_type_mapping[instance][entity])

            except KeyError:
                print "cannot find entity %s" %(w)
                print 'store to remove later'

    top_word_features =  get_top_word_features(all_word_features,word_feature_size)

        
    return top_word_features,entities,feature_data, one_type_mapping


def get_top_word_features(all_word_features,word_feature_size):
    top_word_features = []
    i = 0
    sorted_word_features =  sorted(all_word_features.items(),key = lambda x:x[1],reverse=True)
    for (word,v) in sorted_word_features:
        i += 1
        top_word_features.append(word)
        if i==word_feature_size:
            break
    return top_word_features

def get_cate_info(pure_entities,cate_info_file):
    if os.path.exists(cate_info_file):
        cate_info = json.load(open(cate_info_file))
        new_cate = []
        for entity in pure_entities:
            if entity not in cate_info:
                new_cate.append(entity)
        if len(new_cate)!=0:
            cate_info.update(get_cate_for_entity_list(new_cate))
        with codecs.open(cate_info_file,'w','utf-8') as f:
            f.write(json.dumps(cate_info)) 
    else:
        cate_info = get_cate_for_entity_list(list(pure_entities) )
        with codecs.open(cate_info_file,'w','utf-8') as f:
            f.write(json.dumps(cate_info)) 
    return cate_info

def get_top_cate_for_single_entity_type(cate_info,entities,cate_feature_size):
    cate_hash = {}
    for entity in entities:
        if cate_info[entity]:
            for cate in cate_info[entity]:
                if cate not in cate_hash:
                    cate_hash[cate] = 0
                cate_hash[cate] += 1
    sorted_cates = sorted(cate_hash.items(),key = lambda x : x[1],reverse=True)
    i = 0
    all_cates = []
    for (k,v) in sorted_cates:
        all_cates.append(k)
        i += 1
        if i==cate_feature_size:
            #print "break when i is",i
            break
    #print "return %d category features" %(len(all_cates) )
    return all_cates


def get_cate_features(cate_info, cate_feature_size,negative_entities, positive_entities):
    all_cates = set()

    all_cates.update(get_top_cate_for_single_entity_type(cate_info,negative_entities,cate_feature_size))
    all_cates.update(get_top_cate_for_single_entity_type(cate_info,positive_entities,cate_feature_size))
    
    print "return %d category features" %(len(all_cates) )
    return list(all_cates)





def add_data_to_set(feature_data,all_word_features,all_cates,judgement_vector,feature_vector,all_entities,cate_info,is_positive):
    for identifier in feature_data:
        if is_positive:
            judgement_vector.append(1)
        else:
            judgement_vector.append(0)

        entity = feature_data[identifier]["entity"]
        words = feature_data[identifier]["word_features"]

        all_entities.append(entity)

        single_feature_vector = get_single_feature_vector(words,entity,all_word_features,all_cates,cate_info)

        feature_vector.append(single_feature_vector)




def get_single_feature_vector(words,entity,all_word_features,all_cates,cate_info):
    single_feature_vector = []

    single_feature_vector += get_word_feature_vector(words,all_word_features)
    single_feature_vector += get_cate_feature_vector(entity,cate_info,all_cates)

    

    return single_feature_vector




def get_word_feature_vector(words,all_word_features):
    word_feature_vector = []

    for word in all_word_features:
        if word in words:
            word_feature_vector.append(words[word])
        else:
            word_feature_vector.append(0)

    return word_feature_vector



def get_cate_feature_vector(entity,cate_info,all_cates):
    cate_feature_vector = []
    if cate_info[entity]:
        for cate in all_cates:
            if cate not in cate_info[entity]:
                cate_feature_vector.append(0)
            else:
                cate_feature_vector.append(1)
    else:
        cate_feature_vector += [0]*len(all_cates)

    return cate_feature_vector




def output(all_word_features,all_cates,judgement_vector,feature_vector,all_entities,dest_dir,all_type_mapping):

    with codecs.open(os.path.join(dest_dir,"all_word_features"),"w",'utf-8') as f:
        f.write(json.dumps(all_word_features))

    with codecs.open(os.path.join(dest_dir,"all_cates"),"w",'utf-8') as f:
        f.write(json.dumps(all_cates))


    with codecs.open(os.path.join(dest_dir,"judgement_vector"),"w",'utf-8') as f:
        f.write(json.dumps(judgement_vector))


    with codecs.open(os.path.join(dest_dir,"feature_vector"),"w",'utf-8') as f:
        f.write(json.dumps(feature_vector))

    with codecs.open(os.path.join(dest_dir,"all_entities"),"w",'utf-8') as f:
        f.write(json.dumps(all_entities))

    with codecs.open(os.path.join(dest_dir,"all_type_mapping"),"w",'utf-8') as f:
        f.write(json.dumps(all_type_mapping))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text_dir",'-tp',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/clean_text/noaa')
    parser.add_argument("positive_candidate_file")
    parser.add_argument("negative_candidate_file")
    parser.add_argument("cate_info_file")
    parser.add_argument("dest_dir")
    parser.add_argument("--word_feature_size","-wz",type=int,default=50)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=30)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')


    args=parser.parse_args()
    
    positive_candidates= get_candidates(args.positive_candidate_file)
    negative_candidates= get_candidates(args.negative_candidate_file)

    positive_instance_names = positive_candidates.keys()
    negative_instance_names = negative_candidates.keys()

    negative_documents = get_documents(negative_instance_names,args.text_dir)
    positive_documents = get_documents(positive_instance_names,args.text_dir)
    

    entity_type_mapping = get_entity_type_mapping(args.news_entity_dir,args.required_entity_types,args.required_file_name)


    all_word_features = set()
    entities = set()
    all_type_mapping = []

    negative_word_features,negative_entities,negative_features, negative_type_mapping =\
            get_all_sentence_windows(negative_documents,negative_candidates,args.word_feature_size,entity_type_mapping)

    all_word_features.update(negative_word_features)
    entities.update(negative_entities)
    all_type_mapping += negative_type_mapping

    positive_word_features,positive_entities,positive_features, positive_type_mapping =\
            get_all_sentence_windows(positive_documents,positive_candidates,args.word_feature_size,entity_type_mapping)

    all_word_features.update(positive_word_features)
    entities.update(positive_entities)
    all_type_mapping += positive_type_mapping


    cate_info = get_cate_info(entities,args.cate_info_file)
    
    
    all_word_features = list(all_word_features)
    all_cates = get_cate_features(cate_info,args.cate_feature_size,negative_entities,positive_entities)
    #all_features += all_cates

    judgement_vector = []
    feature_vector = []
    all_entities = []

    add_data_to_set(negative_features,all_word_features,all_cates,judgement_vector,feature_vector,all_entities,cate_info,False)
    add_data_to_set(positive_features,all_word_features,all_cates,judgement_vector,feature_vector,all_entities,cate_info,True)

    output(all_word_features,all_cates,judgement_vector,feature_vector,all_entities,args.dest_dir,all_type_mapping)




if __name__=="__main__":
    main()


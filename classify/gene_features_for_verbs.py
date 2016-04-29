"""
get verb and category features for result tuple data
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Sentence, Model
from get_entity_cate import get_cate_for_entity_list


def process_result_tuple(result_tuple_files,verb_size):
    verbs = {}
    entities = set()
    feature_data = {}
    result_tuples = json.load(open(result_tuple_files))

    for identifier in result_tuples:
        m = re.search('\d+/(\w+)', identifier)
        if m is not None:
            entity = m.group(1)
            entities.add(entity)
        else:
            print "Wrong identifier!"
            sys.exit(-1)

        verb_model = Model(True)
        for single_tuple in result_tuples[identifier]:
            verb = single_tuple['verb']
            verb_model.update(text_list=[verb])
        verb_model.normalize()

        feature_data[identifier] = {
            "entity":entity,
            "verbs":verb_model.model
        }

        for verb in verb_model.model:
            if verb not in verbs:
                verbs[verb] = 0
            verbs[verb] += verb_model.model[verb]

    top_verbs =  get_top_verbs(verbs,verb_size)

    return top_verbs,entities,feature_data


def get_top_verbs(verbs,verb_size):
    top_verbs = []
    i = 0
    sorted_verbs =  sorted(verbs.items(),key = lambda x:x[1],reverse=True)
    for (verb,v) in sorted_verbs:
        i += 1
        top_verbs.append(verb)
        if i==verb_size:
            break
    return top_verbs

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


def get_cate_features(cate_info, cate_feature_size):
    all_cates = []
    cate_hash = {}
    for entity in cate_info:
        if cate_info[entity]:
            for cate in cate_info[entity]:
                if cate not in cate_hash:
                    cate_hash[cate] = 0
                cate_hash[cate] += 1
    sorted_cates = sorted(cate_hash.items(),key = lambda x : x[1],reverse=True)
    i = 0
    for (k,v) in sorted_cates:
        all_cates.append(k)
        i += 1
        if i==cate_feature_size:
            print "break when i is",i
            break
    print "return %d category features" %(len(all_cates) )
    return all_cates





def add_data_to_set(feature_data,all_verbs,all_cates,judgement_vector,feature_vector,cate_info,is_positive):
    for identifier in feature_data:
        if is_positive:
            judgement_vector.append(1)
        else:
            judgement_vector.append(0)

        entity = feature_data[identifier]["entity"]
        verbs = feature_data[identifier]["verbs"]

        single_feature_vector = get_single_feature_vector(verbs,entity,all_verbs,all_cates,cate_info)

        feature_vector.append(single_feature_vector)




def get_single_feature_vector(verbs,entity,all_verbs,all_cates,cate_info):
    single_feature_vector = []

    single_feature_vector += get_verb_feature_vector(verbs,all_verbs)
    single_feature_vector += get_cate_feature_vector(entity,cate_info,all_cates)

    

    return single_feature_vector




def get_verb_feature_vector(verbs,all_verbs):
    verb_feature_vector = []

    for verb in all_verbs:
        if verb in verbs:
            verb_feature_vector.append(verbs[verb])
        else:
            verb_feature_vector.append(0)

    return verb_feature_vector



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




def output(all_verbs,all_cates,judgement_vector,feature_vector,dest_dir):

    with codecs.open(os.path.join(dest_dir,"all_verbs"),"w",'utf-8') as f:
        f.write(json.dumps(all_verbs))

    with codecs.open(os.path.join(dest_dir,"all_cates"),"w",'utf-8') as f:
        f.write(json.dumps(all_cates))


    with codecs.open(os.path.join(dest_dir,"judgement_vector"),"w",'utf-8') as f:
        f.write(json.dumps(judgement_vector))


    with codecs.open(os.path.join(dest_dir,"feature_vector"),"w",'utf-8') as f:
        f.write(json.dumps(feature_vector))





def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive_file","-pf",default="positive_result_tuples")
    parser.add_argument("--negative_file","-nf",default="negative_result_tuples")
    parser.add_argument("cate_info_file")
    parser.add_argument("dest_dir")
    parser.add_argument("--verb_size","-vz",type=int,default=20)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=20)

    args=parser.parse_args()

    all_verbs = set()
    entities = set()
    negative_verbs,negative_entities,negative_features =\
            process_result_tuple(args.negative_file,args.verb_size)

    all_verbs.update(negative_verbs)
    entities.update(negative_entities)

    positive_verbs,positive_entities,positive_features =\
            process_result_tuple(args.positive_file,args.verb_size)

    all_verbs.update(positive_verbs)
    entities.update(positive_entities)


    all_verbs = list(all_verbs)
    entities = list(entities)

    all_features = all_verbs
    cate_info = get_cate_info(entities,args.cate_info_file)
    
    

    all_cates = get_cate_features(cate_info,args.cate_feature_size)
    all_features += all_cates

    judgement_vector = []
    feature_vector = []


    add_data_to_set(negative_features,all_verbs,all_cates,judgement_vector,feature_vector,cate_info,False)
    add_data_to_set(positive_features,all_verbs,all_cates,judgement_vector,feature_vector,cate_info,True)

    output(all_verbs,all_cates,judgement_vector,feature_vector,args.dest_dir)




if __name__=="__main__":
    main()


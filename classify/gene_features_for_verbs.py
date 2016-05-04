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
from nltk.stem.wordnet import WordNetLemmatizer

def process_result_tuple(result_tuple_files,word_feature_size,use_words):
    all_word_features = {}
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

        # word_feature_model = Model(True)
        # for single_tuple in result_tuples[identifier]:
        #     word = single_tuple['verb']
        #     if single_tuple['verb_label'] != 'VB':
        #         word = WordNetLemmatizer().lemmatize(word,'v')
        #     word_feature_model.update(text_list=[word])
        # word_feature_model.normalize()
        if use_words:
            word_feature_model = get_all_words(result_tuples[identifier])
        else:
            word_feature_model = get_all_verbs(result_tuples[identifier])

        feature_data[identifier] = {
            "entity":entity,
            "word_features":word_feature_model.model
        }

        for word in word_feature_model.model:
            if word not in all_word_features:
                all_word_features[word] = 0
            all_word_features[word] += word_feature_model.model[word]

    top_word_features =  get_top_word_features(all_word_features,word_feature_size)

    return top_word_features,entities,feature_data



def get_all_verbs(example_result_tuples):
    verb_model = Model(True,need_stem=True)

    for single_tuple in example_result_tuples:
        word = single_tuple['verb']
        if single_tuple['verb_label'] != 'VB':
            word = WordNetLemmatizer().lemmatize(word,'v')
        try:
            verb_model.update(text_list=[word])
        except TypeError:
            print "Wrong Word!"
            print word
            print single_tuple
            sys.exit(0)
    verb_model.normalize()

    return verb_model





def get_all_words(example_result_tuples):
    
    word_model = Model(True,need_stem=True)

    for single_tuple in example_result_tuples:
        word_model += Sentence(single_tuple['sentence'],remove_stopwords=True).stemmed_model

    word_model.normalize()

    return word_model



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




def output(all_word_features,all_cates,judgement_vector,feature_vector,all_entities,dest_dir):

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




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive_file","-pf",default="positive_result_tuples")
    parser.add_argument("--negative_file","-nf",default="negative_result_tuples")
    parser.add_argument("cate_info_file")
    parser.add_argument("dest_dir")
    parser.add_argument("--use_words","-u",action='store_true')
    parser.add_argument("--word_feature_size","-wz",type=int,default=50)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=30)

    args=parser.parse_args()

    all_word_features = set()
    entities = set()
    negative_word_features,negative_entities,negative_features =\
            process_result_tuple(args.negative_file,args.word_feature_size,args.use_words)

    all_word_features.update(negative_word_features)
    entities.update(negative_entities)

    positive_word_features,positive_entities,positive_features =\
            process_result_tuple(args.positive_file,args.word_feature_size,args.use_words)

    all_word_features.update(positive_word_features)
    entities.update(positive_entities)


    all_word_features = list(all_word_features)
    entities = list(entities)

    all_features = all_word_features[:]
    #cate_info_file = os.path.join(args.dest_dir,"cate_info.json")
    cate_info = get_cate_info(entities,args.cate_info_file)
    
    

    all_cates = get_cate_features(cate_info,args.cate_feature_size,negative_entities,positive_entities)
    all_features += all_cates

    judgement_vector = []
    feature_vector = []
    all_entities = []

    add_data_to_set(negative_features,all_word_features,all_cates,judgement_vector,feature_vector,all_entities,cate_info,False)
    add_data_to_set(positive_features,all_word_features,all_cates,judgement_vector,feature_vector,all_entities,cate_info,True)

    output(all_word_features,all_cates,judgement_vector,feature_vector,all_entities,args.dest_dir)




if __name__=="__main__":
    main()


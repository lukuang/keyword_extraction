"""
get verb/clause words and category features for result tuple data
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
reload(sys)
sys.setdefaultencoding("utf-8")



def read_single_file(file_path, required_entity_types,show):
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
                    data[tag].append(unicode(m.group(1) ) )


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
        if eid == "54807":
            show = True
        else:
            show = False
        entity_type_mapping[eid] = read_single_file(entity_file, required_entity_types,show)
    return entity_type_mapping


def get_year_mapping(query_file):
    year_mapping = {}
    data = json.load(open(query_file))
    for q in data:
        year_mapping[unicode(q["eid"])] = q["year"]

    return year_mapping


def process_result_tuple(result_tuple_files,entity_type_mapping,use_clause_words,is_positive):
    feature_data = []
    entities = set()
    feature_frequency = {}

    result_tuples = json.load(open(result_tuple_files))


    for identifier in result_tuples:
        m = re.search('(.+?)/(.+)$', identifier)
        if m is not None:
            #entity = unicode(m.group(2) )
            instance = m.group(1)
            entity = m.group(2)
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
        # word_feature_model.to_dirichlet()

        if use_clause_words:
            word_feature_model = get_all_words(result_tuples[identifier])
        else:
            word_feature_model = get_all_verbs(result_tuples[identifier])

        judgement = 0
        if is_positive:
            judgement = 1

        single_data = {
                        "entity": entity,
                        "instance":instance,
                        "type":entity_type_mapping[instance][entity],
                        "word_features": word_feature_model.model,
                        "judgement": judgement
                       }

        feature_data.append(single_data)

        for word in word_feature_model.model:
            if word not in feature_frequency:
                feature_frequency[word] = 0
            feature_frequency[word] += 1


    return feature_frequency,entities,feature_data



def get_all_verbs(example_result_tuples):
    verb_model = Model(True,need_stem=True)

    for single_tuple in example_result_tuples:
        word = single_tuple['verb']
        if single_tuple['verb_label'] != 'VB':
            word = WordNetLemmatizer().lemmatize(word,'v')
        try:
            verb_model.update(text_list=[str(word)])
        except TypeError:
            print "Wrong Word!"
            print word
            print type(word)
            print single_tuple
            sys.exit(0)
    verb_model.to_dirichlet()

    return verb_model





def get_all_words(example_result_tuples):
    
    word_model = Model(True,need_stem=True)

    for single_tuple in example_result_tuples:
        word_model += Sentence(single_tuple['sentence'],remove_stopwords=True).stemmed_model

    word_model.to_dirichlet()

    return word_model



def get_top_word_features(all_word_features,word_feature_size):
    top_word_features = []
    i = 0
    sorted_word_features =  sorted(all_word_features.items(),key = lambda x:x[1],reverse=True)
    for (word,v) in sorted_word_features:
        if i==word_feature_size:
            break
        i += 1
        top_word_features.append(word)
        
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
        if i==cate_feature_size:
            #print "break when i is",i
            break
        all_cates.append(k)
        i += 1
        
    #print "return %d category features" %(len(all_cates) )
    return all_cates


def get_cate_features(cate_info, cate_feature_size,negative_entities, positive_entities):
    all_cates = set()

    all_cates.update(get_top_cate_for_single_entity_type(cate_info,negative_entities,cate_feature_size))
    all_cates.update(get_top_cate_for_single_entity_type(cate_info,positive_entities,cate_feature_size))
    
    print "return %d category features" %(len(all_cates) )
    return list(all_cates)





def add_data_to_set(feature_data,all_word_features,all_cates,judgement_vector,feature_vector,entity_info,cate_info,entity_type_mapping,year_mapping,is_positive):
    for identifier in feature_data:
        if is_positive:
            judgement_vector.append(1)
        else:
            judgement_vector.append(0)


        entity = feature_data[identifier]["entity"]
        instance = feature_data[identifier]["instance"]
        words = feature_data[identifier]["word_features"]
        year = year_mapping[instance] 
                

        try:
            single_entity_info = {
                "instance":instance,
                "entity":entity,
                "type": entity_type_mapping[instance][entity],
                "year": year
            }
        except KeyError:
            print "cannot find entity!"
            print "instance: %s, entity: %s" %(instance,entity)
            print type(entity)
            sys.exit(-1)
        else:
            
            entity_info.append(single_entity_info)
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




def output(feature_data,
           negative_feature_frequency, positive_feature_frequency,
           negative_category_frequency,positive_category_frequency,
           dest_dir):

    with codecs.open(os.path.join(dest_dir,"feature_data"),"w",'utf-8') as f:
        f.write(json.dumps(feature_data))

    with codecs.open(os.path.join(dest_dir,"negative_feature_frequency"),"w",'utf-8') as f:
        f.write(json.dumps(negative_feature_frequency))


    with codecs.open(os.path.join(dest_dir,"positive_feature_frequency"),"w",'utf-8') as f:
        f.write(json.dumps(positive_feature_frequency))


    with codecs.open(os.path.join(dest_dir,"negative_category_frequency"),"w",'utf-8') as f:
        f.write(json.dumps(negative_category_frequency))

    with codecs.open(os.path.join(dest_dir,"positive_category_frequency"),"w",'utf-8') as f:
        f.write(json.dumps(positive_category_frequency))
        




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive_file","-pf",default="positive_result_tuples")
    parser.add_argument("--negative_file","-nf",default="negative_result_tuples")
    parser.add_argument("cate_info_file")
    parser.add_argument("dest_dir")
    parser.add_argument("--use_clause_words","-uc",action='store_true')
    parser.add_argument("--new_tornado","-new",action='store_true')
    parser.add_argument("--word_feature_size","-wz",type=int,default=50)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=50)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--query_file","-qf",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/noaa.json")
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')


    args=parser.parse_args()
    print "dest dir",args.dest_dir
    feature_data = []
    entities = set()
    entity_type_mapping = get_entity_type_mapping(args.news_entity_dir,args.required_entity_types,args.required_file_name)
    #print entity_type_mapping
    if not args.new_tornado:
        year_mapping = get_year_mapping(args.query_file)
    else:
        year_mapping = {}
        for instance in entity_type_mapping:
            year_mapping[unicode(instance)] = "2012"

    #print year_mapping

    negative_feature_frequency,negative_entities,negative_features =\
            process_result_tuple(args.negative_file,entity_type_mapping,args.use_clause_words,False)

    feature_data = negative_features
    entities.update(negative_entities)

    positive_feature_frequency,positive_entities,positive_features =\
            process_result_tuple(args.positive_file,entity_type_mapping,args.use_clause_words,True)

    feature_data += positive_features
    entities.update(positive_entities)

    print "there are %d features" %(len(feature_data))
    entities = list(entities)

    #cate_info_file = os.path.join(args.dest_dir,"cate_info.json")
    cate_info = get_cate_info(entities,args.cate_info_file)
    
    negative_category_frequency = {}
    positive_category_frequency = {}

    # add entity information to the feature data:
    for single_data in feature_data:
        entity = single_data["entity"]
        new_cates = cate_info[entity]
        single_data["category"] = new_cates

        if not new_cates: 
            continue

        if single_data["judgement"] == 0:
            for new_cate in new_cates:
                if new_cate not in negative_category_frequency:
                    negative_category_frequency[new_cate] = 0
                negative_category_frequency[new_cate] += 1
        else:
            for new_cate in new_cates:
                if new_cate not in positive_category_frequency:
                    positive_category_frequency[new_cate] = 0
                positive_category_frequency[new_cate] += 1
    

    
    print "output data"
    

    
    output(feature_data,
           negative_feature_frequency, positive_feature_frequency,
           negative_category_frequency,positive_category_frequency,
           args.dest_dir)



if __name__=="__main__":
    main()


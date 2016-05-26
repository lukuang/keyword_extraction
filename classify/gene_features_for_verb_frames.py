"""
use frames as features 
"""
import os
import json
import sys
import re
import argparse
import codecs
import math
from myUtility.corpus import Sentence, Model
from get_entity_cate import get_cate_for_entity_list
from nltk.stem.wordnet import WordNetLemmatizer
reload(sys)
sys.setdefaultencoding("utf-8")

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
                    data[tag].append( unicode(m.group(1)) )

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


def get_year_mapping(query_file):
    year_mapping = {}
    data = json.load(open(query_file))
    for q in data:
        year_mapping[unicode(q["eid"])] = q["year"]

    return year_mapping

def process_result_tuple(verb_frame_file,word_feature_size):
    all_word_features = {}
    entities = set()
    feature_data = {}

    all_verb_frames = json.load(open(verb_frame_file))

    for identifier in all_verb_frames:
        m = re.search('(\d+)/(.+)$', identifier)
        if m is not None:
            instance = unicode(m.group(1))

            entity = unicode(m.group(2))
            entities.add(entity)
        else:
            print "Wrong identifier!"
            sys.exit(-1)

        # word_feature_model = Model(True)
        # for single_tuple in verb_frames[identifier]:
        #     word = single_tuple['verb']
        #     if single_tuple['verb_label'] != 'VB':
        #         word = WordNetLemmatizer().lemmatize(word,'v')
        #     word_feature_model.update(text_list=[word])
        # word_feature_model.normalize()
        

        verb_frames = get_all_frames(all_verb_frames[identifier],entity)
        
        normalize(verb_frames)
        feature_data[identifier] = {
            "entity":entity,
            "instance": instance,
            "word_features":verb_frames
        }

        for word in verb_frames:
            if word not in all_word_features:
                all_word_features[word] = 0
            all_word_features[word] += verb_frames[word]

    top_word_features =  get_top_word_features(all_word_features,word_feature_size)

    return top_word_features,entities,feature_data





def normalize(verb_frames):
    norm = 0
    for verb in verb_frames:
        norm += verb_frames[verb]*verb_frames[verb]

    norm  = math.sqrt(norm)

    for verb in verb_frames:
        verb_frames[verb] /= 1.0*norm


def get_all_frames(example_verb_frames,entity):
    
    
    verb_frames = {}

    for frame in example_verb_frames:
        name = frame['name']
        elements = frame['elements']
        for e_name in elements:
            for text in elements[e_name]:
                if text.find(entity)!=-1:
                    frame_combo = name+"/"+e_name
                    if frame_combo not in verb_frames:
                        verb_frames[frame_combo] = 0
                    verb_frames[frame_combo] += 1

    return verb_frames



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





def add_data_to_set(feature_data,all_word_features,all_cates,judgement_vector,feature_vector,entity_info,cate_info,entity_type_mapping,year_mapping,is_positive):
    for identifier in feature_data:
        if is_positive:
            judgement_vector.append(1)
        else:
            judgement_vector.append(0)

        entity = feature_data[identifier]["entity"]
        instance = feature_data[identifier]["instance"]
        words = feature_data[identifier]["word_features"]
        year  = year_mapping[instance]

        single_entity_info = {
            "instance":instance,
            "entity":entity,
            "type": entity_type_mapping[instance][entity],
            "year":year
        }

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




def output(all_word_features,all_cates,judgement_vector,feature_vector,entity_info,dest_dir):

    with codecs.open(os.path.join(dest_dir,"all_word_features"),"w",'utf-8') as f:
        f.write(json.dumps(all_word_features))

    with codecs.open(os.path.join(dest_dir,"all_cates"),"w",'utf-8') as f:
        f.write(json.dumps(all_cates))


    with codecs.open(os.path.join(dest_dir,"judgement_vector"),"w",'utf-8') as f:
        f.write(json.dumps(judgement_vector))


    with codecs.open(os.path.join(dest_dir,"feature_vector"),"w",'utf-8') as f:
        f.write(json.dumps(feature_vector))

    with codecs.open(os.path.join(dest_dir,"entity_info"),"w",'utf-8') as f:
        f.write(json.dumps(entity_info))

    





def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive_file","-pf",
        default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/src/stanford_parser/data/positive_verb_frames")
    parser.add_argument("--negative_file","-nf",
        default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/src/stanford_parser/data/negative_verb_frames")
    parser.add_argument("cate_info_file")
    parser.add_argument("dest_dir")
    parser.add_argument("--word_feature_size","-wz",type=int,default=50)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=30)
    parser.add_argument("--new_tornado","-new",action='store_true')
    parser.add_argument("--query_file","-qf",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/noaa.json")
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')



    args=parser.parse_args()

    all_word_features = set()
    entities = set()


    entity_type_mapping = get_entity_type_mapping(args.news_entity_dir,args.required_entity_types,args.required_file_name)
    if not args.new_tornado:
        year_mapping = get_year_mapping(args.query_file)
    else:
        year_mapping = {}
        for instance in entity_type_mapping:
            year_mapping[unicode(instance)] = "2012"



    negative_word_features,negative_entities,negative_features =\
            process_result_tuple(args.negative_file,args.word_feature_size)

    all_word_features.update(negative_word_features)
    entities.update(negative_entities)

    positive_word_features,positive_entities,positive_features =\
            process_result_tuple(args.positive_file,args.word_feature_size)

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
    entity_info = []

    add_data_to_set(negative_features,all_word_features,all_cates,judgement_vector,feature_vector,entity_info,cate_info,entity_type_mapping,year_mapping,False)
    add_data_to_set(positive_features,all_word_features,all_cates,judgement_vector,feature_vector,entity_info,cate_info,entity_type_mapping,year_mapping,True)

    output(all_word_features,all_cates,judgement_vector,feature_vector,entity_info,args.dest_dir)




if __name__=="__main__":
    main()
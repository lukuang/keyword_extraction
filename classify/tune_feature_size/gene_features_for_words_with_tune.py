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
        #print "for %s" %instance
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



def get_all_sentence_windows(documents,candidates,entity_type_mapping,is_positive):
    feature_frequency = {}
    entities = set()
    feature_data = []
    for instance in documents:
        #print "%s:" %instance
        # if instance!='59890':
        #     continue
        words = set()

        words.update(candidates[instance])

        #words += entities_judgement[instance][required_type]
        entity_map = get_nochange_map(words)

        temp_windows = {}
        for single_file in documents[instance]:
            #print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_sentence_window(entity_map,sentence.text,temp_windows)


        for entity in candidates[instance]:
            try:
                temp_windows[entity].to_dirichlet()
                identifier = instance+"/"+entity
                judgement = 0
                if is_positive:
                    judgement = 1
                single_data = {
                                "entity": entity,
                                "instance":instance,
                                "type":entity_type_mapping[instance][entity],
                                "word_features": temp_windows[entity].model,
                                "judgement": judgement
                               }

                feature_data.append( single_data )

                for w in temp_windows[entity].model:
                    if w not in feature_frequency:
                        feature_frequency[w] = 0
                    feature_frequency[w] += 1

                entities.add(entity)
            

            except KeyError:
                print "cannot find entity %s" %(w)
                print 'store to remove later'

    print "There are %d feature data" %(len(feature_data))
        
    return feature_data,feature_frequency,entities


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
                "entity": entity,
                "instance": instance,
                "type":entity_type_mapping[instance][entity],
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
    parser.add_argument("--text_dir",'-tp',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/clean_text/noaa')
    parser.add_argument("positive_candidate_file")
    parser.add_argument("negative_candidate_file")
    parser.add_argument("cate_info_file")
    parser.add_argument("dest_dir")
    parser.add_argument("--word_feature_size","-wz",type=int,default=50)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=50)
    parser.add_argument("--new_tornado","-new",action='store_true')
    parser.add_argument("--query_file","-qf",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/noaa.json")
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')


    args=parser.parse_args()
    
    positive_candidates= get_candidates(args.positive_candidate_file)
    negative_candidates= get_candidates(args.negative_candidate_file)
    p = 0
    n = 0

    for k in positive_candidates:
        p += len(positive_candidates[k])

    for k in negative_candidates:
        n += len(negative_candidates[k])

    print "There are %d positive candidates and %d negative candidates"\
        %(p,n)
    
    positive_instance_names = positive_candidates.keys()
    negative_instance_names = negative_candidates.keys()

    negative_documents = get_documents(negative_instance_names,args.text_dir)
    positive_documents = get_documents(positive_instance_names,args.text_dir)
    

    entity_type_mapping = get_entity_type_mapping(args.news_entity_dir,args.required_entity_types,args.required_file_name)
    if not args.new_tornado:
        year_mapping = get_year_mapping(args.query_file)
    else:
        year_mapping = {}
        for instance in entity_type_mapping:
            year_mapping[unicode(instance)] = "2012"


    feature_data = []

    negative_feature_data,negative_feature_frequency, negative_entities =\
            get_all_sentence_windows(negative_documents,negative_candidates,entity_type_mapping,False)

    feature_data += negative_feature_data

    positive_feature_data,positive_feature_frequency, positive_entities =\
            get_all_sentence_windows(positive_documents,positive_candidates,entity_type_mapping,True)

    feature_data += positive_feature_data
    
    entities = list(negative_entities | positive_entities)


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


    #all_features += all_cates

    print "there are %d data" %(len(feature_data) )
    output(feature_data,
           negative_feature_frequency, positive_feature_frequency,
           negative_category_frequency,positive_category_frequency,
           args.dest_dir)




if __name__=="__main__":
    main()


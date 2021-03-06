"""
create data for 5 fold cross validation
"""

import os
import json
import sys
import re
import argparse
import codecs
from nltk.tokenize import sent_tokenize,word_tokenize
from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import KFold
import string
import copy
import random
import shutil


def process_text(single_text):
    single_text = re.sub("\s+"," ",single_text)
    printable = set(string.printable)
    single_text = filter(lambda x: x in printable, single_text)
    return single_text

def get_text(text_dir):
    all_text = ""
    for single_dir in os.walk(text_dir).next()[1]:
        single_dir = os.path.join(text_dir,single_dir)
        for day_dir in os.walk(single_dir).next()[1]:
            day_dir = os.path.join(single_dir,day_dir)
            for single_file in os.walk(day_dir).next()[2]:
                single_file = os.path.join(day_dir,single_file)
                # print "open file %s" %(single_file)
                with  codecs.open(single_file,"r","utf-8") as f:
                    single_text = f.read()
                    single_text = process_text(single_text)
                    all_text += single_text+"\n"
    # print all_text
    return all_text


def reprocess_feature_data(feature_data):
    sentence_map = {}
    k = 0
    for single_data in feature_data:
        k += 1
        sentence = single_data["sentence"]
        # if type(single_data["entity"]) == list:
        #     print "at sentence %d" %(k)
        #     raise TypeError("Wrong Type at the begining!\n:%s" %(single_data)) 
        if sentence not in sentence_map:
            sentence_map[sentence] = single_data
        else:
            old_single_data = sentence_map[sentence]
            if type(old_single_data["entity"]) == list:
                if single_data["judgement"] == 0:
                    continue

                elif single_data["entity"] in old_single_data["entity"]:
                    continue
                
                else:
                   old_single_data["entity"].append(single_data["entity"]) 
            else:
                if old_single_data["entity"] == single_data["entity"]:
                    continue
                if single_data["judgement"] == 0:
                    continue
                else:
                    if old_single_data["judgement"] == 0:
                        old_single_data["entity"] = [ single_data["entity"] ]
                        old_single_data["judgement"] = 1
                    else:
                        old_single_data["entity"] = [ old_single_data["entity"],single_data["entity"] ]

            sentence_map[sentence] = old_single_data
                # if type(old_single_data["entity"]) == list:
                #     for entity in old_single_data["entity"]:
                #         if type(entity) == list:
                #             raise TypeError("Wrong Type!\n:%s\n%s" %(old_single_data,single_data)) 

    # for sentence in sentence_map:
    #     single_data = sentence_map[sentence]
    #     if type(single_data["entity"]) == list:
    #         if "St. Pete Beach" in single_data["entity"]:
    #             print single_data
    #     else:
    #         if "St. Pete Beach" == single_data["entity"]:
    #             print single_data

    # for sentence in sentence_map:
    #     single_data = sentence_map[sentence]
    #     if type(single_data["entity"]) == list:
    #         for entity in single_data["entity"]:
    #             if type(entity) == list:
    #                 raise TypeError("Wrong Type!\n:%s" %(single_data)) 

    for sentence in sorted(sentence_map.keys(),key=lambda x:len(x)):
        need_pop = False
        for old_sentence in sorted(sentence_map.keys(),key=lambda x:len(x)):
            if old_sentence != sentence:
                if sentence in old_sentence:
                    need_pop = True
                    single_data = copy.deepcopy(sentence_map[sentence])
                    old_single_data = copy.deepcopy(sentence_map[old_sentence])
                    if type(old_single_data["entity"]) == list:
                        if type(single_data["entity"]) == list:
                            for entity in single_data["entity"]:
                                if entity in old_single_data["entity"]:
                                    continue
                                else:
                                    old_single_data["entity"].append(entity) 

                        else:
                            entity = single_data["entity"]
                            if single_data["judgement"] == 0:
                                continue
                            else:
                                if entity in old_single_data["entity"]:
                                    continue
                                
                                else:
                                   old_single_data["entity"].append(entity) 
                    else:
                        if type(single_data["entity"]) == list:
                            if old_single_data["judgement"] == 0:
                                old_single_data = single_data
                            else:
                                if old_single_data["entity"] not in single_data["entity"]:
                                    single_data["entity"].append(old_single_data["entity"])
                                old_single_data = single_data
                        else:
                            if old_single_data["entity"] == single_data["entity"]:
                                continue
                            if single_data["judgement"] == 0:
                                continue
                            else:
                                if old_single_data["judgement"] == 0:
                                    old_single_data["entity"] = [ single_data["entity"] ]
                                    old_single_data["judgement"] = 1
                                else:
                                    old_single_data["entity"] = [ old_single_data["entity"],single_data["entity"] ]

                    sentence_map[old_sentence] = old_single_data
                    break
        if need_pop:
            sentence_map.pop(sentence,None)

    # print "-"*20
    # for sentence in sentence_map:
    #     single_data = sentence_map[sentence]
    #     if type(single_data["entity"]) == list:
    #         if "St. Pete Beach" in single_data["entity"]:
    #             print single_data
    #     else:
    #         if "St. Pete Beach" == single_data["entity"]:
    #             print single_data

    new_feature_data = []
    for sentence in  sentence_map:
        single_data = sentence_map[sentence]
        if type(single_data["entity"]) != list:
            single_data["entity"] = [single_data["entity"]]
        new_feature_data.append(single_data) 

    return new_feature_data   


def load_feature_data(feature_dir):
    feature_data = []
    for instance in os.walk(feature_dir).next()[2]:
        feature_data_file = os.path.join(feature_dir,instance)
        instance_feature_data = load_data_set_from_single_file(feature_data_file)
        feature_data += instance_feature_data


    return reprocess_feature_data(feature_data)

def load_data_set_from_single_file(feature_data_file):
    feature_data = []
    raw_data = json.load(codecs.open(feature_data_file,"r","utf-8"))
    for single_data in raw_data:
        single_feature_data = {}
        sentence = single_data["sentence"]
        single_feature_data["sentence"] = process_text( sentence )
        single_feature_data["judgement"] = single_data["judgement"]
        if type(single_data["judgement"]) != int:
            print single_data
        single_feature_data["entity"] = single_data["entity"] 
        feature_data.append(single_feature_data)
    return feature_data


def find_non_tagged_sentences(all_text,feature_data):
    i = 0
    past = []
    for single_data in feature_data:
        sentence = single_data["sentence"]
        index = all_text.find(sentence)
        length  = len(sentence)
        
        if index != -1:

            temp = all_text[:index] +"\n" +all_text[index+length:]
            all_text = temp
            i += 1
        else:
            print all_text
            print past
            print    single_data
            print "Matched %d sentences" %(i) 
            raise ValueError("cannot find sentence:\n%s\n" %(sentence))

        if sentence in past:
            raise ValueError("sentence appear twice!\n%s" %(sentence))
        else:
            past.append(sentence)

    return sent_tokenize(all_text)


def creating_data_indecies(feature_data , non_tagged_sentences):
    cross_validation_indecies = [ ]
    labels = []
    pos = 0
    for single_data in feature_data:
        labels.append(single_data["judgement"])
        if single_data["judgement"] == 1:
            pos += 1 
        if type(single_data["judgement"]) != int:
            print single_data
    print "There are %d samples" %(len(labels))
    print "%d of them are pos" %(pos)
    skf = StratifiedKFold(labels,n_folds=5,shuffle=True)
    for train, test in skf:
        sinlge_set_indecies = {
            "train":{
                "tagged":list(train),
                "non_tagged":[]
            },
            "test":{
                "tagged":list(test),
                "non_tagged":[]
            }
        }
        cross_validation_indecies.append(sinlge_set_indecies)

    kf = KFold(len(non_tagged_sentences), n_folds=5,shuffle=True)
    i = 0
    for train_index, test_index in kf:
        cross_validation_indecies[i]["train"]["non_tagged"] = list(train_index)
        cross_validation_indecies[i]["test"]["non_tagged"] = list(test_index)

        i += 1

    return cross_validation_indecies

def generate_labelled_sentences(feature_data,non_tagged_sentences,set_indecies,only_tagged):
    labelled_sentences = []
    if not only_tagged:
        for non_tagged_index in set_indecies["non_tagged"]:
            sentence = non_tagged_sentences[non_tagged_index]
            single_labelled_sentence = []
            for t in word_tokenize(sentence):
                single_labelled_sentence.append("%s\t0" %(t))

            labelled_sentences.append(single_labelled_sentence)

    for tagged_index in set_indecies["tagged"]:
        single_data = feature_data[tagged_index]
        sentence = single_data["sentence"]
        single_labelled_sentence = []
        
        if single_data["judgement"] == 0:
            for t in word_tokenize(sentence):
                single_labelled_sentence.append("%s\t0" %(t))
        else:
            entity_index_map = []
            for entity in single_data["entity"]:
                index = sentence.find(entity)
                if index == -1:
                    print single_data
                    raise ValueError("cannot find entity \'%s\' in sentence:\n%s" %(entity,sentence) )
                else:
                    entity_index_map.append([index,entity])
            sorted_entities = sorted(entity_index_map,key=lambda x:x[0])
            for entity_pair in sorted_entities:
                entity = entity_pair[1]
                index = sentence.find(entity)
                length  = len(entity)

                before = sentence[:index] 
                for t in word_tokenize(before):
                    single_labelled_sentence.append("%s\t0" %(t))

                for t in word_tokenize(entity):
                    single_labelled_sentence.append("%s\tDAM" %(t))

                sentence = sentence[index+length:]

            for t in word_tokenize(sentence):
                single_labelled_sentence.append("%s\t0" %(t))
        labelled_sentences.append(single_labelled_sentence)

    random.shuffle(labelled_sentences)
    return labelled_sentences


def store_data(cross_validation_indecies,dest_dir,feature_data,
               non_tagged_sentences,property_file,only_tagged):
    all_sentences = []
    for i in range(5):
        dir_name = str(i)
        fold_dir = os.path.join(dest_dir,dir_name)
        if not os.path.exists(fold_dir):
            os.mkdir(fold_dir)
        test_sentences = generate_labelled_sentences(feature_data,non_tagged_sentences,cross_validation_indecies[i]["test"],only_tagged)
        train_sentences = generate_labelled_sentences(feature_data,non_tagged_sentences,cross_validation_indecies[i]["train"],only_tagged)
        train_file = os.path.join(fold_dir,"train.tsv")
        test_file = os.path.join(fold_dir,"test.tsv")
        dest_property_file = os.path.join(fold_dir,"property")

        with codecs.open(train_file,"w","utf-8") as of:
            for sentence in train_sentences:
                for t in sentence:
                    of.write("%s\n" %(t))
                of.write("\n")

        with codecs.open(test_file,"w","utf-8") as of:
            for sentence in test_sentences:
                for t in sentence:
                    of.write("%s\n" %(t))
                of.write("\n")

        shutil.copyfile(property_file,dest_property_file)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text_dir")
    parser.add_argument("feature_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("property_file")
    parser.add_argument("--only_tagged","-ot",action='store_true')
    args=parser.parse_args()

    all_text = get_text(args.text_dir)
    feature_data = load_feature_data(args.feature_dir)
    print "load %d feature data" %(len(feature_data))
    non_tagged_sentences = find_non_tagged_sentences(all_text,feature_data)
    cross_validation_indecies = creating_data_indecies(feature_data , non_tagged_sentences)
    store_data(cross_validation_indecies,args.dest_dir,
               feature_data,non_tagged_sentences,args.property_file,args.only_tagged)

if __name__=="__main__":
    main()


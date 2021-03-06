"""
prepare sentences given candidates
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Document
import xlsxwriter

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
                windows[w] = []
            
            windows[w].append(re.sub("\n"," ",sentence))
    for w in windows:
        windows[w] = list( set(windows[w]) )


def get_nochange_map(words):
    entity_map = {}
    for w in words:
        entity_map[w] = w
    #print json.dumps(entity_map)
    return entity_map



def get_all_sentence_windows(documents,candidates):
    windows = {}
    for instance in documents:
        print "%s:" %instance
        # if instance!='59890':
        #     continue
        words = set()
        windows[instance] = {}
        words.update(candidates[instance])
        windows[instance]= {}
        #words += entities_judgement[instance][required_type]
        entity_map = get_nochange_map(words)

        temp_windows = {}
        for single_file in documents[instance]:
            print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_sentence_window(entity_map,sentence.text,temp_windows)


        for w in candidates[instance]:
            try:
                windows[instance][w] = temp_windows[w]
            except KeyError:
                print "cannot find entity %s" %(w)
                print 'store to remove later'

        
    return windows


def clean_entity_sentences(entity_sentences):
    #clean entity sentences pair that the sentence is already exists for entities that
    # is a string contains the entity
    # example:
    # Jefferson County:
    # Phone lines were down and cell reception was spotty, Sedam said, so they contacted the Jefferson County Sheriff's Department 
    # to put a message out on the radio about the students who were at the Chelsea General Store. 
    #
    # VS.
    # Jefferson County Sheriff's Department:
    # Phone lines were down and cell reception was spotty, Sedam said, so they contacted the Jefferson County Sheriff's Department 
    # to put a message out on the radio about the students who were at the Chelsea General Store. 
    


    new_entity_sentences = {}
    entities =  entity_sentences.keys()

    # store : { small_entity:[big_entities]} mapping
    entity_map = {}
    for small_entity in entities:
        for  big_entity in entities:
            if small_entity != big_entity:
                if small_entity in big_entity:
                    if small_entity not in entity_map:
                        entity_map[small_entity] = []
                    entity_map[small_entity].append(big_entity)

    for entity in  entity_sentences:
        
        # if it is not a "small entity" keep the sentence output
        if entity not in entity_map:
            new_entity_sentences[entity] = entity_sentences[entity]

        else:
            new_entity_sentences[entity] = []
            for sentence in entity_sentences[entity]:
                already_in_big_entities = False
                for big_entity in entity_map[entity]:
                    if sentence in entity_sentences[big_entity]:
                        already_in_big_entities = True
                        break
                if not already_in_big_entities:
                    new_entity_sentences[entity].append(sentence)


    return new_entity_sentences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text_dir",'-tp',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/clean_text/sentence_level_tornado')
    parser.add_argument("candidate_file")
    parser.add_argument("sentence_output_dir")

    args=parser.parse_args()
    
    candidates= get_candidates(args.candidate_file)
    instance_names = candidates.keys()
    documents = get_documents(instance_names,args.text_dir)
    windows = get_all_sentence_windows(documents,candidates)
    i = 0
    sentence_index_map ={}

    total = 0
    for instance in windows:
        # Create a workbook and add a worksheet.
        sentence_output = os.path.join(args.sentence_output_dir,instance+".xlsx")
        workbook = xlsxwriter.Workbook(sentence_output)
        worksheet = workbook.add_worksheet()

        # with codecs.open(args.sentence_output,'w','utf-8') as f:
        row = 0
        col = 0

        sub_entities_sentences = clean_entity_sentences(windows[instance])
        for w in sub_entities_sentences:
            for sentence in sub_entities_sentences[w]:
                # f.write("%s,'%s','%s'\n" %(instance,w,sentence))
                worksheet.write(row, col,     instance)
                worksheet.write(row, col + 1, w)
                worksheet.write(row, col + 2, sentence)
                row += 1
        print "There are %d sentences in %s" %(row,instance)
        total += row
        workbook.close()

    print "There are %d in total" %(total)
                   

    # with codecs.open(args.sentence_index,'w','utf-8') as f:
    #     f.write(json.dumps(sentence_index_map))



if __name__=="__main__":
    main()


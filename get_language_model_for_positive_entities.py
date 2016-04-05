"""
get the language model surrounding some entities
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Document, Sentence


def get_sentence_window(entity_map,sentence,windows):
    """
    Use the whole sentence as the context
    """
    #print sentence
    for w in entity_map:
        
        if sentence.find(w) != -1:
            temp_sentence = sentence
            #print "found sentence %s" %temp_sentence
            for t in entity_map:
                if entity_map[t]:
                    temp_sentence = temp_sentence.replace(entity_map[t],"")
                elif temp_sentence.find(t) != -1:
                    temp_sentence = temp_sentence.replace(t,"")
            #print "after process %s" %temp_sentence
            if entity_map[w]:
                w = entity_map[w]
            if w not in windows:
                windows[w] = Sentence(temp_sentence,remove_stopwords=True).stemmed_model
            else:
                windows[w] += Sentence(temp_sentence,remove_stopwords=True).stemmed_model


def get_entity_map(words):
    entity_map = {}
    multiple = []
    for w in words:
        entity_map[w] = None
        for e in words:
            if w != e:
                if e.find(w)!=-1:
                    if entity_map[w] != None:
                        if entity_map[w].find(e) != -1:
                            pass
                        elif  e.find(entity_map[w]) != -1:
                            entity_map[w] = e
                        else:
                            multiple.append(w)
                            #print "For %s, there are two none substring candidates: %s %s" %(w, e,entity_map[w] )
                            #sys.exit(-1)
                    else:
                        entity_map[w] = e
    # delete the ones that have multiple possibilities
    for w in multiple:
        entity_map.pop(w, None)

    #print json.dumps(entity_map)
    #sys.exit(-1)
    return entity_map  



def get_text_window(entity_map,sentence,windows,window_size):
    """
    Use a sized text window as the context
    """
    
    for w in entity_map:

        if sentence.find(w) != -1:

            temp_sentence = sentence
            #print "found sentence %s" %temp_sentence
            for t in entity_map:
                if t.find(w) != -1:
                    continue
                if entity_map[t]:
                    temp_sentence = temp_sentence.replace(entity_map[t],"")
                elif temp_sentence.find(t) != -1:
                    temp_sentence = temp_sentence.replace(t,"")

            if entity_map[w]:
                w = entity_map[w]

            w_size = w.count(" ")+1

            spaces = [m.start() for m in re.finditer(' ', temp_sentence)]
            
            for m in re.finditer(w,temp_sentence):
                start = m.start()-1
                if start in spaces:
                    w_start = max(0,spaces.index(start)-window_size)
                    w_end = min(len(spaces)-1,spaces.index(start)+window_size+w_size)
                    #window_string = document[spaces[w_start]:spaces[w_end]]
                    window_string = temp_sentence[spaces[w_start]:m.start()-1] +" "+ temp_sentence[m.end()+1:spaces[w_end]]
                else:
                    w_end = min(len(spaces)-1,window_size+w_size-1)
                    #window_string = document[0:spaces[w_end]]
                    window_string = temp_sentence[m.end()+1:spaces[w_end]]
                if w not in windows: 
                    windows[w] = Sentence(window_string,remove_stopwords=True).stemmed_model
                else:
                    windows[w] += Sentence(window_string,remove_stopwords=True).stemmed_model




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
    

def get_all_sentence_windows(documents,entities_judgement):
    windows = {}
    for instance in documents:
        print "%s:" %instance
        words = []
        for entity_type in entities_judgement[instance]:
            words += entities_judgement[instance][entity_type]
            if entity_type not in windows:
                windows[entity_type] = {}
        entity_map = get_entity_map(words)
        temp_windows = {}
        for single_file in documents[instance]:
            print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_sentence_window(entity_map,sentence.text,temp_windows)
        for w in temp_windows:
            for entity_type in entities_judgement[instance]:
                if w in entities_judgement[instance][entity_type]:
                    windows[entity_type][w] = temp_windows[w]
                    break
    return windows

def get_all_text_windows(documents,entities_judgement,window_size):
    windows = {}
    for instance in documents:
        print "%s:" %instance
        words = []
        for entity_type in entities_judgement[instance]:
            words += entities_judgement[instance][entity_type]
            if entity_type not in windows:
                windows[entity_type] = {}
        entity_map = get_entity_map(words)
        temp_windows = {}
        for single_file in documents[instance]:
            print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_text_window(entity_map,sentence.text,temp_windows,window_size)
        for w in temp_windows:
            for entity_type in entities_judgement[instance]:
                if w in entities_judgement[instance][entity_type]:
                    windows[entity_type][w] = temp_windows[w]
                    break
    return windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("top_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("run_id",type=int)
    parser.add_argument("--using_text_window","-u",action='store_true')
    parser.add_argument("--window_size",'-wz',type=int,default=3)
    parser.add_argument("--entity_judgement_file","-e",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/entities_judgement.json")
    args=parser.parse_args()
    
    data = ""
    with open(args.entity_judgement_file) as f:
        data = f.read()

    entities_judgement_data = json.loads(data)
    entities_judgement = {}
    single = entities_judgement_data[args.run_id-1]
    q = single["query_string"]
    single.pop("query_string",None)
    entities_judgement[q] = single
    #for single in entities_judgement_data:
    #    q = single["query_string"]
    #    single.pop("query_string",None)
    #    entities_judgement[q] = single

    args.top_dir = os.path.abspath(args.top_dir)
    instance_names = entities_judgement.keys()
    documents = {}
    for instance in instance_names:
        print "for %s" %instance
        source_dir = os.path.join(args.top_dir,"clean_text",args.disaster_name,instance)
        sub_dirs = os.walk(source_dir).next()[1]
        documents[instance] = {}
        for a_dir in sub_dirs:
            date_dir = os.path.join(source_dir,a_dir)
            print date_dir
            for single_file in get_files(date_dir):
                #print "open file %s" %os.path.join(date_dir,single_file)
                single_file = os.path.join(date_dir,single_file)
                documents[instance][single_file] = Document(single_file,file_path = single_file)

    #show_documents(documents)#debug purpose
    #print json.documents(files,indent=4)
    if args.using_text_window:
        windows = get_all_text_windows(documents,entities_judgement,args.window_size)
    else:    
        windows = get_all_sentence_windows(documents,entities_judgement)
    for entity_type in windows:
        for w in windows[entity_type]:
            windows[entity_type][w] = windows[entity_type][w].model
    with codecs.open(os.path.join(args.dest_dir,q),"w","utf-8") as f:
        f.write(json.dumps(windows))
    #print json.dumps(windows,indent=4)
    print "finished"

if __name__=="__main__":
    main()


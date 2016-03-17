"""
get the language model surrounding some entities
"""

import os
import json
import sys
import re
import argparse
from myUtility.corpus import Document, Sentence


def get_sentence_window(words,sentence,windows):
    """
    Use the whole sentence as the context
    """
    for w in words:
        if w not in windows:
            windows[w] = []
        if sentence.find(w) != -1:
            window_string.replace(w,"")
        windows[w].append(Sentence(window_string,remove_stopwords=True))



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
            windows[w].append(Sentence(window_string,remove_stopwords=True))




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
        break

def get_all_sentence_windows(documents,entities_judgement):
    windows = {}
    for instance in documents:
        print "%s:" %instance
        for entity_type in entities_judgement[instance]:
            if entity_type not in windows:
                windows[entity_type] = {}
            for single_file in documents[instance]:
                for sentence in documents[instance][single_file].sentences:
                    words = entities_judgement[instance][entity_type]
                    get_sentence_window(words,sentence.text,windows[entity_type])
        break
    return windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("top_dir")
    parser.add_argument("--entity_judgement_file","-e",default="entities_judgement.json")
    args=parser.parse_args()
    
    data = ""
    with open(args.entity_judgement_file) as f:
        data = f.read()

    entities_judgement_data = json.loads(data)
    entities_judgement = {}
    for single in entities_judgement_data:
        q = single["query_string"]
        single.pop("query_string",None)
        entities_judgement[q] = single

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
                documents[instance][single_file] = Document(single_file,file_path = os.path.join(date_dir,single_file))

    #show_documents(documents)#debug purpose
    #print json.documents(files,indent=4)
    windows = get_all_sentence_windows(documents,entities_judgement)
    print json.documents(windows,indent=4)

if __name__=="__main__":
    main()


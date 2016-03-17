"""
get the language model surrounding some entities
"""

import os
import json
import sys
import re
import argparse
from myUtility.corpus import Document


def get_sentence_window(words,sentence):
    """
    Use the whole sentence as the context
    """
    windows = {}
    for w in words:
        windows[w] = []
        if sentence.find(w) != -1:
            window_string.replace(w,"")
        windows[w].append(Sentence(window_string))
    return windows



def get_text_window(words,document,window_size):
    """
    Use a window as the context
    """
    windows = {}
    spaces = [m.start() for m in re.finditer(' ', document)]
    for w in words:
        w_size = w.count(" ")+1 
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
            windows[w].append(Sentence(window_string))


    return windows



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
            for sentence in single_file.sentences:
                print sentence
            print "-"*20
        break



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("top_dir")
    parser.add_argument("--entity_judgement_file","-e",default="entities_judgement.json")
    args=parser.parse_args()
    
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
        documents[instance] = []
        for a_dir in sub_dirs:
            for single_file in get_files(os.path.join(source_dir,a_dir)):
                documents[instance][single_file] = Document(single_file,file_path = os.path.join(a_dir,f))

    show_documents(documents)#debug purpose
    #print json.documents(files,indent=4)

if __name__=="__main__":
    main()


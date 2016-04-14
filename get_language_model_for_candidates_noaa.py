"""
get the feature vectors of entities
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Document, Sentence, Model
#from get_entity_cate import get_cate_for_entity_list



def get_sentence_window(entity_map,sentence,windows):
    """
    Use the whole sentence as the context
    """
    #print sentence
    for w in entity_map:
        # if w != u'La. 421':
        #     continue
        # else:
        #     print "YES!"
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





def get_text_window(entity_map,sentence,windows,window_size):
    """
    Use a sized text window as the context
    """
    
    for w in entity_map:

        if sentence.find(w) != -1:

            temp_sentence = sentence
            #print "BEFORE w is %s" %w

            for t in entity_map:
                if t.find(w) != -1 or w.find(t)!= -1:
                    continue
                if entity_map[t]:
                    temp_sentence = temp_sentence.replace(entity_map[t],"")
                elif temp_sentence.find(t) != -1:
                    temp_sentence = temp_sentence.replace(t,"")

            if entity_map[w]:
                w = entity_map[w]

            w_size = w.count(" ")+1

            temp_sentence = re.sub(" +"," ",temp_sentence)
            temp_sentence += ' ' #little trick to ensure that the last token of sentence is a space
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
                    try:
                        window_string = temp_sentence[m.end()+1:spaces[w_end]]
                    except IndexError:
                        print "sentence is %s" %sentence
                        print "temp sentece is %s" %temp_sentence
                        print "m_end and w_end: %d %d" %(m.end(),w_end)
                        sys.exit(-1)
                #print "now w is %s" %w
                if w not in windows: 
                    windows[w] = Sentence(window_string,remove_stopwords=True).stemmed_model
                else:
                    windows[w] += Sentence(window_string,remove_stopwords=True).stemmed_model



def get_nochange_map(words):
    entity_map = {}
    for w in words:
        entity_map[w] = w
    #print json.dumps(entity_map)
    return entity_map


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
    

def get_all_sentence_windows(documents,candidates):
    windows = {}
    for instance in documents:
        print "%s:" %instance
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
                windows[instance][w] = temp_windows[w].model
            except KeyError:
                print "cannot find entity %s" %(w)
                print 'store to remove later'

        
    return windows

def get_all_text_windows(documents,entities_judgement,negative_candidates,window_size):
    #TODO
    #This function needs to be modified
    return None


    windows = {}
    for instance in documents:
        print "%s:" %instance
        words = set()
        windows[instance] = {}
        for e_type in TYPES:
            for my_type in TYPES[e_type]:
                words.update(negative_candidates[instance][my_type])
                windows[instance][my_type] = {}
        #words += entities_judgement[instance][required_type]
        entity_map = get_nochange_map(words)

        temp_windows = {}
        for single_file in documents[instance]:
            print "process file %s" %single_file
            for sentence in documents[instance][single_file].sentences:
                get_text_window(entity_map,sentence.text,temp_windows,window_size)


        for entity_type in negative_candidates[instance]:
            for w in negative_candidates[instance][entity_type]:
                windows[instance][entity_type][w] = temp_windows[w]

    return windows


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


def get_json(source,required_type,positive_entities):
    data = {}
    tag = ""
    with open(source,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\t(.+?):(\d+(\.\d+)?)$",line)
                if m is not None:
                    entity = m.group(1)
                    if entity not in positive_entities:
                        data[tag][entity] = float(m.group(2))
                else:
                    print "line did not match:"
                    print line

    
    return data[required_type]







def get_candidates(candidate_file):
    candidates = json.load(open(candidate_file))
    return candidates




def show_json(data):
    print json.dumps(data,indent=4)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text_dir",'-tp',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/clean_text/noaa')
    parser.add_argument("dest_dir")
    parser.add_argument("candidate_file")

    parser.add_argument("--using_text_window","-u",action='store_true')
    parser.add_argument("--window_size",'-wz',type=int,default=3)
    args=parser.parse_args()
    
    


    
    candidates= get_candidates(args.candidate_file)
    instance_names = candidates.keys()
    documents = get_documents(instance_names,args.text_dir)

 

    if args.using_text_window:
        windows = get_all_text_windows(documents,candidates,args.window_size)

    else:
        windows = get_all_sentence_windows(documents,candidates)
  


    for instance in instance_names:
        print "store result for %s" %instance
        with codecs.open(os.path.join(args.dest_dir,instance),'w','utf-8') as f:
            f.write(json.dumps(windows[instance]))

    print "finished"

if __name__=="__main__":
    main()


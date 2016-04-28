"""
map frame with core text as verb found for entities to entities
"""

import os
import json
import sys
import re
import argparse
import codecs
import traceback

def get_verb_frame(output,entity,verbs,line_num):
    verb_frames = []
    try:
        for frame in output["frames"]:
            for i in range(0,len(frame['target']['spans'])):
                
                core_text = frame['target']['spans'][i]['text']
                if (core_text not in verbs):
                    continue
                else:
                    single_frame = {}
                    single_frame['core_text'] = core_text
                    single_frame['verb_label'] = verbs[core_text]
                    single_frame['name'] = frame['target']['name']
                    single_frame['elements'] = {}
                    single_frame['text'] = ""
                    for annotation in frame['annotationSets'][i]['frameElements']:    
                        element_name = annotation['name']
                        element_text = []
                        
                        for span in annotation['spans']:
                            element_text.append(span['text'])
                            single_frame['text']  += " "+span['text']
        
                         
                        single_frame['elements'][element_name] =element_text
                    if (single_frame['text'].find(entity) == -1):
                            continue
                    else:
                        #single_frame['text'] = frame_text
                        verb_frames.append(single_frame)
    except Exception as e:
        print "error at %s" %line_num
        print e
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60

        #print output
        sys.exit(-1)
    return verb_frames



def map_verb_frames(semafor_output_file,indexed_tuples):
    all_verb_frames = {}
    i=1
    with open(semafor_output_file) as f:
        for line in f:
            line_index = str(i)
            sentence_semafor = json.loads(line.rstrip())
            sentence_result_tuples = indexed_tuples[line_index]["result_tuples"]
            instance = indexed_tuples[line_index]["instance"]
            entity = indexed_tuples[line_index]["entity"]
            verbs = {}
            for single_tuple in sentence_result_tuples:
                verbs[single_tuple["verb"]] = single_tuple["verb_label"]


            verb_frames = get_verb_frame(sentence_semafor,entity,verbs,line_index)
            identifier = instance+'/'+entity
            if identifier not in all_verb_frames:
                all_verb_frames[identifier] = []
            all_verb_frames[identifier] += verb_frames

            i+=1
    print "there are %d sentence frmaes" %(len(all_verb_frames))
    return all_verb_frames


def json_load(json_file):
    return json.load(open(json_file))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("semafor_output_file")
    parser.add_argument("indexed_tuple_file")
    parser.add_argument("output_file")
    args=parser.parse_args()
    indexed_tuple = json_load(args.indexed_tuple_file)
    all_verb_frames = map_verb_frames(args.semafor_output_file,indexed_tuple)
    with codecs.open(args.output_file,'w','utf-8') as f:
        f.write(json.dumps(all_verb_frames))


if __name__=="__main__":
    main()


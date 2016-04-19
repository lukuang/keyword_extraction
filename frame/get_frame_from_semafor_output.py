"""
get frame from SEMAFOR output
"""

import os
import json
import sys
import re
import argparse
import codecs

def get_frame(output):
    all_frames = []
    line_num = 1
    try:
        for frame in output["frames"]:
            for i in range(0,len(frame['target']['spans'])):
                single_frame = {}
                single_frame['name'] = frame['target']['name']
                single_frame['core_text'] = frame['target']['spans'][i]['text']
                single_frame['elements'] = {}
                for annotation in frame['annotationSets'][i]['frameElements']:    
                    element_name = annotation['name']
                    element_text = []
                    
                    for span in annotation['spans']:
                        element_text.append(span['text'])

                    single_frame['elements'][element_name] =element_text
                all_frames.append(single_frame)
            line_num += 1    
    except:
        print "error at %d" %line_num
        print output
        sys.exit(-1)
    return all_frames


def load_sentence_index(sentence_index):
    return json.load(open(sentence_index))


def check(sentence_frames,entity):
    has_entity = False
    for single_frame in sentence_frames:
        frame_text = single_frame['core_text']
        for element_name in single_frame['elements']:
            #for text in single_frame['elements'][element_name]:
            frame_text += "  ".join(single_frame['elements'][element_name])
            has_entity = (frame_text.find(entity) != -1)
    return has_entity



def get_semafor_json(semafor_output):
    data = []
    with open(semafor_output) as f:
        for line in f:
            data.append(json.loads(line.rstrip()))
    print "there are %d sentence frmaes" %(len(data))
    return data

def write_frams(semafor_json,output_file,sentence_index):
    result_json = {}
    i=1
    for sentence_json in semafor_json:
        sentence_frames = get_frame(semafor_json)
        #print sentence_frames
        index = str(i)
        entity = sentence_index[index]['entity']
        instance = sentence_index[index]['instance']
        indentifier = instance+'/'+entity
        if check(sentence_frames,entity):
            if indentifier not in result_json:
                result_json[indentifier] = []
            result_json[indentifier].append(sentence_frames)

        i += 1

    with codecs.open(output_file,'w','utf-8') as f:
        f.write(json.dumps(result_json) )



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("semafor_output")
    parser.add_argument("output_file")
    parser.add_argument("sentence_index")
    args=parser.parse_args()
    sentence_index = load_sentence_index(args.sentence_index)
    semafor_json = get_semafor_json(args.semafor_output)
    write_frams(semafor_json,args.output_file,sentence_index)
    #sentence_frames = get_frame(test_json_output)
    #print json.dumps(sentence_frames,indent=4)

if __name__=="__main__":
    main()


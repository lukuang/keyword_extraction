"""
get frame from SEMAFOR output
"""

import os
import json
import sys
import re
import argparse


def get_frame(output):
    all_frames = []
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
    return all_frames



def get_semafor_json(semafor_output):
    data = []
    with open(semafor_output) as f:
        for line in f:
            data = json.loads(line.rstrip())
    return data

def write_frams(semafor_json,output_file):
    result_json = []
    for sentence_json in semafor_json:
        sentence_frame = get_frame(semafor_json)
        fresult_json.append(sentence_frame)

    with codecs.open(output_file,'w','utf-8') as f:
        f.write(result_json)



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("semafor_output")
    parser.add_argument("output_file")
    args=parser.parse_args()
    semafor_json = get_semafor_json(open(args.semafor_output))
    write_frams(semafor_json,args.output_file)
    #sentence_frame = get_frame(test_json_output)
    #print json.dumps(sentence_frame,indent=4)

if __name__=="__main__":
    main()


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
                
                for span in annotation['name']['spans']:
                    element_text.append(span['text'])

                single_frame['elements'][element_name] =element_text
            all_frames.append(single_frame)
    return all_frames



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("test_json_output")
    args=parser.parse_args()
    test_json_output = json.load(open(args.test_json_output))
    sentence_frame = get_frame(test_json_output)
    print json.dumps(sentence_frame,indent=4)

if __name__=="__main__":
    main()


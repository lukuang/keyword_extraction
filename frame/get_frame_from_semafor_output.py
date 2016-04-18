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
        single_frame = {}
        single_frame['name'] = frame['target']['name']
        single_frame['core_text'] = frame['target']['spans']['text']
        single_frame['elements'] = {}
        for annotation in frame['annotationSets']:    
            single_frame['elements']['name'] = annotation['frameElements']['name']
            single_frame['elements']['text'] = annotation['frameElements']['spans']['text']
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


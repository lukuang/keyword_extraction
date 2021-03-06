"""
get the entity frames with verb as part of the core text
"""

import os
import json
import sys
import re
import argparse
import nltk
import codecs

NEEDED_TAGS = [
    'VB',
    'VBD',
    'VBG',
    'VBN',
    'VBP',
    'VBZ'
]


def read_entity_frame_file(entity_frame_file):
    entity_frame = json.load(open(entity_frame_file))
    return entity_frame



def get_pos_tag(core_text):
    tokens = nltk.word_tokenize(core_text)
    tags = nltk.pos_tag(tokens)
    return tags


def check_core_text(single_frame):
    tags = get_pos_tag(single_frame['core_text'])
    for t in tags:
        if t[1] in NEEDED_TAGS:
            return True
    return False


def get_verb_frames(entity_frame_file):
    entity_verb_frames = {}
    entity_frame = read_entity_frame_file(entity_frame_file)
    i = 0
    for indentifier in entity_frame:
        print "for",indentifier
        for single_frame in entity_frame[indentifier]:
            if check_core_text(single_frame):
                if indentifier not in entity_verb_frames:
                    entity_verb_frames[indentifier] = []
                entity_verb_frames[indentifier].append(single_frame)
        i += 1
        if (i%100==0):
            print "processed %d entities" %i
        
    return entity_verb_frames

def output(entity_verb_frames,output_file):
    with codecs.open(output_file,'w','utf-8') as f:
        f.write(json.dumps(entity_verb_frames))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entity_frame_file")
    parser.add_argument("output_file")

    args=parser.parse_args()
    entity_verb_frames = get_verb_frames(args.entity_frame_file)
    output(entity_verb_frames,args.output_file)

if __name__=="__main__":
    main()


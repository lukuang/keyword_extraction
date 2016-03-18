"""
get average model of different entity types
"""

import os
import json
import sys
import re
import argparse
from myUtility.corpus import Model



def get_model_for_entities(source_dir):
    models = {}
    for instance in os.walk(source_dir).next()[2]:
        data = json.load(open(os.path.join(source_dir,instance)))
        for entity_type in data:
            if entity_type not in models:
                models[entity_type] = Model(True,need_stem = True)
            for entity in data[entity_type]:
                models[entity_type] += Model(True,text_dict=data[entity_type][entity],need_stem=True,input_stemmed=True)
    return models

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir")
    parser.add_argument("dest_file")
    parser.add_argument("--normalize","-n",action='store_true')


    args=parser.parse_args()

    models = get_model_for_entities(args.source_dir)
    for entity_type in models:
        # print "%s:" %entity_type
        if args.normalize:
            models[entity_type].normalize()
        # print json.dumps(models[entity_type].model,indent=True)
        sorted_model = sorted(models[entity_type].model.items(),key=lambda x: x[1], reverse=True)
        for (w,c) in sorted_model:
            print "\t%s:%d" %(w,c)
        print '-'*20


if __name__=="__main__":
    main()

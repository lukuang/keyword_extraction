"""
get top ranked entities for all measures
"""

import os
import json
import sys
import re
import argparse
from read_entity_profile import read_entity_profile, show
from get_entity_cate import get_entity_cate
from myUtility.wikiapi import *
import codecs


def get_top_ranked_entities(entity_profiles):
    #wikipedia_caller = Wikipedia()
    #wikidata_caller = Wikidata()
    top_ranked_entities = {}
    top_ranked_entities["if"] = {}
    for metric in entity_profiles:
        if metric not in top_ranked_entities:
            top_ranked_entities[metric] = {}
        for instance in entity_profiles[metric]:
            for entity_type in entity_profiles[metric][instance]:
                if entity_type not in top_ranked_entities[metric]:
                    top_ranked_entities[metric][entity_type] = {}
                for entity in entity_profiles[metric][instance][entity_type]:
                    if entity not in top_ranked_entities[metric][entity_type]:
                        top_ranked_entities[metric][entity_type][entity] = entity_profiles[metric][instance][entity_type][entity]
                        #top_ranked_entities[metric][entity_type][entity] = 0
                    #top_ranked_entities[metric][entity_type][entity] += 1
    for instance in  entity_profiles["df"]:
        for entity_type in entity_profiles["df"][instance]:
            if entity_type not in top_ranked_entities["if"]:
                top_ranked_entities["if"][entity_type] = {}
            for entity in entity_profiles["df"][instance][entity_type]:
                if entity not in top_ranked_entities["if"][entity_type]:
                    top_ranked_entities[metric][entity_type][entity] = 0
                top_ranked_entities[metric][entity_type][entity] += 1

    return top_ranked_entities

def get_top_ranked_entity_types(top_ranked_entities):
    wikipedia_caller = Wikipedia()
    wikidata_caller = Wikidata()
    top_ranked_entity_types = {}
    for metric in top_ranked_entities:
        if metric not in top_ranked_entity_types:
            top_ranked_entity_types[metric] = {}
        for entity_type in top_ranked_entities[metric]:
            if entity_type not in top_ranked_entity_types[metric]:
                top_ranked_entity_types[metric][entity_type] = {}
            for entity in top_ranked_entities[metric][entity_type]:
                entity_cate = get_entity_cate(entity,wikipedia_caller,wikidata_caller)
                if entity_cate is None:
                    continue
                else:
                    for cid in entity_cate:
                        cate = entity_cate[cid]
                        if cate not in top_ranked_entity_types[metric][entity_type]:
                            top_ranked_entity_types[metric][entity_type][cate] = 0
                        top_ranked_entity_types[metric][entity_type][cate] +=  top_ranked_entities[metric][entity_type][entity]
    return top_ranked_entity_types



def write_to_file(entity_types,output_file):
    with codecs.open(output_file,"w",'utf-8') as f:
        f.write(json.dumps(entity_types))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("entity_dir")
    parser.add_argument("output_file")
    parser.add_argument("--required_entity_types", "-r",nargs='+',default=["ORGANIZATION"])
    parser.add_argument("--name_patterns", "-n",nargs='+', default=[
        'df',
        'dfd',
        'tf'
    ])
    args=parser.parse_args()

    entity_profiles = read_entity_profile(args.entity_dir,args.disaster_name, args.name_patterns,args.required_entity_types)
    top_ranked_entities = get_top_ranked_entities(entity_profiles)
    entity_types = get_top_ranked_entity_types(top_ranked_entities)
    write_to_file(entity_types,args.output_file)

if __name__=="__main__":
    main()


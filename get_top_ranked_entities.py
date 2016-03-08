"""
get top ranked entities for all measures
"""

import os
import json
import sys
import re
import argparse
from read_entity_profile import read_entity_profile, show
from myUtility.wikiapi import *



def get_top_ranked_entities(entity_profiles):
    #wikipedia_caller = Wikipedia()
    #wikidata_caller = Wikidata()
    top_ranked_entities = {}
    for metric in entity_profiles:
        if metric not in top_ranked_entities:
            top_ranked_entities[metric] = {}
        for instance in entity_profiles[metric]:
            for entity_type in entity_profiles[metric][instance]:
                if entity_type is not in top_ranked_entities[metric]:
                    top_ranked_entities[metric][entity_type] = {}
                for entity in entity_profiles[metric][instance][entity_type]:
                    if entity not in top_ranked_entities[metric][entity_type]:
                        top_ranked_entities[metric][entity_type][entity] = entity_profiles[metric][instance][entity_type][entity]

    return top_ranked_entities



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("entity_dir")
    parser.add_argument("--required_entity_types", "-r",nargs='+',default=["ORGANIZATION"])
    parser.add_argument("--name_patterns", "-n",nargs='+', default=[
        'df',
        'dfd',
        'tf'
    ])
    args=parser.parse_args()

    entity_profiles = read_entity_profile(args.entity_dir,args.disaster_name, args.name_patterns,args.required_entity_types)
    top_ranked_entities = get_top_ranked_entities(entity_profiles)
    show(top_ranked_entities)

if __name__=="__main__":
    main()


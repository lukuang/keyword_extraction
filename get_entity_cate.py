"""
get category information for an entity
"""

import os
import json
import sys
import re
import argparse
from myUtility.wikiapi import *


def get_entity_cate(entity,wikipedia_caller,wikidata_caller):
    try:
        entity_name = wikipedia_caller.get_entity_name(entity)
    except wikiexceptions.ResultErrorException:
        print "cannot find an entity for name %s" %entity
        return None
    try:
        entity_info = wikidata_caller.get_entity_info_by_name(entity_name)
    except wikiexceptions.NoClassException:
        print "entity %s has no class info" %entity_name
        return None

    else:
        return entity_info['class_info']

def get_cate_for_entity_list(entity_list):
    wikipedia_caller = Wikipedia()
    wikidata_caller = Wikidata()
    cate_info = {}
    for entity in entity_list:
        result =  get_entity_cate(entity,wikipedia_caller,wikidata_caller)
        if not result:
            cate_info[entity] = None
        else:
            cate_info[entity] = []
            for cid in result:
                cate_info[entity].append(result[cid])
    return cate_info

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entity")
    args=parser.parse_args()
    wikipedia_caller = Wikipedia()
    wikidata_caller = Wikidata()
    entity_cate = get_entity_cate(args.entity,wikipedia_caller,wikidata_caller)
    print entity_cate
    



if __name__=="__main__":
    main()


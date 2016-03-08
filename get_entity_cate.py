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
    
    entity_name = wikipedia_caller.get_entity_name(entity)
    entity_info = wikidata_caller.get_entity_info_by_name(entity_name)
    return entity_info['class_info']

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


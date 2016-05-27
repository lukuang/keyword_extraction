"""
create narrative file for new_tornado for checking
"""

import os
import json
import sys
import re
import argparse
import codecs


def load_json(json_file):
    return json.load(open(json_file))


def get_episode_entities(narrative_entity_file):
    narrative_entities = {}
    original_entities = {}
    with open(narrative_entity_file) as f:
        data = json.load(f)
        for eid in data:
            narrative_entities[eid] = data[eid]['narrative'].keys()
            original_entities[eid] = data[eid]['original'].keys()
    print len(original_entities)
    print len(narrative_entities)

    return narrative_entities,original_entities


def get_manual_label(manual_label_file):
    mapping = {}
    data = load_json(manual_label_file)
    for query in data:
        for eid in data[query]:
            mapping[eid] = query
    return mapping

def creat_narrative(all_narrative_entities,all_original_entities,mapping,dest_file):
    data = {}
    for eid in mapping:
        query = mapping[eid]
        if query not in data:
            data[query]={
                "original":{},
                "narrative":{}
            }
        for entity in all_original_entities[eid]:
            if entity not in data[query]["original"]:
                data[query]["original"].append(entity)
        for entity in all_narrative_entities[eid]:
            if entity not in data[query]["narrative"]:
                data[query]["original"].append(entity)
    with open(dest_file,'w') as f:
        f.write(json.dumps(data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dest_file")
    parser.add_argument("--narrative_entity_file",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/episode_entities.json')
    parser.add_argument("--mapping_file",'-mf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/check/eid.json')
    args=parser.parse_args()

    all_narrative_entities,all_original_entities = get_episode_entities(args.narrative_entity_file)
    mapping = get_manual_label(args.mapping_file)
    creat_narrative(all_narrative_entities,all_original_entities,mapping,args.dest_file)

if __name__=="__main__":
    main()


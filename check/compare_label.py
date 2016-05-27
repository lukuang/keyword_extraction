"""
compare my judgement labels with thtose that are automatically generated
by noaa data
"""

import os
import json
import sys
import re
import argparse
import codecs


def load_json(json_file):
    return json.load(open(json_file))


def get_negative_entities(negative_entity_file):
    return load_json(negative_entity_file)


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


def get_auto_entities(all_narrative_entities,all_original_entities,all_negative_entities, mapping):
    auto_narrative_entities = {}
    auto_original_entities = {}
    auto_negative = {}
    for eid in mapping:

        query = mapping[eid]
        if query not in auto_narrative_entities:
            auto_narrative_entities[query] = []
        try:
            auto_narrative_entities[query] += all_narrative_entities[eid]
        except KeyError:
            pass

        if query not in auto_original_entities:
            auto_original_entities[query] = []
        try:
            auto_original_entities[query] += all_original_entities[eid]
        except KeyError:
            pass


        if query not in auto_negative:
            auto_negative[query] = []
        try:
            auto_negative[query] += all_negative_entities[eid]
        except KeyError:
            pass





    return auto_narrative_entities,auto_original_entities, auto_negative


def get_manual_entities(manual_candidate_dir):
    manual_positive = load_json(os.path.join(manual_candidate_dir,"positive"))
    manual_negative = load_json(os.path.join(manual_candidate_dir,"negative_no_location"))
    return manual_positive, manual_negative


def report(auto_data,manual_data):
    count = 0
    for e in auto_data:
        if e in manual_data:
            count += 1
    try:
        recall = count*1.0/len(manual_data)
    except ZeroDivisionError:
        print "WARNNING: zero size for manual_data"
        recall = 0
    try:
        precision = count*1.0/len(auto_data)
    except ZeroDivisionError:
        print "WARNNING: zero size for auto_data"
        precision = 0

    if recall!=0 and precision!=0:
        f1 = 2/(1/precision + 1/recall)
    else:
        f1 = 0
    print "\trecall: %f(%d/%d)" %(recall,count,len(manual_data))
    print "\tprecision: %f(%d/%d)" %(precision,count,len(auto_data))
    print "\tf1: %f" %(f1)




def compare(auto_narrative_entities,auto_original_entities, auto_negative,\
        manual_positive, manual_negative):
    print "-"*20
    for query in manual_positive:
        print "for query",query
        print "narrative:"
        report(auto_narrative_entities[query],manual_positive[query])
        print "original:"
        report(auto_original_entities[query],manual_positive[query])
        print "negative:"
        report(auto_negative[query],manual_negative[query])
        print "-"*20



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual_candidate_dir","-md",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/candidiates/new_tornado/")
    parser.add_argument("--negative_entity_file","-ngf",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/candidates/all_year/negative_no_location")
    parser.add_argument("--narrative_entity_file",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/episode_entities.json')
    parser.add_argument("--mapping_file",'-mf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/check/eid.json')
    args=parser.parse_args()

    all_narrative_entities,all_original_entities = get_episode_entities(args.narrative_entity_file)
    all_negative_entities = get_negative_entities(args.negative_entity_file)
    mapping = get_manual_label(args.mapping_file)
    auto_narrative_entities,auto_original_entities, auto_negative = \
        get_auto_entities(all_narrative_entities,all_original_entities,all_negative_entities, mapping)
    manual_positive, manual_negative = get_manual_entities(args.manual_candidate_dir)
    compare(auto_narrative_entities,auto_original_entities, auto_negative,\
        manual_positive, manual_negative)


if __name__=="__main__":
    main()


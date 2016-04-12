"""
match entities from narrative and news articles
"""

import os
import json
import sys
import re
import argparse


def read_single_file(file_path, required_entity_types):
    data = {}
    with open(file_path,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = []
            else:
                m = re.search("^\t(.+?):(\d+(\.\d+)?)$",line)
                if m is not None:
                    data[tag].append(m.group(1))
                else:
                    print "line did not match:"
                    print line
    if required_entity_types is not None:
        for tag in data.keys():
            if tag not in required_entity_types:
                data.pop(tag,None)
    return data


def get_narrative_entities(narrative_entity_file):
    narrative_entities = {}
    with open(narrative_entity_file) as f:
        data = json.load(f)
        for eid in data:
            narrative_entities[eid] = data[eid].keys()
    return narrative_entities


def get_news_entities(news_entity_dir,required_entity_types,required_file_name):
    news_entities = {}
    eids = os.walk(news_entity_dir).next()[1]
    for eid in eids:
        entity_file = os.path.join(news_entity_dir,eid,required_file_name)
        news_entities[eid] = read_single_file(entity_file, required_entity_types)
    return news_entities


def match_entities(narrative_entities,news_entities):
    total_narrative = 0 
    total_news = 0
    zero_entity_news = 0
    matched = 0
    average_percentage_narrative = .0
    average_percentage_news = .0
    match_percent_narrative = []
    match_percent_news = []
    for eid in narrative_entities:
        total_narrative += len(narrative_entities[eid])
        total_news += len(news_entities[eid])
        single_match = 0
        for entity in narrative_entities[eid]:
            if entity in news_entities[eid]:
                single_match +=1 
        matched += single_match
        if len(news_entities[eid])) == 0:
            match_percent_news.append(.0)
            zero_entity_news += 1
        else:
            match_percent_news.append((single_match*1.0)/len(news_entities[eid]))
        match_percent_narrative.append((single_match*1.0)/len(narrative_entities[eid]))

    number_of_eids = len(narrative_entities)
    average_percentage_narrative = sum(match_percent_narrative)/number_of_eids
    average_percentage_news = sum(match_percent_news)/number_of_eids

    """
    show the result
    """
    print "-"*20
    print "There are %d episodes and %d of them do not have news entities" %(len(narrative_entities),zero_entity_news)
    print "There are %d narrative entities and %d news entities" %(total_narrative,total_news)
    print "Total matched entities %d" %(matched)
    print "average macthing percentage:\nnarrative %f,\tnews: %f" %(average_percentage_narrative,average_percentage_news)


      

        



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--narrative_entity_file",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/episode_entities.json')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')
    args=parser.parse_args()

    narrative_entities = get_narrative_entities(args.narrative_entity_file)
    news_entities = get_news_entities(args.news_entity_dir,args.required_entity_types,args.required_file_name)
    match_entities(narrative_entities,news_entities)

if __name__=="__main__":
    main()


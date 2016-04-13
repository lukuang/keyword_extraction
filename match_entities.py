"""
match entities from narrative and news articles
"""

import os
import json
import sys
import re
import argparse
reload(sys)
sys.setdefaultencoding('UTF8')

def read_single_file(file_path, required_entity_types):
    # print "process file %s" %file_path
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
                    pass
                    #print "line did not match:"
                    #print line
    returned_data = []

    for tag in required_entity_types:
        if tag in data:
            returned_data += data[tag]
    return returned_data


def get_episode_entities(narrative_entity_file):
    narrative_entities = {}
    original_entities = {}
    with open(narrative_entity_file) as f:
        data = json.load(f)
        for eid in data:
            narrative_entities[eid] = data[eid]['narrative'].keys()
            original_entities[eid] = data[eid]['original'].keys()
    return narrative_entities,original_entities


def get_news_entities(news_entity_dir,required_entity_types,required_file_name):
    news_entities = {}
    eids = os.walk(news_entity_dir).next()[1]
    for eid in eids:
        entity_file = os.path.join(news_entity_dir,eid,required_file_name)
        news_entities[eid] = read_single_file(entity_file, required_entity_types)
    return news_entities


def match_entities(narrative_entities,original_entities,news_entities):
    total_narrative = 0 
    total_original = 0 
    total_episode = 0 
    total_news = 0
    zero_entity_news = 0
    matched = 0
    average_percentage_narrative = .0
    average_percentage_original = .0
    average_percentage_episode = .0
    average_percentage_news = .0
    match_percent_narrative = []
    match_percent_original = []
    match_percent_episode = []
    match_percent_news = []
    for eid in narrative_entities:
        # if eid != '70289':
        #     continue
        # else:
        #     print "narrative_entities:"
        #     print narrative_entities[eid]

        #     print "news_entities:"
        #     print news_entities[eid]
        total_narrative += len(narrative_entities[eid])
        total_original += len(original_entities[eid])
        sinlge_episode_entities = narrative_entities[eid] + original_entities[eid]
        total_episode += len(sinlge_episode_entities)
        total_news += len(news_entities[eid])
        original_match = 0
        narrative_match = 0
        single_match = 0
        for entity in news_entities[eid]:
            if entity in narrative_entities[eid]:
                narrative_match += 1
            elif entity in original_entities[eid]:
                original_match += 1 
        single_match = narrative_match + original_match
        matched += single_match
        if len(news_entities[eid]) == 0:
            match_percent_news.append(.0)
            zero_entity_news += 1
        else:
            match_percent_news.append((single_match*1.0)/len(news_entities[eid]))
        if len(narrative_entities[eid]) == 0:
            match_percent_narrative.append(.0)
        else:
            match_percent_narrative.append((narrative_match*1.0)/len(narrative_entities[eid]))
        match_percent_original.append((original_match*1.0)/len(original_entities[eid]))
        match_percent_episode.append((single_match*1.0)/len(sinlge_episode_entities))

    number_of_eids = len(narrative_entities)
    average_percentage_narrative = sum(match_percent_narrative)/number_of_eids
    average_percentage_original = sum(match_percent_original)/number_of_eids
    average_percentage_episode = sum(match_percent_episode)/number_of_eids
    average_percentage_news = sum(match_percent_news)/number_of_eids

    """
    show the result
    """
    print "-"*20
    print "There are %d episodes and %d of them do not have news entities" %(len(narrative_entities),zero_entity_news)
    print "There are %d episide entities, among which %d are narrative entities and %d are original entities" %(total_episode,total_narrative,total_original)
    print "There are %d news entiies." %(total_news)
    print "Total matched entities %d" %(matched)
    print "average macthing percentage:\nnarrative %f,\toriginal: %f" %(average_percentage_narrative,average_percentage_original)
    print "average macthing percentage:\nepisode %f,\tnews: %f" %(average_percentage_episode,average_percentage_news)


      

        



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--narrative_entity_file",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/episode_entities.json')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')
    args=parser.parse_args()

    narrative_entities,original_entities = get_episode_entities(args.narrative_entity_file)
    news_entities = get_news_entities(args.news_entity_dir,args.required_entity_types,args.required_file_name)
    match_entities(narrative_entities,original_entities,news_entities)

if __name__=="__main__":
    main()


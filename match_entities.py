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

def contained_in_positive(positive,entity):
    for e in positive:
        if e.find(entity)!=-1:
            return True
    return False

def read_single_file(file_path, required_entity_types,no_single_appearance,
    narrative_entities,original_entities):
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
                    entity = m.group(1)
                    if no_single_appearance:
                        
                        if (not contained_in_positive(narrative_entities,entity) ) and (not contained_in_positive(original_entities,entity)):
                            data[tag].append(entity)
                        elif float(m.group(2))>1:
                            data[tag].append(entity)
                            #print "include %s with %s" %(m.group(1),m.group(2)
                        else:
                            pass
                            #print "not include %s with %s" %(m.group(1),m.group(2))
                    else:
                        data[tag].append(entity)
                else:
                    pass
                    #print "line did not match:"
                    #print line
    returned_data = []
    
    for tag in required_entity_types:
        if tag in data:
            returned_data += data[tag]
    returned_data = list( set(returned_data) )
    # if show:
    #     print data
    #     print returned_data
    #     sys.exit(-1)
    return returned_data


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


def get_news_entities(news_entity_dir,required_entity_types,required_file_name,no_single_appearance,
    narrative_entities,original_entities):
    news_entities = {}
    eids = os.walk(news_entity_dir).next()[1]
    #original_entities.keys()
    for eid in eids:
        entity_file = os.path.join(news_entity_dir,eid,required_file_name)
        if eid not in narrative_entities:
            print "NO NARA"
        if eid not in original_entities:
            print "NO ORI"
        narrative_entities[eid],original_entities[eid]

        news_entities[eid] = read_single_file(entity_file, required_entity_types,no_single_appearance,narrative_entities[eid],original_entities[eid])
    return news_entities


def match_entities(narrative_entities,original_entities,news_entities):
    positive = {}
    negative = {}
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

    no_match_original = []
    no_news_entities = []
    for eid in original_entities:

        # if eid == '37771':
            
        #     print "narrative_entities:"
        #     print narrative_entities[eid]

        #     print "news_entities:"
        #     print news_entities[eid]

        #     print "original_entities:"
        #     print original_entities[eid]

        if eid not in news_entities or len(news_entities[eid]) == 0:
            
            zero_entity_news += 1
            no_news_entities.append(eid)
            positive.pop(eid,None)
            negative.pop(eid,None)

            continue

        positive[eid] = []
        negative[eid] = []
        original_match = 0
        narrative_match = 0
        single_match = 0
        for entity in news_entities[eid]:
            if entity in narrative_entities[eid]:
                narrative_match += 1
                positive[eid].append(entity)
            elif entity in original_entities[eid]:
                original_match += 1 
                positive[eid].append(entity)
            else:
                negative[eid].append(entity)
        single_match = narrative_match + original_match
        

        #print positive[eid]
        #print negative[eid]



        if len(news_entities[eid]) == 0:
            
            zero_entity_news += 1
            no_news_entities.append(eid)
            positive.pop(eid,None)
            negative.pop(eid,None)

            continue
        if (original_match==0):
            no_match_original.append(eid)
            positive.pop(eid,None)
            negative.pop(eid,None)
            continue


        

        matched += single_match
        total_narrative += len(narrative_entities[eid])
        total_original += len(original_entities[eid])
        sinlge_episode_entities = narrative_entities[eid] + original_entities[eid]
        total_episode += len(sinlge_episode_entities)
        total_news += len(news_entities[eid])

        if len(narrative_entities[eid]) == 0:
            match_percent_narrative.append(.0)
        else:
            match_percent_narrative.append((narrative_match*1.0)/len(narrative_entities[eid]))

        match_percent_original.append((original_match*1.0)/len(original_entities[eid]))
        match_percent_episode.append((single_match*1.0)/len(sinlge_episode_entities))
        match_percent_news.append((single_match*1.0)/len(news_entities[eid]))


    #number_of_eids = len(narrative_entities)-zero_entity_news-len(no_match_original)
    average_percentage_narrative = sum(match_percent_narrative)/len(match_percent_narrative)
    average_percentage_original = sum(match_percent_original)/len(match_percent_original)
    average_percentage_episode = sum(match_percent_episode)/len(match_percent_episode)
    average_percentage_news = sum(match_percent_news)/len(match_percent_news)

    """
    show the result
    """
    print "-"*20
    print "There are %d episodes and %d of them do not have news entities,\nand %d of them do not match any original entities" %(len(narrative_entities),zero_entity_news,len(no_match_original))
    print "There are %d episide entities, among which %d are narrative entities and %d are original entities" %(total_episode,total_narrative,total_original)
    print "There are %d news entiies." %(total_news)
    print "Total matched entities %d" %(matched)
    print "average macthing percentage:\nnarrative %f,\toriginal: %f" %(average_percentage_narrative,average_percentage_original)
    print "average macthing percentage:\nepisode %f,\tnews: %f" %(average_percentage_episode,average_percentage_news)
    print "The episodes did not match any original entities"
    print no_match_original
    print "The episodes did not have any news entities"
    print no_news_entities
    return positive, negative
        

def output(positive,negative,positive_out,negative_out,overlap,remove_overlap):
    with open(positive_out,'w') as f:
        f.write(json.dumps(positive))

    if(remove_overlap):
        remove_count = 0
        for instance in negative:
            for overlap_instance in overlap[instance]:
                if overlap_instance in positive:
                    for w in positive[overlap_instance]:
                        if w in negative[instance]:
                            negative[instance].remove(w)
                            remove_count += 1
        print "removed %d entities" %remove_count

        
    with open(negative_out,'w') as f:
        f.write(json.dumps(negative))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--narrative_entity_file",'-nf',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/episode_entities.json')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--no_single_appearance",'-ns',action='store_true',
        help="If given, remove entities with idf/tf <=1")
    parser.add_argument("--remove_overlap",'-rl',action='store_true')
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')
    parser.add_argument("--overlap",'-op',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/overlap.json')
    parser.add_argument('--positive_out','-po',default='./positive')
    parser.add_argument('--negative_out','-no',default='./negative')


    args=parser.parse_args()

    narrative_entities,original_entities = get_episode_entities(args.narrative_entity_file)
    news_entities = get_news_entities(args.news_entity_dir,args.required_entity_types,args.required_file_name,args.no_single_appearance,narrative_entities,original_entities)
    overlap = json.load(open(args.overlap))
    positive,negative = match_entities(narrative_entities,original_entities,news_entities)
    output(positive,negative,args.positive_out,args.negative_out,overlap,args.remove_overlap)

if __name__=="__main__":
    main()


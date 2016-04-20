"""
generate csv file for maual annotation
"""

import os
import json
import sys
import re
import argparse
import csv
import codecs


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

def get_news_entities(news_entity_dir,required_entity_types,required_file_name):
    news_entities = {}
    eids = os.walk(news_entity_dir).next()[1]
    for eid in eids:
        entity_file = os.path.join(news_entity_dir,eid,required_file_name)
        news_entities[eid] = read_single_file(entity_file, required_entity_types)
    return news_entities



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION"])
    parser.add_argument("--required_file_name",'-rn',default='df')
    parser.add_argument("--output_file",'-o',default='judgement.csv')
    args=parser.parse_args()


    news_entities = get_news_entities(args.news_entity_dir,args.required_entity_types,args.required_file_name)
    
    fieldnames = ['eid','entity']
    with codecs.open(args.output_file,'w','utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for eid in news_entities:
            for entity in news_entities[eid]:
                row = {}
                row['eid'] = eid
                row['entity'] = entity
                writer.writerow(row)





if __name__=="__main__":
    main()


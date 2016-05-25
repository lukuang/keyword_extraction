"""
create candidate entity files for new tornadoes for checking
"""

import os
import json
import sys
import re
import argparse
import codecs


def get_positive_entities(entity_judgement_file):
    positive = {}
    data = json.load(open(entity_judgement_file))
    for instance in data:
        qid = instance["query_string"]
        positive[qid] = {}
        positive[qid]["LOCATION"] = instance["LOCATION"]
        positive[qid]["ORGANIZATION"] = instance["ORGANIZATION"] + instance["FACILITY"]

    return positive


def read_single_file(file_path, positive,no_single_appearance):
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
                    if m.group(1) not in positive:
                        if no_single_appearance:
                            if float(m.group(2))>1:
                                data[tag].append(m.group(1))
                        else:
                            data[tag].append(m.group(1))

    try:
        sub_negative_no_location = data["ORGANIZATION"]
    except KeyError:
        sub_negative_no_location = []
    try:
        sub_negative = sub_negative_no_location + data["LOCATION"]
    except KeyError:
        sub_negative = sub_negative_no_location
    
    
   
    return sub_negative, sub_negative_no_location

def get_negative_entities(positive,entity_dir,required_file_name,no_single_appearance):
    negative = {}
    negative_no_location = {}
    for qid in positive:
        file_path = os.path.join(entity_dir,qid,required_file_name)
        sub_negative, sub_negative_no_location =\
            read_single_file(file_path,positive[qid],no_single_appearance)
        negative[qid] = sub_negative
        negative_no_location[qid] = sub_negative_no_location

    return negative, negative_no_location



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity.json')
    parser.add_argument("--entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/entity/new_tornado')
    parser.add_argument("--entity_judgement_file",'-ef',default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/entities_judgement.json")
    parser.add_argument("--negative_file","-no",default="negative")
    parser.add_argument("--negative_no_location_file","-nno",default="negative_no_location")
    parser.add_argument("--positive_file","-po",default="positive")
    parser.add_argument("--no_single_appearance",'-ns',action='store_true',
        help="If given, remove entities with idf/tf <=1")
    args=parser.parse_args()


    positive = get_positive_entities(args.entity_judgement_file)
    negative, negative_no_location = \
        get_negative_entities(positive,args.entity_dir,args.required_file_name,args.no_single_appearance)

    with codecs.open(args.positive_file,"w","utf-8") as f:
        f.write(json.dumps(positive))

    with codecs.open(args.negative_no_location_file,"w","utf-8") as f:
        f.write(json.dumps(negative_no_location))

    with codecs.open(args.negative_file,"w","utf-8") as f:
        f.write(json.dumps(negative))


if __name__=="__main__":
    main()



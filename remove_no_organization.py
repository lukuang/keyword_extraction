"""
remove non organization candidates in negative candidates
"""

import os
import json
import sys
import re
import codecs
import argparse

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity.json')
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("negative_candidate_file")
    parser.add_argument("dest_file")
    args=parser.parse_args()

    negative_candidates = json.load(open(args.negative_candidate_file))
    for eid in negative_candidates:
        print "for",eid
        episode_entities = json.load(open(os.path.join(args.news_entity_dir,eid,args.required_file_name)))
        organization_entities = episode_entities["ORGANIZATION"]
        sub_negative =  negative_candidates[eid]
        for e in sub_negative:
            if e not in organization_entities:
                negative_candidates[eid].remove(e)

    with codecs.open(args.dest_file,"w","utf-8") as f:
        f.write(json.dumps(negative_candidates))


if __name__=="__main__":
    main()


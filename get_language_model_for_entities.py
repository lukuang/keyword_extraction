"""
get the language model surrounding some entities
"""

import os
import json
import sys
import re
import argparse




def get_files(a_dir):
    all_files = os.walk(a_dir).next()[2]
    files = []
    for f in all_files:
        files.append( os.path.join(a_dir,f) )
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("top_dir")
    parser.add_argument("--src_dir","-s", default="/lustre/scratch/lukuang/keyphrase_extraction/src")
    parser.add_argument("--top",'-t',type=int,default=10)
    args=parser.parse_args()
    

    args.top_dir = os.path.abspath(args.top_dir)
    raw_dir = os.path.join(args.top_dir, "raw",args.disaster_name)
    instance_names = os.walk(raw_dir).next()[1]
    files = {}
    for instance in instance_names:
        print "for %s" %instance
        source_dir = os.path.join(args.top_dir,"clean_text",args.disaster_name,instance)
        sub_dirs = os.walk(source_dir).next()[1]
        files[instance] = []
        for a_dir in sub_dirs:
            files[instance] += get_files(os.path.join(source_dir,a_dir))
    print json.dumps(files,indent=4)

if __name__=="__main__":
    main()


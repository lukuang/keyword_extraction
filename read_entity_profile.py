"""
get entity profile's for NER results
"""

import os
import json
import sys
import re
import argparse

def read_single_file(file_path):
    data = {}
    with open(file_path,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\t(.+?):(.+)$",line)
                if m is not None:
                    data[tag][m.group(1)] = float(m.group(2))
                else:
                    print "line did not match:"
                    print line
    return data


def get_profiles(entity_sub_dirs, name_patterns):
    entity_profiles = {}
    for name in name_patterns:
        entity_profiles[name] = {}
        for sub_dir in entity_sub_dirs:
            file_path = os.path.join(sub_dir,name)
            entity_profiles[name][sub_dir] = read_single_file(file_path)


def get_dirs(entity_dir,disaster_name):
    dir_location = os.path.join(entity_dir,disaster_name)
    return [ os.path.join(dir_location,f) for f in os.walk(dir_locations).next()[1]]

def show(entity_profiles):
    print json.dumps(entity_profiles,sort_keys=True, indent=4)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("entity_dir")

    args=parser.parse_args()

    name_patterns = [
        'df',
        'dfd',
        'tf'
    ]

    entity_sub_dirs = get_dirs(args.entity_dir,args.disaster_name)
    entity_profiles = get_profiles(entity_sub_dirs, name_patterns)
    show(entity_profiles)


if __name__=="__main__":
    main()


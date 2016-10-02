"""
get required entities from 
"""

import os
import json
import sys
import re
import argparse
import codecs
#reload(sys)
#sys.setdefaultencoding('UTF8')


def get_entities_from_raw(source_file,reuqired_types,remove_single):
    data = {}
    tag = ""
    sub_entity_list = []
    with open(source_file,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\t(.+?):(\d+(\.\d+)?)$",line)
                if m is not None:
                    frequency = float(m.group(2))
                    if remove_single:
                        if frequency > 1:
                            data[tag][m.group(1)] = frequency   
                    else:
                        data[tag][m.group(1)] = frequency
                # else:
                #     print "line did not match:"
                #     print line

    #remove entities with type that is not wanted
    num_of_instances = 0
    for tag in data.keys():
        if tag not in reuqired_types:
            data.pop(tag,None)
        else:
            for entity in data[tag]:
                num_of_instances += data[tag][entity]
            
            sub_entity_list +=  data[tag].keys()

    print "There are %d instances" %(num_of_instances)

    with open(source_file+".json","w") as f:
        f.write(json.dumps(data))
    return num_of_instances, sub_entity_list





def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir")
    parser.add_argument("dest_file")
    parser.add_argument("--reuqired_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--remove_single",'-rs',action="store_true")

    args=parser.parse_args()

    total = 0
    candidates = {}
    for single_dir in os.walk(args.source_dir).next()[1]:
        source_file = os.path.join(args.source_dir,single_dir,"tf")
        disaster_name = single_dir
        sub_total, sub_entity_list= get_entities_from_raw(source_file,args.reuqired_types,args.remove_single)
        total += sub_total
        candidates[disaster_name] = sub_entity_list

    print "Total number of instances %d" %(total)

    with open(args.dest_file,"w") as f:
        f.write(json.dumps(candidates))


if __name__=="__main__":
    main()


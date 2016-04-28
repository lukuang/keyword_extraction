"""
combine the output results of VerbPairFinder
"""

import os
import json
import sys
import re
import argparse
import codecs


NO_NEED = ['were','was','is','has','are','have','had','been','be']


def combine_verbpairfinder_output(s_dir):
    data = {}
    for f in os.walk(s_dir).next()[2]:
        f = os.path.join(s_dir,f)
        temp_data = json.load(open(f))
        for i in temp_data:
            result_tuples = temp_data[i]["result_tuples"]
            new_tuples = []
            if i == "10897":
                print "found!"
                print result_tuples
                for single_tuple in result_tuples:
                    verb  = single_tuple["verb"]
                    if verb  in NO_NEED:
                        print "no need word",verb
                        temp_data[i]["result_tuples"].remove(single_tuple)
                print "result afterwords"
                print result_tuples
                    
            else:
                continue
            for single_tuple in result_tuples:
                verb  = single_tuple["verb"]
                if verb not in NO_NEED:
                    #temp_data[i]["result_tuples"].remove(single_tuple)
                    new_tuples.append(single_tuple)
            temp_data[i]["result_tuples"] = new_tuples


        data.update(temp_data)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("s_dir")
    parser.add_argument("dest_file")

    args=parser.parse_args()
    data = combine_verbpairfinder_output(args.s_dir)
    with codecs.open(args.dest_file,'w','utf-8') as f:
        f.write(json.dumps(data) )


if __name__=="__main__":
    main()


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
            if len(result_tuples)==0:
                continue
            for j  in range(len(result_tuples) ):
                single_tuple = result_tuples[j]
                verb  = single_tuple["verb"]
                if verb in NO_NEED:
                    del temp_data[i]["result_tuples"][j]

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


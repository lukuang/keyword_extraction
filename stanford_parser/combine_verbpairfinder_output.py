"""
combine the output results of VerbPairFinder
"""

import os
import json
import sys
import re
import argparse
import codecs

def combine_verbpairfinder_output(s_dir):
    data = {}
    for f in os.walk(s_dir).next()[2]:
        f = os.path.join(s_dir,f)
        data.update(json.load(open(f)))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("s_dir")
    parser.add_argument("dest_file")

    args=parser.parse_args()
    data = combine_verbpairfinder_output(args.s_dir)
    with codecs.open(args.dest_file,'w','utf-8') as f:
        f.write(data)


if __name__=="__main__":
    main()


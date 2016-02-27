"""
process the results generated by standford NLP
"""

import os
import json
import sys
import re
import argparse


def get_json(source):
    data = {}
    tag = ""
    with open(source,"r") as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^(\w+):$",line)
            if m is not None:
                tag = m.group(1)
                data[tag] = {}
            else:
                m = re.search("^\s+(\w+):(\d+)$",line)
                if m is not None:
                    data[tag][m.group(1)] = int(m.group(2))
                else:
                    print "line did not match:"
                    print line
    with open(source+".json","w") as f:
        f.write(json.dumps(data))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("dest")
    args=parser.parse_args()
    get_json(args.source)

if __name__=="__main__":
    main()


"""
extract text from html files
"""

import os
import json
import sys
import re
import argparse
import codecs
from Html_parser import Html_parser




def check_top(file_name, top):
    m=re.match("^(\d+)-\d+$",file_name)
    if m is not None:
        page = int(m.group(1))
        if page <= top:
            return True
    return False


def get_files(a_dir,top):
    all_files = os.walk(a_dir).next()[2]
    files = []
    for f in all_files:
        if check_top(f,top):
            files.append(f)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir")
    parser.add_argument("dest_dir")
    #parser.add_argument("phrase_dir")
    parser.add_argument("--need_stem","-m",action='store_true',default=False)
    parser.add_argument("--top","-t",type=int,default=10)
    args=parser.parse_args()

    parser = Html_parser(args.need_stem)

    files = get_files(args.source_dir,args.top)
    for f in files:
        dest_file = os.path.join(args.dest_dir,f)
        text = parser.get_text(os.path.join(args.source_dir,f))
        with codecs.open(dest_file,"w","utf-8") as of:
            of.write(text)



if __name__=="__main__":
    main()


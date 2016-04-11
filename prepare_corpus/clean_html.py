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
import langid




def check(file_name, top,first_only):
    m=re.match("^(\d+)-(\d+)$",file_name)
    if m is not None:
        page = int(m.group(1))
        if page <= top:
            if first_only:
                if int(m.group(2)) == 1:
                    return True
            else:    
                return True
    return False


def get_files(a_dir,top,first_only):
    all_files = os.walk(a_dir).next()[2]
    files = []
    for f in all_files:
        if check(f,top,first_only):
            files.append(f)
    return files

def gene_text_single_dir(parser,source_dir,dest_dir,top,first_only):
    files = get_files(source_dir,top,first_only)
    for f in files:
        dest_file = os.path.join(dest_dir,f)
        text = parser.get_text(os.path.join(source_dir,f))
        lan = langid.classify(text)[0]
        if lan != 'en':
            print "Skip non-english doc %s" %(dest_file)
            continue
        with codecs.open(dest_file,"w","utf-8") as of:
            of.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir")
    parser.add_argument("dest_dir")
    #parser.add_argument("phrase_dir")
    parser.add_argument("--need_stem","-m",action='store_true',default=False)
    parser.add_argument("--first_only","-o",action='store_true',default=False)
    parser.add_argument("--top","-t",type=int,default=10)
    args=parser.parse_args()

    parser = Html_parser(args.need_stem)
    sub_dirs = os.walk(args.source_dir).next()[1]
    for a_dir in sub_dirs:
        dest_dir = os.path.join(args.dest_dir,a_dir)
        source_dir = os.path.join(args.source_dir,a_dir)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        gene_text_single_dir(parser,source_dir,dest_dir,args.top, args.first_only)
    



if __name__=="__main__":
    main()


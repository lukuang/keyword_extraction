"""
run the whole process
"""

import os
import json
import sys
import re
import argparse
import subprocess


def call_clean_html(source_dir, dest_dir, top, first_only):
    args_clean_html = [
        'python',
        '/lustre/scratch/lukuang/keyphrase_extraction/src/prepare_corpus/clean_html.py',
        source_dir,
        dest_dir,
        "-t",
        str(top),
    ]
    if first_only:
        args_clean_html.append("-o")

    subprocess.call(args_clean_html)


def gene_entities(dest_dir,entity_dir):

    java_files = {
        "RankEntity" : "tf",
        "RankEntityDF" : "df",
        "RankEntityDFDiscounted" : "dfd"
    }

    args_run_java = [
        'java',
        '-cp',
        "'.:/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/lib/*'",
        "JAVA FILE",
        dest_dir,
    ]

    args_process_result = [
        'python',
        '/lustre/scratch/lukuang/keyphrase_extraction/src/prepare_corpus/process_result.py',
        "JAVA OUTPUT",
        "FINAL OUTPUT",
    ]

    for java_file in java_files:
        final_output = os.path.join(entity_dir,java_files[java_file])
        if os.path.exists(final_output):
            print "Skip already finished dir",entity_dir
            continue
        args_run_java[3] = java_file

        print " ".join(args_run_java)
        p = subprocess.Popen(" ".join(args_run_java), stdout=subprocess.PIPE, shell=True)
        output = p.communicate()[0]
        file_name = os.path.join(entity_dir,java_files[java_file]+"_all_entity")
        with open(file_name,'w') as f:
            f.write(output)
        args_process_result[2] = file_name
        args_process_result[3] = final_output
        subprocess.call(args_process_result)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disaster_name")
    parser.add_argument("top_dir")
    parser.add_argument("--src_dir","-s", default="/lustre/scratch/lukuang/keyphrase_extraction/src/prepare_corpus")
    parser.add_argument("--top",'-t',type=int,default=10)
    parser.add_argument("--first_only","-o",action='store_true',default=False)
    args=parser.parse_args()
    
    args.top_dir = os.path.abspath(args.top_dir)
    raw_dir = os.path.join(args.top_dir, "raw",args.disaster_name)
    instance_names = os.walk(raw_dir).next()[1]
    os.chdir(args.src_dir)
    for instance in instance_names:
        print "for %s" %instance
        source_dir = os.path.join(args.top_dir,"raw",args.disaster_name,instance)
        dest_dir = os.path.join(args.top_dir,"clean_text",args.disaster_name,instance)
        entity_dir = os.path.join(args.top_dir,"entity",args.disaster_name,instance)
        if not os.path.exists(entity_dir):
            os.mkdir(entity_dir)
        call_clean_html(source_dir, dest_dir, args.top, args.first_only)

    
        gene_entities(dest_dir,entity_dir)
    




    







if __name__=="__main__":
    main()


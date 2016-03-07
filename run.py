"""
run the whole process
"""

import os
import json
import sys
import re
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("entity_dir")
    parser.add_argument("--src_dir","-s", default="/lustre/scratch/lukuang/keyphrase_extraction/src")
    parser.add_argument("--top",'-t',type=int,default=10)
    args=parser.parse_args()
    
    args_clean_html = [
        'python',
        '/lustre/scratch/lukuang/keyphrase_extraction/src/clean_html.py',
        args.source_dir,
        args.dest_dir,
        "-t",
        str(args.top),
        '-o'
    ]

    subprocess.call(args_clean_html)


    java_files = {
        "RankEntity" : "tf",
        "RankEntityDF" : "df",
        "RankEntityDFDiscounted" : "dfd"
    }

    os.chdir(args.src_dir)

    args_run_java = [
        'java',
        '-cp',
        "'.:/home/1546/source/stanford-ner-2015-12-09/*:/home/1546/source/stanford-ner-2015-12-09/lib/*'",
        "JAVA FILE",
        args.dest_dir,
    ]

    args_process_result = [
        'python',
        '/lustre/scratch/lukuang/keyphrase_extraction/src/process_result.py',
        "JAVA OUTPUT",
        "FINAL OUTPUT",
    ]

    for java_file in java_files:
        args_run_java[3] = java_file
        print args_run_java
        p = subprocess.Popen(args_run_java, stdout=subprocess.PIPE)
        output = p.communicate()[0]
        file_name = os.path.join(args.entity_dir,java_files[java_file]+"_all_entity")
        with open(file_name,'w') as f:
            f.write(output)
        args_process_result[2] = file_name
        args_process_result[3] = os.path.join(args.entity_dir,java_files[java_file])
        subprocess.call(args_process_result)


    







if __name__=="__main__":
    main()


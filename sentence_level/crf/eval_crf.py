"""
evaluate the crf performances
"""

import os
import json
import sys
import re
import argparse
import codecs
import subprocess

JAVA_LIB_STRING = '"/home/1546/source/Stanford/stanford-ner-2015-12-09/*:/home/1546/source/Stanford/stanford-ner-2015-12-09/lib/*"'


def get_all_dir(data_dir):
    all_dir = {}
    for single_dir in os.walk(data_dir).next()[1]:
        rel_dir_path = os.path.join(data_dir,single_dir)
        all_dir[single_dir] = os.path.abspath(rel_dir_path)

    return all_dir

def eval_every_dir(all_dir):
    train_args = ["java","-cp",JAVA_LIB_STRING,"edu.stanford.nlp.ie.crf.CRFClassifier","-prop","./property"] 
    test_args = ["java","-cp",JAVA_LIB_STRING,"edu.stanford.nlp.ie.crf.CRFClassifier","-loadClassifier","train-model.ser.gz","-testFile","test.tsv"] 
    performances = []
    for single_dir in all_dir:
        # print "For dir:%s" %(single_dir)
        os.chdir(all_dir[single_dir])
        #train 
        t = subprocess.Popen(" ".join(train_args),bufsize=-1,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        t.communicate()
        #test
        test_p = subprocess.Popen(" ".join(test_args),shell=True,bufsize=-1,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        output = test_p.communicate()[1]
        print output
        for line in output.split("\n"):
            if "DAM" in line:
                # print line
                parts = line.rstrip().split()

                now_f1 = float(parts[3])
                print "For dir:%s, f1:%f" %(single_dir,now_f1)
                performances.append(now_f1)


    print "The average is %f" %(sum(performances)/(1.0*len(performances)))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir")
    args=parser.parse_args()

    all_dir = get_all_dir(args.data_dir)
    print all_dir
    eval_every_dir(all_dir)

if __name__=="__main__":
    main()


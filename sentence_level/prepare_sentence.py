"""
prepare sentences given candidates
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Document
import xlsxwriter
reload(sys)
sys.setdefaultencoding("utf-8")

def get_candidates_from_single_file(candidate_file,required_types,remove_single):
    candidates = []
    temp_mapping = {}
    with open(candidate_file) as f:
        for line in f:
            line = line.rstrip()
            m = re.search("^([A-Z]+):(.+?):(.+)$",line)
            #parts = line.split(':')
            try:
                entity_type = m.group(1)
            except Exception:
                print line
                sys.exit(-1)
            if entity_type in required_types:
                entity = m.group(2)
                sentence = m.group(3)
                if entity not in temp_mapping:
                    temp_mapping[entity] = []
                temp_mapping[entity].append(sentence)
            else:
                continue
    for entity in temp_mapping:
        temp_mapping[entity] = list(set(temp_mapping[entity]))
        if remove_single and len(temp_mapping[entity])==1:
            continue
        else:
            for sentence in temp_mapping[entity]:
                candidates.append([entity,sentence])
    return candidates


def get_candidates(candidate_dir,required_types,remove_single):
    candidates = {}
    for instance in os.walk(candidate_dir).next()[2]:
        candidate_file = os.path.join(candidate_dir,instance)
        candidates[instance] = get_candidates_from_single_file(candidate_file,required_types,remove_single)
    return candidates





def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_dir")
    parser.add_argument("sentence_output_dir")
    parser.add_argument("--required_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--remove_single","-rs",action="store_true")

    args=parser.parse_args()
    
    candidates = get_candidates(args.candidate_dir,args.required_types,args.remove_single)


    total = 0
    for instance in candidates:
        # Create a workbook and add a worksheet.
        sentence_output = os.path.join(args.sentence_output_dir,instance+".xlsx")
        workbook = xlsxwriter.Workbook(sentence_output)
        worksheet = workbook.add_worksheet()

        # with codecs.open(args.sentence_output,'w','utf-8') as f:
        row = 0
        col = 0

        for entity,sentence in candidates[instance]:
            # f.write("%s,'%s','%s'\n" %(instance,w,sentence))
            worksheet.write(row, col,     instance)
            worksheet.write(row, col + 1, entity)
            worksheet.write(row, col + 2, sentence)
            row += 1
        print "There are %d sentences in %s" %(row,instance)
        total += row
        workbook.close()

    print "There are %d in total" %(total)
                   

    # with codecs.open(args.sentence_index,'w','utf-8') as f:
    #     f.write(json.dumps(sentence_index_map))



if __name__=="__main__":
    main()


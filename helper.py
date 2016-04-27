"""
helper functions
"""

import os
import json
import sys

##count number of entities in candidate files
def count_entities(file_name,count_only=False):
    data = json.load(open(file_name) )

    if not count_only:
        c = {}
        for i in data:
            for e in data[i]:
                if e not in c:
                    c[e] = 0
                c[e] += 1
        sorted_c = sorted(c.items(),key=lambda x:x[1], reverse =True)
        print sorted_c
    else:  
        c= 0
        for i in data:
            c += len(data[i])
        print "the number is %d" %c

if __name__ = "__main__":
    if(len(sys.args)==2):
        count_entities(sys.args[1])
    elif(len(sys.args)==3):
        if sys.argv[2]=='y':
            count_entities(sys.args[1],True)
        else:
            count_entities(sys.args[1],False)
    else:
        print "Too many arguments"

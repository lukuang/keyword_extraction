"""
helper functions
"""

import os
import json
import sys


def count_entities(file_name,count_only=False):
    data = json.load(file_name)

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
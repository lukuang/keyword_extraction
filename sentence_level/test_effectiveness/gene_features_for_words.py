"""
generate features for words using original files
"""

import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Sentence, Document, Model


def get_word_features(judged_data_file):
    judged_data = json.load(open(judged_data_file))
    feature_data = []
    for single_data in judged_data:
        sentence = single_data["sentence"]
        sentence_model = Sentence(re.sub("\n"," ",sentence),remove_stopwords=False).stemmed_model
        sentence_model.to_dirichlet()

        single_data.pop("sentence",None)
        single_data["word_features"] = sentence_model.model
        feature_data.append(single_data)
    return feature_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("judged_data_file")
    parser.add_argument("feature_data_file")
    args=parser.parse_args()

    feature_data = get_word_features(args.judged_data_file)
    with open(args.feature_data_file,"w") as f:
        f.write(json.dumps(feature_data))


if __name__=="__main__":
    main()


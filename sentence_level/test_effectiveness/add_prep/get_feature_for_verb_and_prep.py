"""
generate verb/clause features
"""
import os
import json
import sys
import re
import argparse
import codecs
from myUtility.corpus import Sentence, Document, Model


def get_all_verbs(result_tuples):
    verb_model = Model(False,need_stem=False)

    for single_tuple in result_tuples:
        word = single_tuple['verb']
        # if single_tuple['verb_label'] != 'VB':
        #     word = WordNetLemmatizer().lemmatize(word,'v')
        try:
            verb_model.update(text_list=[str(word)])
        except TypeError:
            print "Wrong Word!"
            print word
            print type(word)
            print single_tuple
            sys.exit(0)
    verb_model.to_dirichlet()

    return verb_model


def get_all_preps(result_tuples):
    prep_model = Model(False,need_stem=False)

    for single_tuple in result_tuples:
        if 'prep' in single_tuple:
            word = single_tuple['prep']
            # if single_tuple['verb_label'] != 'VB':
            #     word = WordNetLemmatizer().lemmatize(word,'v')
            try:
                prep_model.update(text_list=[str(word)])
            except TypeError:
                print "Wrong Word!"
                print word
                print type(word)
                print single_tuple
                sys.exit(0)
    prep_model.to_dirichlet()

    return prep_model


def get_all_words(result_tuples):
    
    word_model = Model(False,need_stem=False)

    for single_tuple in result_tuples:
        word_model += Sentence(single_tuple['sentence'],remove_stopwords=False).raw_model

    word_model.to_dirichlet()

    return word_model


def get_features(feature_data_file):
    original_data = json.load(open(feature_data_file))
    feature_data = []
    for single_data in original_data:
        result_tuples = single_data["result_tuples"]

        if not result_tuples:
            continue

        else:
            verb_feature_model = get_all_verbs(result_tuples)
            prep_feature_model = get_all_preps(result_tuples)

            single_data.pop("sentence",None)
            single_data["word_features"] = {
                    "verb" : verb_feature_model.model,
                    "prep" : prep_feature_model.model
            }
            feature_data.append(single_data)

    return feature_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_data_file")
    parser.add_argument("dest_file")
    args=parser.parse_args()

    feature_data = get_features(args.feature_data_file)
    with open(args.dest_file,"w") as f:
        f.write(json.dumps(feature_data))


if __name__=="__main__":
    main()

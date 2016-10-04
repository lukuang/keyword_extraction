"""
use cross validation to preport results
"""

import os
import json
import sys
import re
import argparse
from sklearn import cross_validation
import sklearn.metrics
from sklearn.metrics import classification_report
from sklearn import metrics
from collections import Counter,namedtuple
import cPickle
import numpy as np

METHOD = ['linear_svc','logistic_regression',"naive_bayes"]

MaxPara = namedtuple('MaxPara', ['ws_input', 'cs_input', 'ws_real', 'cs_real', 'max_f1',"sub_predicted_y"])


def load_data_set(feature_data_dir,split_data):
    feature_data = []
    for instance in os.walk(feature_data_dir).next()[2]:
        feature_data_file = os.path.join(feature_data_dir,instance)
        instance_feature_data = load_data_set_from_single_file(feature_data_file,split_data)
        feature_data += instance_feature_data

    return feature_data

def load_data_set_from_single_file(feature_data_file,split_data):
    feature_data = json.load(open(feature_data_file))
    if split_data == 0:
        return feature_data
    elif split_data == 1:
        location_only = []
        for single_data in feature_data:
            if "LOCATION" in single_data["type"]:
                location_only.append(single_data)
        return location_only
    elif split_data == 2:
        organization_only = []
        for single_data in feature_data:
            if "ORGANIZATION" in single_data["type"]:
                organization_only.append(single_data)
        return organization_only

    else:
        raise NotImplementedError("no split method %d is implemented" %(split_data))




def get_classifier(method):
    if method == 0:
        from sklearn.svm import SVC
        classifier = SVC(kernel="rbf",C=1)
    elif method == 1:
        from sklearn import linear_model
        classifier = linear_model.LogisticRegression(C=1e5)
    elif method == 2:
        from sklearn.naive_bayes import GaussianNB
        classifier = GaussianNB()
    else: 
        from sklearn import tree
        classifier = tree.DecisionTreeClassifier()

    return classifier





def show_performance_on_entity_types(y,predicted,entity_info):
    Size = namedtuple('Size', ['pos', 'neg'])
    type_size = Size(pos=Counter(),neg=Counter())
    correct_predicted = Size(pos=Counter(),neg=Counter())
    for i in range(len(entity_info)):
        entity_type_list = entity_info[i]["type"]
        if y[i] == 1:
            type_size.pos.update(entity_type_list)
            if predicted[i] == 1:
                correct_predicted.pos.update(entity_type_list)

        else:
            type_size.neg.update(entity_type_list)
            if predicted[i] == 0:
                correct_predicted.neg.update(entity_type_list)

    print "show performance in terms of entity types:"
    print "There are %d entities" %(len(y))
    print "In positive example:"
    for k in type_size.pos.keys():
        print "\tThere are %d %s entities, %d are predicted correctly"\
             %(type_size.pos[k],k,correct_predicted.pos[k])
    print "In negative example:"
    for k in type_size.neg.keys():
        print "\tThere are %d %s entities, %d are predicted correctly"\
             %(type_size.neg[k],k,correct_predicted.neg[k])

def get_limit(features):
    max_size = len(features)
    
    mode = max_size//10
    limit = mode*10
    if limit - max_size < 0:
        limit +=  10
    
    return limit

def prepare_date(feature_data,what_to_tune,size_hard_limit):
    label = []
    words = set()
    categories = set()
    for single_data in feature_data:
        label.append(single_data["judgement"])
        for w in single_data["word_features"]:
            words.add(w)
        if single_data["category"]:
            for c in single_data["category"]:
                categories.add(c)

    ws_limit = min(get_limit(words),size_hard_limit)
    cs_limit = min(get_limit(categories),size_hard_limit)

    print len(words), len(categories)

    para_set = []
    if what_to_tune == 0:
        for ws_input in range(10,ws_limit+10,10):
            para_set.append([ws_input,0])
    elif what_to_tune == 1:
        for cs_input in range(10,cs_limit+10,10):
            para_set.append([0,cs_input])

    elif what_to_tune == 2:
        for ws_input in range(10,ws_limit+10,10):
            for cs_input in range(10,cs_limit+10,10):
                para_set.append([ws_input,cs_input])
    else:
        para_set = [[0,0]]

    return label,para_set,len(words), len(categories)



def get_training_data(train_data):
    negative_feature_frequency = {}
    positive_feature_frequency = {}
    negative_category_frequency = {}
    positive_category_frequency = {}
    train_judgement_vector = []



    for single_data in train_data:
        if single_data["judgement"] == 0:
            train_judgement_vector.append(0)
            for w in single_data["word_features"]: 
                if w not in negative_feature_frequency:
                    negative_feature_frequency[w] = 0
                negative_feature_frequency[w] += 1

            if not single_data["category"]:
                continue

            for c in single_data["category"]:
                if c not in negative_category_frequency:
                    negative_category_frequency[c] = 0
                negative_category_frequency[c] += 1


        else:
            train_judgement_vector.append(1)
            for w in single_data["word_features"]: 
                if w not in positive_feature_frequency:
                    positive_feature_frequency[w] = 0
                positive_feature_frequency[w] += 1

            if not single_data["category"]:
                continue

            for c in single_data["category"]:
                if c not in positive_category_frequency:
                    positive_category_frequency[c] = 0
                positive_category_frequency[c] += 1

    sorted_negative_feature_frequency = sorted(negative_feature_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_positive_feature_frequency = sorted(positive_feature_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_negative_category_frequency = sorted(negative_category_frequency.items(),key = lambda x:x[1],reverse=True)
    sorted_positive_category_frequency = sorted(positive_category_frequency.items(),key = lambda x:x[1],reverse=True)

    return train_judgement_vector,\
           sorted_negative_feature_frequency,\
           sorted_positive_feature_frequency,\
           sorted_negative_category_frequency,\
           sorted_positive_category_frequency


def get_test_judgement(test_data):
    test_judgement_vector = []

    for single_data in test_data:
        if single_data["judgement"] == 0:
            test_judgement_vector.append(0)
        else:
            test_judgement_vector.append(1)


    return test_judgement_vector


def prepare_sub_data(train_data,test_data):



    train_judgement_vector,\
    sorted_negative_feature_frequency,sorted_positive_feature_frequency,\
    sorted_negative_category_frequency,sorted_positive_category_frequency\
        = get_training_data(train_data)

    test_judgement_vector = get_test_judgement(test_data)



    return train_judgement_vector,test_judgement_vector,\
           sorted_negative_feature_frequency,sorted_positive_feature_frequency,\
           sorted_negative_category_frequency,sorted_positive_category_frequency




def get_top_features(sorted_features,feature_size):
    top_features = []
    i = 0
    for (feature,v) in sorted_features:
        if i==feature_size:
            break
        i += 1
        top_features.append(feature)
        
    return top_features


def get_top_common_feature(sorted_positive_feature, sorted_negative_feature,feature_size):
    top_features = get_top_features(sorted_positive_feature,feature_size)
    top_features += get_top_features(sorted_negative_feature,feature_size)

    return list(set(top_features))

def get_sub_feature_vector(sub_feature_date,top_context_feature,
                           top_category_feature,use_stanford_type):
    sub_feature_vector = []
    for single_data in sub_feature_date:
        single_feature_vector = []

        # add context features
        for w in top_context_feature:
            if w in single_data["word_features"]:
                single_feature_vector.append(single_data["word_features"][w])
            else:
                single_feature_vector.append(0)

        # add category features
        if not single_data["category"]:
                single_feature_vector += [0]*len(top_category_feature)
        else:
            for c in top_category_feature:
                if c in single_data["category"]:
                    single_feature_vector.append(1)
                else:
                    single_feature_vector.append(0)
        
        # add Stanford type features if specified

        if use_stanford_type:
            if "ORGANIZATION" in single_data["type"]:
                single_feature_vector.append(1)
            else:
                single_feature_vector.append(0)
            if "LOCATION" in single_data["type"]:
                single_feature_vector.append(1)
            else:
                single_feature_vector.append(0)


        # if len(single_feature_vector)==1:
        #     print single_data
        #     print single_feature_vector

        sub_feature_vector.append(single_feature_vector)

    return sub_feature_vector



def get_feature_vector(train_data,test_data,
                       top_context_feature,top_category_feature,
                       use_stanford_type):
    train_feature_vector =\
        get_sub_feature_vector(train_data,top_context_feature,top_category_feature,
                               use_stanford_type)
    
    test_feature_vector =\
        get_sub_feature_vector(test_data,top_context_feature,top_category_feature,
                               use_stanford_type)
    
    return train_feature_vector, test_feature_vector


def tune(train_data,test_data,clf,ws_input,cs_input,use_stanford_type):
    train_judgement_vector,test_judgement_vector,\
    sorted_negative_feature_frequency,sorted_positive_feature_frequency,\
    sorted_negative_category_frequency,sorted_positive_category_frequency\
        = prepare_sub_data(train_data,test_data)

    top_context_feature = get_top_common_feature(sorted_negative_feature_frequency,sorted_positive_feature_frequency,ws_input)
    top_category_feature = get_top_common_feature(sorted_negative_category_frequency,sorted_positive_category_frequency,cs_input)
    #print top_context_feature
    #print top_category_feature
    ws_real = len(top_context_feature)
    cs_real = len(top_category_feature)

    train_feature_vector, test_feature_vector =\
        get_feature_vector(train_data,test_data,
                           top_context_feature,top_category_feature,use_stanford_type)


    clf.fit(np.array(train_feature_vector), np.array(train_judgement_vector)) 
    temp_predicted_y = clf.predict(test_feature_vector)

    new_f1 = sklearn.metrics.f1_score(test_judgement_vector,temp_predicted_y,average='binary')
    #print "f1 now %f" %new_f1
    max_para = MaxPara._make([ws_input,cs_input,ws_real,cs_real,new_f1,temp_predicted_y])


    return max_para

        
def check_stop(ws_real,cs_real,w_count,c_count,what_to_tune):
    if what_to_tune == 0:
        if ws_real == w_count:
            return True
    elif what_to_tune == 1:
        if cs_real == c_count:
            return True

    elif what_to_tune == 2:
        if ws_real == w_count and  cs_real == c_count:
            return True
    else:
        return False
    return False

def compute_f1(y,predicted):
    true_positive = 0
    false_positive = 0
    false_negative = 0
    for i in range(len(y)):
        if y[i] == 1:
            if predicted[i] == 1:
                true_positive += 1
            else:
                false_negative += 1
        else:
            if predicted[i] == 1:
                false_positive += 1
    try:
        precision = true_positive*1.0/(false_positive+true_positive)
    except ZeroDivisionError:
        precision = 0.0
    try:
        recall = true_positive*1.0/(true_positive+false_negative)
    except ZeroDivisionError:
        recall = 0.0
    if recall == 0 or precision == 0:
        return 0
    else:
        return 2/(1.0/precision + 1.0/recall)



def output_tuning_result(performance_records,max_para,feature_data,\
                         use_stanford_type,clf,dest_dir):
    best = [max_para.ws_input,max_para.cs_input,max_para.sub_predicted_y,max_para.max_f1]

    all_records = {
        "performance_records": performance_records,
        "best": best
    }

    train_judgement_vector,test_judgement_vector,\
    sorted_negative_feature_frequency,sorted_positive_feature_frequency,\
    sorted_negative_category_frequency,sorted_positive_category_frequency\
        = prepare_sub_data(feature_data,[])

    ws_input = max_para.ws_input
    cs_input = max_para.cs_input

    top_context_feature = get_top_common_feature(sorted_negative_feature_frequency,sorted_positive_feature_frequency,ws_input)
    top_category_feature = get_top_common_feature(sorted_negative_category_frequency,sorted_positive_category_frequency,cs_input)
    #print top_context_feature
    #print top_category_feature
    ws_real = len(top_context_feature)
    cs_real = len(top_category_feature)

    train_feature_vector, test_feature_vector =\
        get_feature_vector(feature_data,[],
                           top_context_feature,top_category_feature,use_stanford_type)


    clf.fit(np.array(train_feature_vector), np.array(train_judgement_vector)) 



    record_file = os.path.join(dest_dir,"record")  
    with open(record_file,"w") as f:
        f.write(json.dumps(all_records,indent=2))

    clf_file = os.path.join(dest_dir,"clf")  
    with open(clf_file,"wb") as f:
        cPickle.dump(clf, f)

    word_feature_file = os.path.join(dest_dir,"word_feature")  
    with open(word_feature_file,"w") as f:
        f.write(json.dumps(top_context_feature))

    if use_stanford_type:
        top_category_feature.append("USE_STANFORD_TYPE")

    word_feature_file = os.path.join(dest_dir,"word_feature")  
    with open(word_feature_file,"w") as f:
        f.write(json.dumps(top_context_feature))

    cat_feature_file = os.path.join(dest_dir,"cat_feature")  
    with open(cat_feature_file,"w") as f:
        f.write(json.dumps(top_category_feature))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_data_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("--size_hard_limit","-sl",type=int,default=1000)
    parser.add_argument('--method','-m',type=int,default=1,choices=range(4),
        help=
        """choose methods from:
                0:linear_svc
                1:logistic regression
                2:naive bayes
                3:decision  tree
        """)
    parser.add_argument("--what_to_tune","-w",type=int,default=0,choices=range(4),
        help=
        """choose what to tune:
                0: context only 
                1: category only
                2: both
                3: none
        """)
    parser.add_argument("--use_stanford_type","-us",action='store_true',
        help = 
        """When specified, the type information of Stanford NER
        is used as features
        """
        )
    parser.add_argument("--split_data","-sd",type=int,default=0,choices=range(3),
        help=
        """choose to split data on stanford types or not:
                0: no split 
                1: LOCATION only
                2: ORGANIZATION only
        """)
    args=parser.parse_args()

    feature_data = load_data_set(args.feature_data_dir,args.split_data)
    label,para_set,w_count,c_count = prepare_date(feature_data,args.what_to_tune,args.size_hard_limit)

    clf = get_classifier(args.method)
    

    skf = cross_validation.StratifiedKFold(label,5)

    predicted = [0]*len(label)


    splited_data = []

    for train_index, test_index in skf:
        train_index = train_index.tolist()
        test_index = test_index.tolist()
        splited_data.append((train_index,test_index))


    max_para = MaxPara._make([0,0,0,0,0,[]])


    performance_records = []
    for ws_input,cs_input in para_set:
        predicted = [0]*len(label)
        run_index = 0
        ws_real = 0
        cs_real = 0
        for train_index, test_index in splited_data:
            run_index += 1
            #print "Start run %d" % run_index
            #print "%d training data and %d test data" %(len(train_index),len(test_index))
            train_data = []
            test_data = []

            for i in train_index:
                train_data.append(feature_data[ i ])

            for i in test_index:
                test_data.append(feature_data[ i ])

            sub_max_para = tune(train_data,test_data,clf,ws_input,cs_input,args.use_stanford_type)

            

            ws_real = sub_max_para.ws_real
            cs_real = sub_max_para.cs_real

            for i in range(len(test_index)):
                predicted[ test_index[i] ] = sub_max_para.sub_predicted_y[i]
        #temp = list(predicted)
        new_f1 = sklearn.metrics.f1_score(label,predicted)
        #print compute_f1(label,predicted)
        print "ws_input:%d, cs_input:%d, ws_real:%d, cs_real:%d, f1:%f"\
                %(ws_input, cs_input, 
                  ws_real, cs_real,new_f1)

        performance_records.append([ws_input,cs_input,new_f1])
        if new_f1 > max_para.max_f1:
            print "CHANGE"
            max_para = MaxPara._make([ws_input,cs_input,ws_real,cs_real,new_f1,list(predicted)])

        # if check_stop(ws_real,cs_real,w_count,c_count,args.what_to_tune):
        #     break



    output_tuning_result(performance_records,max_para,
                         feature_data,args.use_stanford_type,clf,args.dest_dir)
    



    y = label

    show_performance_on_entity_types(y,max_para.sub_predicted_y,feature_data)
    print max_para
    #print compute_f1(y,max_para.sub_predicted_y)
    print classification_report(y, max_para.sub_predicted_y)
    #get_top_entities(all_entities,predicted,args.top_size,args.need_positive)

if __name__=="__main__":
    main()


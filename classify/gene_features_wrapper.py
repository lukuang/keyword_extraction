"""
a wapper of generating features for noaa data
"""

import os
import json
import sys
import re
import argparse
import codecs
import subprocess
METHOD = ['words','clasue_words',"verbs","frames"]



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no_organization","-no",action="store_true")
    parser.add_argument('--method','-m',type=int,default=0,choices=range(4),
        help=
        """chose mthods from:
                0:words
                1:clasue words
                2:verbs
                3:frames
        """)
    parser.add_argument("--new_tornado","-new",action='store_true')
    parser.add_argument("--candidate_dir","-cd",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/candidates/all_year/new/no_single")
    parser.add_argument("--text_dir",'-tp',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/clean_text/noaa')
    parser.add_argument("--input_dir","-ind",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/src/stanford_parser/data/noaa/all_year")
    parser.add_argument("--feature_dir","-fd",default="/home/1546/code/keyword_extraction/stanford_parser/data/noaa/all_year/classify")

    parser.add_argument("--word_feature_size","-wz",type=int,default=50)
    parser.add_argument("--cate_feature_size","-cz",type=int,default=30)
    parser.add_argument("--news_entity_dir",'-nd',default='/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/entity/noaa')
    parser.add_argument("--query_file","-qf",default="/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/noaa/noaa.json")
    parser.add_argument("--required_entity_types", "-rt",nargs='+',default=["ORGANIZATION","LOCATION"])
    parser.add_argument("--required_file_name",'-rn',default='df_all_entity')


    args=parser.parse_args()

    #configure base parameters
    base_para = []
    if args.new_tornado:
        base_para.append("-new")
        args.candidate_dir = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/candidiates/new_tornado/"
        args.input_dir = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/stanford_parser/data/new_tornado"
        args.feature_dir = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/src/stanford_parser/data/new_tornado/classify"
        args.news_entity_dir = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/entity/new_tornado/"
        args.text_dir = "/lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/clean_text/new_tornado"
        args.query_file = "no need query file!!"

    base_para += [
        "-wz", str(args.word_feature_size),
        "-cz", str(args.cate_feature_size),
        "-nd", args.news_entity_dir,
        "-qf", args.query_file,
        "-rn", args.required_file_name,
        "-rt"
    ]
    for tag in args.required_entity_types:
        base_para.append(tag)


    #choose feature dir
    if args.no_organization:
        feature_dir = os.path.join(args.feature_dir,"no_location_features")

    else:
        feature_dir = os.path.join(args.feature_dir,"features")
        

    cate_file = os.path.join(feature_dir,"cate_info.json")
    dest_dir = os.path.join(feature_dir,METHOD[args.method])

    #build running command depending on the method used
    if args.method == 0:
        #use words as features
        positive_file = os.path.join(args.candidate_dir,"positive")
        if args.no_organization:
            negative_file = os.path.join(args.candidate_dir,"negative_no_location")
        else:
            negative_file = os.path.join(args.candidate_dir,"negative")
        run_args = [
            "python",
            "/home/1546/code/keyword_extraction/classify/gene_features_for_words.py",
            positive_file,
            negative_file,
            cate_file,
            dest_dir,
            "-tp", args.text_dir
        ]
        run_args += base_para


    elif args.method == 1 or args.method == 2:
        #use clause words/verbs as features
        positive_file = os.path.join(args.input_dir,"positive_result_tuples")
        if args.no_organization:
            negative_file = os.path.join(args.input_dir,"negative_no_location_result_tuples")
        else:
            negative_file = os.path.join(args.input_dir,"negative_result_tuples")

        run_args = [
            "python",
            "/home/1546/code/keyword_extraction/classify/gene_features_for_verbs.py",
            cate_file,
            dest_dir,
            "-pf", positive_file,
            "-nf", negative_file,
        ]

        if args.method == 1:
            run_args.append("-uc")

        run_args += base_para

        
    else:
        #use verb frames as features
        positive_file = os.path.join(args.input_dir,"positive_verb_frames")
        if args.no_organization:
            negative_file = os.path.join(args.input_dir,"negative_no_location_verb_frames")
        else:
            negative_file = os.path.join(args.input_dir,"negative_verb_frames")

        run_args = [
            "python",
            "/home/1546/code/keyword_extraction/classify/gene_features_for_verb_frames.py",
            cate_file,
            dest_dir,
            "-pf", positive_file,
            "-nf", negative_file
        ]

        run_args += base_para

    #run command
    print run_args
    subprocess.call(run_args)
    



if __name__=="__main__":
    main()


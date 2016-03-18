
#!/bin/sh
# Tell the SGE that this is an array job, with "tasks" to be numbered 1 to 10000
#$ -l standby=1
#$ -l m_mem_free=1G
#$ -t 1-7
vpkg_require python
source /home/1546/myEV/bin/activate
# When a single command in the array job is sent to a compute node,
# its task number is stored in the variable SGE_TASK_ID,
# so we can use the value of that variable to get the results we want:
echo python get_language_model_for_entities.py new_tornado  /lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data /lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/models/per_instance  $SGE_TASK_ID
python get_language_model_for_entities.py new_tornado  /lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data  /lustre/scratch/lukuang/Temporal_Summerization/TS-2013/data/disaster_profile/data/models/per_instance  $SGE_TASK_ID

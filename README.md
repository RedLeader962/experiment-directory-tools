# Experiment Directory Tools
Tools to managed an experimentation run folder and create run directory based on creation date

by Luc Coupal


**create_run_directory(** experiments_root_dir, run_name="", UUID=None **)**: A utility function to create a run directory based on creation date.

**clean_result_directory(** experiments_root_dir, keep=5, protected_file_type=('.py', '.cpp', '.hpp') **)**: A utility function to clean a experimentation run folder based on creation date.

    ex:
        /experiment_root_dir
            /current_run
                /Run--myExperiment-112250425472---20180725223506
                    /myExperiment_0_Gradient_clipping_threshold=0.87493
                    /myExperiment_1_Gradient_clipping_threshold=0.97914
                    ...
            /past_run
                /Run--myExperiment-222260435473---20180725223507
                /Run--myExperiment-232222435474---20180725223508
                ...

Usage note: use the 'clean_result_directory' function before 'create_run_directory' otherwise all the newly
created experiments run are going to be move to '/past_run'
    
    
   
#####Note:
- If '/current_run' contain more experiment than 'keep', they are all kept in '/past_run' until the next cleaning
- Deletion from the '/past_run' is aborted if a 'protected_file_type' is detected in a subdirectory
- Be advise that deleted file are erase in place, they are not sent to the trash
- Tested on python 3 and osX

#####Todo:
- Add a user defined flag to prevent the deletion of a flagged important experiment
- Add a parameter & utility fct to move a specific experiment to a 'important_run' folder once flagged
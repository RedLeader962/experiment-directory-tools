import os
import shutil
from datetime import datetime
from collections import namedtuple


CURRENT_RUN_DIR = "/current_run"
PAST_RUN_DIR = "/past_run"


"""
Tools to managed an experimentation run folder and create run directory based on creation date

by Luc Coupal

Note: Tested on python 3 and osX
"""

def create_run_directory(experiments_root_dir, run_name="", UUID=None):
    """
    Utility function to create a run directory based on creation date.

    A run directory can contain multiple experimentation

    'experiment_root_dir' will be organize with a '/current_run' and '/past_run' subdirectory if not already done.

    The naming convention is later use by the 'clean_result_directory' function to manage the 'experiment_root_dir'
    by creation date:

        Run--{run_name}-{UID}-{Timestamp}

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

    :param experiments_root_dir:
    :param run_name: (optional) The name of the run.
    :param UUID: (optional) A universal unique identifier or a any unique id
    :return: The experimentation run directory name
    """

    # --- setup the root directory if necessary ------------------------------------------------------------------------
    _create_required_subdirectory(experiments_root_dir)

    # --- create a new run directory -----------------------------------------------------------------------------------
    utc_now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    run_name = run_name.replace(" ", "_")
    experiment_run_directory = "/Run--{}-{}{}-{}".format(run_name,
                                                         "-" * (30 - len(run_name) - len(str(UUID))),
                                                         UUID,
                                                         utc_now)

    os.mkdir("{}{}".format(experiments_root_dir + CURRENT_RUN_DIR, experiment_run_directory))

    return experiment_run_directory


def clean_result_directory(experiments_root_dir, keep=5, protected_file_type=('.py', '.cpp', '.hpp')):
    """
    Utility function to clean a experimentation run folder based on creation date.
    A run folder can contain multiple experiment run simultaneously with numerous file format.

    Clean two subdirectory:
        - /current_run: transfer the contained experience to /past_run
        - /past_run: keep the 'keep' number most recent experiment and delete the others

    Note:
        - If '/current_run' contain more experiment than 'keep', they are all kept in '/past_run' until the next cleaning
        - Deletion from the '/past_run' is aborted if a 'protected_file_type' is detected in a subdirectory
        - Be advise that deleted file are erase in place, they are not sent to the trash
        - Tested on python 3 and osX

    Todo:
        - Add a user defined flag to prevent the deletion of a flagged important experiment
        - Add a parameter & utility fct to move a specific experiment to a 'important_run' folder once flagged

    :param protected_file_type:
    :param experiments_root_dir: the directory containing the '/current_run' and '/past_run' folder
    :param keep: the minimum number of past experiment to keep in '/past_run'
    :return: None
    """

    current_run_dir = experiments_root_dir + CURRENT_RUN_DIR
    past_run_dir = experiments_root_dir + PAST_RUN_DIR

    # --- setup the root directory if necessary ------------------------------------------------------------------------
    _create_required_subdirectory(experiments_root_dir)

    # --- clean '/past_run' directory ----------------------------------------------------------------------------------
    _clean_past_run_dir(current_run_dir, past_run_dir, keep, protected_file_type)

    # --- clean '/current_run' directory -------------------------------------------------------------------------------
    current_list = os.listdir(current_run_dir)

    if '.DS_Store' in current_list:
        current_list.remove('.DS_Store')

    for each in current_list:
        shutil.move(current_run_dir + "/" + each, past_run_dir)

    return None


def _create_required_subdirectory(experiments_root_dir):
    if not os.path.isdir(experiments_root_dir):
        os.makedirs(experiments_root_dir)

    current_run_dir = experiments_root_dir + CURRENT_RUN_DIR
    past_run_dir = experiments_root_dir + PAST_RUN_DIR

    dir_to_create = [current_run_dir, past_run_dir]

    for each in dir_to_create:
        try:
            os.mkdir(each)
        except FileExistsError:
            pass

    assert os.path.isdir(current_run_dir), "Missing directory '{}{}'".format(experiments_root_dir, CURRENT_RUN_DIR)
    assert os.path.isdir(past_run_dir), "Missing directory '{}{}'".format(experiments_root_dir, PAST_RUN_DIR)


def _clean_past_run_dir(current_run_dir, past_run_dir, keept_nb, protected_file_type):

    assert keept_nb >= 1

    current_run = os.listdir(current_run_dir)

    if '.DS_Store' in current_run:
        current_run.remove('.DS_Store')

    if current_run:
        Experiment_dir_name = namedtuple('Experiment_dir_name', ['prefix', 'timestamp'])

        keepers = list()
        to_be_deleted = list()

        for each in current_run:
            prefix, current_experiment_UTC = convert_log_dir_name_to_datetime_obj(each)
            keepers.append(Experiment_dir_name(prefix=prefix, timestamp=current_experiment_UTC))

        now = datetime.now()
        past_runs = os.listdir(past_run_dir)
        if '.DS_Store' in past_runs:
            past_runs.remove('.DS_Store')

        # --- keep the most recent 'keept_nb' number of past experience ------------------------------------------------
        for each in past_runs:
            prefix, past_exp_UTC = convert_log_dir_name_to_datetime_obj(each)
            a_past_experiment_dir = Experiment_dir_name(prefix=prefix, timestamp=past_exp_UTC)

            # feed keepers with remaining newest past experiment
            if len(keepers) < keept_nb:
                keepers.append(a_past_experiment_dir)
            else:

                for a_keeper in keepers:
                    if now - a_keeper.timestamp > now - a_past_experiment_dir.timestamp:
                        keepers.remove(a_keeper)
                        to_be_deleted.append(a_keeper)
                        keepers.append(a_past_experiment_dir)

                        assert len(keepers) <= keept_nb
                        """
                        break out of loop without executing else clause since all the remainder are suppose to be younger
                        """
                        break
                else:
                    to_be_deleted.append(a_past_experiment_dir)

        # --- test for .py file before deleting ------------------------------------------------------------------------
        for dirpath, dirs_in_dirpath, files_in_dirpath in os.walk(past_run_dir):
            for filename in files_in_dirpath:
                for file_type in protected_file_type:
                    assert not filename.endswith(file_type), \
                        " --> Abort directory cleaning. " \
                        "There is a {} file present in the directory: {}".format(file_type, dirpath)

        # --- delete the oldest experience -----------------------------------------------------------------------------
        for each in to_be_deleted:
            exp_to_delete = each.prefix + each.timestamp.strftime("%Y%m%d%H%M%S")

            shutil.rmtree(past_run_dir + "/" + exp_to_delete)

        return None


def parse_time_stamp(dir_name_with_timestamp):
    _str = dir_name_with_timestamp

    # --- parse time stamp ---------------------------------------------------------------------------------------------
    prefix, year, month, day = _str[:-14], _str[-14:-10], _str[-10:-8], _str[-8:-6]
    hour, minute, second = _str[-6:-4], _str[-4:-2], _str[-2:]

    repr_str = "prefix: \n" + prefix, "year: \n" + year, "month:\n" + month, "day: \n" + day, \
               "hour: \n" + hour, "minute: \n" + minute, "second: \n" + second

    return prefix, year, month, day, hour, minute, second


def convert_log_dir_name_to_datetime_obj(dir_name_with_timestamp):
    prefix, year, month, day, hour, minute, second = parse_time_stamp(dir_name_with_timestamp)
    datetime_obj = datetime(int(year),
                            int(month),
                            int(day),
                            int(hour),
                            int(minute),
                            int(second))
    return prefix, datetime_obj

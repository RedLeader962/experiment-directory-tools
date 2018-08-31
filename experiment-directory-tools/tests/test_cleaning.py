#!/usr/bin/env python
import os
import shutil

import pytest
from datetime import datetime

import experiment_directory_tools

MOCK_DIR = "./mock_up_directory"
CLEANING_DIR = "/clean_result_directory_test_mock"
CLEANING_TEST_DIR = MOCK_DIR + CLEANING_DIR
RELATIVE_FROM_TESTS_CLEANING_DIR = "./tests_utility"

CURRENT = "/current_run"
PAST = "/past_run"

INITIAL_WORKING_DIRECTORY = os.getcwd()


def set_up_cwd():
    print(">>> set_up_cwd, Initial was: ", INITIAL_WORKING_DIRECTORY)
    print(">>> os.path.basename: ", os.path.basename(INITIAL_WORKING_DIRECTORY))

    # if os.path.basename(INITIAL_WORKING_DIRECTORY) == "tests":
    #     os.chdir(RELATIVE_FROM_TESTS_CLEANING_DIR)
    #     print(">>> change cwd to: ", os.getcwd())
    return None


def return_to_initial_working_directory():
    print(">>> return_to_initial_working_directory: {}\n{}".format(INITIAL_WORKING_DIRECTORY, "-"*20))
    if os.path.basename(INITIAL_WORKING_DIRECTORY) == "tests":
        os.chdir(INITIAL_WORKING_DIRECTORY)
    return None


def tearDown():
    """Delete graph directory created for all unit tests"""
    shutil.rmtree(CLEANING_TEST_DIR + CURRENT)
    shutil.rmtree(CLEANING_TEST_DIR + PAST)
    return_to_initial_working_directory()
    return None


@pytest.fixture(scope="function")
def set_up_current_1():
    set_up_cwd()

    starting_number_of_subfolder = 10
    current_subdirectory_size = 1
    kept_nb = 5

    _make_directory(current_subdirectory_size, starting_number_of_subfolder)

    yield starting_number_of_subfolder, current_subdirectory_size, kept_nb

    tearDown()


@pytest.fixture(scope="function")
def set_up_current_2():
    set_up_cwd()

    starting_number_of_subfolder = 10
    current_subdirectory_size = 2
    kept_nb = 5

    _make_directory(current_subdirectory_size, starting_number_of_subfolder)

    yield starting_number_of_subfolder, current_subdirectory_size, kept_nb

    tearDown()


def _make_directory(current_subdirectory_size, starting_number_of_subfolder):
    dir_to_create = [CLEANING_TEST_DIR + CURRENT,
                     CLEANING_TEST_DIR + PAST]

    for each in dir_to_create:
        try:
            os.mkdir(each)
        except FileExistsError:
            pass

    # print(">>> after", os.getcwd())

    subdirectory_to_create = list()
    for idx in range(current_subdirectory_size):
        subdirectory_to_create.append(_create_a_dir(CLEANING_TEST_DIR + CURRENT, "test-no{}-".format(idx)))

    for idx in range(current_subdirectory_size, starting_number_of_subfolder):
        subdirectory_to_create.append(_create_a_dir(CLEANING_TEST_DIR + PAST, "test-no{}-".format(idx)))

    for each in subdirectory_to_create:
        try:
            os.mkdir(each)
        except FileExistsError:
            pass


def _create_a_dir(root, message):
    _UTC_now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    run_directory = "{}/Run-{}-{}".format(root, message, _UTC_now)
    return run_directory


# --- unit test --------------------------------------------------------------------------------------------

def test_clean_directory_1_in_current(set_up_current_1):
    starting_number_of_subfolder, current_size, kept_nb = set_up_current_1

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)

    assert 0 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))


def test_clean_directory_2_in_current(set_up_current_2):
    starting_number_of_subfolder, current_size, kept_nb = set_up_current_2

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)

    assert 0 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))


def test_clean_directory_NO_py_file(set_up_current_2):
    starting_number_of_subfolder, current_size, _ = set_up_current_2

    kept_nb = 1

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))

    past_dir = os.listdir(CLEANING_TEST_DIR + PAST)
    exp_dir = past_dir.pop()

    print("\nthe directory where is the python file: ", exp_dir)
    the_test_file = CLEANING_TEST_DIR + PAST + "/" + exp_dir + "/python_file_dont_delete_test.py"

    with open(the_test_file, 'w+') as f:
        pass

    assert os.path.isfile(the_test_file)

    with pytest.raises(AssertionError) as excinfo:
        experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)
        raise " --> Abort directory cleaning. There is a python file present in the directory" in str(excinfo.value)

    assert os.path.isfile(the_test_file), "FAIL --> the python file was deleted!!!"

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))


def test_create_and_clean_directory_2_in_current(set_up_current_2):
    starting_number_of_subfolder, current_size, kept_nb = set_up_current_2

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 1)

    assert 1 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)

    assert 0 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))


def test_create_5_and_clean_directory_2_in_current(set_up_current_2):
    starting_number_of_subfolder, current_size, kept_nb = set_up_current_2

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 111)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 222)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 333)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 444)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 555)

    assert 5 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)

    assert 0 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))

    list_dir_substring = []
    for dir_str in os.listdir(CLEANING_TEST_DIR + PAST):
        list_dir_substring.extend(dir_str.split('-'))

    assert '111' in list_dir_substring
    assert '222' in list_dir_substring
    assert '333' in list_dir_substring
    assert '444' in list_dir_substring
    assert '555' in list_dir_substring


def test_create_more_than_kept_number(set_up_current_2):
    starting_number_of_subfolder, current_size, kept_nb = set_up_current_2

    assert current_size == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert starting_number_of_subfolder - current_size == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 111)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 222)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 333)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 444)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 555)
    experiment_directory_tools.create_run_directory(CLEANING_TEST_DIR, "new run", 666)

    assert 6 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb == len(os.listdir(CLEANING_TEST_DIR + PAST))

    experiment_directory_tools.clean_result_directory(CLEANING_TEST_DIR, keep=kept_nb)

    assert 0 == len(os.listdir(CLEANING_TEST_DIR + CURRENT))
    assert kept_nb + 1 == len(os.listdir(CLEANING_TEST_DIR + PAST))

    list_dir_substring = []
    for dir_str in os.listdir(CLEANING_TEST_DIR + PAST):
        list_dir_substring.extend(dir_str.split('-'))

    assert '111' in list_dir_substring
    assert '222' in list_dir_substring
    assert '333' in list_dir_substring
    assert '444' in list_dir_substring
    assert '555' in list_dir_substring
    assert '666' in list_dir_substring





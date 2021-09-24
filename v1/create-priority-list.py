#!/usr/bin/env python

"""Create Files Priority List

Create list of files prioritized by changes frequency.
Calculated using commits history.
Files are counted only once for multiple changes in single day.
"""

import subprocess
import os
import argparse

from datetime import datetime, timedelta
from collections import defaultdict
from operator import itemgetter


def getCommitsData():
    year_start = (datetime.today() - timedelta(days=365)).date()
    command = "git --no-pager log --after='" + str(year_start) + "' --name-only --pretty='tformat:|^|%ad|#|' --date=short"
    commits_data = subprocess.run(command, stdout=subprocess.PIPE, encoding='utf-8', shell=True).stdout

    return commits_data


def parseCommitsData(commits_data, files_mask):
    commits = commits_data.split("|^|")

    currently_processed_day = ""
    counted_file_names = set()
    files_counter = defaultdict(int)
    for commit in commits:
        commit_date_files = commit.split("|#|")
        if len(commit_date_files) == 2:
            commit_date = commit_date_files[0]
            if currently_processed_day != commit_date:
                currently_processed_day = commit_date
                counted_file_names.clear()

            commit_file_names = commit_date_files[1].split()
            for file_name in commit_file_names:
                if any(file_name.endswith(file_extension) for file_extension in files_mask):
                    if file_name not in counted_file_names:
                        files_counter[file_name] += 1
                        counted_file_names.add(file_name)

    return files_counter


def printFilesPriorityList(files_counter):
    sorted_files_counter = sorted(files_counter.items(),  key=itemgetter(1), reverse=True)

    priority_list = open("priority_list.csv", "w")
    priority_list.write("FileName,FrequencyOfChanges\n")
    for file_counter in sorted_files_counter:
        priority_list.write(file_counter[0] + "," + str(file_counter[1]) + "\n")
    priority_list.close()


print("Starting to generate files priority list..")

arguments_parser = argparse.ArgumentParser(description='Arguments:')
arguments_parser.add_argument('--files-mask', nargs='*', type=str, default=[".h", ".cc", ".cpp", ".hpp"], help='Optional. Commas separated, files extensions that will be present in resulting files list.')

printFilesPriorityList(parseCommitsData(getCommitsData(), arguments_parser.parse_args().files_mask))

print("Files priority list generation finished..")

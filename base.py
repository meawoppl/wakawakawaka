#!/usr/bin/env python
import argparse
import datetime
import itertools
import os
import subprocess
import uuid


sequence = itertools.count()


def do_commit_on_datetime(datetyme):
    """You found the magic :)"""
    with open("waka.txt", "w") as f:
        f.write(str(uuid.uuid4()))
    sequenced = datetyme + datetime.timedelta(seconds=next(sequence))
    date_string = "--date=%s" % sequenced.isoformat()
    subprocess.check_call(("git", "commit", "waka.txt", "-m", '"waka"', date_string))

DEFAULT_CODE = {" ": 0, "x": 50, "X": 100}


def commit_pattern(pattern_chars, pattern_key=DEFAULT_CODE):
    pattern_daycount = 50 * 7
    assert len(pattern) == pattern_daycount, len(pattern)
    assert isinstance(pattern, str), type(pattern)
    assert all(element in pattern_key for element in pattern_chars)

    rtfn = datetime.datetime.now()

    start_days_back = datetime.timedelta(days=pattern_daycount + rtfn.day + 4)

    start_dt = rtfn - start_days_back
    for day in range(pattern_daycount):
        date_of_commit = start_dt + datetime.timedelta(days=day)
        day_char = pattern_chars[day]
        commit_count = pattern_key[day_char]

        for count in range(commit_count):
            do_commit_on_datetime(date_of_commit)


def load_pattern(pattern_file_path):
    with open(pattern_file_path) as f:
        lines = f.readlines()

    assert len(lines) == 7
    # assert all(len(line) == 51 for line in lines)

    print("Loading:")
    for line in lines:
        print(line[0:50])
        assert len(line) == 51

    # Do a janky transpose operation
    chars = ""
    for week in range(50):
        for day in range(7):
            chars += lines[day][week]
    return chars


def push_pattern(branch_name):
    subprocess.check_call(("git", "push", "origin", branch_name))


class BranchSwitcher:
    """A tiny context manager that switches you into a nonexistant branch, and pulls you back on __exit__"""
    def __init__(self, to_branch):
        # assert to_branch not in self.get_local_branches(), "Will not overwrite locally present branches"
        self._to_branch = to_branch

    def __enter__(self):
        self._before = self.get_current_branchname()
        subprocess.check_output(("git", "checkout", "-b", self._to_branch))

    def __exit__(self, *args):
        subprocess.check_output(("git", "checkout", self._before))

    def get_current_branchname(self):
        branch = subprocess.check_output(("git", "rev-parse", "--abbrev-ref", "HEAD"))
        return branch.strip().decode()

    def get_local_branches(self):
        local_branches = subprocess.check_output(("git", "branch"))
        local_branches = local_branches.decode().replace("*", "").split()
        return set(branch.strip() for branch in local_branches)


def setup_copy(newname, pattern):
    os.chdir("..")
    os.mkdir(newname)
    os.chdir(newname)
    os.copy("../wakawakawaka/LICENSE", ".")
    os.copy("../wakawakawaka/README.md", ".")
    os.copy("../wakawakawaka/base.py", ".")
    os.copy("../wakawakawaka/vote.txt", ".")
    os.copy("../wakawakawaka/waka.txt", ".")
    os.system("git init")
    os.system("")
    os.system("git add .")
    os.system('git commit -am "Base"')
    load_pattern(pattern)
    push_pattern(pattern)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('message_file', default="vote.txt", type=str, help='Message file to load')
    parser.add_argument('branch', default="vote", type=str, help='Branch to push to')

    args = parser.parse_args()

    pattern = load_pattern(args.message_file)
    with BranchSwitcher(args.branch):
        commit_pattern(pattern)
        push_pattern(args.branch)

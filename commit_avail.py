#!/usr/bin/python3
import subprocess
import sys
import os
from acp_process import Run_command

def get_current_branch():
    return subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()

def get_commit_details(cmid):
    return subprocess.check_output(["git", "show", cmid]).strip().decode().splitlines()[0]

def Check_avail():
    # Check if any arguments are passed
    if len(sys.argv) == 2:
        print("To skip copying log, use\n\t$ ./commit.py -i\n\t*only if you copied the log file in /tmp/log\n")
    
    print(f"\nChecking commits in branch --> {get_current_branch()}\n")
    print("Enter all the commits")

    if len(sys.argv) == 2:
        print("Wait, It's logging....")
        Run_command(f"git log > /tmp/log")
        Run_command(f"git log --pretty=oneline > /tmp/1_log")

    print("\n ######################################### \n")

    x = 0  # Available commits count
    y = 0  # Not Available commits count
    z = 0  # May be as Upstream

    # Read multiple lines of commit IDs into the 'commits' list
    commits = []
    print("Now, Enter the commit IDs (one per line). Press Ctrl+D when done:")
    
    try:
        while True:
            line = input()
            if line :
                 commits.append(line)
    except EOFError:
        pass
    if os.path.exists("/tmp/Avail_commit"):
        os.remove("/tmp/Avail_commit")
    if os.path.exists("/tmp/No_Avail_commit"):
        os.remove("/tmp/No_Avail_commit")

    Run_command("touch /tmp/Avail_commit /tmp/No_Avail_commit")
    for cmid in commits:
        res = subprocess.run(f"grep {cmid} /tmp/1_log -q", shell=True, universal_newlines=True)
        if not res.returncode :
            x += 1
            Run_command(f"echo {cmid} >> /tmp/Avail_commit")
            print(f"{get_commit_details(cmid)}   Available")
        else :
            grep_line = subprocess.run(f"grep {cmid} /tmp/log", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
            if grep_line.stdout:
                z += 1
                Run_command(f"echo {cmid} >> /tmp/Avail_commit")
                print(f"commit {cmid} Available like this ")
                for line in grep_line.stdout.splitlines():
                    print(f"\t{line}")
            else:
                y += 1
                Run_command(f"echo {cmid} >> /tmp/No_Avail_commit")
                print(f"commit {cmid}   Not Available")

    print("\n ######################################### \n")
    print(f"\tTotally   -({x})- commits Available directly -({z})- may be as upstream and -({y})- commits Not Available\n")
    print("\tAvailable commits are stored in --> /tmp/Avail_commit")
    print("\t   and not available commits in --> /tmp/No_Avail_commit")

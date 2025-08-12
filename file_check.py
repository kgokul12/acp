#!/usr/bin/env python3

# Script to check the file backported are compiled or not
import subprocess
import os
from acp import Run_command

if __name__ == "__main__":
    print("Enter the no.of commits you backported: ",end="")
    count = int(input())

    log_out = subprocess.run(f'git log -{count} --pretty=format:"%h" ', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    commits = log_out.stdout.splitlines()
    files=[]
    #print(commits)

    for commit in commits:
        log_out = subprocess.run(f'git show {commit} --oneline --name-only', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        name = log_out.stdout.splitlines()[0]
        files = log_out.stdout.splitlines()[1:]
        files_o = [sublist.replace('.c', '.o') for sublist in files]
        
        print(f'\033[96m-- {name}\033[0m')
        for file in files_o :
            if os.path.exists(file):
                res = "\033[92m\u2714\033[0m" # ✔
            else:
                res = "\033[91m\u2718\033[0m" # ✘
            print(f"{file.ljust(50)}\t\t{res}")
        print("")

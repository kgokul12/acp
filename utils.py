#!/usr/bin/env python3
import os
import subprocess
import sys

def Run_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    if result.returncode != 0:
        print(result.stderr)
        print(f"Error: Command failed: {command}")
        exit(1)

def Check_commit_diff():
    # Local function Process diff
    def Process_diff(bp_commit,file_no):
        # check bp_commit
        result = subprocess.run(f"git show {bp_commit} > {file_no}b",stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        grep_out = subprocess.run(f"grep upstream {file_no}b", stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        if not grep_out.stdout:
            print(f"==> For {bp_commit} --> no Upstream id is there")
            print(f"Check commit message of {bp_commit} or check the repo")
            return 1

        up_commit = grep_out.stdout.strip().split()[1]
        result = subprocess.run(f"git show {up_commit}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        if not result.stdout:
            print(f"==> For {bp_commit} --> no Upstream id is there")
            print(f"Check commit message of {bp_commit} or check the repo")
            return 1

        with open (f"{file_no}u",'w') as file:
            file.write(result.stdout)
        print(f"==> Compare {bp_commit} | {up_commit[:14]} :: diff {file_no}b {file_no}u")
        
        result = subprocess.run(f"diff {file_no}b {file_no}u | grep -e '> +' -e '> -' -e '< +' -e '< -'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        diff = result.stdout.strip() or "!* no diff"
        if diff != "!* no diff":
            result = subprocess.run(f"grep -e 'Backport changes' -e 'Backport Changes' {file_no}b", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
            print(f"Deviaton explaination : {'Yes' if result.stdout else 'No'}")
        print(diff)
    # Local function Process_diff ends here

    if len(sys.argv) < 3:
        print("Add commit id you want to check diff or give count to check the list of diffs")
        sys.exit(1)
    try:
        value = int(sys.argv[2])
        print("Checking diff for the following commits")
        result=subprocess.run(f"git log --oneline -{value}", stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        print(result.stdout)
        logs = result.stdout.splitlines()
        bp_commits = []
        for log in logs:
            bp_commits.append(log.split()[0])
        file_no=1
        for bp_commit in bp_commits[::-1]:
            if Process_diff(bp_commit,file_no):
                continue
            file_no += 1

    except ValueError:
        # if commit is given as input
       Process_diff(sys.argv[2],1)    

def Update_acp():
    Run_command(f"wget -P /tmp -q https://raw.githubusercontent.com/kgokul12/Backport/main/Auto_cherry-pick/dist/acp")
    if os.path.exists("/tmp/acp"):
        diff = subprocess.run(f"diff /tmp/acp /usr/bin/acp",stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        if diff.stdout :
            Run_command("sudo cp /tmp/acp /usr/bin/acp")
            print("!Update successfull...")
            os.remove("/tmp/acp")
        else :
            print("!Already up to date...")
        Run_command("acp -h")
        sys.exit(0)
    print("Some problem with updating check after sometimes..")


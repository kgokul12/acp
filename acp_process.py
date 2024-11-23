#!/usr/bin/env python3
import os
import subprocess
import signal
import sys
from utils import Run_command

# Define temporary files
tmpfile = "/tmp/commits"
applied = "/tmp/applied"
sorted_file = "/tmp/sorted"
acp_log = "/home/amd/acp_log"
temp_file_path = "/tmp/tmp_file"
temp_script_path = "/tmp/tmp_script.sh"

sorted_commits=[]
applied_commits=[]
Continue_flag = False

# Function to handle trapped signals
def Sig_catch(signum, frame):
    print("Processing Interrupt...")
    Run_command("git cherry-pick --abort")
    Reset_editor()
    print("cherry-pick aborted...")
    sys.exit(1)

def Trap_signals():
    # Trapping signal SIGINT and SIGTERM
    signal.signal(signal.SIGINT, Sig_catch)
    signal.signal(signal.SIGTERM, Sig_catch)

def Release_signals():
    # Untrap the signals by resetting them to default behavior
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

def Change_core_editor():
    global temp_script_path
    # Create a temporary script to simulate an automated editor
    with open(temp_script_path,'w') as temp_script:
            temp_script.write("#!/bin/bash\nexit\n")
            temp_script_path = temp_script.name

    # Make the temporary script executable
    os.chmod(temp_script_path, 0o755)

    Run_command(f"git config core.editor {temp_script_path}")

def Reset_editor():
    #Reset editor back to "vim"
    if os.path.exists("$PWD/.git/.COMMIT_EDITMSG.swp"):
        os.remove("$PWD/.git/.COMMIT_EDITMSG.swp")
    Run_command(f"git config core.editor 'vi'")
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    os.remove(temp_script_path)

#add commit upstream message.
def Add_upstream_msg(commit):
    global temp_file_path

    # Modify the commit message to include the SHA_ID and additional text
    commit_message = subprocess.check_output("git log -1 --pretty=%B", shell=True, universal_newlines=True).strip()

    # Split the commit message into the first line and the rest
    lines = commit_message.split('\n', 1)
    first_line = lines[0]
    rest_of_message = lines[1] if len(lines) > 1 else ""

    # Combine the new messageg
    new_commit_message = f"{first_line}\n\ncommit {commit} upstream\n\n{rest_of_message}"

    # Write the new commit message to a temporary file
    with open(temp_file_path, mode='w') as temp_file:
        temp_file.write(new_commit_message)
        temp_file_path = temp_file.name

    # Amend the commit with the new message
    print("Adding upstream commit message...")
    Run_command(f"git commit --amend --file={temp_file_path}")

def Get_commit_input():
    commits=[]
    # Read multiple lines of commit IDs into the 'commits' list
    print("Enter the commit IDs (one per line). Press Ctrl+D when done:")
    try:
        while True:
            line = input()
            if line:
                commits.append(line)
    except EOFError:
        pass

    if os.path.exists(tmpfile):
        for commit in commits:
            Run_command(f"echo \"grep -n {commit} {acp_log}\" >> {tmpfile}")
    else:
        with open(tmpfile, "w") as f:
            for commit in commits:
                f.write(f"grep -n {commit} {acp_log}\n")

def Process_commits():
    global sorted_commits, applied_commits
    # Sort and unique the commit IDs, then prepare the grep commands
    if not os.path.exists(acp_log):
        print(f"\nMake a log copy of kernel latest version in Home as {acp_log}")
        print("    eg : checkout to kernel master branch ")
        print(f"         git log --pretty=oneline > {acp_log}")
        print(f"   (or) run acp log (or) acp -lg to create log file")
        sys.exit(1)

    os.chmod(tmpfile, 0o755)

    grep_output = subprocess.run(f"{tmpfile} | sort -ugr", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if not grep_output.stdout.strip():
        print("No commits to process.. May be a invalid commit id")
        sys.exit(1)

    commits = grep_output.stdout.splitlines()

    # Save the output to a file
    with open(sorted_file, "w") as output_file:
        for commit in commits:
            output_file.write(f"{commit}\n")

    for line in commits:
            sorted_commits.append(line.split(':')[1].split()[0])
    print("Commits sorted....")

    # Take all the applied commits from the applied file in applied_commits variable
    if os.path.exists(applied):
        cat_output = subprocess.run(["cat", applied], stdout=subprocess.PIPE, universal_newlines=True)
        applied_commits = cat_output.stdout.splitlines()

# Definition to check the commit is already applied ot not
def Check_commit_status(commit, count):
    if commit in applied_commits and commit == applied_commits[count]:
        # if commit already applied in order skip and return -1
        return -1
    else :
        # Return the value to reset...
        return len(applied_commits) - count

def Apply_commits():
    # Applying the commits
    count = 0
    check_val = -1
    for commit in sorted_commits:
        if check_val == -1:
            check_val = Check_commit_status(commit, count)
            if check_val == -1:
                count += 1
                continue
            else:
                print(f"git reset --hard HEAD~{check_val}")
                Run_command(f"git reset --hard HEAD~{check_val}")
                check_val  = 0

        print(f" --> Applying commit {commit} ....")
        result = subprocess.run(["git", "cherry-pick", commit])
        print(result.returncode)
        if result.returncode != 0:
            print(f"\nConflict occurred while applying commit {commit}")
            print("Resolve the conflict and enter \n'done' / 'd' --> continue \n'abort' / 'a' --> cancel \n'bash' / 'b' --> open bash\n")

            try:
                while True:
                    user_input = input().strip().lower()
                    if user_input == "done" or user_input == 'd':
                        Run_command("git add -u")
                        Run_command("git cherry-pick --continue")
                        break
                    elif user_input == "abort" or user_input == 'a':
                        if os.path.exists("$PWD/.git/.COMMIT_EDITMSG.swp"):
                            os.remove("$PWD/.git/.COMMIT_EDITMSG.swp")
                        Reset_editor()
                        Run_command(f"git config core.editor 'vi'")
                        Run_command("git cherry-pick --abort")
                        sys.exit(1)
                    elif user_input == "bash" or user_input == 'b':
                        print("Entering bash mode... to come out enter 'exit'")
                        subprocess.run("bash")
                    else :
                        print("Invalid input...")
            except EOFError:
                break
        print(f"Commit {commit} successfully applied....")
        Add_upstream_msg(commit)
        Run_command(f"echo {commit} >> {applied}")

    # Display a completion message
    print("All commits have been processed.")

def Cleanup():
    # Clean up the temporary files
    if os.path.exists(tmpfile):
        os.remove(tmpfile)
    if os.path.exists(sorted_file):
        os.remove(sorted_file)
    if os.path.exists(applied):
        os.remove(applied)
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    if os.path.exists(temp_script_path):
        os.remove(temp_script_path)
    i=1
    while True:
        if os.path.exists(f"./{i}b"):
            os.remove(f"./{i}b")
        else :
            break
        if os.path.exists(f"./{i}u"):
            os.remove(f"./{i}u")
        else :
            break
        i+=1

def Auto_cherry_pick():
    if Continue_flag:
        if not os.path.exists(tmpfile):
            print("Add input commits first...")
            #get input commits, process, sort and save into sorted_commits...
            Get_commit_input()
        else :
            Process_commits()
    else :
        #get input commits, process, sort and save into sorted_commits...
        Get_commit_input()
        Process_commits()

    Trap_signals()

    Change_core_editor()

    Apply_commits()

    Reset_editor()

    Release_signals()

    Cleanup()


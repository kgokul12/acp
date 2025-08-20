# ! /usr/bin/bash
# This is a cutomated script to update stable_kernel_master branch in Linux_Backport repo
# using cron jobs
: << usage
format:
30 2 * * 0 /path/to/script
* * * * * command_to_run
- - - - -
| | | | |
| | | | +---- Day of week (0–6, 0 = Sunday)
| | | +------ Month (1–12)
| | +-------- Day of month (1–31)
| +---------- Hour (0–23)
+------------ Minute (0–59)

usage

set -e  # stop on error

# Git repos
torvald_repo="https://github.com/torvalds/linux"
backport_repo="github.com/AMDEPYC/Linux_Backport"

# credentials
username="kgokul12"
token="1DEi9R81axjoYbXZ61xlQXI5zjB0oK0iHimd"

# Temp dir
tmp_dir="/tmp/linux_acp"

echo "[$(date)] Starting script....."

# Clone repo if tmp_dir doesn’t exist, else pull latest
if [ ! -d "$tmp_dir" ]; then
    echo "[$(date)] Cloning torvalds/linux..."
    git clone --single-branch -b master "$torvald_repo" "$tmp_dir" -j10
    git -C "$tmp_dir" remote add lb "https://$username:ghp_$token@$backport_repo"
else
    echo "[$(date)] Repo already exists, pulling latest..."
    git -C "$tmp_dir" fetch origin
    git -C "$tmp_dir" reset --hard origin/master
fi

# Create/update stable_kernel_master branch
echo "[$(date)] Checking out stable_kernel_master branch..."
git -C "$tmp_dir" checkout -B stable_kernel_master origin/master

# Push to Linux_Backport
echo "[$(date)] Pushing stable_kernel_master to Linux_Backport..."
git -C "$tmp_dir" push lb stable_kernel_master --force

# Save commit log
echo "[$(date)] Saving commit log to /home/amd/acp_log"
git -C "$tmp_dir" log --pretty=oneline > "/home/amd/acp_log"

echo "[SUCCESS] $(date): Pushed stable_kernel_master and updated acp_log"
echo "=================="


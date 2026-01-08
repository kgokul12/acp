#!/bin/bash

if ! command -v sshpass &> /dev/null; then
    echo "sshpass not found. Attempting to install..."
fi

hosts=(
"volcano9b5e-host" "volcano9b5e-hostos"
"volcano9dee-hostos" "volcano9dee-host"
"volcano9f6e-hostos" "volcano99fc-os"
"volcano99fc-hostos" "volcano99fc-host"
"volcano9b0c-os" "volcano9b0c-hostos"
"10.86.20.188"
)

working_host=()
offline_host=()

echo "Checking Host online status..."

: > ~/.ssh/known_hosts
rm -f /tmp/sysinfo_errlog /tmp/sysinfo_offline

#Function to get infoo from online hosts
check_host_info() {
    echo "-----------------------------------"
    echo "Checking $1..."

    sshpass -p 'Amd$1234!' ssh -o StrictHostKeyChecking=no "amd@$1" bash 2>>/tmp/sysinfo_errlog << 'EOF'
cat /etc/os-release | grep "PRETTY" | cut -d= -f2 | xargs echo "#Installed OS -->"
cat /etc/motd | xargs echo "#"
ip -4 -o addr show | awk '{print "IP addr:", $4}' | cut -d/ -f1 | grep "10.86"
echo "OS available in other disks:"
lsblk -o NAME | grep -e ^nvm -e home
EOF

    echo "-----------------------------------"
}

i=0
for host in "${hosts[@]}"; do
    if sshpass -p 'Amd$1234!' ssh -o StrictHostKeyChecking=no "amd@$host" ls \
        		>> /tmp/sysinfo_offline 2>> /tmp/sysinfo_errlog; then
        check_host_info "$host"

    else
        if grep -qi "no route" /tmp/sysinfo_errlog; then
            echo "-----------------------------------"
            echo "$host is offline"
            echo "-----------------------------------"
        fi
    fi
    ((i++))
done

echo "#Source code @ /home/amd/.acp/sysinfo.sh"
echo "#errors @ /tmp/sysinfo_errlog"


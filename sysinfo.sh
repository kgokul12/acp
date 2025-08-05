#!/bin/bash

if ! command -v sshpass &> /dev/null; then
        echo "sshpass not found. Attempting to install..."
fi

#Instead of volcano9f8e-os name directly using its ip
hosts=("volcano9b5e-host" "volcano9dee-hostos" "volcano9f6e-hostos" "volcano99fc-os" "volcano9b0c-os" "10.86.20.188")

echo > ~/.ssh/known_hosts
rm -f /tmp/sysinfo_errlog
echo "-----------------------------------"
for host in "${hosts[@]}"; do
    echo "Checking $host..."
    sshpass -p 'Amd$1234!' ssh -o StrictHostKeyChecking=no  "amd@$host" bash 2>>/tmp/sysinfo_errlog << 'EOF'
        cat /etc/os-release | grep "PRETTY" | cut -d= -f2 | xargs echo "#Installed OS -- > $1" ;
        cat /etc/motd | xargs echo "#$1" ;
        ip -4 -o addr show | awk '{print "IP addr:", $4}' | cut -d/ -f1 | grep "10.86"
        echo "OS available in other disks:" ;
        lsblk -o NAME | grep -e ^nvm -e home
EOF
    echo "-----------------------------------"
done

echo "#Source code @ /home/amd/.acp/sysinfo.sh"
echo "#errors @ /tmp/sysinfo_errlog"

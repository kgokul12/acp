# Functions to process each commit ID
read_input() {
    commit_ids=()
    if [ -s "$balance" ]; then
        while IFS= read -r commit_id && [ -n "$commit_id" ]; do
            commit_ids+=("$commit_id")
        done < "$balance"
    else
        while IFS= read -r commit_id && [ -n "$commit_id" ]; do
            commit_ids+=("$commit_id")
            echo "@$commit_id" >> "$tag_file"
        done 
    fi   
    # Process all commits
    for cmid in "${commit_ids[@]}"; do
        process_commit "$cmid" &
    done
    wait
}

process_commit() {
    local cmid=$1
    tag_out=$(git tag --contains="$cmid" --sort=taggerdate | head -n1)
    sed -i "s/^@$cmid/$cmid \t$tag_out/g" "$tag_file"
}

check_once() {
    grep "^@" "$tag_file" > "$balance"
    if [ -s "$balance" ];then 
        sed -i "s/^@//g" "$balance"
        read_input
    fi
}

#====
# Function to handle SIGINT (Ctrl+C)
cleanup() {
    echo "Cleaning up..."
    pkill -P $$  # Kill all child processes
    wait
    exit 1
}

# Set trap to catch SIGINT and call cleanup
trap cleanup SIGINT

#-----MAIN-----
# Get input commit
tag_file="/tmp/tags"
balance="/tmp/balance"

# Check if the file exists and delete it
if [ -f "$tag_file" ]; then
    > "$tag_file"
fi

echo -e "\033[91mRun this command only inside Source kernel tree\033[0m"
echo "Enter the input commit and press 'enter'"
read_input

echo "#Processing tags..."
while true; do
    check_once
    # Checking if the file is empty or not
    if [ ! -s "$balance" ]; then
        break
    fi
    > "$balance"
done

cat "$tag_file"
echo "#Process done, check output @ $tag_file"

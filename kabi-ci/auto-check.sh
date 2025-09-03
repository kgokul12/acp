#! /usr/bin/bash

kabi_dir="/tmp/kabi-ci"
kabi_script="/home/amd/.acp/kabi-ci/check-kabi"
build="yes "" | make modules -j$(nproc) > $kabi_dir/make_output 2>&1"

echo "Enter the no. of patches you want to check kabi:"
read  count

# setup kabi dir
if [ ! -d $kabi_dir ]; then
  mkdir $kabi_dir
fi

rm -rf $kabi_dir/patches 
git format-patch -o $kabi_dir/patches -p$count -q

echo "Setting up kabi workspace"
dir=$(basename "$PWD")
cp -r $PWD $kabi_dir -f 

cd $kabi_dir/$dir

git reset --hard HEAD~$count

echo "Building Modules.kabi"
#Build and check kabi
$build
cp Module.symvers ../Module.base 

echo "Building kernel to check kabi"
echo > $kabi_dir/kabi_out

# Apply patch by patch and check kabi
for p in ../patches/*.patch;
do
  git am $p || echo "git am failed"
  $build
  $kabi_script -k ../Module.base -s Module.symvers > $kabi_dir/kabi_out
  
  if [[ -s "$kabi_dir/kabi_out" ]];
  then
    echo -e "\033[91mKABI errors detected. Symbols \033[0m"
    awk '/^new kabi:/ {in_new=1; next}/^old kabi:/ {in_new=0} in_new {print $2}' $kabi_dir/kabi_out
  else
    echo -e "\033[92mNo KABI errors.\033[0m"
  fi
  cp Module.symvers ../Module.base
done

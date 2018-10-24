#!/bin/bash


if [ -f "~/.bash_profile"  ]; then
    cp -f ~/.bash_profile ~/.bash_profile.bk
fi
cp -f ./env/sysconfig/bash_profile ~/.bash_profile
if [ -f "~/.vimrc"  ]; then
    cp -f ~/.vimrc ~/.vimrc.bk
fi
cp -f ./env/sysconfig/vimrc ~/.vimrc

cp -rf ./env/bin ~/. 
cp -rf ./env/cfg ~/.
cp -rf ./env/log ~/.

if [ -d ".tmp" ]; then
    rm -rf "./.tmp"
fi
mkdir .tmp
cd .tmp
echo "Pypy Downloading..."
wget "https://doc-04-as-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/4ufaukfjni86k1bv8kfhu7i85kt8a09g/1540368000000/14436876053751962895/*/1HJe1NVbkdi8GbnCui1bFI_5m-ffBXZ_m?e=download" -O Pypy2-6.0.0.tar.gz

tar -zxvf ./Pypy2-6.0.0.tar.gz
if [ ! -d "~/.util" ]; then
    mkdir ~/.util
    mkdir ~/.util/python
fi
cd ..
rm -rf ./.tmp

mv Pypy2-6.0.0 ~/.util/python/.
cd ..
cd ..
mv h2_sim src


#!/bin/bash

now_pwd=`pwd`
check=`ls -lthr $now_pwd/main.py | wc -l`
pypy_tar="Pypy2-6.0.0.tar.gz"
sz_tar=2201986033

if [ "$check" != "1" ]; then
    echo "Invalid current directory: PWD=${now_pwd}"
    exit
fi

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

if [ ! -d ".download" ]; then
    mkdir .download
fi
cd .download
echo "Pypy Downloading..."
if [ -f "./${pypy_tar}"  ]; then
    pypy_cksum=`cksum ./${pypy_tar}  | cut -d ' ' -f 1`
fi
if [ "$pypy_cksum" != "2455333854" ]; then
    #wget "https://doc-04-as-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/4ufaukfjni86k1bv8kfhu7i85kt8a09g/1540368000000/14436876053751962895/*/1HJe1NVbkdi8GbnCui1bFI_5m-ffBXZ_m?e=download" -O $pypy_tar
    export PYTHONPATH=""
    python ../google_downloader.py "1HJe1NVbkdi8GbnCui1bFI_5m-ffBXZ_m" $pypy_tar $sz_tar
fi

tar -zxvf ./$pypy_tar
if [ ! -d "~/.util" ]; then
    mkdir ~/.util
    mkdir ~/.util/python
fi
mv Pypy2-6.0.0 ~/.util/python/.
cd ..
#rm -rf ./.download

cd ..
if [ -d "h2_sim" ]; then
    mv h2_sim src
fi

#acccount=`id | cut -d '('  -f 2 | cut -d ')' -f 1`
#
#su - $acccount

source ~/.bash_profile
cd ~

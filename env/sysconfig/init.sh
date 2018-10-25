#!/bin/bash

check_root=`id | grep "(root)" | wc -l`
if [ "$check_root" == 0 ] ; then
        echo "This script must be executed as root account"
            exit
            fi

            echo "Please input simulator user account"
            read sim_account

            check_in_use=`cat /etc/passwd | grep "${sim_account}:" | wc -l`
            if [ "$check_in_use" != 0 ] || [ `expr length "$check_in_use"` == 0 ]; then
                    echo "Account:$sim_account Already in use or invalid"
                        exit
                        fi

                        useradd $sim_account
                        passwd $sim_account

#su - $sim_account
cd /home/$sim_account
git clone https://github.com/srkim90/h2_sim.git
chown $sim_account:$sim_account ./h2_sim
cd h2_sim
echo " -- Please Input this commend --"
echo "cd ~/h2_sim"
echo "./SETUP.sh"
su - $sim_account


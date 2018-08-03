#!/bin/bash
# you can add this script to the end of your /etc/crontab
# without the # at the begining of the line...  ;-)
#  */10 * * * *  	root	/root/testIfActionRequired.sh
NOW=`date`
LOG='log/testIfActionRequired.log'
./ufwbanbadguys.py >./result.txt 
echo "###########################" &>> ${LOG}
#cat ./result.txt  2>&1 | tee -a ${LOG}
if grep -q  '##You can run' ./result.txt
then
   echo "+++ OK FOUND WORK AT ${NOW}" &>> ${LOG}
   source ./result.txt &>> ${LOG}
else
   echo "--- NO COMMAND TO RUN AT ${NOW}" &>> ${LOG}
fi

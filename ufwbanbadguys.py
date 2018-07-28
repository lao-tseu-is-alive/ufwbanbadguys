#!python3
import re

# set the path of the linux ssh auth log
# TODO allow to pass this path as argument to the script
authLog = "/var/log/auth.log"
# set the maximum number of password errors before being
maxAllowedErrors = 5
ipDic = dict()
with open(authLog) as file:
    for line in file:
        line = line.strip()
        # filter lines having 'Failed password attempts'
        if re.match('.*Failed password', line):
            # extract all ip from this line usually there is only one
            ipList = re.findall('[0-9]+(?:\.[0-9]+){3}', line)
            # get the first one
            ip = ipList[0]

            ipDic[ip] = ipDic.get(ip, 0) + 1
for k in sorted(ipDic, key=ipDic.get, reverse=True):
    # for now just display the 'top bad guys ip' and a proposal of ufw command
    # TODO I must check if the ip is already present in the UFW rules
    if ipDic[k] > maxAllowedErrors:
        print("{ip} : {count} ".format(ip=k, count=ipDic[k]))
        print("ufw insert 1 deny from {ip}".format(ip=k))

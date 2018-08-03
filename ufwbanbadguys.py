#!/usr/bin/python3
import re
import subprocess

# set the path of the linux ssh auth log
# TODO allow to pass this path as argument to the script
authLog = "/var/log/auth.log"
whiteList = "config/WHITELIST"
# set the maximum number of password errors before being
maxAllowedErrors = 20

# allows to test if ip is in Sunrise range
def isSunriseIP(ip):
    a, b, c, d = [int(x) for x in ip.split('.')]
    if a != 178: return False
    if b != 39: return False
    if (c < 64) or (c > 127): return False
    return True


# give back array of white listed ip in config file
def getWhiteListIp(whiteListConfigFile):
    with open(whiteListConfigFile, "r") as f:
        return [line.rstrip() for line in f]


# give array of already denied ip in UFW firewall
def getFwDeniedIP():
    deniedIp = []
    ufwResult = subprocess.run(['ufw', 'status'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    for line in ufwResult.split('\n'):
        line = line.strip()
        if re.match('Anywhere\s+DENY\s+([0-9]+(?:\.[0-9]+){3})', line):
            ipList = re.findall('[0-9]+(?:\.[0-9]+){3}', line)
            deniedIp.append(ipList[0])
    return deniedIp


ipWhiteList = getWhiteListIp(whiteList)
# print(ipWhiteList)
# get a list of ip already blocked by UFW
ipBlocked = getFwDeniedIP()
# print(ipBlocked)
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
cmdToRun = ""
cmdToLog = ""
for ipKey in sorted(ipDic, key=ipDic.get, reverse=True):
    if ipDic[ipKey] > maxAllowedErrors:
        if ipKey in ipWhiteList:
            info = ' ## THIS IP IS IN YOUR WHITE LIST ##'
        elif isSunriseIP(ipKey):
            info = ' ## THIS IP IS IN SUNRISE SUBNET ##'
        else:
            if ipKey in ipBlocked:
                info = ' OK ip Already blocked by your UFW firewall'
            else:
                cmdToRun += ("ufw insert 1 deny from {ip}\n".format(ip=ipKey))
                cmdToLog += ("grep '{ip}' /var/log/auth.log > log/badguys/auth_{ip}.log\n".format(ip=ipKey))
                info = ' WARNING you better BAN this IP'
        print("{ip} : {count} --> {msg}".format(ip=ipKey, count=ipDic[ipKey], msg=info))
    
print("\nYou can run this commands:\n")
print(cmdToRun)
print(cmdToLog)

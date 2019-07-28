import speedtest
import os
import subprocess
import psutil
import time
from json import load
from urllib2 import urlopen
from prettytable import PrettyTable
import csv

def kill_openvpn():
    for proc in psutil.process_iter():
        if 'openvpn' in proc.cmdline():
            print(proc.cmdline())
            proc.terminate()
            proc.wait()

def get_ip():
    try:
        my_ip = load(urlopen('http://jsonip.com'))['ip']
    except:
        return 'fail'
    return my_ip

def get_ip():
    try:
        my_ip = load(urlopen('http://jsonip.com'))['ip']
    except:
        return 'fail'
    return my_ip

def get_location(ip):
    try:
        locs = load(urlopen('http://ip-api.com/json/{0}'.format(ip)))
    except:
        return 'fail'
    return locs

def list_process():
    procs = {p.pid: p.info for p in psutil.process_iter(attrs=['name', 'username'])}
    process_list = []
    for key, value in procs.iteritems():
        process_list.append(procs[key]['name'])
    return process_list

servers = []
# If you want to test against a specific server
# servers = [1234]

# sudo openvpn --config /home/chevalier/surfshark_conf/us-nyc.prod.surfshark.com_tcp.ovpn --auth-user-pass /home/chevalier/surfshark_conf/secrets --daemon
print('----------')
print(os.geteuid())
print('----------')

def vpn(myfile):

    vpn_out = subprocess.Popen('openvpn --config /home/chevalier/surfshark_conf/{0} --auth-user-pass /home/chevalier/surfshark_conf/secrets --daemon'.format(myfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return vpn_out

def tester():
    s = speedtest.Speedtest()
    time.sleep(1)
    s.get_servers(servers)
    s.get_best_server()
    s.download()
    s.upload()
    #s.results.share()

    results_dict = s.results.dict()
    return results_dict

def without_vpn():

    kill_openvpn()
    time.sleep(2)
    ip = get_ip()
    locs = get_location(str(ip))
    res = tester()
    return ['WITHOUT VPN', ip, locs['country'], locs['city'], float(res['download'])/1000000, float(res['upload'])/1000000]
    print("\n-----Vpn result : {0} {1} -- {2}".format(float(res['download'])/1000000, float(res['upload'])/1000000, ip))


directory = '/home/chevalier/surfshark_conf'
x = PrettyTable(["file name", "IP", "Country", "City", "Download", "Upload"])
x.add_row(without_vpn())

for filename in os.listdir(directory):
    if filename.endswith(".ovpn"):
        vpn_outs = vpn(filename)
        time.sleep(7)
        ps_list = list_process()
        if 'openvpn' in ps_list:
            print("\n-----Vpn Success : {0}".format(filename))
            time.sleep(4)
            ip = get_ip()
            locs = get_location(str(ip))
            res = tester()
            print("\n-----Vpn result : {0} {1} -- {2}".format(res['download'], res['upload'], ip))
            time.sleep(1)

            x.add_row([str(filename), ip, locs['country'], locs['city'], float(res['download']) / 1000000, float(res['upload']) / 1000000])
            print(x)
            with open('/tmp/result.txt', 'w+') as the_file:
                the_file.write(str(x))
            kill_openvpn()
            continue
        else:
            print(filename, ': FAIL')
        retval = vpn_outs.wait()
        continue
    else:
        continue

print(x)

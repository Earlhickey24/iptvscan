# iptvscan
# Script for scanning and saving IPTV playlist.
# Python v.3 required for using. https://www.python.org/downloads/

# How to use
# - First of all, make sure that the channels you want to scan are provided using multicast IPTV technology. https://en.wikipedia.org/wiki/Multicast_address
# Even if someone calls it IPTV, it doesn't mean it is. If you don't know what technology is used, then it's most likely not multicast IPTV.
# At this point it is an outdated technology and I find it strange to hear that it is still used anywhere today.
# - Next, you need to know at least one IP address and port with working IPTV. The script will allow you to scan other channels.
# If first number in IP adress less 224 - this not multicast IPTV.
# - Install python version 3 from https://www.python.org/downloads/
# - Open iptvscan.py in text editor and edit variables ip_start, ip_end and list of ports.
# - Run iptvscan.py

# Author: joddude <joddude@gmail.com>

# Disclaimer:
# This script is free and provided "as is" without any warranty.
# You can use it at your own risk.
# The author assumes no responsibility for any moral or material damage caused
# by the use of this software, any loss of profit as a result of or during use.

#------------------------------------------------------------------------------

ip_start = '23.153.216.68'
ip_end   = '23.153.216.254'
ports    = [1234, 1235, 1238, 1239, 1250, 1251, 1252, 1281, 1282, 1283, 1284,
            1292, 2101, 2104, 2178, 2191, 2192, 2193, 2194, 2201, 2208, 2223,
            2224, 2225, 2226, 2345, 4120, 5140, 6000, 8004, 8012, 8024, 8028,8080,
            8124, 8138, 8224, 8302, 9000, 9008, 9012, 9020, 9024, 9040, 9044,
            9048, 9052, 9068, 9072, 9076, 9132, 9136, 9148, 9208]

timeout=1               # seconds
random_search = False   # False or True

#------------------------------------------------------------------------------

import socket
import struct
import os, sys
import time, datetime
import random

#------------------------------------------------------------------------------

playlist_name = 'IPTV-'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.m3u'

#------------------------------------------------------------------------------

def main():
    scan_list = generate_scan_list(ip_start, ip_end, ports)
    if random_search:
        random.shuffle(scan_list)
    print(f'IP from {ip_start} to {ip_end} ({len(scan_list)})\n')
    print('Ports:', *ports, '\n')
    print('Playlist name:', playlist_name, '\n')
    with open(playlist_name, 'w') as f:
        f.write('#EXTM3U\n\n')
    found_channels = 0
    update_progress(0, 'Scan '+ip_start+':'+str(ports[0]))
    for counter, scan_item in enumerate(scan_list, start=1):
        if iptv_test(scan_item['ip'], scan_item['port'], timeout):
            write_to_playlist(scan_item['ip'], str(scan_item['port']))
            found_channels +=1
        update_progress(counter/len(scan_list), 'Scan '+scan_item['ip']+':'+str(scan_item['port']), '(Found '+str(found_channels)+' channels)    ')
    print(f'\nFound {found_channels} channels.')

#------------------------------------------------------------------------------

def write_to_playlist(ip, port):
    with open(playlist_name, 'a') as f:
        f.write(f'#EXTINF:-1,IPTV Channel {ip}:{port}\n')
        f.write(f'udp://@{ip}:{port}\n')
        f.write('\n')

#------------------------------------------------------------------------------

def iptv_test(ip, port, timeout=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(timeout)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    mreq = struct.pack('4sl', socket.inet_aton(ip), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    try:
        if sock.recv(10240):
            return True
        else:
            return False
    except socket.timeout:
        return False

#------------------------------------------------------------------------------

def generate_scan_list(ip_start, ip_end, ports):
    start = list(map(int, ip_start.split('.')))
    end = list(map(int, ip_end.split('.')))
    temp = start
    ip_range = []
    ip_range.append(ip_start)
    while temp != end:
        start[3] += 1
        for i in (3, 2, 1):
            if temp[i] == 256:
                temp[i] = 0
                temp[i-1] += 1
        ip_range.append('.'.join(map(str, temp)))
    scan_list = []
    for ip in ip_range:
        for port in ports:
            scan_list.append({'ip': ip, 'port': port})
    return scan_list

#------------------------------------------------------------------------------

def update_progress(progress, title='Progress', status = ''):
    barLength = 50
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = 'error: progress var must be float\r\n'
    if progress < 0:
        progress = 0
        status = 'Halt'+' '*21+'\r\n'
    if progress >= 1:
        progress = 1
        status = 'Done'+' '*21+'\r\n'
    block = int(round(barLength*progress))
    text = '\r'+title+': [{0}] {1}% {2}'.format( '#'*block + '-'*(barLength-block), round(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

#------------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        print('IPTV scan started. Press Ctrl+C to stop.\n')
        main()
    except KeyboardInterrupt:
        print('\n\nYou pressed Ctrl+C. Stop')
        sys.exit()
    except:
        import sys
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
    finally:
        print('IPTV scan finished. Press Enter to exit ...')
        input()

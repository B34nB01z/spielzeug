#!/usr/bin/python3

import os
import re
import sys
import csv
import time
import socket
import shutil
from argparse import ArgumentParser

PROTOCOLS = {
    'tcp': {
        'type': socket.SOCK_STREAM,
        'known_ports': './tcp.csv',
    },
    'udp': {
        'type': socket.SOCK_DGRAM,
        'known_ports': './udp.csv'
    },
}

def print_delim(sym: str = '=') -> None:
    print('='*shutil.get_terminal_size().columns)

def main():
    print_delim()
    print('''`7MM                                  `7MM        `7MM                                  `7MM      
  MM                                    MM          MM                                    MM      
  MM  ,MP'`7MMpMMMb.  ,pW"Wq.   ,p6"bo  MM  ,MP'    MM  ,MP'`7MMpMMMb.  ,pW"Wq.   ,p6"bo  MM  ,MP'
  MM ;Y     MM    MM 6W'   `Wb 6M'  OO  MM ;Y       MM ;Y     MM    MM 6W'   `Wb 6M'  OO  MM ;Y   
  MM;Mm     MM    MM 8M     M8 8M       MM;Mm mmmmm MM;Mm     MM    MM 8M     M8 8M       MM;Mm   
  MM `Mb.   MM    MM YA.   ,A9 YM.    , MM `Mb.     MM `Mb.   MM    MM YA.   ,A9 YM.    , MM `Mb. 
.JMML. YA..JMML  JMML.`Ybmd9'   YMbmd'.JMML. YA.  .JMML. YA..JMML  JMML.`Ybmd9'   YMbmd'.JMML. YA.''')
    print_delim()

    parser = ArgumentParser()
    parser.add_argument('host', type=str, help='The target host ... ')
    parser.add_argument('range', type=str, help='The port range to scan (use \'*\' to scan all) ... ')
    parser.add_argument('-p', '--protocol', type=str, help='TCP or UDP?', default='tcp')
    args = parser.parse_args()

    host = args.host
    if not re.match(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', args.host):
        try:
            host = socket.gethostbyname(args.host)
        except socket.gaierror:
            print(f'[-] The hostname "{args.host}" couldn\'t be resolved ... ')
            os._exit(1)

    prange = ()
    if args.range == '*':
        prange = (0,2**16)
    elif re.match(r'\d+-\d+', args.range):
        prange = tuple([int(x) for x in args.range.split('-')])
    else:
        print(f'[-] Unknown range format "{args.range}"! Make sure you specify the range in this "{{from}}-{{to}}" format ... ')
        os._exit(1)

    if not args.protocol.lower() in ['tcp', 'udp']:
        print(f'[-] Unknown transport layer protocol!')
        os._exit(1)

    prot = PROTOCOLS[args.protocol.lower()]['type']

    print('[*] Loading list of known port assignments ... ')
    known = dict()
    with open(PROTOCOLS[args.protocol.lower()]['known_ports'], 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        reader.__next__()
        for r in reader:
            known[int(r[1])] = r[2]

    print('[*] Let the scanning begin ... ')
    stime = time.time()

    try:
        for p in range(*prange):
            sock = socket.socket(socket.AF_INET, prot)
            sock.settimeout(2)
            print(f'\r[*] Trying :{p} ... ', end='')
            try:
                if not sock.connect_ex((host, p)):
                    print('\r[+] Port :{}{} is open'.format(p, f' ({known[p]})' if p in known.keys() else ''))
                    print(f' -> First 64 bytes: {sock.recv(64)}')
            except socket.timeout:
                pass
            sock.close()
    except KeyboardInterrupt:
        print('[*] Interrupted. Exiting ... ')
        os._exit(0)
    except socket.error:
        print('[-] Couldn\'t connect to server ... Exiting ... ')
        os._exit(1)

    print(f'\r[+] Finished scanning after {time.time()-stime:.2f}s ... ')

if __name__ == '__main__':
    main()
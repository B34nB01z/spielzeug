#!/usr/bin/python3

import os
import sys
import time
import shutil
import random
from typing import *
import requests as req
from stem import Signal
from stem.control import Controller
from argparse import ArgumentParser

try:
    ENV_TOR_PWD = bool(os.environ['TOR_PWD'])
except:
    ENV_TOR_PWD = False
    print(f'[!] Warning: "TOR_PWD" is not an environment variable... You\'ll have to use a custom config!')

DEFAULT_TOR_CONF = {
    'port': 9050,
    'control_port': 9051,
    'control_pass': os.environ['TOR_PWD'] if ENV_TOR_PWD else '',
}

DEFAULT_USER_AGENTS = [
    'Mozilla/5.0 (Linux; U; Android 4.0.4; en-us; Glass 1 Build/IMM76L; XE7) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Dalvik/1.6.0 (Linux; U; Android 4.1.1; BroadSign Xpress 1.0.14 B- (720) Build/JRO03H)',
    'Mozilla/5.0 (X11; GNU/Linux) AppleWebKit/601.1 (KHTML, like Gecko) Tesla QtCarBrowser Safari/601.1',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.0.146.3-Gen4_12000410) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; PalmSource/Palm-D050; Blazer/4.3) 16;320x448',
    'Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/606.4 (KHTML, like Gecko) NF/6.0.1.15.4 NintendoBrowser/5.1.0.20393',
    'atc/1.0 watchOS/6.1.1 model/Watch2,4 hwp/t8002 build/17S449 (6; dt:134)',
    'BlackBerry8520/5.0.0.681 Profile/MIDP-2.1 Configuration/CLDC-1.1 VendorID/600'
]

def print_delim(sym: str = '=') -> None:
    print('='*shutil.get_terminal_size().columns)

class Bowser(req.Session):
    def __init__(self, *args, user_agents: List[str] = DEFAULT_USER_AGENTS, tor_conf: object = DEFAULT_TOR_CONF, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_agents = user_agents
        self.tor_conf: object = tor_conf
        self.proxies = dict(http=f'socks5://localhost:{self.tor_conf["port"]}', https=f'socks5://localhost:{self.tor_conf["port"]}',)
        self.new_identiy()

    def new_identiy(self) -> None:
        with Controller.from_port(port=self.tor_conf['control_port']) as ctrl:
            ctrl.authenticate(password=self.tor_conf['control_pass'])
            ctrl.signal(Signal.NEWNYM)
        self.headers = { 'User-Agent': random.choice(self.user_agents), }

def main():
    print_delim()
    print(''' ,,                                                           
*MM                                                           
 MM                                                           
 MM,dMMb.   ,pW"Wq.`7M'    ,A    `MF',pP"Ybd  .gP"Ya `7Mb,od8 
 MM    `Mb 6W'   `Wb VA   ,VAA   ,V  8I   `" ,M'   Yb  MM' "' 
 MM     M8 8M     M8  VA ,V  VA ,V   `YMMMa. 8M""""""  MM     
 MM.   ,M9 YA.   ,A9   VVV    VVV    L.   I8 YM.    ,  MM     
 P^YbmdP'   `Ybmd9'     W      W     M9mmmP'  `Mbmmd'.JMML.   ''')
    print_delim()

    parser = ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help='The URL you want to get ... ')
    parser.add_argument('-b', '--browser', type=str, help='The browser you want to use to view the downloaded pages ... ', default='firefox')
    args = parser.parse_args()

    b = Bowser()
    if args.url:
        print(f'[*] Retrieving "{args.url}" ... "')
        stime = time.time()
        try:
            with open('out.html', 'w') as f:
                f.write(b.get(args.url).text)
        except Exception:
            print('[-] Couldn\' get specified URL ... ')
        print(f'[+] Finished after {time.time()-stime:.2f}s')
    else:
        try:
            while True:
                url = input('> ')
                stime = time.time()
                try:
                    with open('out.html', 'w') as f:
                        f.write(b.get(url).text)
                    os.system(f'{args.browser} out.html')
                except Exception:
                    print('[-] Couldn\'t get specified URL ... ')
                print(f'[*] Retrieved page aftter {time.time()-stime:.2f}s')
        except KeyboardInterrupt:
            print('[*] Got interrupt. Exiting ... ')

if __name__ == '__main__':
    main()
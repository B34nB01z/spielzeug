#!/usr/bin/python3

import os
import sys
import time
import shutil
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

def print_delim(sym: str = '=') -> None:
    print('='*shutil.get_terminal_size().columns)

class Bowser(req.Session):
    def __init__(self, *args, tor_conf: object = DEFAULT_TOR_CONF, **kwargs):
        super().__init__(*args, **kwargs)
        self.tor_conf: object = tor_conf
        self.proxies = dict(http=f'socks5://localhost:{self.tor_conf["port"]}', https=f'socks5://localhost:{self.tor_conf["port"]}',)

    def new_identiy(self) -> None:
        with Controller.from_port(port=self.tor_conf['control_port']) as ctrl:
            ctrl.authenticate(password=self.tor_conf['control_pass'])
            ctrl.signal(Signal.NEWNYM)

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
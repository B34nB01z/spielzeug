#!/usr/bin/python3

import os
import sys
import time
import shutil
from typing import *
from threading import Thread
from argparse import ArgumentParser

# -- HASHING MODULES -- #
import crypt
import bcrypt
# -- HASHING MODULES -- #

HASHES = {
    'crypt': {
        'salt_len_required': True,
        'compare': (lambda w, h, l: crypt.crypt(w, h[:l]) == h),
    },
    'bcrypt': {
        'salt_len_required': False,
        'compare': (lambda w, h, l: bcrypt.checkpw(w.encode(), h.encode())),
    },
}

cu_found: bool = False

def print_delim(sym: str = '=') -> None:
    print('='*shutil.get_terminal_size().columns)

def crack(ws: List[str], h: str, sl: Optional[int], cmp: Callable[[str, str, Optional[int]], bool]) -> None:
    global cu_found
    for w in ws:
        if cu_found:
            break
        if cmp(w, h, sl):
            print(f'\r[+] Cracked "{h}" ... "{w}"')
            cu_found = True
            break

def main():
    global cu_found

    print_delim()
    print(''' ,,                                                                                              
*MM                                                                    `7MM                      
 MM                                                                      MM                      
 MM,dMMb.   .gP"Ya   ,6"Yb.  `7MMpMMMb.  ,p6"bo `7Mb,od8 ,6"Yb.  ,p6"bo  MM  ,MP'.gP"Ya `7Mb,od8 
 MM    `Mb ,M'   Yb 8)   MM    MM    MM 6M'  OO   MM' "'8)   MM 6M'  OO  MM ;Y  ,M'   Yb  MM' "' 
 MM     M8 8M""""""  ,pm9MM    MM    MM 8M        MM     ,pm9MM 8M       MM;Mm  8M""""""  MM     
 MM.   ,M9 YM.    , 8M   MM    MM    MM YM.    ,  MM    8M   MM YM.    , MM `Mb.YM.    ,  MM     
 P^YbmdP'   `Mbmmd' `Moo9^Yo..JMML  JMML.YMbmd' .JMML.  `Moo9^Yo.YMbmd'.JMML. YA.`Mbmmd'.JMML. ''')
    print_delim()

    parser = ArgumentParser()
    parser.add_argument('hashes', type=str, help='Path to the file containing hashes - one per line ... ')
    parser.add_argument('wordlist', type=str, help='Path to wordlist - one word per line ... ')
    parser.add_argument('-t', '--hash-type', type=str, help='The hashes\' hash type ... ', default='crypt')
    parser.add_argument('-s', '--salt-len', type=int, help='The salt length (if required) ... ')
    parser.add_argument('--threads', type=int, help='How many threads to use ... ', default=4)
    args = parser.parse_args()

    if not args.hash_type in HASHES.keys():
        print('[-] Unknown hash type ... The following types are currently supported: ')
        for k in HASHES.keys():
            print(f' - {k}')
        os._exit(1)

    if HASHES[args.hash_type]['salt_len_required'] and not args.salt_len:
        print('[-] The selected hash type requires you to specify the salt length (-s, --salt-len) ... ')
        os._exit(1)

    if not os.path.isfile(args.hashes):
        print(f'[-] The hashes-file "{args.hashes}" is either not a file or couldn\'t be found on disk ... ')
        os._exit(1)

    if not os.path.isfile(args.wordlist):
        print(f'[-] The wordlist-file "{args.wordlist}" is either not a file or couldn\'t be found on disk ... ')
        os._exit(1)

    print('[*] Let the cracking begin ... ')
    stime = time.time()

    with open(args.hashes, 'r') as hl:
        ws = []
        with open(args.wordlist, 'r') as wl:
            ws = [l.strip() for l in wl.readlines()]
        parts = len(ws)//args.threads
        for h in hl.readlines():
            cu_found = False
            h = h.strip()
            print(f'[*] Cracking "{h}" ...', end='')
            sys.stdout.flush()

            ts = []
            for i in range(args.threads-1):
                ts.append(Thread(target=crack, args=(ws[i*parts:(i+1)*parts], h, args.salt_len, HASHES[args.hash_type]['compare'])))
                ts[-1].start()
            ts.append(Thread(target=crack, args=(ws[(args.threads-1)*parts:], h, args.salt_len, HASHES[args.hash_type]['compare'])))
            ts[-1].start()

            for t in ts:
                t.join()

            if not cu_found:
                print(f'\r[-] Couldn\'t crack "{h}" ... no matches found!')

    print(f'[*] Finished after {time.time()-stime:.2f}s ... ')

if __name__ == '__main__':
    main()

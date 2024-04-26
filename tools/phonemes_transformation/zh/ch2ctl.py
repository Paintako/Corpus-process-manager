# !/usr/bin/env python
# _*_coding:utf-8_*_

import socket
import struct
import argparse
def askForService(chinese:str):
    '''
    將中文轉換成威晨制定的 CTL
    Param:
        chinese    :(str) Chinese characters will be converted to CTL.
    '''
    global HOST
    global PORT
    global TOKEN
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if len(chinese)==0:
            raise  ValueError ("Input text should not be empty!!!")
        sock.connect((HOST, PORT))
        msg = bytes(TOKEN + "@@@" + chinese, "utf-8")
        msg = struct.pack(">I", len(msg)) + msg
        sock.sendall(msg)
        result=""
        while True:
            l = sock.recv(8192)
            if not l:
                break
            result += l.decode(encoding="UTF-8")
    finally:
        sock.close()
    return result

global HOST
global PORT
global TOKEN
HOST, PORT = "140.116.245.157", 2005
TOKEN = "mi2stts"

if __name__=='__main__':
    data = '做教授是我一生的願望'
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', default=data, help='Text will be converted to CTL.')
    args = parser.parse_args()
    result = askForService(chinese=args.text)
    print(result)
    
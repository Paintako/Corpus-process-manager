# !/usr/bin/env python
# _*_coding:utf-8_*_

import socket
import struct
import argparse
def askForService(tai_luo:str):
    '''
    將台羅拼音轉換成威晨制定的CTL拼音
    Praams:
        tai_luo    :(str) Tai-luo will be converted to CTL.
    '''
    global HOST
    global PORT
    global TOKEN
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if len(tai_luo)==0:
            raise  ValueError ("Input text should not be empty!!!")
        sock.connect((HOST, PORT))
        msg = bytes(TOKEN + "@@@" + tai_luo, "utf-8")
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
HOST, PORT = "140.116.245.157", 2004
TOKEN = "mi2stts"

if __name__=='__main__':
    #初一 十五 攏 著 去 廟裡 拜拜
    # data = "tshe1 it4 tsap8 goo7 long2 tioh8 khi3 bio7 li2 pai3 pai3"
    #做 教授 是 我 一生 的 願望
    # data = "tso2 kau2 siu7 si3 gua1 it8 sing1 e7 guan3 bong7 。"
    
    data = "gua1 i1 king1 siunn3 bo5 khah1 ho2 e7 ke2 tshik8 ah4"
    data = "bu7 kik8 thian7 lun7 tshan7 enn1"
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', default=data, help='Text will be converted to CTL.')
    args = parser.parse_args()
    result = askForService(tai_luo=args.text)
    print(result)
    

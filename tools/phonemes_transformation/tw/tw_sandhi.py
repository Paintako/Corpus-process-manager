# !/usr/bin/env python
# _*_coding:utf-8_*_

import socket
import struct
import argparse
def askForService(tai_luo:str):
    '''
    將輸入的台羅拼音進行轉調
    若句子的台羅拼音不是從 ch2tl的api產生的
    麻煩請將獨立語意的詞彙用hyphen的符號(-)連接起來
    Params:
        tai_luo    :(str) Tai-luo will be sandhi.
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
HOST, PORT = "140.116.245.157", 2003
TOKEN = "mi2stts"

if __name__=='__main__':
    #初一 十五 攏 著 去 廟裡 拜拜
    # data = "tshe1 it4 tsap8 goo7 long2 tioh8 khi3 bio7 li2 pai3 pai3"
    #做 教授 是 我 一生 的 願望
    # data = "tso2 kau2 siu7 si3 gua1 it8 sing1 e7 guan3 bong7。"
    
    
    data = "i1 to7 na2 tshin1 tshiunn7 gua2 e5 tshin1 lang5 kang7 khuan2" # 伊 就 若親像 我 的 親人 仝款
    data = "khuann3 tioh8 lang5 ang1 a2 boo2 e5 kam2 tsing5 hiah4 ni7 a2 ho2"# 看著 人 翁仔某 的 感情 遐爾仔 好
    # data = "guan2 e5 tshu3 pinn1 long2 tsiann5 ho2 tau3 tin7" # 阮 的 厝邊 攏 誠 好 鬥陣
    # data = "tsit4 bue2 hi5 a2 khi2 ma2 u7 sann1 kin1" # 這 尾 魚仔 起碼 有 三 斤
    # data = "lok8 kang2 si7 tsit8 e5 tsin1 lau7 jiat8 e5 poo1 thau5" # 鹿港 是 一个 真 鬧熱 的 埠頭
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', default=data, help='Text will be sandhi.')
    args = parser.parse_args()
    result = askForService(tai_luo=args.text)
    print(result)
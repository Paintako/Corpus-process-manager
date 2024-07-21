# !/usr/bin/env python
# - - coding: utf-8 - -**

import socket
import struct
import argparse
import json

def askForService(text:str, accent:str, direction:str):
    '''
        將輸入的中文轉換成客語，或客語漢字轉為中文。\
        todo: 若輸入為客語數字調，則輸出亦為客語數字調，可將符號調客語轉成數字調客語。\
            Params:
            text:       (str) Text will be translate from Chinese to Hakka.
            accent: 客語腔調 (可用四縣(hedusi)或海陸(hedusai)腔)
            direction: 中翻客(ch2hk)或客翻中(hk2ch)
            2023/7/30: direction新增客語漢字到拼音(hkji2pin)
        output: dict形式
        out_dict["hakkaTL"] : 翻譯客語結果 (數字調)
        out_dict["interCH"] : 翻譯客語結果 (客語漢字)
        out_dict["hakkaTRN"] : 翻譯客語結果 (數字調) 轉成trn
        
    '''
    global HOST
    global PORT
    global TOKEN
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if len(text)==0:
            raise  ValueError ("Input text should not be empty!!!")
        sock.connect((HOST, PORT))
        msg = bytes(TOKEN + "@@@" + text + "@@@" + accent + "@@@" + direction, "utf-8")
        msg = struct.pack(">I", len(msg)) + msg
        sock.sendall(msg)
        result = ""
        while True:
            l = sock.recv(8192)
            if not l:
                break
            result += l.decode(encoding="UTF-8")
            TLresult = json.loads(result)
    except Exception as e:
        print(e)
        return {"hakkaTRN": "Exceptions occurs"}
            
    finally:
        sock.close()
        
    return TLresult

global HOST
global PORT
global TOKEN
HOST, PORT = "140.116.245.157", 30005
TOKEN = "mi2stts"

if __name__=='__main__':
    text = "我先去喝水"
    text2 = "景氣毋好，生理失敗背債个人，緊來緊多。"
    text3 = "豆腐蘸豆油食盡合味"
    text = '晚上去散步'
    text = '有兜人主張打胎合法 毋過有兜人極力反對'
    text = '人之初，性本善。' 
    accent = 'hedusi' # 四縣
    direction = "ch2hk"
    direction2 = "hk2ch"
    direction3 = "hkji2pin"
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', default=text, help='Text will be translate from Chinese to Hakka.')
    parser.add_argument('--accent', default=accent, help='Select your hakka accent (available in hedusi and hedusai).')
    parser.add_argument('--direction', default=direction3, help='TL direction includes ch2hk and hk2ch.')
    args = parser.parse_args()
    #args = parser.parse_args()
    
    result = askForService(text=args.text, accent=args.accent, direction = args.direction)
    print(result)
    if (result['hakkaTRN'] == 'Exceptions occurs'):
        print(f'Error: {result["hakkaTRN"]}')

    
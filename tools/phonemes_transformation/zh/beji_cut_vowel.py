from pypinyin import lazy_pinyin, pinyin, Style
import re
from typing import List
import os


punc = "：，；、。？！“”‘’':,;.?!"

def get_initials_finals(word: str) -> List[List[str]]:
    initials = []
    finals = []

    orig_initials = lazy_pinyin(
        word, neutral_tone_with_five=True, style=Style.INITIALS)
    orig_finals = lazy_pinyin(
        word, neutral_tone_with_five=True, style=Style.FINALS_TONE3)

    for c, v in zip(orig_initials, orig_finals):
        if re.match(r'i\d', v):
            if c in ['z', 'c', 's']:
                v = re.sub('i', 'ii', v)
            elif c in ['zh', 'ch', 'sh', 'r']:
                v = re.sub('i', 'iii', v)
        c = c.strip()
        v = v.strip()
        if c == v:
            if not len(c) == 1:
                for char in c:
                    initials.append(char)
                    finals.append(char)
                continue
            if c in punc and v in punc:            
                initials.append(c)
                finals.append(v)
                continue
        
        if c and c not in punc:
            initials.append(c)
            # initials.append(c + v[-1] +' ')
        else:
            initials.append(c)
        if v not in punc:
            finals.append(v)
        else:
            finals.append(v)

    return initials, finals

def to_half_width(text):
    converted_text = ''
    for char in text:
        ascii_code = ord(char)
        # 如果是全角字符
        if 65281 <= ascii_code <= 65374:
            converted_char = chr(ascii_code - 65248)  # 转换为半角
        else:
            converted_char = char
        converted_text += converted_char
    return converted_text

def cut_vowel(word: str) -> str:
    word = to_half_width(word.strip())
    word = word.replace("嗯","恩")
    initials, finals = get_initials_finals(word=word.strip())

    phones = ""
    for init, final in zip(initials, finals):
        if init == final:
            phones = f'{phones} {init} '
            continue
        else:      
            phones+=init
            phones = f'{phones}{final} '
    
    result = phones.strip().replace("  "," ").replace("   "," ")
    if not result.endswith('。') and not (result.endswith('!') or result.endswith('?')):
        result += ' 。'
    
    return result

if __name__ == "__main__":
    # d1 eng13 d1 eng13 , u12 b1 iao14 ai14 z1 ao14 k1 in14 j1 e15 l1 !1。
    result =  cut_vowel("第一次測試國語合成")
    print(result)


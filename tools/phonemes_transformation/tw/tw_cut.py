import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from typing import Dict, List, Tuple
from tw.ch2tl import askForService as ch2tl
from tw.tw_sandhi import askForService as tw_sandhi
from tw.tl2ctl import askForService as tl2ctl

class tw_frontend():
    def __init__(self):
        self.punc = "：，；。？！“”‘’':,;.?!"


    def _get_initials_finals(self, sentence: str) -> Tuple[List[List[str]], bool]:
        initials = []
        finals = [] 

        sentence = sentence.replace("0", "")

        orig_initials, orig_finals = self._cut_vowel(sentence)
        for c, v in zip(orig_initials, orig_finals):
            if c and c not in self.punc:
                initials.append(c+'0')
            else:
                initials.append(c)
            if v not in self.punc:
                finals.append(v[:-1]+'0'+v[-1])
            else:
                finals.append(v)
    
        return initials, finals, True

    def _g2p(self, sentences: List[str]) -> Tuple[List[List[str]], bool]:
        phones_list = []

        initials, finals, status = self._get_initials_finals(sentences)
        if status == False:
            return [], False
        for c, v in zip(initials, finals):
            if c and c not in self.punc:
                phones_list.append(c)
            if c and c in self.punc:
                phones_list.append('sil ')
            if v and v not in self.punc:
                phones_list.append(v)
        
        return phones_list, True
    
    def _cut_vowel(self, sentence):
        vowel_list = ['a', 'e', 'i', 'o', 'u']
        initials = []
        finals = []
        flag = True
        word_lst = sentence.split()
        for word in word_lst:
            if word in self.punc:
                initials.append(word)
                finals.append('')
                
            for i, char in enumerate(word):
                if char in vowel_list:
                    initials.append(word[: i].strip())
                    finals.append(word[i :].strip())
                    flag = False
                    break
            if flag:
                for i, char in enumerate(word):
                    if char in ['m', 'n']:
                        initials.append(word[: i].strip())
                        finals.append(word[i :].strip())
                        flag = False
                        break
            flag = True

        return initials, finals

    def get_phonemes(self, sentence: str) -> List[str]:
        phonemes, status = self._g2p(sentence)
        if status == False:
            return [], False
        print(phonemes)
        r = ''
        for p in phonemes:
            r = f'{r}{p} '
        
        return r, True
    
if __name__ == "__main__":
    tw = tw_frontend()
    while(1):
        print(f'Enter text: ')
        text = input()
        tl = ch2tl(text)
        tl = tl['tailuo']
        print(f'Taiwanese: {tl}')
        sandhi = tw_sandhi(tl)
        print(f'Sandhi: {sandhi}')
        ctl = tl2ctl(sandhi)
        print(f'CTL: {ctl}')
        result, status = tw.get_phonemes(ctl)
        print(f'Phonemes: {result}')
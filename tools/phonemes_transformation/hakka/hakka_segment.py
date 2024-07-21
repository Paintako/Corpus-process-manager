import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from typing import List, Tuple
import re
from hakka.ch2hak import askForService

class hakka_frontend():
    def __init__(self, language_id: int):
        self.punc = "：，；。？！“”‘’':,;.?!"
        self.language_id = language_id
        
    def _get_initials_finals(self, sentence: str) -> List[List[str]]:
        initials = []
        finals = []
        orig_initials, orig_finals = self._cut_vowel(sentence)
        
        # print(f'orig_initials = {orig_initials}, orig_finals = {orig_finals}')
        for c, v in zip(orig_initials, orig_finals):
            if c and c not in self.punc:
                initials.append(f'{c}{self.language_id} ')
            else:
                initials.append(c)
            if v != '':
                v = remove_hak(v)
                v = v.strip()
                v = f'{v[:-1]}{self.language_id}{v[-1]}'
            finals.append(f'{v} ')

        return initials, finals

    def _g2p(self,
             sentences: List[str]) -> List[List[str]]:
        phones_list = []

        initials, finals = self._get_initials_finals(sentences)

        for c, v in zip(initials, finals):
            if c and c not in self.punc:
                phones_list.append(c)
            if c and c in self.punc:
                phones_list.append('sil')
            if v and v not in self.punc:
                phones_list.append(v)
        
        return phones_list
    
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

    def get_phonemes(self,
                     sentence: str,
                     print_info: bool=True) -> List[List[str]]:
        if '-' in sentence:
            sentence = sentence.replace('-', '')    
        phonemes = self._g2p(sentence) 
        result = ''
        for p in phonemes:
            if not '-' in p:
                result += f'{p} '
            else:
                result += f'{p}'  
        return result.replace("  "," ").strip().replace("  "," ")

def remove_hak(input_content):
    result = ''
    for ph in input_content.strip().split():
        if '2' in ph and not re.search(r'22', ph):
            ph = re.sub(r'2', '', ph)
        else:
            ph = re.sub(r'2', '', ph, 1)
        result += ph + ' '
    return result


if __name__ == "__main__":
    ha_frontend = hakka_frontend(language_id=3)
    result = ha_frontend.get_phonemes("gni23 kim28 pu28 gnit28 kam21 kook28 gnioong21 pan28 ? tsrhi25 too21 toong28 thiam21 。")
    print(result)
    ha_frontend = hakka_frontend(language_id=2)
    result = ha_frontend.get_phonemes("gni23 kim28 pu28 gnit28 kam21 kook28 gnioong21 pan28 ? tsrhi25 too21 toong28 thiam21 。")
    print(result)
    # while(1):
    #     text = input("Please input a sentence: ")
    #     if text == 'exit':
    #         break
    #     hakka = askForService(text=text, accent='hedusi', direction='hkji2pin')
    #     print(f'Original: {text} -> Hakka: {hakka["hakkaTRN"][-2]}')
    #     ctl = ha_frontend.get_phonemes(hakka['hakkaTRN'][-2])
    #     print(f'After cut vowel -> {ctl}')
    #     print('------------------------------------')

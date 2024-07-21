import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from zh.ch2ctl import askForService as ch2ctl
from typing import List
import re
from opencc import OpenCC

class Frontend():
    def __init__(self,
                 g2p_model="mandarin",
                 phone_vocab_path=None,
                 ctlornot=False):

        self.punc = list("：，；。？！“”‘’':,;.?!")
        self.ctlornot = ctlornot
        self.g2p_model = g2p_model
        self.vocab_phones = {}
    
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
                    if char in ['m', 'n', 'y']:
                        initials.append(word[: i].strip())
                        finals.append(word[i :].strip())
                        flag = False
                        break
            flag = True

        return initials, finals
    
    def _get_initials_finals(self, sentence: str) -> List[List[str]]:
        initials = []
        finals = []
        if not self.ctlornot:
            ctl_text = ch2ctl(chinese=sentence)
        else:
            ctl_text = sentence
        orig_initials, orig_finals = self._cut_vowel(ctl_text)
        for c, v in zip(orig_initials, orig_finals):
            if c and c not in self.punc:
                initials.append(c + '4 ')
            if c and c in self.punc:
                initials.append(c)
                finals.append('')
            if v != '':
                finals.append(v[:-1]+'4'+v[-1])
        return initials, finals
        
    def _g2p(self,
             sentences: str,
             merge_sentences: bool=False) -> List[List[str]]:
        # seg = re.sub('[a-zA-Z]+', '', sentences)
        phones = []
        seg_cut = re.split(r'(\[laugh\])', sentences)
        phones_list = []
        for word in seg_cut:
            if word == '[laugh]':
                phones.append('[laugh]')
                phones_list.append(phones)
                continue
            if word == '':
                continue
            sub_initials, sub_finals = self._get_initials_finals(word)
            for c, v in zip(sub_initials, sub_finals):
                # NOTE: post process for pypinyin outputs
                # we discriminate i, ii and iii
                if c and c not in self.punc:
                    phones.append(c)
                if c and c in self.punc:
                    phones.append(c)
                if v and v not in self.punc:
                    phones.append(v)

            phones_list.append(phones)
        return phones_list


    def get_phonemes(self,
                     sentence: str,
                     merge_sentences: bool=False,
                     print_info: bool=True) -> List[List[str]]:
        if not self.ctlornot:
            cc = OpenCC('s2twp')
            sentence = cc.convert(sentence)
            sentence = sentence.replace("-", "")
            if ',' in sentence:
                sentence = sentence.replace(",", ", ")
        print(f'Processing: {sentence}')
        phonemes = self._g2p(
            sentence, merge_sentences=merge_sentences)
        phonemes = phonemes[0]
        result = ''
        for p in phonemes:
            if not p.endswith('-'):
                result += p + ' '
            else:
                result += p
        result = result.replace("  "," ").strip()
        result = result.replace(",", "sil ")
        return result
        

if __name__ == "__main__":
    zh = Frontend(ctlornot=True)
    i = "tsuoo4 tsciau4 sroou4 srir4 uoo3 i1 srong1 to0 yeen4 uang4"
    print(zh.get_phonemes(i))
    zh = Frontend(ctlornot=False)
    while(1):
        text = input("Enter a sentence: ")
        text = text.strip()
        print(zh.get_phonemes(text))
    # text = 'tscioou4 srir4 tsron1 to0 hon3 nan2 uan2 tschyeen2 pu4 toong3'
    # print(zh._get_initials_finals(text))

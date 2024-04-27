import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from .ch2ctl import askForService as ch2ctl
from typing import List
import re
from opencc import OpenCC

class Frontend():
    def __init__(self,
                 g2p_model="mandarin",
                 phone_vocab_path=None,
                 ctlornot=False):

        self.punc = "：，；。？！“”‘’':,;.?!"
        # self.punc = ""
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
                initials.append(c)
            else:
                initials.append(c)
            finals.append(v)

        return initials, finals
        
    def _g2p(self,
             sentences: List[str],
             merge_sentences: bool=False) -> List[List[str]]:
        # seg = re.sub('[a-zA-Z]+', '', sentences)
        phones = []
        seg_cut = [sentences]
        initials = []
        finals = []
        phones_list = []
        for word in seg_cut:
            sub_initials, sub_finals = self._get_initials_finals(word)    
            initials.append(sub_initials)
            finals.append(sub_finals)
            # assert len(sub_initials) == len(sub_finals) == len(word)
        initials = sum(initials, [])
        finals = sum(finals, [])
        for c, v in zip(initials, finals):
            # NOTE: post process for pypinyin outputs
            # we discriminate i, ii and iii
            if c and c not in self.punc:
                phones.append(c)
            if c and c in self.punc:
                phones.append('sil')
            if v and v not in self.punc:
                phones.append(v)
        print(phones)
        phones_list.append(phones)
        if merge_sentences:
            merge_list = sum(phones_list, [])
            # rm the last 'sil' to avoid the noise at the end
            # cause in the training data, no 'sil' in the end
            if merge_list[-1] == 'sil':
                merge_list = merge_list[:-1]
            phones_list = []
            phones_list.append(merge_list)
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
        phonemes = self._g2p(
            sentence, merge_sentences=merge_sentences)
        phonemes = phonemes[0]
        result = ''
        for p in phonemes:
            if not p[-1].isdigit() and p != 'sil':
                result += p + ''
            else:
                result += p + ' '
        result = result.replace("  "," ").strip()
        result = result.replace(",", "sil ")
        return result
        

if __name__ == "__main__":
    zh = Frontend(ctlornot=False)
    sentence = "你好，我是中文前端"
    phonemes = zh.get_phonemes(sentence)
    print(phonemes)
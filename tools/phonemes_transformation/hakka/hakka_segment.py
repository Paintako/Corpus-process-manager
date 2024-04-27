from typing import List, Tuple
import re

class hakka_frontend():
    def __init__(self):
        self.punc = "：，；。？！“”‘’':,;.?!"
        
    def _get_initials_finals(self, sentence: str) -> List[List[str]]:
        initials = []
        finals = []
        orig_initials, orig_finals = self._cut_vowel(sentence)
        
        # print(f'orig_initials = {orig_initials}, orig_finals = {orig_finals}')
        for c, v in zip(orig_initials, orig_finals):
            if c and c not in self.punc:
                initials.append(f'{c}')
            else:
                initials.append(c)
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
        r = ''
        for p in phonemes:
            if not p.endswith('-'):
                r = f'{r}{p}'
            else:
                r = f'{r} {p}'
        return remove_hak(r.replace("  "," ").strip().replace("  "," "))

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
    sentence = 'an22 tsoo22 。 sirt28 pau22 mang25 ? sirt28 pau22 le22 。 ng25 ngai25 ki25 。 ng25 koong22 ma22 ke23 ? ng25 he23 ma22 sa25 。 ngai25 he23 a21 lin25 。 an22 kiu22 moo25 khoon23 too22 。 ng25 hoo22 moo25 ?'
    ha_frontend = hakka_frontend()
    phonemes = ha_frontend.get_phonemes(sentence)
    
    print(phonemes)

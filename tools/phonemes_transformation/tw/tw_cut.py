from typing import Dict, List, Tuple

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
                initials.append(f'{c}')
            else:
                initials.append(c)
                continue

            finals.append(f'{v} ')
            
            
    
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
        r = ''
        for p in phonemes:
            if not p.endswith('-'):
                r = f'{r}{p}'
            else:
                r = f'{r} {p}'
        r = r.strip()
        
        return r, True
    
if __name__ == "__main__":
    tw = tw_frontend()
    text = [
        "manni2 ti3 au3 piah4 koong1 dlang5 e7 phainn1 ue7",
        "gua1 i1 kieng1 sciunn3 bo7 kh ah1 h o2 e7 ke3 ti3 ah3",
        "tscit8 kieng7 tiam2 sci3 sng3 dlang7 thau5 sciu7 tscinn5 e7",
        "dli1 e7 pak8 too2 nann1 e3 hia2 ninn7 tua3 khieen1",
        "gua1 tsu3 thau5 tioh8 bo7 scioong7 scin3 i7 e7 ue7"

    ]
    for t in text:
        result = tw.get_phonemes(t)
        print(result[0])
    print(tw.get_phonemes("tschieng7 san7 kang2 , sua7 tsciu1"))

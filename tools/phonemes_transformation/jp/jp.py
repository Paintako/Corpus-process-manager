import MeCab
import pykakasi
import string
import re

# mc = MeCab.Tagger("-Owakati")
kks = pykakasi.kakasi()


ascii_punctuation = string.punctuation
ascii_punctuation += '、。！？「」『』・…‥―〈〉《》〔〕【】〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟‧﹏.'

class jp2roman:
    def __init__(self) -> None:
        pass

    def get_phoememe(self, text):
        text = self._fullwidth_to_halfwidth(text) # convert fullwidth to halfwidth
        rst, katana = self._jp2roman(text) # convert japanese to romaji
        text_sub = re.sub(f'[{re.escape(string.punctuation)}]', ' sil', rst)

        final = self._add_langID(text_sub)
        return final, katana

    def _jp2roman(self, text: str) -> str:
        # convert text to hiragana
        result = kks.convert(text)
        hiragana = ''.join([item['hira'] for item in result])
        
        # convert hiragana to katakana
        katakana = kks.convert(hiragana)
        katakana = ''.join([item['kana'] for item in katakana])
        
        # convert katakana to romaji (phonemes)
        result = ''
        for char in katakana:
            romaji = kks.convert(char)
            result += romaji[0]['hepburn'] + ' '
                
        if not len(result.split()) == len(katakana):
            raise ValueError('The length of phonemes is not equal to the length of katakana')
        return result, katakana

    def _fullwidth_to_halfwidth(self, input_str):
        result_str = ""
        
        for char in input_str:
            # 如果字符是全角字符，则进行转换
            if ord(char) >= 0xFF01 and ord(char) <= 0xFF5E:
                result_str += chr(ord(char) - 0xFEE0)
            else:
                result_str += char
        
        return result_str


    def _add_langID(self, text: str) -> str:
        result = ''
        for seg in text.split():
            if 'sil' == seg:
                result += seg + ' '
                continue
            seg = seg.strip().lower() + '5'
            result += seg + ' '
        return result

if __name__ == "__main__":
    text = "田中さんにもらったお菓子を食べました。"
    jp2roman = jp2roman()
    while(1):
        print(f'Enter word:')
        word = input()
        result, katana = jp2roman.get_phoememe(word)
        print(katana)
        print(result)

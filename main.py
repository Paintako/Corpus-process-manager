import os
import tqdm
import random
import re
import librosa
import soundfile as sf
import unicodedata
import json

from tools.phonemes_transformation.tw import tw_cut
from tools.phonemes_transformation.hakka import hakka_segment
from tools.phonemes_transformation.en import en
from tools.phonemes_transformation.zh import tradi_cut_vowel, beji_cut_vowel
from tools.phonemes_transformation.indo import indo_ipa


# from tools.asr.whisper_punctuator import punctuator
# import whisper

class audioProcess:
    def __init__(self, samplerate):
        self.samplerate = samplerate
    
    def resample(self, wav_path):
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f'File not found: {wav_path}, please check the path.')
        # 讀取音頻文件
        y, sr = librosa.load(wav_path)

        # 重採樣到 22kHz，設置位深為16位，並轉換為單通道
        resampe_y = librosa.resample(y=y, orig_sr=sr, target_sr=self.samplerate)
        yt, index = librosa.effects.trim(resampe_y)
        sf.write(wav_path, yt, self.samplerate, 'PCM_16')

class textProcess:
    def __init__(self):
        self.languageMap = {
            'tw' : 0,
            'beji' : 1,
            'hakka' : 2,
            'trandition_zh' : 4,
        }

        # self.whisper_model = whisper.load_model("base")
        # self.punctuator = punctuator.Punctuator(language="zh", punctuations=",.?", initial_prompt="Hello, everyone.")

        self.beji_cut = beji_cut_vowel.cut_vowel
        self.tradi_cut = tradi_cut_vowel.Frontend(ctlornot=True)
        self.tradi_cut_noneCTL = tradi_cut_vowel.Frontend(ctlornot=False)
        self.hailu_hakka_frontend = hakka_segment.hakka_frontend(language_id=3) # 海陸腔
        self.sixsian_hakka_frontend = hakka_segment.hakka_frontend(language_id=2) # 四縣腔
        self.tw_cut = tw_cut.tw_frontend()
        self.en_cut = en.english_cleaners2
        self.id_cut = indo_ipa.g2p

    def remove_languageId(self, input_content, language):
        result = ''
        languageId = self.languageMap[language]
        for ph in input_content.strip().split():
            if str(languageId) in ph and not re.search(f'{languageId}{languageId}', ph):
                ph = re.sub(f'{languageId}', '', ph)
            else:
                ph = re.sub(f'{languageId}', '', ph, 1)
            result += ph + ' '
        return result

    def contains_only_chinese_and_numbers(self, text):
        # 使用正则表达式查找字符串中的所有数字部分
        numbers = re.findall(r'\d+', text)
        alpha = re.findall(r'[a-zA-Z]', text)
        if numbers or alpha:
            # 如果字符串中有数字部分，说明不是全中文字符串
            return False
        return True 
    
    def to_half_width(self, text):
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

    
    def is_only_punctuation(self, text):
        # 使用正則表達式檢查字串是否只包含標點符號
        return bool(re.fullmatch(r'[^\w\s]+', text))

    def content_punctuation(self, text):
        texted_process = self.to_half_width(text)
        texted_process = re.sub(r'(\W)\1+', r'\1 ', texted_process)
        if texted_process.endswith('…'):
            texted_process = texted_process[:-1] + '。'
        texted_process = texted_process.replace('\\n', '。')

        if '+' in texted_process or '-' in texted_process or '・' in texted_process or '·' in texted_process:
            return text, None

        if not self.contains_only_chinese_and_numbers(texted_process):
            return text, None

        if '↑' in texted_process or '↓' in texted_process:
            return text, None

        if '——' in texted_process:
            return text, None
        
        texted_process = texted_process.replace('…', '')
        texted_process = texted_process.replace('」', '').replace('「', '').replace('『', '').replace('』', '').replace('《', '').replace('》', '').replace("(","").replace(")","").replace("[","").replace("]","")
        
        if '\\' in texted_process or '_' in texted_process or '^' in texted_process or '~' in texted_process:
            return text, None
        
        
        texted_process = texted_process.replace('...', '')

        texted_process = texted_process.replace("!!", "!")
        texted_process = texted_process.replace("??", "?")

        if '???' == texted_process:
            return text, None

        if texted_process.startswith(','):
            texted_process = texted_process[1:]
        
        if len(texted_process) < 3:
            return text, None
        texted_process = texted_process.strip()
        if not texted_process.endswith('。') and not (texted_process.endswith('!') or texted_process.endswith('?')):
            texted_process += '。'
        
        if self.is_only_punctuation(texted_process):
            return text, None

        return text, texted_process


    def fullwidth_to_halfwidth(self, text):
        result = ""
        for char in text:
            # Check if the character is a fullwidth character
            if unicodedata.east_asian_width(char) == 'F':
                # Convert fullwidth to halfwidth
                result += chr(ord(char) - 65248)
            else:
                result += char
        return result

    def remove_punctuation_except_comma(self, text):
        # 這個正則表達式會匹配除了逗號外的所有標點符號
        pattern = re.compile(r'[^\w\s,，]')
        return pattern.sub('', text)

    def contains_english(self, input_str):
        pattern = re.compile(r'[a-zA-Z]')
        return bool(pattern.search(input_str))

    def check_language(self, input_str):
        input_str = self.fullwidth_to_halfwidth(input_str.replace(" ","").replace("　",""))
        input_str = self.remove_punctuation_except_comma(input_str)
        return not self.contains_english(input_str)

    def contains_chinese(self, text):
        # 使用正則表達式檢查是否包含中文字符
        pattern = re.compile(r'^[\u4e00-\u9fa5]+$')
        return bool(pattern.match(text))

    def has_digits(self, input_string):
        pattern = r'\d'  # 正則表達式匹配任何數字
        return bool(re.search(pattern, input_string))

class DatasetProcesser:
    def __init__(self, dataset_suffix):
        self.dataset_suffix = dataset_suffix
        self.audioProcss = audioProcess(samplerate=44100)
        self.textProcess = textProcess()
        self.cwd = os.getcwd()
        # os.system(f'rm {self.cwd}/{dataset_suffix}/*.txt')
        

    def get_last_speaker_id(self, filepath):
        # Read the last line of the file
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    last_speaker_id = int(last_line.split('|')[1])
                    return last_speaker_id + 1
        # If the file is empty or doesn't exist, start from 0
        except:
            return 0


    def process_zh(self, path, label, english_or_not):
        os.chdir(os.path.join(self.cwd,path))
        cwd = os.getcwd()
        # Get the starting speaker id from the last line of the val file
        dataset_suffix = self.dataset_suffix

        for folder in os.listdir():
            starting_speaker_id = self.get_last_speaker_id(
                f'{self.cwd}/{dataset_suffix}/{label}_test.txt')
            if not os.path.isdir(os.path.join(cwd, folder)):
                continue

            input_path = f'{cwd}/{folder}'
            folder_files = os.listdir(folder)
            wav_files = [file for file in folder_files if file.endswith('.wav')]

            if len(wav_files) < 2:
                continue

            if 'opendataset' in path:
                traing_len = min(50, len(wav_files))
                test_len = min(5, len(wav_files) - traing_len)
            elif len(wav_files) == 3:
                traing_len = 2
                test_len = 1
            else:
                traing_len = int(len(wav_files)*0.95)
                test_len = int(traing_len * 0.05)
            random.shuffle(wav_files)

            # split train and test set
            train_files = wav_files[:traing_len]
            test_files = wav_files[traing_len:traing_len + test_len]

            print(f'Processing: {folder}')
            print(f'train_files: {len(train_files)}, test_files: {len(test_files)}')

            if len(train_files) == 2:
                train_files*=200

            if len(test_files) == 0:
                continue
    
            # write train and test set
            run_list = ['train', 'test']
            for run in run_list:
                with open(f'{self.cwd}/{dataset_suffix}/{label}_{run}.txt', 'a') as f:
                    files = train_files if run == 'train' else test_files
                    for file in files:
                        if 'trandition_zh' in input_path:
                            txt_file_path = f'{folder}/{file.replace(".wav", ".json")}'
                            if not os.path.exists(txt_file_path):
                                with open(txt_file_path.replace(".json", ".txt"), 'r') as txt:
                                    txt_content = txt.read()
                                    txt_content = txt_content.strip()
                                    # if not self.textProcess.check_language(input_str=txt_content):
                                    #     continue
                                    txt_content = self.textProcess.tradi_cut_noneCTL.get_phonemes(txt_content)
                                    f.write(
                                        f'{cwd}/{folder}/{file}|{starting_speaker_id}|TZH|{txt_content}\n'
                                    )
                            else:       
                                with open(txt_file_path, 'r') as txt:
                                    try:
                                        txt_content = json.load(txt)['ctl_text']
                                    except:
                                        continue
                                    txt_content = self.textProcess.tradi_cut.get_phonemes(txt_content)
                                    f.write(
                                        f'{cwd}/{folder}/{file}|{starting_speaker_id}|TZH|{txt_content}\n'
                                    )
                        else:
                            txt_file_path = f'{folder}/{file.replace(".wav", ".txt")}'
                            if not os.path.exists(txt_file_path):
                                continue
                            with open(txt_file_path, 'r') as txt:
                                txt_content = txt.read()
                                txt_content = txt_content.strip()
                                if 'genshin' in path or 'esd' in path:
                                    if not self.textProcess.contains_only_chinese_and_numbers(txt_content):
                                        print(f'{txt_content} has number')
                                        continue
                                    text, txt_content = self.textProcess.content_punctuation(text=txt_content)
                                    if not txt_content:
                                        continue    
                                        
                                    wav_file = f'{cwd}/{folder}/{file}'
                                
                                    txt_content = txt_content.replace("(","").replace(")","")
                                    txt_content = txt_content.replace("[","").replace("]","")
                                else:
                                    if not self.textProcess.check_language(input_str=txt_content):
                                        print(f'not chinese: {txt_content}, {cwd}/{folder}/{file}')
                                        continue
                                    if not self.textProcess.contains_chinese(text=txt_content):
                                        print(f'not chinese: {txt_content}, {cwd}/{folder}/{file}')
                                        continue
                                result = self.textProcess.beji_cut(word=txt_content)
                                f.write(
                                    f'{cwd}/{folder}/{file}|{starting_speaker_id}|ZH|{result}\n'
                                )
                                
                print(f'writing {run} done, {folder}')
            with open(f'{self.cwd}/{dataset_suffix}/{label}_id.txt', 'a') as f:
                f.write(f'{starting_speaker_id}|{folder}\n')


    def process(self, path, label, english_or_not, hakka_or_not):
        os.chdir(os.path.join(self.cwd,path))
        cwd = os.getcwd()
        print(f'processing: {path}')
        # Get the starting speaker id from the last line of the val file
        dataset_suffix = self.dataset_suffix
        print(os.listdir())
        for folder in os.listdir():
            starting_speaker_id = self.get_last_speaker_id(
                f'{self.cwd}/{dataset_suffix}/{label}_test.txt')
            if not os.path.isdir(os.path.join(cwd, folder)):
                continue
            folder_files = os.listdir(folder)
            input_path = f'{cwd}/{folder}'
            wav_files = [file for file in folder_files if file.endswith('.wav')]
            for wav in wav_files:
                if not os.path.exists(f'{input_path}/{wav.replace(".wav", ".txt")}'):
                    wav_files.remove(wav)
                    continue
        
            random.shuffle(wav_files)

            if len(wav_files) < 5:
                continue

            wav_len = len(wav_files)
            traing_len = int(wav_len * 0.95)
            test_len = wav_len - traing_len

            if test_len == 0:
                test_len = 1
                traing_len -= 1

            # split train and test set
            train_files = wav_files[:traing_len]
            test_files = wav_files[traing_len:]
            
            # write train and test set
            run_list = ['train', 'test']
            for run in run_list:
                files = train_files if run == 'train' else test_files
                for file in files:
                    with open(f'{self.cwd}/{dataset_suffix}/{label}_{run}.txt', 'a') as f:
                        if '/tw/' in path or '/en/' in path or '/indonesian/' in path:
                            txt_file_path = f'{input_path}/{file.replace(".wav", ".json")}'
                        elif '/jp/' in path:
                            txt_file_path = f'{input_path}/{file}.json'
                        else:
                            txt_file_path = f'{input_path}/{file.replace(".wav", ".txt")}'
                        if not os.path.exists(txt_file_path):
                            # If .txt file doesn't exist, try opening .normalized.txt
                            txt_file_path = f'{input_path}/{file.replace(".wav", ".normalized.txt")}'
                            if not os.path.exists(txt_file_path):
                                continue
                        if not english_or_not:
                            with open(txt_file_path, 'r') as txt:
                                if hakka_or_not:
                                    txt_content = txt.readlines()[-1].strip().lower()
                                    if 'hailu' in path:
                                        txt_content = self.textProcess.hailu_hakka_frontend.get_phonemes(txt_content)
                                    else:
                                        txt_content = self.textProcess.sixsian_hakka_frontend.get_phonemes(txt_content)
                                    f.write(
                                        f'{cwd}/{folder}/{file}|{starting_speaker_id}|HAK|{txt_content}\n'
                                    )
                                else:
                                    if '/tw/' in path:
                                        txt_content = json.load(txt)['tailou']
                                        txt_content, status = self.textProcess.tw_cut.get_phonemes(txt_content)
                                        if not status:
                                            continue
                                        f.write(
                                            f'{cwd}/{folder}/{file}|{starting_speaker_id}|TW|{txt_content}\n'
                                        )
                                    
                                    if '/double' in path:
                                        try:
                                            txt_content = txt.readlines()[0].strip().lower()
                                        except:
                                            continue
                                        f.write(
                                            f'{cwd}/{folder}/{file}|{starting_speaker_id}|DB|{txt_content}\n'
                                        )

                                    if '/indonesian' in path:
                                        # txt_content = txt.readlines()[0].strip().lower()
                                        # txt_content = self.textProcess.id_cut(txt_content)
                                        txt_content = json.load(txt)['g2p'].lower()
                                        if self.textProcess.has_digits(input_string=txt_content):
                                            continue
                                        f.write(
                                            f'{cwd}/{folder}/{file}|{starting_speaker_id}|ID|{txt_content}\n'
                                        )
                                    
                                    if '/jp/' in path:
                                        txt_content = json.load(txt)['phonemes'].lower()
                                        f.write(
                                            f'{cwd}/{folder}/{file}|{starting_speaker_id}|JP|{txt_content}\n'
                                        )

                        else:
                            with open(txt_file_path, 'r') as txt:
                                txt_content = json.load(txt)['phonemes'].lower()
                            with open(txt_file_path, 'r') as txt:
                                f.write(
                                    f'{cwd}/{folder}/{file}|{starting_speaker_id}|EN|{txt_content}\n'
                                )
            with open(f'{self.cwd}/{dataset_suffix}/{label}_id.txt', 'a') as f:
                f.write(f'{starting_speaker_id}|{folder}\n')

if __name__ == "__main__":
    # path, label = parse_paths()
    # process(path, label)
    corpus_list = [
        # f'corpus/zh/corpus/other',
        # f'corpus/zh/corpus/other/for_student',
        f'corpus/hakka/corpus/nycu/Hakka_TTS_four_couties',
        f'corpus/hakka/corpus/nycu/Hakka_TTS_hailu',
        # f'corpus/en/corpus/Lirbri',    
        # f'corpus/indonesian/corpus',
        # f'corpus/zh/corpus/aidata',
        # f'corpus/zh/corpus/MAGIC',
        f'corpus/tw/corpus/neutral',
        # f'corpus/zh/corpus/azure',
        # f'corpus/zh/corpus/opendataset/THCHS',
        f'corpus/zh/corpus/opendataset/MAGIC',
        # f'corpus/en/corpus/vctk/corpus',
        # f'corpus/en/corpus/other/t1_excited',
        # f'corpus/indonesian/corpus/azure',
        f'corpus/trandition_zh/azure_synthesis',
        f'corpus/trandition_zh/dinter/',
        # f'corpus/genshin/classified',
    ]

    dataset_suffix = "dataset"

    dp = DatasetProcesser(dataset_suffix=dataset_suffix)

    for corpus_path in corpus_list:
        if not ('Lirbri' in corpus_path or 'vctk' in corpus_path):
            if 'zh' in corpus_path:
                dp.process_zh(path=f'{corpus_path}',
                           label="mixed_5",
                           english_or_not=False)
            if 'hakka' in corpus_path:
                dp.process(path=f'{corpus_path}',
                        label="mixed_5",
                        english_or_not=False,
                        hakka_or_not=True)
            if 'tw' in corpus_path:
                dp.process(path=f'{corpus_path}',
                        label="mixed_5",
                        english_or_not=False,
                        hakka_or_not=False)
            if 'double' in corpus_path:
                dp.process(path=f'{corpus_path}',
                        label="mixed_5",
                        english_or_not=False,
                        hakka_or_not=False)
            if 'indonesian' in corpus_path:
                dp.process(path=f'{corpus_path}',
                        label="mixed_5",
                        english_or_not=False,
                        hakka_or_not=False)
            if 'genshin' in corpus_path:
                dp.process_zh(path=f'{corpus_path}',
                    label="mixed_5",
                    english_or_not=False)
            if '/jp/' in corpus_path:
                dp.process(path=f'{corpus_path}',
                        label="mixed_5",
                        english_or_not=False,
                        hakka_or_not=False)
        else:
            dp.process(path=f'{corpus_path}',
                    label="mixed_5",
                    english_or_not=True,
                    hakka_or_not=False)

    # process_gen('corpus/zh/corpus/gen',label="mixed_5")

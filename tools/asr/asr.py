from whisper_punctuator import punctuator
import whisper
import os
import shutil
import tqdm
from cn2an_test import text_normalize
from opencc import OpenCC
import re

def contains_non_chinese_characters(s):
    # 匹配任何非中文字符（包括英文字母）
    english_letter_pattern = re.compile(r'[A-Za-z]')
    
    # 搜索字符串中是否包含英文字母
    match = english_letter_pattern.search(s)
    
    return match is not None


def remove_punctuation(text):
    # 使用正則表達式匹配所有標點符號
    return re.sub(r'[^\w\s]', '', text)


def asr(wav_file: os.path.abspath, model) -> str:
    audio = whisper.load_audio(wav_file)
    audio = whisper.pad_or_trim(audio)

    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    _, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)
    print(f"Detected language: {language}")

    options = whisper.DecodingOptions(language='zh')
    result = whisper.decode(model, mel, options)
    return result.text

if __name__ == "__main__":
    base_dir = "/home/p76111652/Linux_DATA/synthesis/corpus/22k/tools/asr/vocal_output.wav_10"
    bad_dir = "./bad"
    if not os.path.exists(bad_dir):
        os.mkdir(bad_dir)
    model = whisper.load_model("tiny")
    for f in tqdm.tqdm(os.listdir(base_dir)):
        if f.endswith('.wav'):
            wav_file = os.path.join(base_dir, f)
            text = asr(wav_file, model)
            print(text)
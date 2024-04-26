import librosa
import soundfile as sf
import wave
import tqdm
import os
# from tools.style_gen import style_gen

class trimProcesser:
    def __init__(self):
        self.samplerate = 22050

    def get_sample_rate(self, file_path):
        with wave.open(file_path, 'r') as wf:
            samplerate = wf.getframerate()
        return samplerate

    def read_duraion(self, file_path):
        y, sr = librosa.load(file_path, sr=self.samplerate)
        duration = librosa.get_duration(y=y, sr=sr)
        return duration

    def chsr(self, wave_path, origin_sr, target_sr):
        # 讀取音頻文件
        y, sr = librosa.load(wave_path, origin_sr)
        resampe_y = librosa.resample(y=y, orig_sr=sr, target_sr=target_sr)
        yt, _ = librosa.effects.trim(resampe_y)
        sf.write(wave_path, yt, target_sr, 'PCM_16')
        print(f'{wave_path} has been resampled to {target_sr}Hz')

    def trim_bad(self):
        file_list = [
            'too_short.txt',
            'too_long.txt',
            'corrupted.txt'
        ]

        bad_list = []
        for file in file_list:
            if not os.path.exists(f'./dataset/{file}'):
                continue
            with open(f'./dataset/{file}', 'r', encoding='utf8') as f:
                lines = f.readlines()
                for line in lines:
                    bad_list.append(line.strip())

        bad_list = list(set(bad_list))

        with open(f'./dataset/mixed_5_train.txt', 'r' , encoding='utf8') as f:
            lines_old = f.readlines()
            lines = lines_old.copy()  # 使用copy()创建一个新的列表
            lines_to_remove = []  # 创建一个存储要删除行的列表
            for line in lines:
                file = line.split('|')[0]
                if file in bad_list:
                    lines_to_remove.append(line)  # 将要删除的行添加到lines_to_remove列表中
                
                if '�' in line:
                    lines_to_remove.append(line)
            
            for line in lines_to_remove:
                if not line in lines:
                    continue
                lines.remove(line)  # 从lines中删除要删除的行
            
            print(len(lines_old))
            print(len(lines))

        for line in lines:
            with open(f'./dataset/mixed_5_train_new.txt', 'a', encoding='utf8') as f:
                f.write(line)


        with open(f'./dataset/mixed_5_test.txt', 'r' , encoding='utf8') as f:
            lines_old = f.readlines()
            lines = lines_old.copy()  # 使用copy()创建一个新的列表
            lines_to_remove = []  # 创建一个存储要删除行的列表
            for line in lines:
                file = line.split('|')[0]
                if file in bad_list:
                    lines_to_remove.append(line)  # 将要删除的行添加到lines_to_remove列表中
                
                if '�' in line:
                    lines_to_remove.append(line)
            
            for line in lines_to_remove:
                if not line in lines:
                    continue
                lines.remove(line)  # 从lines中删除要删除的行
            
        for line in lines:
            with open(f'./dataset/mixed_5_test_new.txt', 'a', encoding='utf8') as f:
                f.write(line)


    def read_file(self):
        dataset_files = [
            'mixed_5_train.txt',
            'mixed_5_test.txt'
        ]
        for file in dataset_files:
            with open(f'./dataset/{file}', 'r', encoding='utf8') as f:
                lines = f.readlines()
                for line in tqdm.tqdm(lines):
                    file = line.split('|')[0]
                    if not os.path.exists(file):
                        with open(f'./dataset/corrupted.txt', 'a', encoding='utf8') as f:
                            f.write(file + '\n')
                        continue
                    sr = self.get_sample_rate(file)
                    if int(sr) != self.samplerate:
                        self.chsr(file, sr, self.samplerate)
                    duration = self.read_duraion(file)
                    if duration < 0.2:
                        with open(f'./dataset/too_short.txt', 'a', encoding='utf8') as f:
                            f.write(file + '\n')
                    if duration > 15:
                        with open(f'./dataset/too_long.txt', 'a', encoding='utf8') as f:
                            f.write(file + '\n')

if __name__ == "__main__":
    tp = trimProcesser()
    tp.read_file()
    tp.trim_bad()
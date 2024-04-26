import librosa
import numpy as np
import soundfile as sf


class AudioAugmentation:
    def __init__(self, wav_path):
        self.y, self.sr = librosa.load(wav_path, sr=None)

    def time_stretch(self, rate):
        y_stretch = librosa.effects.time_stretch(self.y, rate)
        return y_stretch

    def pitch_shift(self, n_steps):
        y_pitch_shift = librosa.effects.pitch_shift(self.y, self.sr, n_steps)
        return y_pitch_shift

    def add_gaussian_noise(self, amplitude):
        y_noise = self.y + amplitude * np.random.normal(size=self.y.shape)
        return y_noise

    def permutate_files(self, path, path_2):
        y1, sr = librosa.load(path, sr=None)
        y2, _ = librosa.load(path_2, sr=None)

        # trim silence
        y1_trimmed, _ = librosa.effects.trim(y1)
        y2_trimmed, _ = librosa.effects.trim(y2)

        with open(f'{path.replace(".wav", ".txt")}', 'r') as f:
            text1 = f.readlines()[0].strip()
        
        with open(f'{path_2.replace(".wav", ".txt")}', 'r') as f:
            text2 = f.readlines()[0].strip()
        
        # make silence between two audio
        silence = np.zeros(sr) * 0.1
        y = np.concatenate((y1_trimmed, silence, y2_trimmed))
        text = text1 + ' , ' + text2
        return y, sr, text


    def save_wav(self, y, sr, output_path):
        sf.write(output_path, y, sr)
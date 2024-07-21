from aug import AudioAugmentation
import os
from itertools import permutations
from threading import Thread
from tqdm import tqdm

def shift(input_path):
    wav_files = [f for f in os.listdir(input_path) if f.endswith('.wav')]
    strech_rate = [0.8, 1.2]
    for wav in wav_files:
        # perform time_strech
        aug = AudioAugmentation(wav_path = os.path.join(input_path, wav))
        strech_rate = 0.8
        y_stretch = aug.time_stretch(rate=strech_rate)
        sr = aug.sr
        output_path = os.path.join(input_path, f"{wav.split('.')[0]}_{strech_rate}.wav")
        aug.save_wav(y_stretch, sr, output_path)

        # write text file too
        with open(os.path.join(input_path, wav.replace('.wav', '.txt')), 'r') as f:
            text = f.read()
        
        with open(os.path.join(input_path, f"{wav.split('.')[0]}_{strech_rate}.txt"), 'w') as f:
            f.write(text)

def process_files(input_path, perm):
    aug = AudioAugmentation(wav_path=os.path.join(input_path, perm[0]))
    y, sr, text = aug.permutate_files(os.path.join(input_path, perm[0]), os.path.join(input_path, perm[1]))
    output_path = os.path.join(input_path, f"{perm[0].split('.')[0]}_{perm[1].split('.')[0]}.wav")
    aug.save_wav(y, sr, output_path)
    with open(os.path.join(input_path, f"{perm[0].split('.')[0]}_{perm[1].split('.')[0]}.txt"), 'w') as f:
        f.write(text)

def main(input_path):
    wav_files = [f for f in os.listdir(input_path) if f.endswith('.wav')]
    permutations_list = list(permutations(wav_files, 2))
    # permutate files
    threads = []
    with tqdm(total=len(permutations_list), desc="Processing Files") as pbar:
        for perm in permutations_list:
            t = Thread(target=process_files, args=(input_path, perm))
            t.start()
            threads.append(t)
            pbar.update(1)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()

if __name__ == "__main__":
    input_path = "/home/p76111652/Linux_DATA/synthesis/corpus/22k/aangry/very_angry"
    main(input_path)
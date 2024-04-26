import warnings
import numpy as np
import torch
warnings.filterwarnings("ignore", category=UserWarning)
from pyannote.audio import Inference, Model
import os

import tqdm

model = Model.from_pretrained("pyannote/wespeaker-voxceleb-resnet34-LM")
inference = Inference(model, window="whole")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
inference.to(device)


def get_style_vector(wav_path):
    return inference(wav_path)


def save_style_vector(wav_path):
    if os.path.exists(f"{wav_path}.npy"):
        return
    try:
        style_vec = get_style_vector(wav_path)
    except Exception as e:
        raise e
    
    if np.isnan(style_vec).any():
        raise f"NaN value found in style vector: {wav_path}"

    np.save(f"{wav_path}.npy", style_vec)  # `test.wav` -> `test.wav.npy`


def process_line(line):
    try:
        save_style_vector(line)
        return line, None
    except Exception as e:
        return line, e

def save_average_style_vector(style_vectors, filename="style_vectors.npy"):
    average_vector = np.mean(style_vectors, axis=0)
    np.save(filename, average_vector)


def run(path):
    with open(path, "r") as f:
        lines = f.readlines()
    
    lines = [line.split("|")[0] for line in lines if line.strip()]
    style_vectors = []
    for line in tqdm.tqdm(lines):
        line, error = process_line(line)
        if error:
            print(f"Error processing {line}: {error}")
        else:
            style_vectors.append(np.load(f"{line.split('|')[0]}.npy"))
    save_average_style_vector(style_vectors)

if __name__ == "__main__":
    train_path = f'/home/p76111652/Linux_DATA/synthesis/corpus/22k/dataset/mixed_5_train.txt'
    val_path = f'/home/p76111652/Linux_DATA/synthesis/corpus/22k/dataset/mixed_5_val.txt'

    run(train_path)
    run(val_path)
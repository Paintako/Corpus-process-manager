import argparse
from concurrent.futures import ThreadPoolExecutor
import warnings

import numpy as np
import torch
from tqdm import tqdm

warnings.filterwarnings("ignore", category=UserWarning)
from pyannote.audio import Inference, Model

model = Model.from_pretrained("pyannote/wespeaker-voxceleb-resnet34-LM")
inference = Inference(model, window="whole")

def get_style_vector(wav_path):
    return inference(wav_path)


def save_style_vector(wav_path, name):
    try:
        style_vec = get_style_vector(wav_path)
    except Exception as e:
        print("\n")
        raise
    
    if np.isnan(style_vec).any():
        print("\n")
        raise (f'NaN value found in style vector: {wav_path}')
        
    np.save(f"{name}.npy", style_vec)  # `test.wav` -> `test.wav.npy`


def process_line(wav_path, name):
    try:
        save_style_vector(wav_path)
        return name, None
    except Exception as e:
        return name, "nan_error"


def save_average_style_vector(style_vectors, filename="style_vectors.npy"):
    average_vector = np.mean(style_vectors, axis=0)
    np.save(filename, average_vector)


if __name__ == "__main__":
    file = '/home/p76111652/Linux_DATA/synthesis/corpus/16k/dataset/mixed_5_val.txt'
    training_lines = []

    with open(file, encoding="utf-8") as f:
        training_lines.extend(f.readlines())
    
    for f in training_lines:
        path = f.split('|')[0]
        name = path.split('/')[-1].split('.')[0]

        save_style_vector(path, name)

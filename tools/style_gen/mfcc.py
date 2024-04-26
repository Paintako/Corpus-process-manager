import librosa
import numpy as np

import os
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def extract_mfcc(file_path, max_length):
    # 讀取音訊文件
    audio, sr = librosa.load(file_path, sr=None)
    
    # 提取 MFCC 特徵
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    print(f'{file_path}, {mfccs.shape}')
    
    # 將 MFCC 特徵向量填充或截斷為相同長度
    if mfccs.shape[1] < max_length:
        # 填充
        mfccs = np.pad(mfccs, ((0, 0), (0, max_length - mfccs.shape[1])), mode='constant')
    elif mfccs.shape[1] > max_length:
        # 截斷
        mfccs = mfccs[:, :max_length]
    
    return mfccs

# 設定最大長度
max_length = 300  # 例如，假設最大長度為 300

wav_dir = './F64/wavs/'

# 建立一個空列表，用於存儲每個MFCC特徵向量和檔案名
mfccs_list = []
file_names = []
for file in os.listdir(wav_dir):
    if file.endswith(".wav"):
        file_path = os.path.join(wav_dir, file)
        mfccs = extract_mfcc(file_path, max_length)
        mfccs_list.append(mfccs)
        file_names.append(file)

# 將列表轉換為NumPy數組
mfccs_array = np.array(mfccs_list)

# 將 MFCC 特徵向量展平，以便適用於 KMeans 算法
mfccs_flattened = mfccs_array.reshape(mfccs_array.shape[0], -1)

# 指定 KMeans 模型的參數
n_clusters = 5  # 假設我們要分成 5 個群

# 初始化 KMeans 模型並擬合數據
kmeans_model = KMeans(n_clusters=n_clusters, random_state=42)
kmeans_model.fit(mfccs_flattened)

# 獲取每個 MFCC 特徵向量的群分配
cluster_labels = kmeans_model.labels_

# 打印每個群的檔案名
cluster_files = {i: [] for i in range(n_clusters)}
for idx, label in enumerate(cluster_labels):
    cluster_files[label].append(file_names[idx])

for cluster, files in cluster_files.items():
    print(f"Cluster {cluster}: {', '.join(files)}")

# 可視化群分配結果
# 使用 t-SNE 降維以便視覺化
tsne = TSNE(n_components=2, random_state=42)
mfccs_tsne = tsne.fit_transform(mfccs_flattened)

# 繪製 t-SNE 圖形並根據 KMeans 結果著色
plt.figure(figsize=(10, 8))
for i in range(n_clusters):
    plt.scatter(mfccs_tsne[cluster_labels == i, 0], mfccs_tsne[cluster_labels == i, 1], label=f'Cluster {i}')
plt.title('t-SNE Visualization of MFCC Clusters')
plt.xlabel('t-SNE Dimension 1')
plt.ylabel('t-SNE Dimension 2')
plt.legend()
plt.show()
plt.savefig("kmeans_cluster.png")
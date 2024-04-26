import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

wav_dir = "/home/p76111652/Linux_DATA/synthesis/corpus/44k/corpus/genshin/gorou"

base_dir = "/home/p76111652/Linux_DATA/synthesis/corpus/44k/corpus/genshin/"


for folder in os.listdir(base_dir):
    embs = []
    names = []
    if not os.path.isdir(os.path.join(base_dir, folder)):
        continue
    for file in os.listdir(os.path.join(base_dir, folder)):
        if file.endswith(".npy"):
            xvec = np.load(os.path.join(base_dir, folder, file))
            embs.append(np.expand_dims(xvec, axis=0))
            names.append(file)
    if len(embs) == 0:
        continue
    speaker_id = folder
    x = np.concatenate(embs, axis=0)

    tsne = TSNE(n_components=2, random_state=42, metric="cosine")
    x_tsne = tsne.fit_transform(x)


    method = "k"
    n_clusters = 6  # Change to 6 clusters
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    y_predict = model.fit_predict(x)
    y_predict_tsne = model.fit_predict(x_tsne)

    label_dict = {"ang": 0, "dis": 1, "fea": 2, "hap": 3, "sad": 4, "sur": 5}
    true_label_dict = {0: "ang", 1: "dis", 2: "fea", 3: "hap", 4: "sad", 5: "sur"}

    # Printing each cluster
    for cluster_id in range(n_clusters):
        cluster_samples = [names[i] for i in range(len(y_predict)) if y_predict[i] == cluster_id]
        print(f"Cluster {cluster_id}: {cluster_samples}")
        if not os.path.exists(f'genshi/{cluster_id}'):
            os.makedirs(f'genshi/{speaker_id}_E0{cluster_id}')
        for sample in cluster_samples:
            os.system(f'cp {base_dir}/{speaker_id}/{sample} genshi/{speaker_id}_E0{cluster_id}')
            os.system(f'cp {base_dir}/{speaker_id}/{sample.replace(".npy", "")} genshi/{speaker_id}_E0{cluster_id}')
            os.system(f'cp {base_dir}/{speaker_id}/{sample.replace(".wav.npy", ".txt")} genshi/{speaker_id}_E0{cluster_id}')


# embs = []
# names = []
# for file in os.listdir(wav_dir):
#     if file.endswith(".npy"):
#         xvec = np.load(os.path.join(wav_dir, file))
#         embs.append(np.expand_dims(xvec, axis=0))
#         names.append(file)

# x = np.concatenate(embs, axis=0)

# tsne = TSNE(n_components=2, random_state=42, metric="cosine")
# x_tsne = tsne.fit_transform(x)

# method = "k"
# n_clusters = 6  # Change to 6 clusters

# if method == "k":
#     model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
# else:
#     raise ValueError("Only 'k' method is supported for now")

# y_predict = model.fit_predict(x)
# y_predict_tsne = model.fit_predict(x_tsne)

# label_dict = {"ang": 0, "dis": 1, "fea": 2, "hap": 3, "sad": 4, "sur": 5}
# true_label_dict = {0: "ang", 1: "dis", 2: "fea", 3: "hap", 4: "sad", 5: "sur"}

# # Printing each cluster
# for cluster_id in range(n_clusters):
#     cluster_samples = [names[i] for i in range(len(y_predict)) if y_predict[i] == cluster_id]
#     print(f"Cluster {cluster_id}: {cluster_samples}")
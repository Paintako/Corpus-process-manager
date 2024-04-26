import argparse
import json
import os
import shutil

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.manifold import TSNE
from umap import UMAP


# Get path settings
# with open(os.path.join("configs", "paths.yml"), "r", encoding="utf-8") as f:
    # path_config: dict[str, str] = yaml.safe_load(f.read())
    # dataset_root = path_config["dataset_root"]
    # assets_root = path_config["assets_root"]

dataset_root = "."

MAX_CLUSTER_NUM = 10
MAX_AUDIO_NUM = 15
DEFAULT_STYLE: str = "Neutral"
GRADIO_THEME: str = "Nord Dark"

tsne = TSNE(n_components=2, random_state=42, metric="cosine")
umap = UMAP(n_components=2, random_state=42, metric="cosine", n_jobs=1, min_dist=0.0)

wav_files = []
x = np.array([])
x_reduced = None
y_pred = np.array([])
mean = np.array([])
centroids = []


def load(model_name, reduction_method):
    global wav_files, x, x_reduced, mean
    wavs_dir = os.path.join(dataset_root, model_name)
    style_vector_files = [
        os.path.join(wavs_dir, f) for f in os.listdir(wavs_dir) if f.endswith(".npy")
    ]
    wav_files = [f.replace(".npy", "") for f in style_vector_files]
    style_vectors = [np.load(f) for f in style_vector_files]
    x = np.array(style_vectors)
    mean = np.mean(x, axis=0)
    if reduction_method == "t-SNE":
        x_reduced = tsne.fit_transform(x)
    elif reduction_method == "UMAP":
        x_reduced = umap.fit_transform(x)
    else:
        raise ValueError("Invalid reduction method")
    x_reduced = np.asarray(x_reduced)
    plt.figure(figsize=(6, 6))
    plt.scatter(x_reduced[:, 0], x_reduced[:, 1])
    return plt


def do_clustering(n_clusters=4, method="KMeans"):
    global centroids, x_reduced, y_pred
    if method == "KMeans":
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        y_pred = model.fit_predict(x)
    elif method == "Agglomerative":
        model = AgglomerativeClustering(n_clusters=n_clusters)
        y_pred = model.fit_predict(x)
    elif method == "KMeans after reduction":
        assert x_reduced is not None
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        y_pred = model.fit_predict(x_reduced)
    elif method == "Agglomerative after reduction":
        assert x_reduced is not None
        model = AgglomerativeClustering(n_clusters=n_clusters)
        y_pred = model.fit_predict(x_reduced)
    else:
        raise ValueError("Invalid method")

    centroids = []
    for i in range(n_clusters):
        centroids.append(np.mean(x[y_pred == i], axis=0))

    return y_pred, centroids


def do_dbscan(eps=2.5, min_samples=15):
    global centroids, x_reduced, y_pred
    model = DBSCAN(eps=eps, min_samples=min_samples)
    assert x_reduced is not None
    y_pred = model.fit_predict(x_reduced)
    n_clusters = max(y_pred) + 1
    centroids = []
    for i in range(n_clusters):
        centroids.append(np.mean(x[y_pred == i], axis=0))
    return y_pred, centroids


def representative_wav_files(cluster_id, num_files=1):
    # 在 y_pred 中找到關於 cluster_index 的 Medoids
    cluster_indices = np.where(y_pred == cluster_id)[0]
    cluster_vectors = x[cluster_indices]
    # 計算群集內所有向量之間的距離
    distances = pdist(cluster_vectors)
    distance_matrix = squareform(distances)

    # 計算每個向量與其他所有向量的平均距離
    mean_distances = distance_matrix.mean(axis=1)

    # 按平均距離從最小到最大獲取 num_files 個索引
    closest_indices = np.argsort(mean_distances)[:num_files]

    return cluster_indices[closest_indices]


def do_dbscan_gradio(eps=2.5, min_samples=15):
    global x_reduced, centroids

    y_pred, centroids = do_dbscan(eps, min_samples)

    assert x_reduced is not None

    cmap = plt.get_cmap("tab10")
    plt.figure(figsize=(6, 6))
    for i in range(max(y_pred) + 1):
        plt.scatter(
            x_reduced[y_pred == i, 0],
            x_reduced[y_pred == i, 1],
            color=cmap(i),
            label=f"風格 {i + 1}",
        )
    # Noise cluster (-1) is black
    plt.scatter(
        x_reduced[y_pred == -1, 0],
        x_reduced[y_pred == -1, 1],
        color="black",
        label="雜訊",
    )
    plt.legend()

    n_clusters = max(y_pred) + 1

    if n_clusters > MAX_CLUSTER_NUM:
        # raise ValueError(f"The number of clusters is too large: {n_clusters}")
        return [
            plt,
            gr.Slider(maximum=MAX_CLUSTER_NUM),
            f"群集數過多，請嘗試更改參數。: {n_clusters}",
        ] + [gr.Audio(visible=False)] * MAX_AUDIO_NUM

    elif n_clusters == 0:
        return [
            plt,
            gr.Slider(maximum=MAX_CLUSTER_NUM),
            f"沒有群集。請嘗試更改參數。",
        ] + [gr.Audio(visible=False)] * MAX_AUDIO_NUM

    return [plt, gr.Slider(maximum=n_clusters, value=1), n_clusters] + [
        gr.Audio(visible=False)
    ] * MAX_AUDIO_NUM


def representative_wav_files_gradio(cluster_id, num_files=1):
    cluster_id = cluster_id - 1  # 因為 UI 從 1 開始，所以將索引調整為從 0 開始
    closest_indices = representative_wav_files(cluster_id, num_files)
    actual_num_files = len(closest_indices)  # 為了處理文件數量較少的情況
    import os
    if not os.path.exists(f'style_class'):
        os.makedirs(f'style_class')

    os.system(f'rm -r style_class/*')
    for i in closest_indices:
        os.system(f'cp {wav_files[i]} style_class')
        os.system(f'cp {str(wav_files[i]).replace(".wav", ".txt")} style_class')
    
    os.system(f'tar cvf style_class.tar style_class')
        
    return [
        gr.Audio(wav_files[i], visible=True, label=wav_files[i])
        for i in closest_indices
    ] + [gr.update(visible=False)] * (MAX_AUDIO_NUM - actual_num_files)

def do_clustering_gradio(n_clusters=4, method="KMeans"):
    global x_reduced, centroids
    y_pred, centroids = do_clustering(n_clusters, method)

    assert x_reduced is not None
    cmap = plt.get_cmap("tab10")
    plt.figure(figsize=(6, 6))
    for i in range(n_clusters):
        plt.scatter(
            x_reduced[y_pred == i, 0],
            x_reduced[y_pred == i, 1],
            color=cmap(i),
            label=f"Style {i + 1}",
        )
    plt.legend()

    return [plt, gr.Slider(maximum=n_clusters, value=1)] + [
        gr.Audio(visible=False)
    ] * MAX_AUDIO_NUM


def save_style_vectors_from_clustering(model_name, style_names_str: str):
    """保存風格中心和质心"""
    result_dir = os.path.join(config.assets_root, model_name)
    os.makedirs(result_dir, exist_ok=True)
    style_vectors = np.stack([mean] + centroids)
    style_vector_path = os.path.join(result_dir, "style_vectors.npy")
    if os.path.exists(style_vector_path):
        logger.info(f"備份 {style_vector_path} 至 {style_vector_path}.bak")
        shutil.copy(style_vector_path, f"{style_vector_path}.bak")
    np.save(style_vector_path, style_vectors)

    # 更新 config.json
    config_path = os.path.join(result_dir, "config.json")
    if not os.path.exists(config_path):
        return f"{config_path} 不存在。"
    style_names = [name.strip() for name in style_names_str.split(",")]
    style_name_list = [DEFAULT_STYLE] + style_names
    if len(style_name_list) != len(centroids) + 1:
        return f"風格數量不匹配。請確認使用逗號正確分隔了 {len(centroids)} 個: {style_names_str}"
    if len(set(style_names)) != len(style_names):
        return f"風格名稱重複。"

    logger.info(f"備份 {config_path} 至 {config_path}.bak")
    shutil.copy(config_path, f"{config_path}.bak")
    with open(config_path, "r", encoding="utf-8") as f:
        json_dict = json.load(f)
    json_dict["data"]["num_styles"] = len(style_name_list)
    style_dict = {name: i for i, name in enumerate(style_name_list)}
    json_dict["data"]["style2id"] = style_dict
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(json_dict, f, indent=2, ensure_ascii=False)
    return f"成功!\n已保存至 {style_vector_path} 並更新 {config_path}。"


def save_style_vectors_from_files(
    model_name, audio_files_str: str, style_names_str: str
):
    """從音頻文件中創建並保存風格向量"""
    global mean
    if len(x) == 0:
        return "錯誤: 請先加載風格向量。"
    mean = np.mean(x, axis=0)

    result_dir = os.path.join(config.assets_root, model_name)
    os.makedirs(result_dir, exist_ok=True)
    audio_files = [name.strip() for name in audio_files_str.split(",")]
    style_names = [name.strip() for name in style_names_str.split(",")]
    if len(audio_files) != len(style_names):
        return f"音頻文件數量和風格名稱數量不匹配。請確保使用逗號正確分隔了 {len(style_names)} 個: {audio_files_str} 和 {style_names_str}"
    style_name_list = [DEFAULT_STYLE] + style_names
    if len(set(style_names)) != len(style_names):
        return f"風格名稱重複。"
    style_vectors = [mean]

    wavs_dir = os.path.join(dataset_root, model_name, "wavs")
    for audio_file in audio_files:
        path = os.path.join(wavs_dir, audio_file)
        if not os.path.exists(path):
            return f"{path} 不存在。"
        style_vectors.append(np.load(f"{path}.npy"))
    style_vectors = np.stack(style_vectors)
    assert len(style_name_list) == len(style_vectors)
    style_vector_path = os.path.join(result_dir, "style_vectors.npy")
    if os.path.exists(style_vector_path):
        logger.info(f"備份 {style_vector_path} 至 {style_vector_path}.bak")
        shutil.copy(style_vector_path, f"{style_vector_path}.bak")
    np.save(style_vector_path, style_vectors)

    # 更新 config.json
    config_path = os.path.join(result_dir, "config.json")
    if not os.path.exists(config_path):
        return f"{config_path} 不存在。"
    logger.info(f"備份 {config_path} 至 {config_path}.bak")
    shutil.copy(config_path, f"{config_path}.bak")

    with open(config_path, "r", encoding="utf-8") as f:
        json_dict = json.load(f)
    json_dict["data"]["num_styles"] = len(style_name_list)
    style_dict = {name: i for i, name in enumerate(style_name_list)}
    json_dict["data"]["style2id"] = style_dict

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(json_dict, f, indent=2, ensure_ascii=False)
    return f"成功!\n已保存至 {style_vector_path} 並更新 {config_path}。"


initial_md = f"""
# Style Bert-VITS2 創建風格向量

要使用 Style-Bert-VITS2 進行精細的風格指定音頻合成，需要手動為每個模型創建風格向量文件 `style_vectors.npy`。

但是，在訓練過程中會自動創建平均風格 "{DEFAULT_STYLE}"，因此您也可以直接使用它（在這種情況下，不會使用此 WebUI）。

由於此過程與訓練完全無關，因此您可以獨立重複嘗試任意次數。此外，它可能在訓練期間也很快。

## 方法

- 方法1：自動將音頻文件按風格分開，並取其平均值進行保存
- 方法2：手動選擇代表性風格的音頻文件，並保存其風格向量
- 方法3：自己努力並專注地創建（如果原始風格標籤等可用，例如 JVNV 語料庫，則可能更好）

"""

method1 = f"""
將從訓練中提取的風格向量加載並在可視化過程中進行風格分類。

步驟：
1. 查看圖表
2. 確定風格數量（不包括平均風格）
3. 進行風格分類並檢查結果
4. 決定風格名稱並保存

詳情：將透過適當的算法對風格向量（256維）進行聚類，並保存每個聚類的中心向量（以及整體平均向量）。

平均風格（{DEFAULT_STYLE}）將自動保存。
"""

dbscan_md = """
將使用 DBSCAN 方法進行風格分類。
儘管此方法可能僅適用於顯著的特徵，但可以提取比方法1更清晰的特徵，並可能創建出更好的風格向量。
但是，無法事先指定風格數量。

參數：
- eps：將相互之間距離小於此值的點連接起來，形成相同的風格分類。該值越小，風格數量越多，該值越大，風格數量越少。
- min_samples：將一個點視為風格核心點所需的鄰近點數量。該值越小，風格數量越多，該值越大，風格數量越少。

對於 UMAP，eps 可以大約為 0.3，對於 t-SNE，可以大約為 2.5。min_samples 取決於數據量，因此請嘗試不同值。

詳情：
https://ja.wikipedia.org/wiki/DBSCAN
"""


with gr.Blocks(theme=GRADIO_THEME) as app:
    gr.Markdown(initial_md)
    with gr.Row():
        model_name = gr.Textbox(placeholder="your_model_name", label="模型名稱")
        reduction_method = gr.Radio(
            choices=["UMAP", "t-SNE"],
            label="降維方法",
            info="v 1.3之前使用t-SNE，但UMAP可能更好。",
            value="UMAP",
        )
        load_button = gr.Button("加載風格向量", variant="primary")
    output = gr.Plot(label="音頻風格可視化")
    load_button.click(load, inputs=[model_name, reduction_method], outputs=[output])
    with gr.Tab("方法1: 自動進行風格分類"):
        with gr.Tab("風格分類1"):
            n_clusters = gr.Slider(
                minimum=2,
                maximum=10,
                step=1,
                value=4,
                label="生成的風格數量（不包括平均風格）",
                info="請通過上圖進行嘗試並錯誤的確定風格數量。",
            )
            c_method = gr.Radio(
                choices=[
                    "降維後的分層",
                    "降維後的KMeans",
                    "分層",
                    "KMeans",
                ],
                label="算法",
                info="選擇進行分類（聚類）的算法。請嘗試不同選擇。",
                value="降維後的分層",
            )
            c_button = gr.Button("執行風格分類")
        with gr.Tab("風格分類2: DBSCAN"):
            gr.Markdown(dbscan_md)
            eps = gr.Slider(
                minimum=0.1,
                maximum=10,
                step=0.01,
                value=0.3,
                label="eps",
            )
            min_samples = gr.Slider(
                minimum=1,
                maximum=50,
                step=1,
                value=15,
                label="min_samples",
            )
            with gr.Row():
                dbscan_button = gr.Button("執行風格分類")
                num_styles_result = gr.Textbox(label="風格數量")
        gr.Markdown("風格分類結果")
        gr.Markdown(
            "注意: 因為將原始的256維數據降至2維，所以位置關係不準確。"
        )
        with gr.Row():
            gr_plot = gr.Plot()
            with gr.Column():
                with gr.Row():
                    cluster_index = gr.Slider(
                        minimum=1,
                        maximum=MAX_CLUSTER_NUM,
                        step=1,
                        value=1,
                        label="風格編號",
                        info="顯示所選風格的代表音頻。",
                    )
                    num_files = gr.Slider(
                        minimum=1,
                        maximum=MAX_AUDIO_NUM,
                        step=1,
                        value=5,
                        label="顯示幾個代表音頻",
                    )
                    get_audios_button = gr.Button("獲取代表音頻")
                with gr.Row():
                    audio_list = []
                    for i in range(MAX_AUDIO_NUM):
                        audio_list.append(gr.Audio(visible=False, show_label=True))
            c_button.click(
                do_clustering_gradio,
                inputs=[n_clusters, c_method],
                outputs=[gr_plot, cluster_index] + audio_list,
                
            )
            dbscan_button.click(
                do_dbscan_gradio,
                inputs=[eps, min_samples],
                outputs=[gr_plot, cluster_index, num_styles_result] + audio_list,
            )
            get_audios_button.click(
                representative_wav_files_gradio,
                inputs=[cluster_index, num_files],
                outputs=audio_list,
            )
        gr.Markdown("如果結果看起來好，請保存它。")
        style_names = gr.Textbox(
            "生氣, 悲傷, 快樂",
            label="風格名稱",
            info=f"請使用','分隔風格名稱（可以使用中文）。例如：'生氣, 悲傷, 快樂'或'Angry, Sad, Happy'。平均音頻將自動保存為{DEFAULT_STYLE}。",
        )
        with gr.Row():
            save_button1 = gr.Button("保存風格向量", variant="primary")
            info2 = gr.Textbox(label="保存結果")

        save_button1.click(
            save_style_vectors_from_clustering,
            inputs=[model_name, style_names],
            outputs=[info2],
        )
    with gr.Tab("方法2: 手動選擇風格"):
        gr.Markdown(
            "在下面的文本框中，請以逗號分隔，依次輸入每個風格的代表音頻文件名，並在其旁邊以逗號分隔輸入相應的風格名稱。"
        )
        gr.Markdown("例如：`angry.wav, sad.wav, happy.wav`和`生氣, 悲傷, 快樂`")
        gr.Markdown(
            f"注意: {DEFAULT_STYLE}風格將自動保存，請不要手動指定名為{DEFAULT_STYLE}的風格。"
        )
        with gr.Row():
            audio_files_text = gr.Textbox(
                label="音頻文件名", placeholder="angry.wav, sad.wav, happy.wav"
            )
            style_names_text = gr.Textbox(
                label="風格名稱", placeholder="生氣, 悲傷, 快樂"
            )
        with gr.Row():
            save_button2 = gr.Button("保存風格向量", variant="primary")
            info2 = gr.Textbox(label="保存結果")
            save_button2.click(
                save_style_vectors_from_files,
                inputs=[model_name, audio_files_text, style_names_text],
                outputs=[info2],
            )

parser = argparse.ArgumentParser()
parser.add_argument(
    "--server-name",
    type=str,
    default=None,
    help="Server name for Gradio app",
)
parser.add_argument(
    "--no-autolaunch",
    action="store_true",
    default=False,
    help="Do not launch app automatically",
)
parser.add_argument("--share", action="store_true", default=False)
args = parser.parse_args()

app.launch(
    inbrowser=not args.no_autolaunch, server_name=args.server_name, share=args.share
)
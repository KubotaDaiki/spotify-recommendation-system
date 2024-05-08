import json
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer


def connect_to_database(database: str):
    # .envから環境変数を読み込む
    load_dotenv()

    # データベースに接続&初期設定
    connection = psycopg2.connect(
        host="localhost",
        database=database,
        user="postgres",
        password=os.environ["PASSWORD"],
    )
    connection.autocommit = True
    connection.set_client_encoding("utf-8")
    cursor = connection.cursor()
    return connection, cursor


# プレイリストをデータフレームに読み込む
spotify_df = pd.DataFrame()
path = "spotify_million_playlist_dataset/data"
for i, file_name in enumerate(os.listdir(path)):
    if i >= 500:
        break
    with open(os.path.join(path, file_name), "r") as j:
        contents = json.loads(j.read())
    spotify_df = pd.concat(
        [spotify_df, pd.json_normalize(contents["playlists"])],
        ignore_index=True,
    )

# トラック名をリストとして抽出し、列に追加
list_track_name_col = []
for row in spotify_df.iloc():
    track_names = []
    for track in row["tracks"]:
        track_names.append(track["track_name"])
    list_track_name_col.append(track_names)
spotify_df["track_names"] = list_track_name_col

# トラックリストをバイナリ行列化し、コサイン類似度を計算
mlb = MultiLabelBinarizer(sparse_output=True)
playlist_matrix = mlb.fit_transform(spotify_df["track_names"])
similarity_matrix = cosine_similarity(playlist_matrix.transpose(), dense_output=False)
# sparse_output=TrueにすることでCSR形式になっているので、扱いやすいCOO形式に変換
similarity_matrix = similarity_matrix.tocoo()


# # データベースに接続&初期設定
connection, cursor = connect_to_database("spotify")


# 重複のないトラック名のリストをデータベースに格納
cursor.execute("DELETE FROM music;")
cursor.execute("DELETE FROM similarity_matrix;")
for i, name in enumerate(mlb.classes_):
    cursor.execute(
        "INSERT INTO music (id, name) VALUES (%s, %s);",
        (i, name),
    )


similarity_matrix = [
    (int(row), int(col), float(value))
    for row, col, value in zip(
        similarity_matrix.row,
        similarity_matrix.col,
        similarity_matrix.data,
    )
]
execute_values(
    cursor,
    "INSERT INTO similarity_matrix (row_music_id, col_music_id, value) VALUES %s",
    similarity_matrix,
)

# # 接続を閉じる
cursor.close()
connection.close()

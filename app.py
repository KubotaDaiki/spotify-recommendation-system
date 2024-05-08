import streamlit as st
from dotenv import load_dotenv
import psycopg2
import os


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


# データベースに接続&初期設定
connection, cursor = connect_to_database("spotify")

# トラック情報を取得
cursor.execute("SELECT id, name FROM music;")
tracks = cursor.fetchall()
track_names = [track_name[1] for track_name in tracks]

# セレクトボックスで選択されたトラック名に対応するIDを取得
select_name = st.selectbox("タイトルを選択", track_names)
select_id = list(filter(lambda x: x[1] == select_name, tracks))[0][0]

# 選択されたトラックに類似した楽曲を取得
cursor.execute(
    """
    SELECT music.name, sm.value FROM similarity_matrix AS sm
    JOIN music ON music.id = sm.col_music_id
    WHERE sm.row_music_id=%s AND sm.row_music_id<>sm.col_music_id
    ORDER BY sm.value DESC
    LIMIT 10;
    """,
    (select_id,),
)
recommended_tracks = cursor.fetchall()
recommended_tracks = [{"推薦された楽曲": track[0], "類似度": track[1]} for track in recommended_tracks]

# 推薦された楽曲を表示
st.table(recommended_tracks)

# 接続を閉じる
cursor.close()
connection.close()

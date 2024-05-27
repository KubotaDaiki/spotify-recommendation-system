from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psycopg2
import os

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def recommendation(track_name: str):
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

    # 全トラック情報を取得
    cursor.execute("SELECT id, name FROM music;")
    tracks = cursor.fetchall()

    # トラック名に対応するIDを取得
    track_id = list(filter(lambda x: x[1] == track_name, tracks))[0][0]

    # 選択されたトラックに類似した楽曲を取得
    cursor.execute(
        """
        SELECT music.name, sm.value FROM similarity_matrix AS sm
        JOIN music ON music.id = sm.col_music_id
        WHERE sm.row_music_id=%s AND sm.row_music_id<>sm.col_music_id
        ORDER BY sm.value DESC
        LIMIT 10;
        """,
        (track_id,),
    )
    recommended_tracks = cursor.fetchall()
    recommended_tracks = [
        {"楽曲": track[0], "類似度": track[1]} for track in recommended_tracks
    ]

    # 接続を閉じる
    cursor.close()
    connection.close()

    return recommended_tracks

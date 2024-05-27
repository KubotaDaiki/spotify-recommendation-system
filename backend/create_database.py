import psycopg2
from dotenv import load_dotenv
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


def main():
    # データベースに接続&初期設定
    connection, cursor = connect_to_database("postgres")
    # データベースを作成
    cursor.execute("CREATE DATABASE spotify")
    # 接続を閉じる
    cursor.close()
    connection.close()

    # データベースに接続&初期設定
    connection2, cursor2 = connect_to_database("spotify")
    # 類似度を格納するテーブルを作成
    cursor2.execute(
        """
        CREATE TABLE similarity_matrix (
            id SERIAL PRIMARY KEY,
            value DOUBLE PRECISION NOT NULL,
            row_music_id INTEGER NOT NULL,
            col_music_id INTEGER NOT NULL
        );
        """
    )
    # トラック名を格納するテーブルを作成
    cursor2.execute(
        """
        CREATE TABLE music (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
    )
    # 接続を閉じる
    cursor2.close()
    connection2.close()


main()

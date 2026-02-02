import sqlite3
import pandas as pd

# DB 연결
conn = sqlite3.connect('assets.db')

# 테이블 목록 확인
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# (선택) 판다스로 데이터 읽기
df = pd.read_sql_query("SELECT * FROM assets", conn)
print(df)

conn.close()

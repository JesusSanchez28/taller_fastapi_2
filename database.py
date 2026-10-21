import os
from pathlib import Path
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

load_dotenv(Path(__file__).with_name('.env'))

def get_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ['DB_PORT']),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        charset='utf8mb4', cursorclass=DictCursor,
        autocommit=False, connect_timeout=5,
        read_timeout=10, write_timeout=10,
    )

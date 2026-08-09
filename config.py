import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "6036")
DB_NAME = os.getenv("DB_NAME", "db_viagens")
DRIVE_FILE_ID = os.getenv("DRIVE_FILE_ID", "https://drive.google.com/drive/folders/1J_0kDNI_2p3wHtmgbiwTpGD744beMvdL?usp=sharing")
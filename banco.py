import psycopg2
from psycopg2.extras import execute_values
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def conectar_banco():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )


def inserir_em_lote(conn, sql, dados, tamanho_lote=1000):
    cursor = conn.cursor()
    execute_values(
        cursor,
        sql,
        dados,
        page_size=tamanho_lote
    )
    conn.commit()
    cursor.close()
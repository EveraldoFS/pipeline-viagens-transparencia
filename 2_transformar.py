import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse
import re

# ============================================================
# CONFIGURACAO
# ============================================================
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_viagens"
DB_USER = "postgres"
DB_PASS = "6036"

def conectar_banco():
    try:
        database_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"📌 Conectando ao banco...")
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexão estabelecida com sucesso!")
        return engine
    except Exception as e:
        print(f"❌ Erro de conexao: {e}")
        raise

def converter_data_br(data_str):
    if pd.isna(data_str) or data_str == '' or data_str is None:
        return None
    try:
        data_str = str(data_str).strip()
        partes = data_str.split('/')
        if len(partes) == 3 and partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit():
            return f"{partes[2]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
    except:
        pass
    return None

def converter_valor_br(valor_str):
    if pd.isna(valor_str) or valor_str == '' or valor_str is None:
        return 0.0
    try:
        valor_str = str(valor_str).replace('R$', '').replace(' ', '').replace('\t', '').replace('\n', '')
        valor_str = valor_str.replace('.', '').replace(',', '.')
        return float(valor_str)
    except:
        return 0.0

def converter_boolean(valor_str):
    if pd.isna(valor_str) or valor_str == '':
        return None
    valor_str = str(valor_str).strip().upper()
    if valor_str == 'SIM':
        return True
    elif valor_str == 'NÃO' or valor_str == 'NAO':
        return False
    return None

def limpar_texto(texto):
    if pd.isna(texto) or texto is None:
        return None
    texto = str(texto).strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto if texto else None

def processar_silver_viagem(engine):
    print("\n" + "="*60)
    print("🔄 PROCESSANDO SILVER_VIAGEM")
    print("="*60)
    
    colunas_para_inserir = [
        'id_viagem', 'num_proposta', 'situacao', 'viagem_urgente',
        'cod_orgao_superior', 'nome_orgao_superior',
        'data_inicio', 'data_fim', 'duracao_dias',
        'valor_diarias', 'valor_passagens', 'valor_devolucao', 'valor_outros_gastos',
        'valor_total', 'custo_medio_diario',
        'flag_erro', 'mensagem_erro'
    ]
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS silver_viagem CASCADE;"))
        conn.execute(text("""
            CREATE TABLE silver_viagem (
                id_viagem VARCHAR(20) PRIMARY KEY,
                num_proposta VARCHAR(50),
                situacao VARCHAR(50),
                viagem_urgente BOOLEAN,
                cod_orgao_superior VARCHAR(20),
                nome_orgao_superior VARCHAR(255),
                data_inicio DATE,
                data_fim DATE,
                duracao_dias INTEGER,
                valor_diarias DECIMAL(12,2),
                valor_passagens DECIMAL(12,2),
                valor_devolucao DECIMAL(12,2),
                valor_outros_gastos DECIMAL(12,2),
                valor_total DECIMAL(12,2),
                custo_medio_diario DECIMAL(12,2),
                flag_erro BOOLEAN DEFAULT FALSE,
                mensagem_erro TEXT
            );
        """))
        conn.commit()
    print("🧹 Tabela silver_viagem recriada com todas as colunas")
    
    df = pd.read_sql_query("SELECT * FROM raw_viagem;", engine)
    print(f"📊 Lidos {len(df):,} registros da raw_viagem")
    
    # Converte datas
    df['data_inicio'] = df['data_inicio'].apply(converter_data_br)
    df['data_fim'] = df['data_fim'].apply(converter_data_br)
    
    # Converte valores
    df['valor_diarias'] = df['valor_diarias'].apply(converter_valor_br)
    df['valor_passagens'] = df['valor_passagens'].apply(converter_valor_br)
    df['valor_devolucao'] = df['valor_devolucao'].apply(converter_valor_br)
    df['valor_outros_gastos'] = df['valor_outros_gastos'].apply(converter_valor_br)
    
    # Calcula valor_total
    df['valor_total'] = df['valor_diarias'] + df['valor_passagens'] + df['valor_devolucao'] + df['valor_outros_gastos']
    
    # Calcula duracao_dias
    df['data_inicio_dt'] = pd.to_datetime(df['data_inicio'], errors='coerce')
    df['data_fim_dt'] = pd.to_datetime(df['data_fim'], errors='coerce')
    df['duracao_dias'] = (df['data_fim_dt'] - df['data_inicio_dt']).dt.days.fillna(0).astype(int)
    
    # Calcula custo_medio_diario
    df['custo_medio_diario'] = df.apply(
        lambda row: row['valor_total'] / row['duracao_dias'] if row['duracao_dias'] > 0 else 0, 
        axis=1
    )
    
    # Converte viagem_urgente
    df['viagem_urgente'] = df['viagem_urgente'].apply(converter_boolean)
    
    # Limpa textos
    df['situacao'] = df['situacao'].apply(limpar_texto)
    df['nome_orgao_superior'] = df['nome_orgao_superior'].apply(limpar_texto)
    
    # Flag de erro
    df['flag_erro'] = False
    df['mensagem_erro'] = None
    
    df_silver = df[colunas_para_inserir].copy()
    df_silver = df_silver[df_silver['id_viagem'].notna()]
    df_silver = df_silver.drop_duplicates(subset=['id_viagem'])
    
    print(f"📊 Registros a inserir: {len(df_silver):,}")
    df_silver.to_sql('silver_viagem', engine, if_exists='append', index=False, chunksize=10000)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM silver_viagem"))
        count = result.scalar()
        print(f"✅ silver_viagem: {count:,} registros inseridos")

def main():
    print("="*60)
    print("🚀 TRANSFORMAÇÃO PARA CAMADA SILVER")
    print("="*60)
    
    try:
        engine = conectar_banco()
        processar_silver_viagem(engine)
        print("\n✅ TRANSFORMAÇÃO CONCLUÍDA!")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
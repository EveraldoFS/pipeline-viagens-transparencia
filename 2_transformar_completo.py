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

def limpar_texto(texto):
    if pd.isna(texto) or texto is None:
        return None
    texto = str(texto).strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto if texto else None

# ============================================================
# SILVER_PASSAGEM
# ============================================================

def processar_silver_passagem(engine):
    print("\n" + "="*60)
    print("🔄 PROCESSANDO SILVER_PASSAGEM")
    print("="*60)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS silver_passagem CASCADE;"))
        conn.execute(text("""
            CREATE TABLE silver_passagem (
                id_passagem SERIAL PRIMARY KEY,
                id_viagem VARCHAR(20),
                num_proposta VARCHAR(50),
                meio_transporte VARCHAR(100),
                pais_origem_ida VARCHAR(100),
                uf_origem_ida VARCHAR(50),
                cidade_origem_ida VARCHAR(100),
                pais_destino_ida VARCHAR(100),
                uf_destino_ida VARCHAR(50),
                cidade_destino_ida VARCHAR(100),
                pais_origem_volta VARCHAR(100),
                uf_origem_volta VARCHAR(50),
                cidade_origem_volta VARCHAR(100),
                pais_destino_volta VARCHAR(100),
                uf_destino_volta VARCHAR(50),
                cidade_destino_volta VARCHAR(100),
                valor_passagem DECIMAL(12,2),
                taxa_servico DECIMAL(12,2),
                data_emissao DATE,
                hora_emissao VARCHAR(10)
            );
        """))
        conn.commit()
    print("🧹 Tabela silver_passagem recriada")
    
    df = pd.read_sql_query("SELECT * FROM raw_passagem;", engine)
    print(f"📊 Lidos {len(df):,} registros da raw_passagem")
    
    # Converte datas
    df['data_emissao'] = df['data_emissao'].apply(converter_data_br)
    
    # Converte valores
    df['valor_passagem'] = df['valor_passagem'].apply(converter_valor_br)
    df['taxa_servico'] = df['taxa_servico'].apply(converter_valor_br)
    
    # Limpa textos
    df['meio_transporte'] = df['meio_transporte'].apply(limpar_texto)
    
    # Remove registros sem id_viagem
    df_silver = df[df['id_viagem'].notna()]
    df_silver = df_silver.drop_duplicates(subset=['id_passagem']) if 'id_passagem' in df_silver.columns else df_silver
    
    print(f"📊 Registros a inserir: {len(df_silver):,}")
    df_silver.to_sql('silver_passagem', engine, if_exists='append', index=False, chunksize=10000)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM silver_passagem"))
        count = result.scalar()
        print(f"✅ silver_passagem: {count:,} registros inseridos")

# ============================================================
# SILVER_PAGAMENTO
# ============================================================

def processar_silver_pagamento(engine):
    print("\n" + "="*60)
    print("🔄 PROCESSANDO SILVER_PAGAMENTO")
    print("="*60)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS silver_pagamento CASCADE;"))
        conn.execute(text("""
            CREATE TABLE silver_pagamento (
                id_pagamento SERIAL PRIMARY KEY,
                id_viagem VARCHAR(20),
                num_proposta VARCHAR(50),
                cod_orgao_superior VARCHAR(20),
                nome_orgao_superior VARCHAR(255),
                cod_orgao_pagador VARCHAR(20),
                nome_orgao_pagador VARCHAR(255),
                cod_unidade_gestora VARCHAR(20),
                nome_unidade_gestora VARCHAR(255),
                tipo_pagamento VARCHAR(50),
                valor DECIMAL(12,2)
            );
        """))
        conn.commit()
    print("🧹 Tabela silver_pagamento recriada")
    
    df = pd.read_sql_query("SELECT * FROM raw_pagamento;", engine)
    print(f"📊 Lidos {len(df):,} registros da raw_pagamento")
    
    # Converte valor
    df['valor'] = df['valor'].apply(converter_valor_br)
    
    # Limpa textos
    df['nome_orgao_pagador'] = df['nome_orgao_pagador'].apply(limpar_texto)
    df['nome_unidade_gestora'] = df['nome_unidade_gestora'].apply(limpar_texto)
    df['tipo_pagamento'] = df['tipo_pagamento'].apply(limpar_texto)
    df['nome_orgao_superior'] = df['nome_orgao_superior'].apply(limpar_texto)
    
    df_silver = df[df['id_viagem'].notna()]
    df_silver = df_silver.drop_duplicates(subset=['id_pagamento']) if 'id_pagamento' in df_silver.columns else df_silver
    
    print(f"📊 Registros a inserir: {len(df_silver):,}")
    df_silver.to_sql('silver_pagamento', engine, if_exists='append', index=False, chunksize=10000)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM silver_pagamento"))
        count = result.scalar()
        print(f"✅ silver_pagamento: {count:,} registros inseridos")

# ============================================================
# SILVER_TRECHO
# ============================================================

def processar_silver_trecho(engine):
    print("\n" + "="*60)
    print("🔄 PROCESSANDO SILVER_TRECHO")
    print("="*60)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS silver_trecho CASCADE;"))
        conn.execute(text("""
            CREATE TABLE silver_trecho (
                id_trecho SERIAL PRIMARY KEY,
                id_viagem VARCHAR(20),
                num_proposta VARCHAR(50),
                sequencia_trecho INTEGER,
                origem_data DATE,
                origem_pais VARCHAR(100),
                origem_uf VARCHAR(50),
                origem_cidade VARCHAR(100),
                destino_data DATE,
                destino_pais VARCHAR(100),
                destino_uf VARCHAR(50),
                destino_cidade VARCHAR(100),
                meio_transporte VARCHAR(100),
                numero_diarias DECIMAL(10,2),
                missao VARCHAR(10)
            );
        """))
        conn.commit()
    print("🧹 Tabela silver_trecho recriada")
    
    df = pd.read_sql_query("SELECT * FROM raw_trecho;", engine)
    print(f"📊 Lidos {len(df):,} registros da raw_trecho")
    
    # Converte datas
    df['origem_data'] = df['origem_data'].apply(converter_data_br)
    df['destino_data'] = df['destino_data'].apply(converter_data_br)
    
    # Converte sequencia para inteiro
    df['sequencia_trecho'] = pd.to_numeric(df['sequencia_trecho'], errors='coerce').fillna(0).astype(int)
    
    # Converte numero_diarias
    df['numero_diarias'] = df['numero_diarias'].apply(converter_valor_br)
    
    # Limpa textos
    df['meio_transporte'] = df['meio_transporte'].apply(limpar_texto)
    df['missao'] = df['missao'].apply(limpar_texto)
    
    df_silver = df[df['id_viagem'].notna()]
    df_silver = df_silver.drop_duplicates(subset=['id_trecho']) if 'id_trecho' in df_silver.columns else df_silver
    
    print(f"📊 Registros a inserir: {len(df_silver):,}")
    df_silver.to_sql('silver_trecho', engine, if_exists='append', index=False, chunksize=10000)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM silver_trecho"))
        count = result.scalar()
        print(f"✅ silver_trecho: {count:,} registros inseridos")

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("🚀 PROCESSANDO TABELAS SILVER FALTANTES")
    print("="*60)
    
    try:
        engine = conectar_banco()
        
        processar_silver_passagem(engine)
        processar_silver_pagamento(engine)
        processar_silver_trecho(engine)
        
        print("\n" + "="*60)
        print("📊 RESUMO FINAL - TABELAS SILVER")
        print("="*60)
        
        for tabela in ['silver_passagem', 'silver_pagamento', 'silver_trecho']:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                count = result.scalar()
                print(f"   {tabela}: {count:,} registros")
        
        print("\n✅ PROCESSAMENTO CONCLUÍDO!")
        print("🎯 Agora execute: python 3_gold.py")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
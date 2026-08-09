import os
import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse

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
        password_encoded = urllib.parse.quote_plus(DB_PASS)
        database_url = f"postgresql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"📌 Conectando ao banco...")
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexão estabelecida com sucesso!")
        return engine
    except Exception as e:
        print(f"❌ Erro de conexao: {e}")
        raise

# ============================================================
# MAPEAMENTO CORRETO DAS COLUNAS (baseado no ver.py)
# ============================================================
COLUNAS_MAP = {
    'raw_viagem': {
        'Identificador do processo de viagem': 'id_viagem',
        'Número da Proposta (PCDP)': 'num_proposta',
        'Situação': 'situacao',
        'Viagem Urgente': 'viagem_urgente',
        'Justificativa Urgência Viagem': 'justificativa',
        'Código do órgão superior': 'cod_orgao_superior',
        'Nome do órgão superior': 'nome_orgao_superior',
        'Código órgão solicitante': 'cod_orgao_solicitante',
        'Nome órgão solicitante': 'nome_orgao_solicitante',
        'CPF viajante': 'cpf_viajante',
        'Nome': 'nome',
        'Cargo': 'cargo',
        'Função': 'funcao',
        'Descrição Função': 'descricao_funcao',
        'Período - Data de início': 'data_inicio',
        'Período - Data de fim': 'data_fim',
        'Destinos': 'destinos',
        'Motivo': 'motivo',
        'Valor diárias': 'valor_diarias',
        'Valor passagens': 'valor_passagens',
        'Valor devolução': 'valor_devolucao',
        'Valor outros gastos': 'valor_outros_gastos'
    },
    'raw_passagem': {
        'Identificador do processo de viagem': 'id_viagem',
        'Número da Proposta (PCDP)': 'num_proposta',
        'Meio de transporte': 'meio_transporte',
        'País - Origem ida': 'pais_origem_ida',
        'UF - Origem ida': 'uf_origem_ida',
        'Cidade - Origem ida': 'cidade_origem_ida',
        'País - Destino ida': 'pais_destino_ida',
        'UF - Destino ida': 'uf_destino_ida',
        'Cidade - Destino ida': 'cidade_destino_ida',
        'País - Origem volta': 'pais_origem_volta',
        'UF - Origem volta': 'uf_origem_volta',
        'Cidade - Origem volta': 'cidade_origem_volta',
        'Pais - Destino volta': 'pais_destino_volta',
        'UF - Destino volta': 'uf_destino_volta',
        'Cidade - Destino volta': 'cidade_destino_volta',
        'Valor da passagem': 'valor_passagem',
        'Taxa de serviço': 'taxa_servico',
        'Data da emissão/compra': 'data_emissao',
        'Hora da emissão/compra': 'hora_emissao'
    },
    'raw_pagamento': {
        'Identificador do processo de viagem': 'id_viagem',
        'Número da Proposta (PCDP)': 'num_proposta',
        'Código do órgão superior': 'cod_orgao_superior',
        'Nome do órgão superior': 'nome_orgao_superior',
        'Codigo do órgão pagador': 'cod_orgao_pagador',
        'Nome do órgao pagador': 'nome_orgao_pagador',
        'Código da unidade gestora pagadora': 'cod_unidade_gestora',
        'Nome da unidade gestora pagadora': 'nome_unidade_gestora',
        'Tipo de pagamento': 'tipo_pagamento',
        'Valor': 'valor'
    },
    'raw_trecho': {
        'Identificador do processo de viagem ': 'id_viagem',
        'Número da Proposta (PCDP)': 'num_proposta',
        'Sequência Trecho': 'sequencia_trecho',
        'Origem - Data': 'origem_data',
        'Origem - País': 'origem_pais',
        'Origem - UF': 'origem_uf',
        'Origem - Cidade': 'origem_cidade',
        'Destino - Data': 'destino_data',
        'Destino - País': 'destino_pais',
        'Destino - UF': 'destino_uf',
        'Destino - Cidade': 'destino_cidade',
        'Meio de transporte': 'meio_transporte',
        'Número Diárias': 'numero_diarias',
        'Missao?': 'missao'
    }
}

def carregar_csv(engine, csv_file, tabela):
    print(f"📤 Carregando {csv_file} na tabela {tabela}...")
    
    try:
        # Detecta separador
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            sep = ';' if ';' in first_line else ','
        
        print(f"   📌 Separador: '{sep}'")
        
        # Lê o CSV
        try:
            df = pd.read_csv(csv_file, sep=sep, encoding='utf-8', dtype=str, low_memory=False)
        except:
            df = pd.read_csv(csv_file, sep=sep, encoding='latin1', dtype=str, low_memory=False)
        
        print(f"   📊 Lidos {len(df)} registros")
        
        # Renomeia colunas conforme mapeamento
        if tabela in COLUNAS_MAP:
            df = df.rename(columns=COLUNAS_MAP[tabela])
        
        # Mantém apenas as colunas que existem no mapeamento
        colunas_esperadas = list(COLUNAS_MAP[tabela].values())
        df = df[colunas_esperadas]
        
        print(f"   📋 Colunas: {df.columns.tolist()[:3]}...")
        
        if df.empty:
            print("   ⚠️ Arquivo vazio!")
            return False
        
        # Limpa a tabela
        with engine.connect() as conn:
            conn.execute(text(f"TRUNCATE TABLE {tabela} CASCADE;"))
            conn.commit()
        print("   🧹 Tabela limpa")
        
        # Insere dados
        print("   🚀 Inserindo dados...")
        df.to_sql(tabela, engine, if_exists='append', index=False, chunksize=5000)
        
        print(f"✅ {csv_file} carregado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("="*60)
    print("🚀 EXTRAÇÃO DE DADOS - RAW")
    print("="*60)
    
    engine = conectar_banco()
    
    # Mapeamento arquivo -> tabela
    arquivos = {
        '2025_Viagem.csv': 'raw_viagem',
        '2025_Passagem.csv': 'raw_passagem',
        '2025_Pagamento.csv': 'raw_pagamento',
        '2025_Trecho.csv': 'raw_trecho'
    }
    
    sucessos = 0
    for arquivo, tabela in arquivos.items():
        if os.path.exists(arquivo):
            print(f"\n📋 {arquivo} → {tabela}")
            if carregar_csv(engine, arquivo, tabela):
                sucessos += 1
        else:
            print(f"\n⚠️ Arquivo não encontrado: {arquivo}")
    
    print("\n" + "="*60)
    print(f"✅ {sucessos}/4 CSVs carregados")
    
    # Verifica registros
    print("\n📊 REGISTROS NAS TABELAS RAW:")
    for tabela in ['raw_viagem', 'raw_passagem', 'raw_pagamento', 'raw_trecho']:
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                count = result.scalar()
                print(f"   {tabela}: {count:,} registros")
        except Exception as e:
            print(f"   {tabela}: Erro ao contar - {e}")

if __name__ == "__main__":
    main()
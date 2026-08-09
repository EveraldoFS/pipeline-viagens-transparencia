import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
import urllib.parse
import os

# ============================================================
# CONFIGURACAO
# ============================================================
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_viagens"
DB_USER = "postgres"
DB_PASS = "6036"

# Criar pasta para gráficos
os.makedirs('graficos', exist_ok=True)

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

def criar_tabela_gold(engine):
    """Cria a tabela gold_resumo_pagamentos_mensais"""
    print("\n" + "="*60)
    print("📊 CRIANDO TABELA GOLD")
    print("="*60)
    
    # Remove tabela se existir
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS gold_resumo_pagamentos_mensais CASCADE;"))
        conn.execute(text("DROP VIEW IF EXISTS vw_resumo_pagamentos_mensais CASCADE;"))
        conn.commit()
    
    # Query para criar a tabela agregada
    query = """
    CREATE TABLE gold_resumo_pagamentos_mensais AS
    SELECT 
        DATE_TRUNC('month', v.data_inicio) AS mes,
        v.nome_orgao_superior,
        COUNT(DISTINCT v.id_viagem) AS total_viagens,
        SUM(v.valor_total) AS total_gasto,
        AVG(v.valor_total) AS gasto_medio_por_viagem,
        SUM(p.valor) AS total_pagamentos,
        COUNT(DISTINCT p.id_pagamento) AS total_pagamentos_realizados
    FROM silver_viagem v
    LEFT JOIN silver_pagamento p ON v.id_viagem = p.id_viagem
    WHERE v.data_inicio IS NOT NULL
    GROUP BY mes, v.nome_orgao_superior
    ORDER BY mes DESC, total_gasto DESC;
    """
    
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()
    print("✅ Tabela gold_resumo_pagamentos_mensais criada com sucesso!")
    
    # Criar VIEW
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIEW vw_resumo_pagamentos_mensais AS
            SELECT * FROM gold_resumo_pagamentos_mensais;
        """))
        conn.commit()
    print("✅ VIEW vw_resumo_pagamentos_mensais criada com sucesso!")

def analise_1_top_orgaos(engine):
    """Análise 1: Top 10 órgãos que mais gastaram (SILVER)"""
    print("\n" + "="*60)
    print("📊 ANÁLISE 1 - TOP 10 ÓRGÃOS QUE MAIS GASTARAM")
    print("="*60)
    
    query = """
    SELECT 
        nome_orgao_superior,
        COUNT(*) AS total_viagens,
        SUM(valor_total) AS total_gasto,
        AVG(valor_total) AS gasto_medio
    FROM silver_viagem
    WHERE valor_total > 0
    GROUP BY nome_orgao_superior
    ORDER BY total_gasto DESC
    LIMIT 10;
    """
    
    df = pd.read_sql_query(query, engine)
    print(df.to_string(index=False))
    
    # Gráfico
    plt.figure(figsize=(12, 8))
    bars = plt.barh(df['nome_orgao_superior'], df['total_gasto'], color='steelblue')
    plt.xlabel('Total Gasto (R$)')
    plt.title('Top 10 Órgãos que Mais Gastaram em Viagens')
    plt.gca().invert_yaxis()
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, df['total_gasto']):
        plt.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2, 
                f'R$ {valor:,.2f}', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('graficos/analise_1_top_orgaos.png', dpi=300)
    print("✅ Gráfico salvo: graficos/analise_1_top_orgaos.png")
    plt.close()
    
    return df

def analise_2_viagens_por_mes(engine):
    """Análise 2: Quantidade de viagens por mês (SILVER)"""
    print("\n" + "="*60)
    print("📊 ANÁLISE 2 - VIAGENS POR MÊS")
    print("="*60)
    
    query = """
    SELECT 
        DATE_TRUNC('month', data_inicio) AS mes,
        COUNT(*) AS total_viagens,
        SUM(valor_total) AS total_gasto
    FROM silver_viagem
    WHERE data_inicio IS NOT NULL
    GROUP BY mes
    ORDER BY mes;
    """
    
    df = pd.read_sql_query(query, engine)
    df['mes'] = pd.to_datetime(df['mes'])
    df['mes_str'] = df['mes'].dt.strftime('%Y-%m')
    print(df[['mes_str', 'total_viagens', 'total_gasto']].to_string(index=False))
    
    # Gráfico
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Gráfico 1: Total de viagens
    axes[0].plot(df['mes_str'], df['total_viagens'], marker='o', color='darkblue', linewidth=2)
    axes[0].fill_between(df['mes_str'], df['total_viagens'], alpha=0.3)
    axes[0].set_xlabel('Mês')
    axes[0].set_ylabel('Total de Viagens')
    axes[0].set_title('Total de Viagens por Mês')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Gráfico 2: Total gasto
    axes[1].bar(df['mes_str'], df['total_gasto'], color='coral')
    axes[1].set_xlabel('Mês')
    axes[1].set_ylabel('Total Gasto (R$)')
    axes[1].set_title('Total Gasto por Mês')
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('graficos/analise_2_viagens_por_mes.png', dpi=300)
    print("✅ Gráfico salvo: graficos/analise_2_viagens_por_mes.png")
    plt.close()
    
    return df

def analise_3_tipo_pagamento(engine):
    """Análise 3: Distribuição de tipos de pagamento (GOLD)"""
    print("\n" + "="*60)
    print("📊 ANÁLISE 3 - DISTRIBUIÇÃO POR TIPO DE PAGAMENTO")
    print("="*60)
    
    query = """
    SELECT 
        tipo_pagamento,
        COUNT(*) AS quantidade,
        SUM(valor) AS total_valor,
        AVG(valor) AS valor_medio
    FROM silver_pagamento
    WHERE valor > 0
    GROUP BY tipo_pagamento
    ORDER BY total_valor DESC;
    """
    
    df = pd.read_sql_query(query, engine)
    print(df.to_string(index=False))
    
    # Gráficos
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Pizza - Quantidade
    cores = sns.color_palette('Set3', len(df))
    axes[0].pie(df['quantidade'], labels=df['tipo_pagamento'], autopct='%1.1f%%', colors=cores, startangle=90)
    axes[0].set_title('Distribuição por Tipo de Pagamento - Quantidade')
    
    # Gráfico 2: Barras - Total Valor
    bars = axes[1].bar(df['tipo_pagamento'], df['total_valor'], color=cores)
    axes[1].set_xlabel('Tipo de Pagamento')
    axes[1].set_ylabel('Total (R$)')
    axes[1].set_title('Total por Tipo de Pagamento')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Adicionar valores
    for bar, valor in zip(bars, df['total_valor']):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                    f'R$ {valor:,.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('graficos/analise_3_tipo_pagamento.png', dpi=300)
    print("✅ Gráfico salvo: graficos/analise_3_tipo_pagamento.png")
    plt.close()
    
    return df

def analise_4_resumo_mensal_gold(engine):
    """Análise 4: Resumo mensal da tabela GOLD"""
    print("\n" + "="*60)
    print("📊 ANÁLISE 4 - RESUMO MENSAL (GOLD)")
    print("="*60)
    
    query = """
    SELECT 
        DATE_TRUNC('month', mes) AS mes,
        COUNT(DISTINCT nome_orgao_superior) AS total_orgaos,
        SUM(total_viagens) AS total_viagens,
        SUM(total_gasto) AS total_gasto,
        AVG(gasto_medio_por_viagem) AS gasto_medio_global
    FROM gold_resumo_pagamentos_mensais
    GROUP BY mes
    ORDER BY mes;
    """
    
    df = pd.read_sql_query(query, engine)
    df['mes'] = pd.to_datetime(df['mes'])
    df['mes_str'] = df['mes'].dt.strftime('%Y-%m')
    print(df[['mes_str', 'total_orgaos', 'total_viagens', 'total_gasto']].to_string(index=False))
    
    # Gráfico
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Gráfico 1: Total de Órgãos
    axes[0, 0].bar(df['mes_str'], df['total_orgaos'], color='forestgreen')
    axes[0, 0].set_xlabel('Mês')
    axes[0, 0].set_ylabel('Quantidade')
    axes[0, 0].set_title('Total de Órgãos por Mês')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Gráfico 2: Total de Viagens
    axes[0, 1].bar(df['mes_str'], df['total_viagens'], color='darkorange')
    axes[0, 1].set_xlabel('Mês')
    axes[0, 1].set_ylabel('Quantidade')
    axes[0, 1].set_title('Total de Viagens por Mês')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Gráfico 3: Total Gasto
    axes[1, 0].bar(df['mes_str'], df['total_gasto'], color='crimson')
    axes[1, 0].set_xlabel('Mês')
    axes[1, 0].set_ylabel('Total Gasto (R$)')
    axes[1, 0].set_title('Total Gasto por Mês')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Gráfico 4: Gasto Médio
    axes[1, 1].plot(df['mes_str'], df['gasto_medio_global'], marker='o', color='purple', linewidth=2)
    axes[1, 1].set_xlabel('Mês')
    axes[1, 1].set_ylabel('Gasto Médio (R$)')
    axes[1, 1].set_title('Gasto Médio Global por Mês')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graficos/analise_4_resumo_mensal_gold.png', dpi=300)
    print("✅ Gráfico salvo: graficos/analise_4_resumo_mensal_gold.png")
    plt.close()
    
    return df

def analise_5_duracao_viagens(engine):
    """Análise 5: Distribuição da duração das viagens"""
    print("\n" + "="*60)
    print("📊 ANÁLISE 5 - DURAÇÃO DAS VIAGENS")
    print("="*60)
    
    query = """
    SELECT 
        CASE 
            WHEN duracao_dias <= 1 THEN '1 dia'
            WHEN duracao_dias <= 3 THEN '2-3 dias'
            WHEN duracao_dias <= 7 THEN '4-7 dias'
            WHEN duracao_dias <= 15 THEN '8-15 dias'
            WHEN duracao_dias <= 30 THEN '16-30 dias'
            ELSE 'Mais de 30 dias'
        END AS categoria_duracao,
        COUNT(*) AS total_viagens,
        AVG(valor_total) AS valor_medio,
        SUM(valor_total) AS total_gasto
    FROM silver_viagem
    WHERE duracao_dias >= 0
    GROUP BY categoria_duracao
    ORDER BY MIN(duracao_dias);
    """
    
    df = pd.read_sql_query(query, engine)
    print(df.to_string(index=False))
    
    # Gráfico
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Total de viagens por categoria
    cores = sns.color_palette('Blues_r', len(df))
    axes[0].bar(df['categoria_duracao'], df['total_viagens'], color=cores)
    axes[0].set_xlabel('Duração')
    axes[0].set_ylabel('Total de Viagens')
    axes[0].set_title('Total de Viagens por Duração')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Adicionar valores
    for i, valor in enumerate(df['total_viagens']):
        axes[0].text(i, valor + 100, f'{valor:,}', ha='center', va='bottom', fontsize=9)
    
    # Gráfico 2: Valor médio por categoria
    axes[1].bar(df['categoria_duracao'], df['valor_medio'], color='coral')
    axes[1].set_xlabel('Duração')
    axes[1].set_ylabel('Valor Médio (R$)')
    axes[1].set_title('Valor Médio por Duração')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Adicionar valores
    for i, valor in enumerate(df['valor_medio']):
        axes[1].text(i, valor + 50, f'R$ {valor:,.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('graficos/analise_5_duracao_viagens.png', dpi=300)
    print("✅ Gráfico salvo: graficos/analise_5_duracao_viagens.png")
    plt.close()
    
    return df

def main():
    print("="*60)
    print("🏆 CAMADA GOLD - ANÁLISES E VISUALIZAÇÕES")
    print("="*60)
    
    try:
        engine = conectar_banco()
        
        # 1. Criar tabela Gold
        criar_tabela_gold(engine)
        
        # 2. Executar análises
        analise_1_top_orgaos(engine)
        analise_2_viagens_por_mes(engine)
        analise_3_tipo_pagamento(engine)
        analise_4_resumo_mensal_gold(engine)
        analise_5_duracao_viagens(engine)
        
        # 3. Resumo final
        print("\n" + "="*60)
        print("📊 RESUMO FINAL - CAMADA GOLD")
        print("="*60)
        
        # Verificar tabela Gold
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM gold_resumo_pagamentos_mensais"))
            count = result.scalar()
            print(f"   gold_resumo_pagamentos_mensais: {count:,} registros")
            
            result = conn.execute(text("SELECT COUNT(*) FROM vw_resumo_pagamentos_mensais"))
            count = result.scalar()
            print(f"   vw_resumo_pagamentos_mensais: {count:,} registros (VIEW)")
        
        print("\n📁 Gráficos salvos na pasta 'graficos/'")
        print("\n✅ CAMADA GOLD CONCLUÍDA COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
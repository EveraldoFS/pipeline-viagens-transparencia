import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def criar_tabelas():
    try:
        # Conexão com o banco de dados
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "postgres")
        )
        cursor = conn.cursor()
        
        print("📖 Lendo o arquivo 0_criar_banco_simples.sql...")
        
        # Lê o arquivo novo sem acentos
        with open("0_criar_banco_simples.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        print("✅ Arquivo lido com sucesso!")
        print("🚀 Criando as tabelas no banco de dados...")
        
        # Executa o script SQL
        cursor.execute(sql_script)
        conn.commit()
        
        print("\n✅ SUCESSO! Todas as 8 tabelas foram criadas com sucesso!")
        print("   📊 Camada RAW (dados brutos):")
        print("   - raw_viagem")
        print("   - raw_passagem")
        print("   - raw_pagamento")
        print("   - raw_trecho")
        print("   📊 Camada SILVER (dados tratados):")
        print("   - silver_viagem")
        print("   - silver_passagem")
        print("   - silver_pagamento")
        print("   - silver_trecho")
        
        # Verifica se as tabelas foram criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_%'
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        print("\n📋 Tabelas existentes no banco:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎯 Proximo passo: Executar o script 1_extrair.py para carregar os dados!")
        
    except psycopg2.Error as e:
        print(f"\n❌ ERRO DE BANCO DE DADOS: {e}")
        print("\n💡 Verifique se:")
        print("   - O PostgreSQL esta rodando")
        print("   - As credenciais no arquivo .env estao corretas")
        print("   - O banco de dados existe")
        
    except FileNotFoundError:
        print("\n❌ ERRO: Arquivo 0_criar_banco_simples.sql nao encontrado!")
        print("💡 Verifique se o arquivo esta na mesma pasta que este script")
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO CRIACAO DAS TABELAS DO PROJETO")
    print("=" * 60)
    criar_tabelas()
    print("\n" + "=" * 60)
    print("🏁 FIM DA EXECUCAO")
    print("=" * 60)
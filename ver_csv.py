import os
import pandas as pd

print("="*70)
print("🔍 ANALISANDO CSVs NA PASTA data/")
print("="*70)

# Caminho da pasta data
pasta_data = 'data'

if not os.path.exists(pasta_data):
    print(f"\n❌ Pasta '{pasta_data}' não encontrada!")
    print("📂 Pastas disponíveis:", os.listdir('.'))
    exit()

print(f"\n📂 Conteúdo da pasta '{pasta_data}':")
for arquivo in os.listdir(pasta_data):
    print(f"   - {arquivo}")

# Procura apenas os CSVs que começam com 2025
csvs = []
for arquivo in os.listdir(pasta_data):
    if arquivo.endswith('.csv') and '2025' in arquivo:
        csvs.append(os.path.join(pasta_data, arquivo))

if not csvs:
    print("\n❌ Nenhum CSV 2025 encontrado!")
    exit()

print(f"\n📋 CSVs encontrados: {len(csvs)}")
for csv in csvs:
    print(f"   - {csv}")

print("\n" + "="*70)
print("📋 ANALISANDO COLUNAS DE CADA CSV")
print("="*70)

for csv_file in csvs:
    try:
        # Detecta separador
        with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            sep = ';' if ';' in first_line else ',' if ',' in first_line else '\t'
        
        print(f"\n📄 {os.path.basename(csv_file)}")
        print(f"   Separador: '{sep}'")
        
        # Lê apenas os cabeçalhos
        df = pd.read_csv(csv_file, sep=sep, nrows=0, encoding='utf-8', dtype=str)
        
        print(f"   Total de colunas: {len(df.columns)}")
        print(f"   Colunas:")
        for i, col in enumerate(df.columns, 1):
            print(f"      {i:2d}. {repr(col)}")
            
    except Exception as e:
        print(f"\n❌ Erro ao ler {csv_file}: {e}")

print("\n" + "="*70)
print("✅ FIM DA ANÁLISE")
print("="*70)
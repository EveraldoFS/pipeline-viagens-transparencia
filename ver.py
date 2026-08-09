import pandas as pd

arquivos = ['2025_Viagem.csv', '2025_Passagem.csv', '2025_Pagamento.csv', '2025_Trecho.csv']

for f in arquivos:
    try:
        df = pd.read_csv(f, sep=';', nrows=0, encoding='latin1')
        print(f"\n{f}:")
        print(f"  {list(df.columns)}")
    except Exception as e:
        print(f"\n{f}: ERRO - {e}")
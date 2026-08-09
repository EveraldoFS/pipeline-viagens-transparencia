import time
import importlib

extrair_module = importlib.import_module("1_extrair")
transformar_module = importlib.import_module("2_transformar")
gold_module = importlib.import_module("3_gold")

def executar_pipeline():
    inicio = time.time()
    print("=" * 60)
    print("INICIANDO PIPELINE DE DADOS: VIAGENS TRANSPARÊNCIA")
    print("=" * 60)

    try:
        # Etapa 1: Camada Raw
        print("\n[ETAPA 1/3] EXTRAÇÃO E CARGA RAW...")
        extrair_module.extrair_e_carregar_raw()

        # Etapa 2: Camada Silver
        print("\n[ETAPA 2/3] TRANSFORMAÇÃO E CARGA SILVER...")
        transformar_module.transformar_e_carregar_silver()

        # Etapa 3: Camada Gold
        print("\n[ETAPA 3/3] GERAÇÃO DE MÉTRICAS E CAMADA GOLD...")
        gold_module.gerar_camada_gold()

        fim = time.time()
        tempo_total = round(fim - inicio, 2)
        print("\n" + "=" * 60)
        print(f"PIPELINE EXECUTADO COM SUCESSO EM {tempo_total} SEGUNDOS!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] O pipeline foi interrompido: {e}")

if __name__ == "__main__":
    executar_pipeline()
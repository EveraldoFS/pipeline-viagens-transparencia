pipeline-viagens-transparencia/
├── README.md                    # Documentação do projeto
├── requirements.txt             # Dependências
├── .gitignore                   # Arquivos ignorados
├── 0_criar_banco.sql           # Criação das tabelas
├── 1_extrair.py                # Extração e carga RAW
├── 2_transformar.py            # Transformação RAW → SILVER
├── 3_gold.py                   # Análises e camada GOLD
├── transformacao.log           # Logs de transformação
└── graficos/                   # Pasta com gráficos
    ├── analise_1_top_orgaos.png
    ├── analise_2_viagens_por_mes.png
    ├── analise_3_tipo_pagamento.png
    ├── analise_4_resumo_mensal_gold.png
    └── analise_5_duracao_viagens.png
pandas>=2.0.0
psycopg2>=2.9.0
sqlalchemy>=2.0.0
requests>=2.31.0
matplotlib>=3.7.0
seaborn>=0.12.0
python-dotenv>=1.0.0

# Projeto Final – Pipeline de Dados de Viagens a Serviço

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Objetivos](#objetivos)
- [Fonte dos Dados](#fonte-dos-dados)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura da Solução](#arquitetura-da-solução)
- [Pipeline ETL](#pipeline-etl)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Perguntas de Negócio](#perguntas-de-negócio)
- [Principais Resultados](#principais-resultados)
- [Visualizações](#visualizações)
- [Como Executar o Projeto](#como-executar-o-projeto)
- [Melhorias Futuras](#melhorias-futuras)
- [Licença](#licença)
- [Autor](#autor)

---

## Sobre o Projeto

Este projeto foi desenvolvido como requisito de avaliação da disciplina de **Análise de Dados**.

O objetivo foi construir um pipeline de ETL para extração, tratamento, modelagem e análise de dados de viagens a serviço da Administração Pública Federal.

Os dados foram armazenados em um banco de dados PostgreSQL seguindo a **Arquitetura Medalhão (Raw, Silver e Gold)** .

---

## Objetivos

- Automatizar a extração dos dados
- Realizar o tratamento e a padronização dos dados
- Modelar o banco de dados com integridade referencial
- Construir um pipeline ETL organizado
- Desenvolver consultas analíticas para responder perguntas de negócio
- Produzir visualizações para interpretação dos resultados

---

## Fonte dos Dados

Os dados foram obtidos a partir do **Portal da Transparência do Governo Federal**.

---

## Tecnologias Utilizadas

- **Python** – Linguagem principal
- **PostgreSQL** – Banco de dados
- **SQLAlchemy** – ORM e conexão com banco
- **Pandas** – Manipulação de dados
- **Matplotlib** – Geração de gráficos
- **Seaborn** – Visualização de dados
- **Jupyter Notebook** – Análises exploratórias
- **Requests** – Download de arquivos
- **Git** e **GitHub** – Controle de versão

---

## Arquitetura da Solução

O projeto foi estruturado seguindo a **Arquitetura Medalhão**.

### Camada Raw

Armazenamento dos dados exatamente como extraídos da fonte original.

### Camada Silver

Limpeza, padronização e modelagem dos dados com conversão de tipos, tratamento de valores, PK, FK e constraints.

### Camada Gold

Consolidação das informações com JOIN, GROUP BY, agregações, tabela e VIEW para análises.

---

## Pipeline ETL

1. Criação da estrutura do banco de dados
2. Extração automatizada dos arquivos
3. Carga da camada Raw
4. Limpeza e transformação
5. Carga da camada Silver
6. Construção da camada Gold
7. Análise dos dados e visualizações

---

## Estrutura do Projeto

pipeline-viagens-transparencia/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── 3_gold.py
├── 3_analise.ipynb
├── banco.py
├── transformacao.log
├── graficos/
│ ├── analise_1_top_orgaos.png
│ ├── analise_2_viagens_por_mes.png
│ ├── analise_3_tipo_pagamento.png
│ ├── analise_4_resumo_mensal_gold.png
│ └── analise_5_duracao_viagens.png
└── data/


---

## Perguntas de Negócio

Foram respondidas **4 perguntas de negócio**.

### 1. Viagens urgentes custam mais por dia?

**Fonte:** silver_viagem

**Insight:** Viagens urgentes custam **17,6% mais por dia** (R$ 892,21 vs R$ 758,43).

**Recomendação:** Planejar viagens com antecedência reduz custos.

### 2. Custo médio diário vs duração da viagem?

**Fonte:** silver_viagem

**Insight:** O custo médio diário é maior em viagens de 1 dia (R$ 1.181,61) e diminui em viagens mais longas.

**Recomendação:** Viagens mais longas diluem o custo fixo.

### 3. Evolução mensal dos pagamentos?

**Fonte:** gold_resumo_pagamentos_mensais

**Insight:** DIÁRIAS lideram os pagamentos em todos os meses.

**Recomendação:** Monitorar sazonalidade dos gastos.

### 4. Perfil de gasto dos órgãos pagadores?

**Fonte:** gold_resumo_pagamentos_mensais

**Insight:** Justiça e Defesa têm alto volume e ticket baixo; Relações Exteriores têm ticket alto.

**Recomendação:** Focar otimização nos maiores gastadores.

---

## Principais Resultados

| Insight | Dado |
|---------|------|
| Maior gastador | Ministério da Justiça: R$ 830,3 milhões |
| Tipo mais comum | DIÁRIAS: 872.637 registros |
| Duração mais comum | 1 dia: 251.164 viagens |
| Total de viagens | 812.048 |
| Total gasto | ~R$ 2,5 bilhões |
| Urgência | 17,6% mais caras por dia |
| Custo por dia | 1 dia: R$ 1.182/dia |

---

## Visualizações

| Gráfico | Descrição |
|---------|-----------|
| analise_1_top_orgaos.png | Top 10 órgãos que mais gastaram |
| analise_2_viagens_por_mes.png | Viagens e gastos por mês |
| analise_3_tipo_pagamento.png | Distribuição por tipo de pagamento |
| analise_4_resumo_mensal_gold.png | Resumo mensal (Gold) |
| analise_5_duracao_viagens.png | Duração das viagens |

---

## Como Executar o Projeto

### 1. Clone o repositório

git clone https://github.com/EveraldoFS/pipeline-viagens-transparencia.git
cd pipeline-viagens-transparencia

### 2. Crie um ambiente virtual

python -m venv venv

### 3. Ative o ambiente virtual

source venv/bin/activate

### 4. Instale as dependências

pip install -r requirements.txt

### 5. Configure o arquivo .env

cp .env.example .env

### 6. Execute o projeto

# Criação das tabelas
psql -U postgres -d db_viagens -f 0_criar_banco.sql

# Extração e carga RAW
python 1_extrair.py

# Transformação RAW -> SILVER
python 2_transformar.py

# Análises e camada GOLD
python 3_gold.py

# Visualizar análises no notebook
jupyter notebook 3_analise.ipynb

---

## Melhorias Futuras

- Dashboard Interativo com Streamlit ou Power BI
- Pipeline Agendado com Apache Airflow
- Data Warehouse com modelagem dimensional
- Previsão de Gastos com Machine Learning
- API REST para disponibilizar dados
- Alertas para anomalias nos gastos
- Containerização com Docker
- Testes Automatizados com pytest
- Atualização periódica automática dos dados

### Prioridade de Implementação

| Prioridade | Melhoria | Impacto |
|------------|----------|---------|
| Alta | Dashboard Interativo | Visualização imediata |
| Média | Pipeline Agendado | Redução de trabalho manual |
| Baixa | Machine Learning | Valor agregado a longo prazo |

---

## Licença

Este projeto foi desenvolvido para fins acadêmicos e educacionais.

---

## Autor

**EveraldoFS**

- GitHub: https://github.com/EveraldoFS

  

  

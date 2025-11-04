# ANÁLISE DE DADOS DE CRIPTOMOEDAS
> PROJETO FINAL DE BIG DATA - 15/09/2025 - 13/10/2025
<p align="center"> <img src="https://img.shields.io/badge/Tecnologia-PySpark%20%7C%20Pandas%20%7C%20PostgreSQL-306998?style=for-the-badge&logo=apachespark&logoColor=white&labelColor=282c34" /> </p>

## Visão Geral do Projeto
Este projeto consiste em um pipeline de **Big Data** para processamento e análise de um grande volume de transações de criptomoedas da Binance. O objetivo principal é extrair insights valiosos sobre a **volatilidade**, a **agressividade de mercado** e a **correlação** entre diversas Altcoins e seus principais pares (*Bitcoin e Ethereum*).

------------------------------------------
## 1. Arquitetura e Fluxo de Dados
O projeto implementa uma arquitetura robusta e híbrida para lidar com o volume massivo de dados (28GB), focando na redução e padronização para análise de alta qualidade.

### Fluxo do Pipeline:

    ````mermaid`
    graph TD
        A[Kaggle/Binance (28GB, 1 min, Parquet)] --> B{Tratamento Pandas};
        B --> C{Downsampling PySpark};
        C --> D[PostgreSQL (2GB, 30 min, data_cripto)];
        D --> E[Queries SQL e Gráficos Analíticos];
        E --> F(Insights Finais);

        style A fill:#f9f,stroke:#333
        style D fill:#ccf,stroke:#333

## 2. Extração e Tratamento dos Dados
A principal etapa do projeto foi transformar o dataset inicial de 28GB em um conjunto de dados limpo e analiticamente útil de **2GB**.

### 2.1. Extração dos Dados
- **Fonte Original:** `Kaggle` (Transações da Binance).
- **Volume Inicial:** **28GB** em formato **Parquet** (dados a cada **1 minuto**).
- **Estratégia Parquet:** Utilização de **Parquet** para que ferramentas de consulta pudessem acessar apenas dados relevantes, otimizando I/O.

### 2.2. Pipeline de Tratamento
| Etapa | Ferramenta | Descrição |
| :--- | :--- | :--- |
| **Filtros Iniciais** | `Pandas` | Redução de dados para transações que envolviam apenas pares **BTC** ou **ETH**. |
| **Timestamp** (`tratamento_panda.py`) | `Pandas` | Conversão e padronização do formato do *timestamp* (resolvendo problemas de tipo de dado para o `PySpark`/`PostgreSQL`) |
| **Downsampling** (`REAL.py`) | `PySpark` | Redução da granularidade dos dados de 1 minuto para **30 minutos** (1800 segundos), consolidando métricas OHLCV. |
| **Colunas Finais** | `Pandas` | Seleção das colunas chave: `open`, `high`, `low`, `close`, `volume`, e métricas de agressividade (`taker_buy_...`). |
| **Formato Intermediário** | `Pandas` | Conversão dos arquivos `Parquet` tratados para **CSV** para facilitar a ingestão no `PostgreSQL`. |

### 2.3. Desafio PySpark
Houve um problema inicial na leitura do tipo do timestamp pelo `PySpark`, que foi contornado:
    **Resolução:** Ajuste no ambiente para compatibilidade (**Java 17, Hadoop 3.3, PySpark 3.5**) e utilização do `Pandas` para pré-processar o timestamp antes de injetar no *DataFrame* Spark.

## 3. Armazenamento e Consulta
### 3.1. Armazenamento (`postgres.py`)
- **Banco de Dados:** PostgreSQL
- **Nome do Banco:** `bigdata_cripto` (na porta `5433`)
- **Tabela:** `dados_kline_30min`
- **Processo:** O script `postgres.py` gerencia a conexão e a importação dos múltiplos arquivos CSV (dados em 30 min) para o banco de dados.

### 3.2. Estrutura de Dados
Os arquivos Parquet finais confirmam a base de dados para análise:
- `dados/criptomoedas/BTC/`: Altcoins tratadas em relação ao Bitcoin (ex: 1INCH-BTC, AAVE-BTC, ADA-BTC, ALICE-BTC).
- `dados/criptomoedas/ETH/`: Altcoins tratadas em relação ao Ethereum (ex: AAVE-ETH, ADA-ETH, ARK-ETH, BAT-ETH).

## 4. Insights Chave Gerados
A análise de dados limpos no PostgreSQL permitiu a geração de insights críticos sobre o comportamento do mercado de criptomoedas:

### A. Correlação de Mercado Entre BTC e ETH
- **Ferramenta:** Query SQL (`coeficiente_relacao.sql`) usando a função `CORR()`.
- **Resultado:** Cálculo do **Coeficiente de Correlação de Pearson** entre os preços de `close` de BTCUSDT e ETHUSDT.
    *Este resultado é a **prova analítica** da forte codependência de preço entre os dois ativos líderes.*

### B. Volatilidade Relativa
- **Visualização:** Gráfico de Pizza (`pizza_criptos.png`)
- **Análise:** Compara a proporção de volatilidade de várias Altcoins em relação ao BTC (pares `*-BTC`).
- **Conclusão:** Ajuda a quantificar o risco relativo de cada ativo comparado ao Bitcoin.

### C. Agressividade de Mercado
- **Visualização:** Gráfico de Linha (`agressividade BTC ETH.png`)
- **Análise:** Estudo da `agressividade_liquida` (volume de compradores vs. vendedores) e sua influência na média de preços ETH/BTC.
- **Conclusão:** Demonstra como o desequilíbrio na pressão de negociação afeta a direção de preço dos pares principais.
-------------------------------------------------------------------
## Créditos:
### Autores
* [**@eopabro** - Pablo Henrique](https://github.com/eopabro) 
* [**@LucaAtanazio** - Luca Atanazio](https://github.com/LucaAtanazio) 
### Professor
*  [**@Willgnner-Santos** - Willgnner Ferreira Santos](https://github.com/Willgnner-Santos) - BIG DATA
  
> **Licença:** MIT License [FACULDADE DE TEC SENAI DE DESENV.GERENCIAL / Uso Acadêmico]
  



# Dashboard de Controle: Simulação Avançada de TTL (Mocking Time)

Simulação de Cache com TTL para Otimização de Consultas

**Equipe:** Luca Atanazio - Lucas Faria - Pablo Henrique

---

## OBJETIVO DO PROJETO

Este projeto demonstra a arquitetura de um sistema de cache utilizando o conceito de **Time-To-Live (TTL)**, semelhante ao implementado por soluções como o Memcached. O foco é simular a otimização de consultas de dados frequentemente acessados, como preços e níveis de estoque, em um cenário de **Hortifrúti**, onde a validade e a volatilidade dos dados (preço/estoque) são críticas.

---

## TECNOLOGIAS E BIBLIOTECAS UTILIZADAS

O projeto foi desenvolvido inteiramente em Python e utiliza as seguintes bibliotecas para construir tanto a lógica de *backend* (cache) quanto a interface de *frontend* (dashboard):

* **Streamlit:** Utilizado para criar a interface do usuário (UI). O Streamlit permite transformar scripts Python em aplicações web interativas com facilidade, sendo essencial para visualizar o estado do cache e as interações do funcionário.
* **Pandas:** Usado para estruturar e formatar os dados do cache em um `DataFrame`. Isso garante uma visualização clara e organizada do Status da Cache para o usuário.
* **Time:** Biblioteca padrão do Python, fundamental para o controle do TTL. Ela é usada para medir o tempo atual (`time.time()`) e calcular o momento exato de expiração dos registros (`expiry_time`).

---

## USO DE "Mocking Time" PARA O CONTROLE DE VALIDADE

O desafio em simular TTLs de longa duração (como dias ou semanas) é a impossibilidade de aguardar o tempo real na demonstração. Para resolver isso, implementamos o conceito de **Mocking Time (Relógio Falso)**:

1.  **Offset de Tempo:** Uma variável de estado (`st.session_state.time_offset`) armazena o tempo lógico que foi artificialmente avançado.
2.  **Relógio Falso:** A função `get_current_time()` substitui o `time.time()` e retorna o tempo real **mais** o *Offset* acumulado.
3.  **Salto Temporal:** O funcionário pode, em um clique, adicionar 86.400 segundos (1 dia) ou mais ao *Offset*, forçando a expiração imediata dos registros antigos, enquanto o tempo de espera real é de apenas **10 segundos** para efeito visual.

Essa técnica permite a simulação realista da validade de alimentos em hortifrutis, como a maça (TTL de 14 dias) ou o estoque de morango (TTL de 3 dias), provando o conceito de TTL sem a necessidade de longas esperas.

---

## FERRAMENTAS DO FUNCIONÁRIO (Interações com o Cache)

O Dashboard oferece três ferramentas principais que simulam a interação de uma aplicação de varejo com o Memcached:

### 1. Novo Registro (SET)

* **Função:** Adiciona ou atualiza um item no cache, definindo seu **Time-To-Live (TTL)** em segundos.
* **Cenário de Uso:** Quando o sistema de estoque recebe uma nova remessa ou o gerente define um novo preço, o dado é registrado com uma validade. Por exemplo, o preço da alface pode ter um TTL de 7 dias.

### 2. Consultar (GET)

* **Função:** Tenta recuperar um dado do cache.
* **Resultados:**
    * **Cache HIT (Sucesso):** O dado é encontrado e está válido.
    * **Cache MISS (Falha):** O dado não está no cache ou **expirou** (seu TTL chegou a zero), indicando que o sistema deve buscar a informação no Banco de Dados principal para recarregá-la.

### 3. Salto Temporal & Invalidação (DELETE)

* **Salto Temporal:** A ferramenta que usa o **Mocking Time** para avançar o relógio lógico em até 7 dias, permitindo testar a expiração automática de longos TTLs em segundos.
* **Invalidação Manual (DELETE):** Permite que um funcionário (ou um sistema de controle de qualidade) force a remoção imediata de um registro específico.
    * **Cenário de Uso:** Se o estoque de tomates estragar subitamente, o funcionário usa o **DELETE** para invalidar o registro imediatamente. A próxima consulta **GET** resultará em um **Cache MISS**, forçando a busca do novo estoque (zero) no banco principal.

---

## APLICAÇÃO PRÁTICA EM HORTIFRUTIS

Este sistema simula o gerenciamento de dados de produtos perecíveis, onde a latência é baixa (clientes consultando preços) e a validade é alta:

* **Preços (TTL Médio):** Itens como maçãs ou uvas têm TTLs de 3 a 5 dias, pois seus preços não mudam diariamente.
* **Estoque (TTL Longo):** Itens não perecíveis em grandes quantidades, como estoque de caixas de cebola, podem ter TTLs de 90 dias, pois são estáveis.
* **Itens Perecíveis (TTL Curto/Médio):** O estoque de alface tem um TTL de 7 dias, exigindo uma atualização mais frequente para refletir a alta rotatividade ou o descarte.

O uso deste dashboard valida a eficácia do cache para a **otimização de consultas**, reduzindo a carga no banco de dados principal e garantindo que o cliente sempre receba a informação mais **confiável** e atualizada, seja pela expiração automática (TTL) ou pela invalidação manual (DELETE).
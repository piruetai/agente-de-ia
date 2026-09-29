# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores (data, canal, tema e resumo de atendimentos passados) |
| `perfil_investidor.json` | JSON | Personalizar recomendações com base em perfil de risco, renda, patrimônio, tolerância a risco (`aceita_risco`) e metas financeiras |
| `produtos_financeiros.json` | JSON | Sugerir produtos compatíveis com o perfil e a tolerância a risco do cliente |
| `transacoes.csv` | CSV | Analisar padrão de gastos e receitas do cliente, por categoria e no período disponível |

---

## Adaptações nos Dados

Os quatro arquivos mockados fornecidos não foram alterados em seu conteúdo. A adaptação feita foi de **pré-processamento**, não dos dados em si: antes de entregar qualquer informação ao modelo, um módulo Python (`contexto_mia.py`) lê os quatro arquivos e calcula, fora do LLM, as métricas que a Mia precisa citar:

- Percentual de progresso de cada meta e valor que falta;
- Aporte mensal necessário para completar cada meta no prazo;
- Totais de entradas, saídas e saldo do período das transações;
- Gastos agrupados por categoria, com percentual sobre o total.

Essa decisão veio diretamente dos testes de avaliação: quando o modelo tentava fazer esses cálculos sozinho, ele errava (ex.: respondeu um aporte mensal de R$ 5.000,00 em vez de R$ 625,00). Ao pré-calcular tudo em código e instruir o modelo a apenas citar os números prontos (regra 6 do system prompt), esse tipo de erro foi eliminado.

Também identificamos uma lacuna nos dados originais: a meta "Entrada do apartamento" não tem um campo de valor já acumulado, só o valor necessário e o prazo. Em vez de o modelo inventar um valor, o código sinaliza explicitamente "valor acumulado NÃO informado nos dados" quando esse campo não existe, e o system prompt instrui a Mia a admitir essa limitação.

---

## Estratégia de Integração

### Como os dados são carregados?

Os quatro arquivos (`perfil_investidor.json`, `produtos_financeiros.json`, `transacoes.csv` e `historico_atendimento.csv`) são carregados uma única vez, no início da execução do `app.py` (Streamlit), a partir da pasta `data/`. Eles ficam em memória durante toda a sessão — não há releitura do disco a cada pergunta do cliente.

### Como os dados são usados no prompt?

Os dados não entram diretamente no system prompt. O fluxo é:

1. Os quatro arquivos passam pela função `montar_contexto()`, que gera um bloco de texto único (o "CONTEXTO DO CLIENTE") já com os cálculos prontos, as transações recentes, o histórico de atendimento e o catálogo de produtos formatado em JSON.
2. Esse contexto é montado uma vez por sessão e reaproveitado em todas as perguntas.
3. A cada pergunta, a função `perguntar(msg)` monta o prompt enviado ao Ollama concatenando três partes: o **SYSTEM_PROMPT** (regras fixas de comportamento da Mia, que não mudam por cliente), o **CONTEXTO DO CLIENTE** (dinâmico, gerado no passo 1) e a **pergunta do cliente**.

Ou seja: as regras de comportamento são estáticas, e os dados do cliente são injetados dinamicamente a cada chamada — mas calculados só uma vez por sessão, não recalculados a cada pergunta.

---

## Exemplo de Contexto Montado

```
DATA DE REFERÊNCIA: 2025-10-25

CLIENTE: João Silva, 32 anos, Analista de Sistemas
PERFIL: moderado | ACEITA RISCO: não
RENDA MENSAL: R$ 5.000,00
OBJETIVO PRINCIPAL: Construir reserva de emergência
PATRIMÔNIO: R$ 15.000,00 | RESERVA DE EMERGÊNCIA: R$ 10.000,00

METAS:
- Completar reserva de emergência: valor necessário R$ 15.000,00 | prazo 2026-06 (8 meses) | acumulado R$ 10.000,00 (66,7%) | faltam R$ 5.000,00 | aporte mensal necessário ≈ R$ 625,00
- Entrada do apartamento: valor necessário R$ 50.000,00 | prazo 2027-12 (26 meses) | valor acumulado NÃO informado nos dados

RESUMO DO PERÍODO DAS TRANSAÇÕES:
- Entradas: R$ 5.000,00
- Saídas: R$ 2.488,90
- Saldo: R$ 2.511,10

GASTOS POR CATEGORIA:
- moradia: R$ 1.380,00 (55,4% dos gastos)
- alimentacao: R$ 570,00 (22,9% dos gastos)
- transporte: R$ 295,00 (11,9% dos gastos)
- saude: R$ 188,00 (7,6% dos gastos)
- lazer: R$ 55,90 (2,2% dos gastos)

TRANSAÇÕES RECENTES:
(tabela completa do transacoes.csv)

ATENDIMENTOS ANTERIORES:
(tabela completa do historico_atendimento.csv)

PRODUTOS DISPONÍVEIS:
(JSON completo do produtos_financeiros.json)
```

Esse bloco é o que a função `montar_contexto()` gera de fato (função disponível em `contexto_mia.py`), com valores já calculados — não é uma simulação simplificada do que o agente recebe.

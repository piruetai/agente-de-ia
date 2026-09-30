# Código da Aplicação

Esta pasta contém o código do seu agente financeiro.

## Estrutura

```
src/
├── app.py              # Aplicação principal (Streamlit/Gradio)
├── config.py
├── contextom.py
├── dados.py
├── prompt.py
└── requirements.txt    # Dependências
```

## requirements.txt

```
pandas
requests
streamlit

```

## Como Rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
streamlit run app.py
```

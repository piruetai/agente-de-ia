import pandas as pd
import json
import streamlit as st
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
@st.cache_data
def carregar_dados():
    perfil = json.load(open(DATA_DIR / "perfil_investidor.json", encoding="utf-8"))
    transacoes = pd.read_csv(DATA_DIR / "transacoes.csv")
    historico = pd.read_csv(DATA_DIR / "historico_atendimento.csv")
    produtos = json.load(open(DATA_DIR / "produtos_financeiros.json", encoding="utf-8"))
    return perfil, transacoes, historico, produtos

perfil, transacoes, historico, produtos = carregar_dados()
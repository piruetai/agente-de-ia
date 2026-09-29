import streamlit as st
import requests

# Importações
from contextom import contexto
from config import OLLAMA_URL, MODELO, ICONE
from prompt import SYSTEM_PROMPT


# ============ CHAMAR OLLAMA ============
def perguntar(msg):
    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    r = requests.post(OLLAMA_URL, 
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False
        },
        timeout=500
    )

    r.raise_for_status()

    return r.json()["response"]


# ============ Interface ============
st.title("📈 Mia, sua consultora pessoal!")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []


# ============ HISTÓRICO ============
for autor, texto in st.session_state.mensagens:

    if autor == "user":
        st.chat_message("user").write(texto)

    elif autor == "assistant":
        st.chat_message(
            "assistant",
            avatar="../assets/avatar.png"
        ).write(texto.replace("$", r"\$"))


# ============ NOVA MENSAGEM ============
if pergunta := st.chat_input("Como posso ajudar?"):

    st.session_state.mensagens.append(("user", pergunta))

    st.chat_message("user").write(pergunta)

    with st.spinner("Mia está pensando..."):

        resposta = perguntar(pergunta)

    st.session_state.mensagens.append(("assistant", resposta))

    st.chat_message("assistant", avatar=ICONE).write(resposta.replace("$", r"\$")
)
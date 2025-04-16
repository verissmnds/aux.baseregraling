import streamlit as st
import os
from datetime import datetime
import re

# Usuário e senha fixos
USUARIO_CORRETO = "dapplab@ling"
SENHA_CORRETA = "1.2.3.4"

# Função para checar parênteses
def checar_parenteses(texto):
    abertura = texto.count('(')
    fechamento = texto.count(')')
    if abertura > fechamento:
        return f"⚠️ Faltam {abertura - fechamento} parêntese(s) de fechamento.", "#fff3cd"
    elif fechamento > abertura:
        return f"⚠️ Faltam {fechamento - abertura} parêntese(s) de abertura.", "#fff3cd"
    else:
        return "✓ Parênteses balanceados.", "#d4edda"

# Configuração da página
st.set_page_config(page_title="Banco de dados de regras linguísticas", layout="wide")

# Alterando o estilo para manter os textos pretos e o fundo claro
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: white !important;  /* Fundo claro */
            color: black !important;  /* Texto preto */
            font-family: 'Proxima Nova', sans-serif !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: black !important;  /* Títulos em preto */
        }
        textarea, input, .stButton > button, .stRadio > div {
            font-size: 16px !important;
            color: black !important;  /* Textos em preto nos campos */
        }
        .stTextInput > div > div > input {
            background-color: #f5f5f5 !important;  /* Fundo claro para inputs */
        }
        .stTextArea > div > div > textarea {
            background-color: #f5f5f5 !important;  /* Fundo claro para text area */
        }
        .stButton > button {
            background-color: #f0f0f0 !important;  /* Fundo claro para botões */
        }
    </style>
""", unsafe_allow_html=True)

# Controle de sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown(""" 
<h1 style='font-family: "Proxima Nova", sans-serif; color: black; text-align: center;'>📚 Banco de dados de regras linguísticas</h1>
""", unsafe_allow_html=True)
    st.markdown(""" 
        <style>
        body {
            background-color: white;
            color: black;
            font-family: 'Proxima Nova', sans-serif;
            text-align: center;
        }
            textarea, input, .stButton > button {
                font-size: 16px;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<h2 style='font-family: Proxima Nova; color: black;'>🔐 Acesso restrito</h2>", unsafe_allow_html=True)
    col_login = st.columns(2)[1]
    with col_login:
        usuario = st.text_input("Usuário", key="usuario")
        senha = st.text_input("Senha", type="password", key="senha")
    if st.button("Entrar"):
        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")
    
    st.stop()

# Título principal
st.markdown(""" 
<h1 style='font-family: "Proxima Nova", sans-serif; color: black; text-align: center;'>📚 Banco de dados de regras linguísticas</h1>
""", unsafe_allow_html=True)

# Interface principal
abas = st.tabs(["Cadastrar nova regra linguística", "Buscar por regra linguística"])

with abas[0]:
    st.subheader("Cadastrar nova regra linguística")
    col1, col2 = st.columns(2)
    with col1:
        projeto = st.text_input("Nome do projeto")
        analista = st.text_input("Analista responsável")
        titulo_regra = st.text_input("Título da regra")
    with col2:
        regra = st.text_area("Elaboração de regras linguística", height=200)
        ferramenta = st.radio("Ferramenta utilizada", ["ELK", "FPK", "YT", "BW", "Outra"])

    if regra:
        operadores_permitidos = {
            "ELK": ["OR", "AND", "NOT"],
            "FPK": ["OR", "AND", "NOT"],
            "YT": ["|"],
            "BW": ["OR", "AND", "NEAR/", "~", "NOT"],
            "Outra": []
        }
        op_ativos = operadores_permitidos.get(ferramenta, [])

        st.markdown("**Visualização da regra com operadores destacados (campo 'Regra linguística aplicada'):**", unsafe_allow_html=True)

        if ferramenta != "Outra":
            regra_destacada = regra
            if "OR" in op_ativos:
                regra_destacada = re.sub(r'\bOR\b', '<span style="color:green;font-weight:bold">OR</span>', regra_destacada)
            if "AND" in op_ativos:
                regra_destacada = re.sub(r'\bAND\b', '<span style="color:blue;font-weight:bold">AND</span>', regra_destacada)
            if "NOT" in op_ativos:
                regra_destacada = re.sub(r'\bNOT\b', '<span style="color:red;font-weight:bold">NOT</span>', regra_destacada)
            if "NEAR/" in op_ativos:
                regra_destacada = re.sub(r'\bNEAR/\d+\b', lambda m: f'<span style="color:orange;font-weight:bold">{m.group()}</span>', regra_destacada)
            if "~" in op_ativos:
                regra_destacada = regra_destacada.replace("~", '<span style="color:purple;font-weight:bold">~</span>')
            if "|" in op_ativos:
                regra_destacada = regra_destacada.replace("|", '<span style="color:green;font-weight:bold">|</span>')
            st.markdown(f"<div style='padding:10px;border:1px solid #ddd;border-radius:5px'>{regra_destacada}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding:10px;border:1px solid #ddd;border-radius:5px'>{regra}</div>", unsafe_allow_html=True)

        alerta_parenteses, cor = checar_parenteses(regra)
        st.markdown(f"<div style='background-color:{cor};padding:10px;border-radius:5px'>{alerta_parenteses}</div>", unsafe_allow_html=True)

    data = st.text_input("Data do registro (opcional)", placeholder="AAAA-MM-DD")
    if st.button("Salvar entrada"):
        if projeto and analista and titulo_regra and regra:
            st.success("Entrada salva com sucesso!")
        else:
            st.warning("Preencha todos os campos obrigatórios.")

with abas[1]:
    st.subheader("Buscar por regra linguística")
    nome_projeto = st.text_input("Digite o nome da regra ou projeto para buscar")
    st.info("Esta funcionalidade foi desativada.")

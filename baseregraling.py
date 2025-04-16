import streamlit as st
import os
from datetime import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------- Configuração da API do Google Sheets ----------
# Caminho para o arquivo JSON com as credenciais da conta de serviço
CAMINHO_CREDENCIAL = "dappbaseregrasling-999bb55f05e8.json"  # coloque o nome correto do seu arquivo
ID_PLANILHA = "1qO_3WQkEnDI__xCLT_hsYWg0hYfRWpL2eCCf26QJLrs"


@st.cache_resource
def conectar_planilha():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(CAMINHO_CREDENCIAL, escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(ID_PLANILHA)
    
    # Acessar a aba correta pelo nome
    sheet = planilha.worksheet('160425')  # Nome da aba
    return sheet

# ---------- Função para checar parênteses ----------
def checar_parenteses(texto):
    abertura = texto.count('(')
    fechamento = texto.count(')')
    if abertura > fechamento:
        return f"⚠️ Faltam {abertura - fechamento} parêntese(s) de fechamento.", "#fff3cd"
    elif fechamento > abertura:
        return f"⚠️ Faltam {fechamento - abertura} parêntese(s) de abertura.", "#fff3cd"
    else:
        return "✓ Parênteses balanceados.", "#d4edda"

# ---------- Autenticação ----------
USUARIO_CORRETO = "dapplab@ling"
SENHA_CORRETA = "1.2.3.4"

st.set_page_config(page_title="Banco de dados de regras linguísticas", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: white !important;
            color: black !important;
            font-family: 'Proxima Nova', sans-serif !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: black !important;
        }
        textarea, input, .stButton > button, .stRadio > div {
            font-size: 16px !important;
            color: black !important;
        }
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #f5f5f5 !important;
        }
        .stButton > button {
            background-color: #f0f0f0 !important;
        }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: black;'>🔐 Acesso restrito</h2>", unsafe_allow_html=True)
    col_login = st.columns(2)[1]
    with col_login:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

st.markdown("<h1 style='text-align: center;'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)
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

        alerta_parenteses, cor = checar_parenteses(regra)
        st.markdown(f"<div style='background-color:{cor};padding:10px;border-radius:5px'>{alerta_parenteses}</div>", unsafe_allow_html=True)

    data = st.text_input("Data do registro (opcional)", placeholder="AAAA-MM-DD")
    if st.button("Salvar entrada"):
        if projeto and analista and titulo_regra and regra:
            nova_linha = [str(projeto).strip(), str(analista).strip(), str(titulo_regra).strip(),
                          str(regra).strip(), str(ferramenta).strip(), str(data or datetime.today().strftime('%Y-%m-%d'))]
            try:
                # Tente enviar a linha para o Google Sheets
                sheet.append_row(nova_linha)
                st.success("Entrada salva com sucesso na planilha do Google Sheets!")
            except gspread.exceptions.APIError as e:
                st.error(f"Ocorreu um erro ao salvar os dados: {e}")
                st.write("Detalhes do erro:", e.response)
        else:
            st.warning("Preencha todos os campos obrigatórios.")

with abas[1]:
    st.subheader("Buscar por regra linguística")
    nome_projeto = st.text_input("Digite o nome da regra ou projeto para buscar")
    st.info("Esta funcionalidade foi desativada.")

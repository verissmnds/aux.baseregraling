import streamlit as st
import pandas as pd
from datetime import datetime
import re

USUARIO_CORRETO = "dapplab@ling"
SENHA_CORRETA = "1.2.3.4"

# Banco de dados em memória
if "banco_dados" not in st.session_state:
    st.session_state.banco_dados = pd.DataFrame(columns=[
        "Projeto", "Analista", "Título da Regra", "Regra", "Ferramenta", "Data"
    ])

def salvar_em_memoria(projeto, analista, titulo_regra, regra, ferramenta, data):
    nova_linha = {
        "Projeto": projeto,
        "Analista": analista,
        "Título da Regra": titulo_regra,
        "Regra": regra,
        "Ferramenta": ferramenta,
        "Data": data or datetime.now().strftime("%Y-%m-%d")
    }
    st.session_state.banco_dados = pd.concat([
        st.session_state.banco_dados,
        pd.DataFrame([nova_linha])
    ], ignore_index=True)
    st.success("Entrada salva com sucesso!")

def buscar_por_termo(termo):
    df = st.session_state.banco_dados
    cond_proj = df["Projeto"].str.contains(termo, case=False, na=False)
    cond_regra = df["Regra"].str.contains(termo, case=False, na=False)
    df_filtro = df[cond_proj | cond_regra]
    if df_filtro.empty:
        return f"Nenhuma entrada encontrada para: {termo}"
    return df_filtro

def checar_parenteses(texto):
    abertura = texto.count('(')
    fechamento = texto.count(')')
    if abertura > fechamento:
        return f"⚠️ Faltam {abertura - fechamento} parêntese(s) de fechamento.", "#fff3cd"
    elif fechamento > abertura:
        return f"⚠️ Faltam {fechamento - abertura} parêntese(s) de abertura.", "#fff3cd"
    else:
        return "✓ Parênteses balanceados.", "#d4edda"

st.set_page_config(page_title="Banco de dados de regras linguísticas", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 class='centered'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='centered'>🔐 Acesso restrito</h2>", unsafe_allow_html=True)

    col_login = st.columns(3)[1]
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

        st.markdown("**Visualização da regra com operadores destacados:**", unsafe_allow_html=True)
        st.markdown(f"<div style='padding:10px;border:1px solid #ddd;border-radius:5px'>{regra_destacada}</div>", unsafe_allow_html=True)

        alerta_parenteses, cor = checar_parenteses(regra)
        st.markdown(f"<div style='background-color:{cor};padding:10px;border-radius:5px'>{alerta_parenteses}</div>", unsafe_allow_html=True)

    data = st.text_input("Data do registro (opcional)", placeholder="AAAA-MM-DD")
    if st.button("Salvar entrada"):
        if projeto and analista and titulo_regra and regra:
            salvar_em_memoria(projeto, analista, titulo_regra, regra, ferramenta, data)
        else:
            st.warning("Preencha todos os campos obrigatórios.")

with abas[1]:
    st.subheader("Buscar por regra linguística")
    nome_projeto = st.text_input("Digite o nome da regra ou projeto para buscar")

    if nome_projeto:
        resultado = buscar_por_termo(nome_projeto)
        if isinstance(resultado, str):
            st.info(resultado)
            resultado = pd.DataFrame(columns=st.session_state.banco_dados.columns)
    else:
        resultado = st.session_state.banco_dados

    for idx, row in resultado.iterrows():
        with st.expander(f"📄 {row['Título da Regra']} – {row['Projeto']}"):
            regra_formatada = row['Regra'].replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            st.markdown(f"""
            <div style='background-color: #1e1e1e; border-left: 4px solid #3399ff; border-right: 4px solid #3399ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-family: \"Proxima Nova\", sans-serif;'>
                <strong style='color: #00ffff;'>Elaboração de regras linguística:</strong><br><br>
                <code style='color: white;'>{regra_formatada}</code>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Analista:** {row['Analista']} | **Ferramenta:** {row['Ferramenta']} | **Data:** {row['Data']}")

            if st.button(f"🗑️ Deletar regra", key=f"del_{idx}"):
                if st.radio("Tem certeza que deseja excluir esta regra?", ["Não", "Sim"], index=0, key=f"confirma_{idx}") == "Sim":
                    st.session_state.banco_dados.drop(index=resultado.index[idx], inplace=True)
                    st.success("Regra deletada com sucesso!")
                    st.experimental_rerun()

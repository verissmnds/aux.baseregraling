import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
 
# Usuário e senha fixos
USUARIO_CORRETO = "dapplab@ling"
SENHA_CORRETA = "1.2.3.4"
 
# Caminho do arquivo CSV
csv_path = "queries_linguisticas.csv"
# Banco de dados em memória
if "banco_dados" not in st.session_state:
    st.session_state.banco_dados = pd.DataFrame(columns=[
        "Projeto", "Analista", "Título da Regra", "Regra", "Ferramenta", "Data"
    ])
 
# Função para salvar os dados
def salvar_csv(projeto, analista, titulo_regra, regra, ferramenta, data):
    nova_linha = {
        "Projeto": projeto,
        "Analista": analista,
        "Título da Regra": titulo_regra,
        "Regra": regra,
        "Ferramenta": ferramenta,
        "Data": data or datetime.now().strftime("%Y-%m-%d")
    }

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    else:
        df = pd.DataFrame([nova_linha])

    df.to_csv(csv_path, index=False)
    st.session_state.banco_dados = pd.concat([
        st.session_state.banco_dados,
        pd.DataFrame([nova_linha])
    ], ignore_index=True)
    st.success("Entrada salva com sucesso!")

# Função para buscar por regra ou projeto
def buscar_por_projeto(termo):
    if not os.path.exists(csv_path):
        return "Nenhum arquivo encontrado."

    df = pd.read_csv(csv_path)
    cond_proj = df["Projeto"].str.contains(termo, case=False, na=False)
    df_filtro = df[cond_proj]

    if df_filtro.empty:
        return f"Nenhuma entrada encontrada para: {termo}"
    return df_filtro

def buscar_por_termo(termo):
    df = st.session_state.banco_dados
    cond_proj = df["Projeto"].str.contains(termo, case=False, na=False)
    cond_regra = df["Regra"].str.contains(termo, case=False, na=False)
    df_filtro = df[cond_proj | cond_regra]

    if df_filtro.empty:
        return f"Nenhuma entrada encontrada para: {termo}"
    return df_filtro

# Função para checar parênteses
def checar_parenteses(texto):
    abertura = texto.count('(')
    fechamento = texto.count(')')
    
    if abertura != fechamento:
        return "⚠️ Parênteses desbalanceados!", "#f8d7da"
    else:
        return "✓ Parênteses balanceados.", "#d4edda"

# Configuração da página
st.set_page_config(page_title="Banco de dados de regras linguísticas", layout="wide")

# Controle de sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
    <style>
        body {
            background-color: white;
            color: black;
            font-family: 'Proxima Nova', sans-serif;
        }
        .centered {
            text-align: center;
            color: black;
        }
        input, textarea, .stButton > button {
            font-size: 16px;
            color: black !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='centered'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='centered'>🔐 Acesso restrito</h2>", unsafe_allow_html=True)

    st.stop()

# Interface principal
st.download_button(
    label="📥 Baixar base de dados CSV",
    data=open(csv_path, "rb") if os.path.exists(csv_path) else b"",
    file_name="queries_linguisticas.csv",
    mime="text/csv"
)

st.markdown("<h1 style='text-align: center;'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)

abas = st.tabs(["Cadastrar nova regra linguística", "Buscar por regra linguística"])

with abas[0]:
    projeto = st.text_input("Projeto")
    analista = st.text_input("Analista")
    titulo_regra = st.text_input("Título da Regra")
    regra = st.text_area("Regra linguística aplicada")
    ferramenta = st.selectbox("Ferramenta", ["Outra", "AND", "OR", "NEAR", "~", "|", "NOT"])
    data = st.text_input("Data do registro (opcional)", placeholder="AAAA-MM-DD")

    if st.button("Salvar entrada"):
        if projeto and analista and titulo_regra and regra:
            salvar_csv(projeto, analista, titulo_regra, regra, ferramenta, data)
        else:
            st.warning("Preencha todos os campos obrigatórios.")

with abas[1]:
    nome_projeto = st.text_input("Digite o nome da regra ou projeto para buscar")

    if nome_projeto:
        resultado = buscar_por_projeto(nome_projeto)
        resultado = buscar_por_termo(nome_projeto)
        if isinstance(resultado, str):
            st.info(resultado)
            resultado = pd.DataFrame(columns=['Projeto', 'Analista', 'Título da Regra', 'Regra', 'Ferramenta', 'Data'])
    else:
        resultado = pd.read_csv(csv_path)
        resultado = st.session_state.banco_dados

    for idx, row in resultado.iterrows():
        with st.expander(f"📄 {row['Título da Regra']} – {row['Projeto']}"):
            regra_formatada = row['Regra'].replace('<', '&lt;').replace('>', '&gt;').replace(' ', '<br>')
            regra_formatada = row['Regra'].replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            st.markdown(f"""
                <div style='background-color: #1e1e1e; border-left: 4px solid #3399ff; border-right: 4px solid #3399ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-family: "Proxima Nova", sans-serif;'>
                    <strong style='color: #00ffff;'>Elaboração de regras linguística:</strong><br><br>
                    {regra_formatada}
                </div>
            """, unsafe_allow_html=True)

            if st.button(f"🗑️ Deletar regra", key=f"del_{idx}"):
                if st.radio("Tem certeza que deseja excluir esta regra?", ["Não", "Sim"], index=0, key=f"confirma_{idx}") == "Sim":
                    df = pd.read_csv(csv_path)
                    df = df.drop(resultado.index[idx])
                    df.to_csv(csv_path, index=False)
                    st.session_state.banco_dados.drop(index=resultado.index[idx], inplace=True)
                    st.success("Regra deletada com sucesso!")
                    st.experimental_rerun()

            st.markdown("**Abrir em:**")
            conteudo_encoded = row['Regra'].replace(' ', '%20').replace('\n', '%0A')
            bloco_nota_link = f"data:text/plain,{conteudo_encoded}"
            google_docs_link = "https://drive.google.com/drive/folders/14PxmRK90jiYs2RfZsjrvqtHMyYiDEADY"
            onedrive_link = "https://onedrive.live.com/edit.aspx"

            st.markdown(f"- [📄 Baixar bloco de notas]({bloco_nota_link})")
            st.markdown(f"- [📝 Criar novo Google Docs com esse título]({google_docs_link})")
            st.markdown(f"- [☁️ Abrir OneDrive para colar]({onedrive_link})")

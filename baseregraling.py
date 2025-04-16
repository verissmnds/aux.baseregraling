import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------- Configuração da API do Google Sheets ----------
CAMINHO_CREDENCIAL = "dappbaseregrasling-999bb55f05e8.json"  # coloque o nome correto do seu arquivo
ID_PLANILHA = "1qO_3WQkEnDI__xCLT_hsYWg0hYfRWpL2eCCf26QJLrs"

# Função para conectar ao Google Sheets
@st.cache_resource
def conectar_planilha():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(CAMINHO_CREDENCIAL, escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(ID_PLANILHA)
    return planilha.sheet1

sheet = conectar_planilha()

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

# ---------- Interface do usuário ----------
st.title("Cadastro de Regras Linguísticas")
projeto = st.text_input("Nome do Projeto")
analista = st.text_input("Analista Responsável")
titulo_regra = st.text_input("Título da Regra")
regra = st.text_area("Elaboração da Regra")
ferramenta = st.radio("Ferramenta Utilizada", ["ELK", "FPK", "YT", "BW", "Outra"])

if st.button("Salvar"):
    try:
        # Preparando os dados para envio
        nova_linha = [
            str(projeto).strip(),
            str(analista).strip(),
            str(titulo_regra).strip(),
            str(regra).strip(),
            str(ferramenta).strip(),
            str(datetime.today().strftime('%Y-%m-%d'))  # Data automática, ou pode ser customizada
        ]
        
        # Exibe o conteúdo da nova linha no log para verificação
        st.write("Tentando salvar os seguintes dados:", nova_linha)

        # Tente enviar a linha para o Google Sheets
        sheet.append_row(nova_linha)
        st.success("Dados salvos com sucesso na planilha!")

    except gspread.exceptions.APIError as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {e}")
        st.write("Detalhes do erro:", e.response)

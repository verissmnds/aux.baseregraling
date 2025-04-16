import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- CONFIGURAÇÕES ---
CAMINHO_CREDENCIAL = "dappbaseregrasling-999bb55f05e8.json"  # Coloque o nome correto do seu arquivo de credenciais
ID_PLANILHA = "1qO_3WQkEnDI__xCLT_hsYWg0hYfRWpL2eCCf26QJLrs"  # Substitua pelo ID da sua planilha

# --- CONEXÃO COM O GOOGLE SHEETS ---
@st.cache_resource
def conectar_planilha():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(CAMINHO_CREDENCIAL, escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(ID_PLANILHA)
    return planilha.sheet1

sheet = conectar_planilha()

# --- INTERFACE DO USUÁRIO ---
st.title("Cadastro de Regras Linguísticas")

projeto = st.text_input("Nome do Projeto")
analista = st.text_input("Analista Responsável")
titulo_regra = st.text_input("Título da Regra")
elaboracao = st.text_area("Elaboração da Regra")
ferramenta = st.text_input("Ferramenta Utilizada")
data = st.date_input("Data de Registro", value=date.today())

if st.button("Salvar"):
    try:
        # Converte todos os campos para texto antes de enviar
        nova_linha = [
            str(projeto).strip(),
            str(analista).strip(),
            str(titulo_regra).strip(),
            str(elaboracao).strip(),
            str(ferramenta).strip(),
            str(data.strftime('%Y-%m-%d')) if hasattr(data, 'strftime') else str(data).strip()
        ]

        sheet.append_row(nova_linha)
        st.success("Dados salvos com sucesso na planilha!")

    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {e}")

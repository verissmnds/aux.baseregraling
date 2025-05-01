import streamlit as st
from datetime import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# ---------- Configuração da API do Google Sheets ----------
API_INFO = dict(st.secrets["api_info"])
ID_PLANILHA = st.secrets["id_planilha"]["value"]
NOME_ABA = st.secrets["nome_aba"]["value"]

# ---------- Autenticação ----------
USUARIO_CORRETO = st.secrets["usuario"]["value"]
SENHA_CORRETA = st.secrets["senha"]["value"]

# ---------- Funções do Google Sheets ----------
def conectar_planilha():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(API_INFO, escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(ID_PLANILHA)
    return planilha.worksheet(NOME_ABA)

def obter_todos_dados():
    sheet = conectar_planilha()
    return sheet.get_all_records()

def obter_todos_dados_com_ids():
    sheet = conectar_planilha()
    dados = sheet.get_all_records()
    # Adiciona o ID da linha (começando de 2 pois a linha 1 é cabeçalho)
    for i, registro in enumerate(dados, start=2):
        registro['ID'] = i
    return dados

def atualizar_registro(linha_id, novos_dados):
    sheet = conectar_planilha()
    # Converte o dicionário para lista na ordem das colunas
    colunas = sheet.row_values(1)
    valores = [novos_dados.get(col, "") for col in colunas]
    sheet.update(f"A{linha_id}:F{linha_id}", [valores])

# ---------- Funções auxiliares ----------
def checar_parenteses(texto):
    abertura = texto.count('(')
    fechamento = texto.count(')')
    if abertura > fechamento:
        return f"⚠️ Faltam {abertura - fechamento} parêntese(s) de fechamento.", "#fff3cd"
    elif fechamento > abertura:
        return f"⚠️ Faltam {fechamento - abertura} parêntese(s) de abertura.", "#fff3cd"
    else:
        return "✓ Parênteses balanceados.", "#d4edda"

def destacar_operadores(regra, ferramenta):
    operadores_permitidos = {
        "ELK": ["OR", "AND", "NOT"],
        "FPK": ["OR", "AND", "NOT"],
        "YT": ["|"],
        "BW": ["OR", "AND", "NEAR/", "~", "NOT"],
        "Outra": []
    }
    op_ativos = operadores_permitidos.get(ferramenta, [])
    regra_destacada = regra
    
    for op in op_ativos:
        if op == "OR":
            regra_destacada = re.sub(r'\bOR\b', '<span style="color:green;font-weight:bold">OR</span>', regra_destacada)
        elif op == "AND":
            regra_destacada = re.sub(r'\bAND\b', '<span style="color:blue;font-weight:bold">AND</span>', regra_destacada)
        elif op == "NOT":
            regra_destacada = re.sub(r'\bNOT\b', '<span style="color:red;font-weight:bold">NOT</span>', regra_destacada)
        elif op == "NEAR/":
            regra_destacada = re.sub(r'\bNEAR/\d+\b', lambda m: f'<span style="color:orange;font-weight:bold">{m.group()}</span>', regra_destacada)
        elif op == "~":
            regra_destacada = regra_destacada.replace("~", '<span style="color:purple;font-weight:bold">~</span>')
        elif op == "|":
            regra_destacada = regra_destacada.replace("|", '<span style="color:green;font-weight:bold">|</span>')
    
    return regra_destacada

# ---------- Configuração da página ----------
st.set_page_config(page_title="Banco de dados de regras linguísticas", layout="wide")

st.markdown("""
    <style>
        /* Mantenha apenas o essencial */
        .main {
            max-width: 1200px;
            padding: 2rem;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Verificação de login ----------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: black;'>🔐 Acesso restrito</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
                st.session_state.autenticado = True
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    st.stop()

# ---------- Página principal ----------
st.markdown("<h1 style='text-align: center;'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)

# Abas principais
tab1, tab2, tab3 = st.tabs(["Cadastrar nova regra", "Buscar regras", "Editar regras"])

# ---------- Cadastro de nova regra ----------
with tab1:
    st.subheader("Cadastrar nova regra linguística")
    
    with st.form("nova_regra_form"):
        col1, col2 = st.columns(2)
        with col1:
            projeto = st.text_input("Nome do Projeto*")
            analista = st.text_input("Analista Responsável*")
            titulo_regra = st.text_input("Título da Regra*")
        with col2:
            regra = st.text_area("Elaboração de regras linguística*", height=150)
            ferramenta = st.radio("Ferramenta*", ["ELK", "FPK", "YT", "BW", "Outra"])
        
        data = st.text_input("Data do registro", placeholder="AAAA-MM-DD", value=datetime.today().strftime('%Y-%m-%d'))
        
        submitted = st.form_submit_button("Salvar entrada")
        
        if submitted:
            if not all([projeto, analista, titulo_regra, regra]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)")
            else:
                nova_linha = {
                    "Nome do Projeto": projeto.strip(),
                    "Analista Responsável": analista.strip(),
                    "Título da Regra": titulo_regra.strip(),
                    "Regra": regra.strip(),
                    "Ferramenta": ferramenta.strip(),
                    "Data": data or datetime.today().strftime('%Y-%m-%d')
                }
                
                try:
                    sheet = conectar_planilha()
                    sheet.append_row(list(nova_linha.values()))
                    st.success("Regra cadastrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {str(e)}")
    
    if regra:
        st.markdown("**Visualização da regra com operadores destacados:**")
        regra_destacada = destacar_operadores(regra, ferramenta)
        st.markdown(f"<div class='card'>{regra_destacada}</div>", unsafe_allow_html=True)
        
        alerta_parenteses, cor = checar_parenteses(regra)
        st.markdown(f"<div class='card' style='background-color:{cor}'>{alerta_parenteses}</div>", unsafe_allow_html=True)

# ---------- Busca de regras ----------
with tab2:
    st.subheader("Buscar regras linguísticas")
    
    nome_projeto = st.text_input("Digite o Nome do Projeto ou da regra para buscar")
    
    dados = obter_todos_dados()
    
    if nome_projeto:
        dados_filtrados = [reg for reg in dados if nome_projeto.lower() in reg["Nome do Projeto"].lower() or 
                          nome_projeto.lower() in reg["Título da Regra"].lower()]
    else:
        dados_filtrados = dados
    
    if dados_filtrados:
        df = pd.DataFrame(dados_filtrados)
        st.dataframe(df)
    else:
        st.warning("Nenhuma regra encontrada com os critérios de busca.")

# ---------- Edição de regras ----------
with tab3:
    st.subheader("Editar regras existentes")
    
    dados_com_ids = obter_todos_dados_com_ids()
    
    if not dados_com_ids:
        st.warning("Nenhuma regra cadastrada para edição.")
    else:
        regra_selecionada = st.selectbox(
            "Selecione a regra para editar",
            options=dados_com_ids,
            format_func=lambda x: f"{x['ID']} - {x['Nome do Projeto']} - {x['Título da Regra']}"
        )
        
        if regra_selecionada:
            with st.form("editar_regra_form"):
                col1, col2 = st.columns(2)
                with col1:
                    projeto = st.text_input("Nome do Projeto*", value=regra_selecionada["Nome do Projeto"])
                    analista = st.text_input("Analista Responsável*", value=regra_selecionada["Analista Responsável"])
                    titulo_regra = st.text_input("Título da Regra*", value=regra_selecionada["Título da Regra"])
                with col2:
                    regra = st.text_area("Regra*", 
                                        value=regra_selecionada["Regra"], 
                                        height=150)
                    ferramenta = st.radio("Ferramenta*", 
                                         ["ELK", "FPK", "YT", "BW", "Outra"],
                                         index=["ELK", "FPK", "YT", "BW", "Outra"].index(regra_selecionada["Ferramenta"]))
                
                data = st.text_input("Data", value=regra_selecionada["Data"])
                
                submitted = st.form_submit_button("Atualizar regra")
                
                if submitted:
                    if not all([projeto, analista, titulo_regra, regra]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*)")
                    else:
                        novos_dados = {
                            "Nome do Projeto": projeto.strip(),
                            "Analista Responsável": analista.strip(),
                            "Título da Regra": titulo_regra.strip(),
                            "Regra": regra.strip(),
                            "Ferramenta": ferramenta.strip(),
                            "Data": data.strip()
                        }
                        
                        try:
                            atualizar_registro(regra_selecionada['ID'], novos_dados)
                            st.success("Regra atualizada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {str(e)}")
            
            if regra:
                st.markdown("**Visualização da regra com operadores destacados:**")
                regra_destacada = destacar_operadores(regra, ferramenta)
                st.markdown(f"<div class='card'>{regra_destacada}</div>", unsafe_allow_html=True)
                
                alerta_parenteses, cor = checar_parenteses(regra)
                st.markdown(f"<div class='card' style='background-color:{cor}'>{alerta_parenteses}</div>", unsafe_allow_html=True)
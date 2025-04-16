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
 def salvar_em_memoria(projeto, analista, titulo_regra, regra, ferramenta, data):
     nova_linha = {
         "Projeto": projeto,
         "Analista": analista,
 @@ -21,31 +21,21 @@ def salvar_csv(projeto, analista, titulo_regra, regra, ferramenta, data):
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
 @@ -56,32 +46,12 @@ def checar_parenteses(texto):
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
 
 @@ -99,29 +69,7 @@ def checar_parenteses(texto):
 
     st.stop()
 
 # Captura Ctrl+Enter para login automático
 st.markdown("""
 <script>
     document.addEventListener("keydown", function(e) {
         if (e.ctrlKey && e.key === "Enter") {
             window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', key: 'ctrl_enter_triggered', value: true}, '*');
         }
     });
 </script>
 """, unsafe_allow_html=True)
 
 # Título principal
 st.markdown("""
 <h1 style='font-family: \"Proxima Nova\", sans-serif; color: white; text-align: center;'>📚 Banco de dados de regras linguísticas</h1>
 """, unsafe_allow_html=True)
 
 # Interface principal
 st.download_button(
     label="📥 Baixar base de dados CSV",
     data=open(csv_path, "rb") if os.path.exists(csv_path) else b"",
     file_name="queries_linguisticas.csv",
     mime="text/csv"
 )
 st.markdown("<h1 style='text-align: center;'>📚 Banco de dados de regras linguísticas</h1>", unsafe_allow_html=True)
 
 abas = st.tabs(["Cadastrar nova regra linguística", "Buscar por regra linguística"])
 
 @@ -146,33 +94,30 @@ def checar_parenteses(texto):
         }
         op_ativos = operadores_permitidos.get(ferramenta, [])
 
         st.markdown("**Visualização da regra com operadores destacados (campo 'Regra linguística aplicada'):**", unsafe_allow_html=True)
 
         if ferramenta != "Outra":
             regra_destacada = regra
             if "OR" in op_ativos:
                 regra_destacada = re.sub(r'\\bOR\\b', '<span style="color:green;font-weight:bold">OR</span>', regra_destacada)
             if "AND" in op_ativos:
                 regra_destacada = re.sub(r'\\bAND\\b', '<span style="color:blue;font-weight:bold">AND</span>', regra_destacada)
             if "NOT" in op_ativos:
                 regra_destacada = re.sub(r'\\bNOT\\b', '<span style="color:red;font-weight:bold">NOT</span>', regra_destacada)
             if "NEAR/" in op_ativos:
                 regra_destacada = re.sub(r'\\bNEAR/\\d+\\b', lambda m: f'<span style="color:orange;font-weight:bold">{m.group()}</span>', regra_destacada)
             if "~" in op_ativos:
                 regra_destacada = regra_destacada.replace("~", '<span style="color:purple;font-weight:bold">~</span>')
             if "|" in op_ativos:
                 regra_destacada = regra_destacada.replace("|", '<span style="color:green;font-weight:bold">|</span>')
             st.markdown(f"<div style='padding:10px;border:1px solid #ddd;border-radius:5px'>{regra_destacada}</div>", unsafe_allow_html=True)
         else:
             st.markdown(f"<div style='padding:10px;border:1px solid #ddd;border-radius:5px'>{regra}</div>", unsafe_allow_html=True)
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
             salvar_csv(projeto, analista, titulo_regra, regra, ferramenta, data)
             salvar_em_memoria(projeto, analista, titulo_regra, regra, ferramenta, data)
         else:
             st.warning("Preencha todos os campos obrigatórios.")
 
 @@ -181,12 +126,12 @@ def checar_parenteses(texto):
     nome_projeto = st.text_input("Digite o nome da regra ou projeto para buscar")
 
     if nome_projeto:
         resultado = buscar_por_projeto(nome_projeto)
         resultado = buscar_por_termo(nome_projeto)
         if isinstance(resultado, str):
             st.info(resultado)
             resultado = pd.DataFrame(columns=['Projeto', 'Analista', 'Título da Regra', 'Regra', 'Ferramenta', 'Data'])
             resultado = pd.DataFrame(columns=st.session_state.banco_dados.columns)
     else:
         resultado = pd.read_csv(csv_path)
         resultado = st.session_state.banco_dados
 
     for idx, row in resultado.iterrows():
         with st.expander(f"📄 {row['Título da Regra']} – {row['Projeto']}"):
 @@ -202,18 +147,6 @@ def checar_parenteses(texto):
 
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

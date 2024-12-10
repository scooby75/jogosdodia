import streamlit as st
import pandas as pd
import re

# Função para comparar substrings dos nomes das equipes de forma mais flexível
def comparar_nomes_substrings(nome1, nome2):
    nome1 = nome1.lower().replace("fc", "").strip()  # Remover "FC" e normalizar
    nome2 = nome2.lower().replace("fc", "").strip()  # Remover "FC" e normalizar
    return nome1 in nome2 or nome2 in nome1

# URLs dos arquivos no GitHub
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Upload do arquivo "Jogos do Dia"
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")

if jogos_dia_file:
    # Ler o arquivo "Jogos do Dia"
    jogos_dia = pd.read_csv(jogos_dia_file)

    # Exibir as colunas do arquivo "Jogos do Dia"
    st.write("Colunas do arquivo 'Jogos do Dia':", jogos_dia.columns)
    
    # Carregar os arquivos diretamente das URLs
    equipes_casa = pd.read_csv(url_equipes_casa)
    equipes_fora = pd.read_csv(url_equipes_fora)

    # Exibir as colunas do arquivo equipes_fora.csv
    st.write("Colunas do arquivo equipes_fora.csv:", equipes_fora.columns)
    
    # Aplicar o filtro de PIA_HA >= 0.75
    equipes_fora_filtradas = equipes_fora[equipes_fora['PIA_HA'] >= 0.75]

    # Exibir equipes fora com o filtro PIA_HA >= 0.75
    st.subheader("Equipes fora com PIA_HA >= 0.75")
    st.dataframe(equipes_fora_filtradas)
    

else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

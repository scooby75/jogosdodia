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
    
    # Comparação de equipes
    jogos_merged = []
    for _, jogo in jogos_dia.iterrows():
        # Separar os times da coluna 'Evento' (exemplo: 'Persija Jakarta v Pusamania Borneo FC')
        evento = jogo['Evento']
        
        # Usar expressão regular para separar os times
        match = re.match(r"(.+) v (.+)", evento)
        if match:
            time_casa = match.group(1).strip()
            time_fora = match.group(2).strip()
            
            # Comparar time da casa com equipes_casa
            similar_times_casa = equipes_casa[equipes_casa['Equipe_Casa'].apply(lambda x: comparar_nomes_substrings(time_casa, x))]
            
            # Comparar time de fora com equipes_fora
            similar_times_fora = equipes_fora_filtradas[equipes_fora_filtradas['Equipe_Fora'].apply(lambda x: comparar_nomes_substrings(time_fora, x))]
            
            if not similar_times_casa.empty and not similar_times_fora.empty:
                st.write(f"Jogo: {evento}, Equipes encontradas - Casa: {similar_times_casa['Equipe_Casa'].values[0]}, Fora: {similar_times_fora['Equipe_Fora'].values[0]}")
            else:
                st.warning(f"Não encontrou times correspondentes para o evento: {evento}")
        else:
            st.warning(f"Formato inválido para o evento: {evento}")
    
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

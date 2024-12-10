import streamlit as st
import pandas as pd

# Função para comparar substrings dos nomes das equipes
def comparar_nomes_substrings(nome1, nome2):
    return nome1.lower() in nome2.lower() or nome2.lower() in nome1.lower()

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
        # Acesse o nome da coluna corretamente
        nome_time_fora = jogo['Time_Fora']  # Ajuste o nome da coluna conforme necessário
        
        # Encontrar a linha correspondente em equipes_fora com base na comparação de substrings
        similar_times_fora = equipes_fora_filtradas[equipes_fora_filtradas['Equipe_Fora'].apply(lambda x: comparar_nomes_substrings(nome_time_fora, x))]
        
        if not similar_times_fora.empty:
            st.write(f"Jogo: {nome_time_fora}, Equipes encontradas: {similar_times_fora}")
        else:
            st.warning(f"Não encontrou time correspondente para: {nome_time_fora}")
    
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

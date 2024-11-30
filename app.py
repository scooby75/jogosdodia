import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Função para limpar e extrair odds
def extrair_odds(valor):
    if isinstance(valor, str):
        try:
            return pd.to_numeric(valor.split('(')[0].replace(",", "").strip())
        except ValueError:
            return None
    return valor

# Função para verificar similaridade
def is_similar(team, team_list):
    return any(fuzz.partial_ratio(team, equipe) > 80 for equipe in team_list)

# Carregar dados dos arquivos remotos
@st.cache_data
def carregar_dados(url):
    return pd.read_csv(url)

# URLs dos arquivos
url_melhores_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Casa.csv"
url_melhores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Fora.csv"
url_piores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Piores_Equipes_Fora.csv"

melhores_casa = carregar_dados(url_melhores_casa)
melhores_away = carregar_dados(url_melhores_away)
piores_away = carregar_dados(url_piores_away)

# Upload do arquivo "Jogos do Dia"
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")

if jogos_dia_file:
    # Ler e processar o arquivo
    jogos_dia = pd.read_csv(jogos_dia_file)
    jogos_dia_validos = jogos_dia[jogos_dia['Evento'].str.contains(' v ', na=False)]
    jogos_dia_validos['Time_Casa'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[0].strip())
    jogos_dia_validos['Time_Fora'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[1].strip())
    jogos_dia_validos['Home'] = jogos_dia_validos['Home'].apply(extrair_odds)
    jogos_dia_validos['Away'] = jogos_dia_validos['Away'].apply(extrair_odds)
    jogos_dia_validos['The Draw'] = jogos_dia_validos['The Draw'].apply(extrair_odds)

    # Filtros "HA -0.25"
    st.subheader("HA -0.25")
    melhores_home_filtrados = melhores_casa[melhores_casa['W'] >= 3]
    piores_away_filtrados = piores_away[piores_away['L'] >= 4]

    piores_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(lambda x: is_similar(x, piores_away_filtrados['Equipe'])) &
        jogos_dia_validos['Time_Casa'].apply(lambda x: is_similar(x, melhores_home_filtrados['Equipe'])) &
        (jogos_dia_validos['Home'] <= 2.5)
    ]
    st.dataframe(piores_away_jogos)

    # Outros filtros podem ser ajustados com lógica similar
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

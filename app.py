import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

# Função para normalizar os nomes
def normalize_name(name):
    return ''.join(e for e in name.lower().strip() if e.isalnum())

# Função para comparar nomes usando similaridade
def match_team(team_name, team_list, threshold=80):
    normalized_team = normalize_name(team_name)
    matches = process.extract(normalized_team, [normalize_name(t) for t in team_list], scorer=fuzz.ratio)
    best_match, score = matches[0]
    if score >= threshold:
        return team_list[matches.index((best_match, score))]
    return None

# Aplicativo Streamlit
st.title("Comparação de Jogos do Dia")

# Upload de arquivos
betfair_file = st.file_uploader("Carregar Jogos do dia Betfair.csv", type="csv")
casa_file = st.file_uploader("Carregar Melhores_Equipes_Casa.csv", type="csv")
away_file = st.file_uploader("Carregar Melhores_Equipes_Away.csv", type="csv")
piores_file = st.file_uploader("Carregar Piores_Equipes_Fora.csv", type="csv")

if betfair_file and casa_file and away_file and piores_file:
    # Carregar os dados
    jogos_dia = pd.read_csv(betfair_file)
    melhores_casa = pd.read_csv(casa_file)
    melhores_away = pd.read_csv(away_file)
    piores_fora = pd.read_csv(piores_file)

    # Colunas de interesse
    jogos_dia['Time_Casa'] = jogos_dia['Evento'].apply(lambda x: x.split(' vs ')[0])
    jogos_dia['Time_Fora'] = jogos_dia['Evento'].apply(lambda x: x.split(' vs ')[1])

    # Processar os jogos com base nos critérios
    casa_matches = jogos_dia[jogos_dia['Time_Casa'].apply(lambda x: match_team(x, melhores_casa['Equipe']) is not None)]
    away_matches = jogos_dia[jogos_dia['Time_Fora'].apply(lambda x: match_team(x, melhores_away['Equipe']) is not None)]
    piores_matches = jogos_dia[jogos_dia['Time_Fora'].apply(lambda x: match_team(x, piores_fora['Equipe']) is not None)]

    # Exibir os resultados
    st.subheader("Melhores Equipes em Casa")
    st.dataframe(casa_matches)

    st.subheader("Melhores Equipes Fora")
    st.dataframe(away_matches)

    st.subheader("Piores Equipes Fora")
    st.dataframe(piores_matches)

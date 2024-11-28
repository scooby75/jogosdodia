import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Função para verificar se a coluna existe em um DataFrame
def verificar_coluna(df, coluna):
    if coluna not in df.columns:
        st.error(f"A coluna '{coluna}' não foi encontrada no arquivo. Verifique e tente novamente.")
        return False
    return True

# Upload dos arquivos
st.title("Comparador de Jogos do Dia")
st.write("Envie os arquivos necessários para a análise.")

jogos_dia = st.file_uploader("Envie o arquivo 'Jogos do Dia Betfair.csv'", type=["csv"])
melhores_casa = st.file_uploader("Envie o arquivo 'Melhores Equipes Casa.csv'", type=["csv"])
melhores_away = st.file_uploader("Envie o arquivo 'Melhores Equipes Away.csv'", type=["csv"])
piores_fora = st.file_uploader("Envie o arquivo 'Piores Equipes Fora.csv'", type=["csv"])

if jogos_dia and melhores_casa and melhores_away and piores_fora:
    # Leitura dos arquivos
    jogos_dia = pd.read_csv(jogos_dia)
    melhores_casa = pd.read_csv(melhores_casa)
    melhores_away = pd.read_csv(melhores_away)
    piores_fora = pd.read_csv(piores_fora)

    # Verificar colunas no arquivo 'Jogos do Dia Betfair.csv'
    if not verificar_coluna(jogos_dia, "Evento") or not verificar_coluna(jogos_dia, "Competição"):
        st.stop()

    # Separar times da coluna 'Evento'
    jogos_dia['Time_Casa'] = jogos_dia['Evento'].apply(lambda x: x.split(' v ')[0] if ' v ' in x else "")
    jogos_dia['Time_Fora'] = jogos_dia['Evento'].apply(lambda x: x.split(' v ')[1] if ' v ' in x else "")

    # Verificar colunas em outros arquivos
    if not verificar_coluna(melhores_casa, "Equipe") or not verificar_coluna(melhores_casa, "Liga"):
        st.stop()
    if not verificar_coluna(melhores_away, "Equipe") or not verificar_coluna(melhores_away, "Liga"):
        st.stop()
    if not verificar_coluna(piores_fora, "Equipe") or not verificar_coluna(piores_fora, "Liga"):
        st.stop()

    # Comparação por Time e Liga
    melhores_casa_jogos = jogos_dia[
        jogos_dia['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_casa['Equipe'])
        ) & jogos_dia['Competição'].apply(
            lambda x: any(fuzz.partial_ratio(x, liga) > 80 for liga in melhores_casa['Liga'])
        )
    ]

    melhores_away_jogos = jogos_dia[
        jogos_dia['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_away['Equipe'])
        ) & jogos_dia['Competição'].apply(
            lambda x: any(fuzz.partial_ratio(x, liga) > 80 for liga in melhores_away['Liga'])
        )
    ]

    piores_fora_jogos = jogos_dia[
        jogos_dia['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in piores_fora['Equipe'])
        ) & jogos_dia['Competição'].apply(
            lambda x: any(fuzz.partial_ratio(x, liga) > 80 for liga in piores_fora['Liga'])
        )
    ]

    # Exibição dos resultados
    st.subheader("Jogos com Melhores Equipes Casa:")
    st.dataframe(melhores_casa_jogos)

    st.subheader("Jogos com Melhores Equipes Fora:")
    st.dataframe(melhores_away_jogos)

    st.subheader("Jogos com Piores Equipes Fora:")
    st.dataframe(piores_fora_jogos)

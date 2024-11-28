import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Carregar os arquivos CSV
st.title("Comparação de Jogos do Dia")
uploaded_files = st.file_uploader(
    "Envie os arquivos CSV (Jogos do dia Betfair, Melhores_Equipes_Casa, Melhores_Equipes_Away, Piores_Equipes_Fora)",
    accept_multiple_files=True,
    type=["csv"],
)

if len(uploaded_files) == 4:
    # Identificar os arquivos enviados
    jogos_dia_file = next((f for f in uploaded_files if "Jogos do dia Betfair" in f.name), None)
    melhores_casa_file = next((f for f in uploaded_files if "Melhores_Equipes_Casa" in f.name), None)
    melhores_away_file = next((f for f in uploaded_files if "Melhores_Equipes_Away" in f.name), None)
    piores_away_file = next((f for f in uploaded_files if "Piores_Equipes_Fora" in f.name), None)

    if None in [jogos_dia_file, melhores_casa_file, melhores_away_file, piores_away_file]:
        st.error("Certifique-se de enviar todos os 4 arquivos necessários.")
    else:
        # Ler os dados dos arquivos
        jogos_dia = pd.read_csv(jogos_dia_file)
        melhores_casa = pd.read_csv(melhores_casa_file)
        melhores_away = pd.read_csv(melhores_away_file)
        piores_away = pd.read_csv(piores_away_file)

        # Identificar e tratar problemas no formato da coluna Evento
        st.subheader("Verificação dos dados na coluna 'Evento'")
        problemas = jogos_dia[~jogos_dia['Evento'].str.contains(' vs ', na=False)]
        if not problemas.empty:
            st.warning("Foram encontrados problemas no formato da coluna 'Evento':")
            st.dataframe(problemas)

        # Filtrar apenas linhas válidas
        jogos_dia_validos = jogos_dia[jogos_dia['Evento'].str.contains(' vs ', na=False)]

        # Adicionar colunas Time_Casa e Time_Fora
        def extract_time_casa(evento):
            try:
                return evento.split(' vs ')[0]
            except IndexError:
                return None

        def extract_time_fora(evento):
            try:
                return evento.split(' vs ')[1]
            except IndexError:
                return None

        jogos_dia_validos['Time_Casa'] = jogos_dia_validos['Evento'].apply(extract_time_casa)
        jogos_dia_validos['Time_Fora'] = jogos_dia_validos['Evento'].apply(extract_time_fora)

        # Exibir os jogos válidos
        st.subheader("Jogos válidos com Time_Casa e Time_Fora")
        st.dataframe(jogos_dia_validos)

        # Comparação com Melhores_Equipes_Casa
        st.subheader("Jogos com Melhores Equipes em Casa")
        melhores_casa_jogos = jogos_dia_validos[
            jogos_dia_validos['Time_Casa'].apply(
                lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_casa['Equipe'])
            )
        ]
        st.dataframe(melhores_casa_jogos)

        # Comparação com Melhores_Equipes_Away
        st.subheader("Jogos com Melhores Equipes Fora")
        melhores_away_jogos = jogos_dia_validos[
            jogos_dia_validos['Time_Fora'].apply(
                lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_away['Equipe'])
            )
        ]
        st.dataframe(melhores_away_jogos)

        # Comparação com Piores_Equipes_Fora
        st.subheader("Jogos com Piores Equipes Fora")
        piores_away_jogos = jogos_dia_validos[
            jogos_dia_validos['Time_Fora'].apply(
                lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in piores_away['Equipe'])
            )
        ]
        st.dataframe(piores_away_jogos)

else:
    st.info("Por favor, envie os 4 arquivos necessários para análise.")

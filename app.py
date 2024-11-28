import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Título do aplicativo
st.title("Comparação de Jogos do Dia")

# Upload de arquivos separados
st.subheader("Envie os arquivos necessários")

# Upload de cada arquivo individualmente
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")
melhores_casa_file = st.file_uploader("Envie o arquivo 'Melhores_Equipes_Casa.csv'", type="csv")
melhores_away_file = st.file_uploader("Envie o arquivo 'Melhores_Equipes_Fora.csv'", type="csv")
piores_away_file = st.file_uploader("Envie o arquivo 'Piores_Equipes_Fora.csv'", type="csv")

# Verificar se todos os arquivos foram enviados
if all([jogos_dia_file, melhores_casa_file, melhores_away_file, piores_away_file]):
    # Ler os dados dos arquivos CSV
    jogos_dia = pd.read_csv(jogos_dia_file)
    melhores_casa = pd.read_csv(melhores_casa_file)
    melhores_away = pd.read_csv(melhores_away_file)
    piores_away = pd.read_csv(piores_away_file)

    # Verificar e corrigir o formato da coluna Evento
    st.subheader("Verificação dos dados na coluna 'Evento'")
    problemas = jogos_dia[~jogos_dia['Evento'].str.contains(' v ', na=False)]
    if not problemas.empty:
        st.warning("Foram encontrados problemas no formato da coluna 'Evento':")
        st.dataframe(problemas)
    else:
        st.success("Todos os dados estão no formato esperado.")

    # Filtrar apenas linhas válidas
    jogos_dia_validos = jogos_dia[jogos_dia['Evento'].str.contains(' v ', na=False)]

    # Adicionar colunas Time_Casa e Time_Fora
    def extract_time_casa(evento):
        try:
            return evento.split(' v ')[0].strip()
        except IndexError:
            return None

    def extract_time_fora(evento):
        try:
            return evento.split(' v ')[1].strip()
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
    st.info("Por favor, envie todos os arquivos para realizar a análise.")

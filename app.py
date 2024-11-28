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

    # Filtrar jogos que não contêm 'UEFA', 'AFC Champions', 'Reservas', 'Friendlies Women's International', ou 'U21' na coluna 'Competição'
    jogos_dia_validos = jogos_dia_validos[~jogos_dia_validos['Competição'].str.contains('UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21', case=False, na=False)]

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
    st.subheader("Jogos válidos")
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

    # Análise H2H: Melhores Times em Casa vs Piores Times Fora
    st.subheader("H2H: Melhores Times em Casa vs Piores Times Fora")

    # Filtrar os melhores times em casa com W >= 4
    melhores_casa_filtrados = melhores_casa[melhores_casa['W'] >= 4]

    # Filtrar os piores times fora com L >= 4
    piores_away_filtrados = piores_away[piores_away['L'] >= 5]

    # Combinar as equipes para análise H2H
    h2h_jogos = jogos_dia_validos[
        jogos_dia_validos.apply(
            lambda row: any(
                fuzz.partial_ratio(row['Time_Casa'], casa) > 80 for casa in melhores_casa_filtrados['Equipe']
            ) and any(
                fuzz.partial_ratio(row['Time_Fora'], fora) > 80 for fora in piores_away_filtrados['Equipe']
            ),
            axis=1
        )
    ]

    if not h2h_jogos.empty:
        st.dataframe(h2h_jogos)
    else:
        st.info("Não há jogos com os melhores times em casa contra os piores times fora.")
else:
    st.info("Por favor, envie todos os arquivos para realizar a análise.")

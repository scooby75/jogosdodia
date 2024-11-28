import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Título do aplicativo
st.title("Comparação de Jogos do Dia")

# URLs dos arquivos no GitHub
url_melhores_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Casa.csv"
url_melhores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Fora.csv"
url_piores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Piores_Equipes_Fora.csv"

# Função para limpar e extrair odds
def extrair_odds(valor):
    if isinstance(valor, str):
        try:
            return pd.to_numeric(valor.split('(')[0].replace(",", "").strip())
        except ValueError:
            return None
    return valor

# Upload do arquivo "Jogos do Dia"
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")

if jogos_dia_file:
    # Ler o arquivo "Jogos do Dia"
    jogos_dia = pd.read_csv(jogos_dia_file)

    # Carregar os arquivos diretamente das URLs
    melhores_casa = pd.read_csv(url_melhores_casa)
    melhores_away = pd.read_csv(url_melhores_away)
    piores_away = pd.read_csv(url_piores_away)

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

    # Filtrar jogos que não contêm palavras-chave indesejadas
    jogos_dia_validos = jogos_dia_validos[
        ~jogos_dia_validos['Competição'].str.contains(
            'UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21', 
            case=False, 
            na=False
        )
    ]

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

    # Corrigir as odds para Home, Away e The Draw
    jogos_dia_validos['Home'] = jogos_dia_validos['Home'].apply(extrair_odds)
    jogos_dia_validos['Away'] = jogos_dia_validos['Away'].apply(extrair_odds)
    jogos_dia_validos['The Draw'] = jogos_dia_validos['The Draw'].apply(extrair_odds)

    # Exibir os jogos válidos
    st.subheader("Jogos válidos")
    st.dataframe(jogos_dia_validos)

    # Comparação com Melhores_Equipes_Casa
    st.subheader("Jogos com Melhores Equipes em Casa")
    melhores_casa_filtrados = melhores_casa[melhores_casa['W'] >= 5]  # Filtrar W >= 5
    melhores_casa_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] <= 2.2)  # Filtrar jogos com odds Home <= 2.2
    ]
    st.dataframe(melhores_casa_jogos)

    # Comparação com Melhores_Equipes_Fora
    st.subheader("Jogos com Melhores Equipes Fora")
    melhores_away_filtrados = melhores_away[melhores_away['W'] >= 5]  # Filtrar W >= 5
    melhores_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_away_filtrados['Equipe'])
        ) & (jogos_dia_validos['Away'] <= 2.2)  # Filtrar jogos com odds Away <= 2.2
    ]
    st.dataframe(melhores_away_jogos)

    # Comparação com Piores_Equipes_Fora
    st.subheader("Jogos com Piores Equipes Fora")
    piores_away_filtrados = piores_away[piores_away['L'] <= 1]  # Filtrar L <= 1
    piores_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in piores_away_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] <= 2.5)  # Filtrar jogos com odds Home <= 2.5
    ]
    st.dataframe(piores_away_jogos)

    # Análise H2H: Melhores Times em Casa vs Piores Times Fora
    st.subheader("H2H: Melhores Times em Casa vs Piores Times Fora")

    # Filtrar os melhores times em casa com W >= 5
    melhores_casa_h2h = melhores_casa_filtrados

    # Filtrar os piores times fora com L <= 1
    piores_away_h2h = piores_away_filtrados

    # Combinar as equipes para análise H2H
    h2h_jogos = jogos_dia_validos[
        jogos_dia_validos.apply(
            lambda row: any(
                fuzz.partial_ratio(row['Time_Casa'], casa) > 80 for casa in melhores_casa_h2h['Equipe']
            ) and any(
                fuzz.partial_ratio(row['Time_Fora'], fora) > 80 for fora in piores_away_h2h['Equipe']
            ),
            axis=1
        )
    ]

    if not h2h_jogos.empty:
        st.dataframe(h2h_jogos)
    else:
        st.info("Não há jogos com os melhores times em casa contra os piores times fora.")
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Título do aplicativo
st.title("Comparação de Jogos do Dia")

# URLs dos arquivos no GitHub
url_melhores_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Casa.csv"
url_melhores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Fora.csv"
url_piores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Piores_Equipes_Fora.csv"
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

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
    equipes_casa = pd.read_csv(url_equipes_casa)
    equipes_fora = pd.read_csv(url_equipes_fora)

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
    palavras_indesejadas = (
        'UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21|English Premier League 2|Israeli Cup|Friendly Matches|Malaysian Cup|Copa de França|Copa de Inglaterra|Scottish FA Cup'
    )
    jogos_dia_validos = jogos_dia_validos[
        ~jogos_dia_validos['Competição'].str.contains(palavras_indesejadas, case=False, na=False)
    ]

    # Adicionar colunas Time_Casa e Time_Fora
    jogos_dia_validos['Time_Casa'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[0].strip())
    jogos_dia_validos['Time_Fora'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[1].strip())

    # Corrigir as odds para Home, Away e The Draw
    for coluna in ['Home', 'Away', 'The Draw']:
        jogos_dia_validos[coluna] = jogos_dia_validos[coluna].apply(extrair_odds)

    # Exibir os jogos válidos
    st.subheader("Jogos válidos")
    st.dataframe(jogos_dia_validos)

    # Análise: Back Home
    st.subheader("Back Home")
    melhores_casa_filtrados = melhores_casa[melhores_casa['W'] >= 5]
    back_home_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] >= 1.45) & (jogos_dia_validos['Home'] <= 2.2)
    ]
    st.dataframe(back_home_jogos)

    # Análise: Back Away
    st.subheader("Back Away")
    melhores_away_filtrados = melhores_away[melhores_away['W'] >= 5]
    back_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_away_filtrados['Equipe'])
        ) & (jogos_dia_validos['Away'] >= 1.45) & (jogos_dia_validos['Away'] <= 2.2)
    ]
    st.dataframe(back_away_jogos)

    # Análise: HA -0.25
    st.subheader("HA -0.25")
    piores_away_filtrados = piores_away[piores_away['L'] >= 4]
    melhores_home_filtrados = melhores_casa[melhores_casa['W'] >= 3]
    ha_negativo_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in piores_away_filtrados['Equipe'])
        )
        & (jogos_dia_validos['Home'] >= 1.80) & (jogos_dia_validos['Home'] <= 2.2)
        & jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_home_filtrados['Equipe'])
        )
    ]
    st.dataframe(ha_negativo_jogos)

    # Análise: HA +0.25
    st.subheader("HA +0.25")
    ha_pos_filtrados = melhores_casa[(melhores_casa['W'] + melhores_casa['D']) >= 6]
    ha_pos_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in ha_pos_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] >= 1.60) & (jogos_dia_validos['Home'] <= 2.3)
    ]
    st.dataframe(ha_pos_jogos)

    # Análise: HA +1
      
    st.subheader("HA +1")
    ha_mais_um_filtrados = melhores_away[
        (melhores_away['W'] + melhores_away['D']) >= 6
        & (melhores_away['GD'] > 0)  
    ]
    
    ha_mais_um_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in ha_mais_um_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] >= 2.60) & (jogos_dia_validos['Away'] >= 2.4)
    ]
    
    st.dataframe(ha_mais_um_jogos)

   
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

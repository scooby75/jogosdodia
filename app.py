import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Título do aplicativo
st.title("Comparação de Jogos do Dia")

# URLs dos arquivos no GitHub

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
        'UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21|English Premier League 2|Israeli Cup|Friendly Matches|Malaysian Cup|Copa de França|Copa de Inglaterra|Scottish FA Cup|U23|Sub23|Cup|Copa|CAF Champions League|(W)|EFL Trophy'
    )
    jogos_dia_validos = jogos_dia_validos[~jogos_dia_validos['Competição'].str.contains(palavras_indesejadas, case=False, na=False)]

    # Adicionar colunas Time_Casa e Time_Fora
    jogos_dia_validos['Time_Casa'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[0].strip())
    jogos_dia_validos['Time_Fora'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[1].strip())

    # Corrigir as odds para Home, Away e The Draw
    for coluna in ['Home', 'Away', 'The Draw']:
        jogos_dia_validos[coluna] = jogos_dia_validos[coluna].apply(extrair_odds)

    # Exibir os jogos válidos
    st.subheader("Jogos válidos")
    st.dataframe(jogos_dia_validos)

   
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

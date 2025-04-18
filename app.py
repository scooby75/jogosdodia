import streamlit as st
import pandas as pd

# URLs dos arquivos CSV
home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"
away_fav_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_Favorito.csv"
overall_stats_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/overall_stats.csv"
sf_home = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/scored_first_home.csv"
sf_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/scored_first_away.csv"



# Função para carregar os dados
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# Carregar os dados das URLs
home_data = load_data(home_url)
away_data = load_data(away_url)
away_fav_data = load_data(away_fav_url)
overall_stats_data = load_data(overall_stats_url)

# Função para normalizar os nomes das colunas (remove espaços extras, etc.)
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

# Normalizar os nomes das colunas
home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)
overall_stats_data = normalize_columns(overall_stats_data)

# Definir as colunas principais para filtragem
home_team_col = "Equipe"
away_team_col = "Equipe_Fora"
away_fav_team_col = "Equipe_Fora"
overall_stats_col = "Equipe"

# Listar as colunas necessárias para cada dataset
required_columns_home = ["GP", "Liga","PIH", "PIH_HA", "Rank_Home", "PPG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "GF_AVG_Home", "GD_Home", "Pts_Home"]
required_columns_away = ["GP", "Liga","PIA", "PIA_HA", "Rank_Away", "PPG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "GF_AVG_Away", "GD_Away", "Pts_Away"]
required_columns_overall = ["GP", "Liga","PIO", "PIO_HA", "Rank_Overall", "PPG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "GF_AVG_Overall", "GD_Overall", "Pts_Overall"]

# Verificar se as colunas necessárias estão presentes
missing_columns_home = [col for col in required_columns_home if col not in home_data.columns]
missing_columns_away = [col for col in required_columns_away if col not in away_data.columns]
missing_columns_away_fav = [col for col in required_columns_away if col not in away_fav_data.columns]
missing_columns_overall = [col for col in required_columns_overall if col not in overall_stats_data.columns]

# Exibir mensagens de erro se houver colunas ausentes
if missing_columns_home:
    st.error(f"Colunas ausentes no dataset Home: {missing_columns_home}")
if missing_columns_away:
    st.error(f"Colunas ausentes no dataset Away: {missing_columns_away}")
if missing_columns_away_fav:
    st.error(f"Colunas ausentes no dataset Away (Favorito): {missing_columns_away_fav}")
if missing_columns_overall:
    st.error(f"Colunas ausentes no dataset Overall: {missing_columns_overall}")

# Prosseguir apenas se não houver colunas ausentes
if not (missing_columns_home or missing_columns_away or missing_columns_away_fav or missing_columns_overall):
    # Filtros para seleção de equipes
    equipe_home = st.sidebar.selectbox(
        "Selecione a equipe Home:",
        sorted(home_data[home_team_col].unique())
    )

    equipe_away = st.sidebar.selectbox(
        "Selecione a equipe Away:",
        sorted(away_data[away_team_col].unique())
    )

    equipe_away_fav = st.sidebar.selectbox(
        "Selecione a equipe Away (Favorito):",
        sorted(away_fav_data[away_fav_team_col].unique())
    )



    # Exibir os dados
    st.subheader("Overall")
    st.dataframe(overall_filtered_team.reset_index(drop=True))

    st.subheader("Home")
    st.dataframe(home_filtered_team.reset_index(drop=True))

    st.subheader("Away (Zebra)")
    st.dataframe(away_filtered_team.reset_index(drop=True))

    st.subheader("Away (Favorito)")
    st.dataframe(away_fav_filtered_team.reset_index(drop=True))

  

else:
    st.error("Corrija os problemas com as colunas ausentes antes de prosseguir.")

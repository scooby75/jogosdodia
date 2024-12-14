import streamlit as st
import pandas as pd

# Configurar o título do aplicativo
st.title("Análise de Confrontos Diretos")

# URLs dos arquivos CSV
home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"
away_fav_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_favorito.csv"

# Função para carregar os dados
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# Carregar os dados das URLs
home_data = load_data(home_url)
away_data = load_data(away_url)
away_fav_data = load_data(away_fav_url)

# Verificar as colunas disponíveis
st.write("Colunas Home:", home_data.columns.tolist())
st.write("Colunas Away:", away_data.columns.tolist())
st.write("Colunas Away (Favorito):", away_fav_data.columns.tolist())

# Definir as colunas principais para filtragem
home_team_col = "Equipe"
away_team_col = "Equipe_Fora"
away_fav_team_col = "Equipe_Fora"

# Verificar se as colunas necessárias existem nos datasets
required_columns_home = ["PIH", "PIH_HA", "GD_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home", "Pts_Home"]
required_columns_away = ["PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away", "Pts_Away"]

if set(required_columns_home).issubset(home_data.columns) and \
   set(required_columns_away).issubset(away_data.columns) and \
   set(required_columns_away).issubset(away_fav_data.columns):
    
    # Sidebar para seleção de equipes
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

    # Filtrar os dados para as equipes selecionadas
    home_filtered = home_data[home_data[home_team_col] == equipe_home][required_columns_home]
    away_filtered = away_data[away_data[away_team_col] == equipe_away][required_columns_away]
    away_fav_filtered = away_fav_data[away_fav_data[away_fav_team_col] == equipe_away_fav][required_columns_away]

    # Exibir os dados filtrados
    st.subheader("Home")
    st.dataframe(home_filtered.reset_index(drop=True))

    st.subheader("Away")
    st.dataframe(away_filtered.reset_index(drop=True))

    st.subheader("Away (Favorito)")
    st.dataframe(away_fav_filtered.reset_index(drop=True))
else:
    st.error("Colunas necessárias ausentes em um ou mais datasets.")

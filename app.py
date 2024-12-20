import streamlit as st
import pandas as pd

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

# Função para normalizar os nomes das colunas (remove espaços extras, etc.)
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

# Normalizar os nomes das colunas
home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)

# Definir as colunas principais para filtragem
home_team_col = "Equipe"
away_team_col = "Equipe_Fora"
away_fav_team_col = "Equipe_Fora"

# Listar as colunas necessárias para cada dataset
required_columns_home = ["PIH", "PIH_HA", "GD_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home", "Pts_Home"]
required_columns_away = ["PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away", "Pts_Away"]

# Verificar se as colunas necessárias estão presentes
missing_columns_home = [col for col in required_columns_home if col not in home_data.columns]
missing_columns_away = [col for col in required_columns_away if col not in away_data.columns]
missing_columns_away_fav = [col for col in required_columns_away if col not in away_fav_data.columns]

# Exibir mensagens de erro se houver colunas ausentes
if missing_columns_home:
    st.error(f"Colunas ausentes no dataset Home: {missing_columns_home}")
if missing_columns_away:
    st.error(f"Colunas ausentes no dataset Away: {missing_columns_away}")
if missing_columns_away_fav:
    st.error(f"Colunas ausentes no dataset Away (Favorito): {missing_columns_away_fav}")

# Prosseguir apenas se não houver colunas ausentes
if not (missing_columns_home or missing_columns_away or missing_columns_away_fav):
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

    # Filtros independentes para PIH e PIA
    pih_min, pih_max = st.sidebar.slider("Intervalo de PIH", float(home_data["PIH"].min()), float(home_data["PIH"].max()), (0.0, 1.0))
    pia_min, pia_max = st.sidebar.slider("Intervalo de PIA", float(away_data["PIA"].min()), float(away_data["PIA"].max()), (0.0, 1.0))

    # Aplicar filtros de PIH e PIA nos datasets completos
    home_filtered_pih = home_data[
        (home_data["PIH"] >= pih_min) & 
        (home_data["PIH"] <= pih_max)
    ][[home_team_col] + required_columns_home]

    away_filtered_pia = away_data[
        (away_data["PIA"] >= pia_min) & 
        (away_data["PIA"] <= pia_max)
    ][[away_team_col] + required_columns_away]

    # Filtrar os dados para as equipes selecionadas
    home_filtered_team = home_data[home_data[home_team_col] == equipe_home][required_columns_home]
    away_filtered_team = away_data[away_data[away_team_col] == equipe_away][required_columns_away]
    away_fav_filtered_team = away_fav_data[away_fav_data[away_fav_team_col] == equipe_away_fav][required_columns_away]

    # Exibir os dados filtrados
    st.subheader("Home")
    st.dataframe(home_filtered_team.reset_index(drop=True))

    st.subheader("Away (Zebra)")
    st.dataframe(away_filtered_team.reset_index(drop=True))

    st.subheader("Away (Favorito)")
    st.dataframe(away_fav_filtered_team.reset_index(drop=True))

    st.subheader("Home (Filtro por PIH)")
    st.dataframe(home_filtered_pih.reset_index(drop=True))

    st.subheader("Away (Filtro por PIA)")
    st.dataframe(away_filtered_pia.reset_index(drop=True))
else:
    st.error("Corrija os problemas com as colunas ausentes antes de prosseguir.")

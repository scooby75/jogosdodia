import streamlit as st
import pandas as pd

# Configurar o título do aplicativo
st.title("H2H")

# URLs dos arquivos CSV
home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"
away_fav_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_favorito.csv"

# Carregar os dados
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

home_data = load_data(home_url)
away_data = load_data(away_url)
away_fav_data = load_data(away_fav_url)

# Colunas específicas para filtragem
home_team_col = "Equipe"
away_team_col = "Equipe_Fora"
away_fav_team_col = "Equipe_Fora"  # Corrigido para "Equipe_Fora"

# Verificar se as colunas existem
if home_team_col not in home_data.columns or away_team_col not in away_data.columns or away_fav_team_col not in away_fav_data.columns:
    st.error("Erro: Não foi possível identificar a coluna de equipes nos dados carregados.")
else:
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

    # Filtrar os dados para Home, Away e Away (Favorito)
    home_filtered = home_data[home_data[home_team_col] == equipe_home][[
        "Pts_Home", "PIH", "PIH_HA", "GD_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA"
    ]] if equipe_home else home_data[[
        "Pts_Home", "PIH", "PIH_HA", "GD_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA"
    ]]

    away_filtered = away_data[away_data[away_team_col] == equipe_away][[
        "Pts_Away", "PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA"
    ]] if equipe_away else away_data[[
        "Pts_Away", "PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA"
    ]]

    away_fav_filtered = away_fav_data[away_fav_data[away_fav_team_col] == equipe_away_fav][[
        "Pts_Away", "PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA"
    ]] if equipe_away_fav else away_fav_data[[
        "Pts_Away", "PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA"
    ]]

    # Exibir os dados filtrados para Home, Away e Away (Favorito) sem o índice
    st.subheader("Jogos - Home")
    st.dataframe(home_filtered.reset_index(drop=True))  # Remover o índice

    st.subheader("Jogos - Away")
    st.dataframe(away_filtered.reset_index(drop=True))  # Remover o índice

    st.subheader("Jogos - Away (Favorito)")
    st.dataframe(away_fav_filtered.reset_index(drop=True))  # Remover o índice

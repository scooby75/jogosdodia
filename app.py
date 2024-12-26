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

# Normalizar colunas
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)

# Verificar colunas necessárias
required_columns_home = ["GP", "Liga", "PIH", "PIH_HA", "GD_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home", "Pts_Home"]
required_columns_away = ["GP", "Liga", "PIA", "PIA_HA", "GD_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away", "Pts_Away"]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Seleção de Equipes", "1x2 (Home e Away)", "HA +0.25", "Média de Gols"])

with tab1:
    st.header("Seleção de Equipes")
    equipe_home = st.selectbox("Selecione a equipe Home:", sorted(home_data["Equipe"].unique()))
    equipe_away = st.selectbox("Selecione a equipe Away:", sorted(away_data["Equipe_Fora"].unique()))

    home_filtered_team = home_data[home_data["Equipe"] == equipe_home]
    away_filtered_team = away_data[away_data["Equipe_Fora"] == equipe_away]

    st.subheader("Dados da Equipe Home")
    st.dataframe(home_filtered_team)

    st.subheader("Dados da Equipe Away")
    st.dataframe(away_filtered_team)

with tab2:
    st.header("1x2 (Home e Away)")
    pih_min, pih_max = st.slider("1x2 (Home)", 0.0, 1.0, (0.0, 1.0))
    pia_min, pia_max = st.slider("1x2 (Away)", 0.0, 1.0, (0.0, 1.0))

    home_filtered_pih = home_data[(home_data["PIH"] >= pih_min) & (home_data["PIH"] <= pih_max)]
    away_filtered_pia = away_data[(away_data["PIA"] >= pia_min) & (away_data["PIA"] <= pia_max)]

    st.subheader("1x2 (Home)")
    st.dataframe(home_filtered_pih)

    st.subheader("1x2 (Away)")
    st.dataframe(away_filtered_pia)

with tab3:
    st.header("HA +0.25")
    piha_min, piha_max = st.slider("HA +0.25 (Home)", 0.0, 1.0, (0.0, 1.0))
    piah_min, piah_max = st.slider("HA +0.25 (Away)", 0.0, 1.0, (0.0, 1.0))

    home_filtered_piha = home_data[(home_data["PIH_HA"] >= piha_min) & (home_data["PIH_HA"] <= piha_max)]
    away_filtered_piah = away_data[(away_data["PIA_HA"] >= piah_min) & (away_data["PIA_HA"] <= piah_max)]

    st.subheader("HA +0.25 (Home)")
    st.dataframe(home_filtered_piha)

    st.subheader("HA +0.25 (Away)")
    st.dataframe(away_filtered_piah)

with tab4:
    st.header("Média de Gols")
    gf_avg_home_min, gf_avg_home_max = st.slider("Média de Gols (Home)", 0.0, 3.0, (0.0, 3.0))
    gf_avg_away_min, gf_avg_away_max = st.slider("Média de Gols (Away)", 0.0, 3.0, (0.0, 3.0))

    home_filtered_gf_avg = home_data[(home_data["GF_AVG_Home"] >= gf_avg_home_min) & (home_data["GF_AVG_Home"] <= gf_avg_home_max)]
    away_filtered_gf_avg = away_data[(away_data["GF_AVG_Away"] >= gf_avg_away_min) & (away_data["GF_AVG_Away"] <= gf_avg_away_max)]

    st.subheader("Média de Gols (Home)")
    st.dataframe(home_filtered_gf_avg)

    st.subheader("Média de Gols (Away)")
    st.dataframe(away_filtered_gf_avg)

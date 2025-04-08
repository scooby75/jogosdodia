import streamlit as st
import pandas as pd

# URLs dos arquivos
home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"
away_fav_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_Favorito.csv"
overall_stats_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/overall_stats.csv"
sf_home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/scored_first_home.csv"
sf_away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/scored_first_away.csv"

# Função para carregar os dados com cache
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# Normalização dos nomes das colunas
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

# Carregando os dados
home_data = normalize_columns(load_data(home_url))
away_data = normalize_columns(load_data(away_url))
away_fav_data = normalize_columns(load_data(away_fav_url))
overall_stats_data = normalize_columns(load_data(overall_stats_url))
sf_home = normalize_columns(load_data(sf_home_url))
sf_away = normalize_columns(load_data(sf_away_url))

# Definição de colunas essenciais
required_columns_home = ["GP", "Liga", "PIH", "PIH_HA", "Rank_Home", "PPG_Home", "Perc.", 
                         "Odd_Justa_MO", "Odd_Justa_HA", "GF_AVG_Home", "GD_Home", "Pts_Home"]
required_columns_away = ["GP", "Liga", "PIA", "PIA_HA", "Rank_Away", "PPG_Away", "Perc.", 
                         "Odd_Justa_MO", "Odd_Justa_HA", "GF_AVG_Away", "GD_Away", "Pts_Away"]
required_columns_overall = ["GP", "Liga", "PIO", "PIO_HA", "Rank_Overall", "PPG_Overall", 
                            "Odd_Justa_MO", "Odd_Justa_HA", "GF_AVG_Overall", "GD_Overall", "Pts_Overall"]

# Verificação de colunas ausentes
def check_missing_columns(df, required_cols, name):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Colunas ausentes no dataset {name}: {missing}")
    return missing

missing_home = check_missing_columns(home_data, required_columns_home, "Home")
missing_away = check_missing_columns(away_data, required_columns_away, "Away")
missing_away_fav = check_missing_columns(away_fav_data, required_columns_away, "Away (Favorito)")
missing_overall = check_missing_columns(overall_stats_data, required_columns_overall, "Overall")

# Se não houver colunas ausentes, mostra os filtros e análises
if not (missing_home or missing_away or missing_away_fav or missing_overall):

    equipe_home = st.sidebar.selectbox("Selecione a equipe Home:", sorted(home_data["Equipe"].unique()))
    equipe_away = st.sidebar.selectbox("Selecione a equipe Away:", sorted(away_data["Equipe_Fora"].unique()))
    equipe_away_fav = st.sidebar.selectbox("Selecione a equipe Away (Favorito):", sorted(away_fav_data["Equipe_Fora"].unique()))

    # Filtros personalizados
    pih_min, pih_max = st.sidebar.slider("1x2 (Home)", 0.0, 1.0, (0.0, 1.0))
    pia_min, pia_max = st.sidebar.slider("1x2 (Away)", 0.0, 1.0, (0.0, 1.0))
    piha_min, piha_max = st.sidebar.slider("HA +0.25 (Home)", 0.0, 1.0, (0.0, 1.0))
    piah_min, piah_max = st.sidebar.slider("HA +0.25 (Away)", 0.0, 1.0, (0.0, 1.0))

    gf_avg_home_min, gf_avg_home_max = st.sidebar.slider("Média de Gols (Home)", 
        float(home_data["GF_AVG_Home"].min()), 
        float(home_data["GF_AVG_Home"].max()), 
        (float(home_data["GF_AVG_Home"].min()), float(home_data["GF_AVG_Home"].max())))

    gf_avg_away_min, gf_avg_away_max = st.sidebar.slider("Média de Gols (Away)", 
        float(away_data["GF_AVG_Away"].min()), 
        float(away_data["GF_AVG_Away"].max()), 
        (float(away_data["GF_AVG_Away"].min()), float(away_data["GF_AVG_Away"].max())))

    # Aplicar os filtros
    home_filtered_team = home_data[home_data["Equipe"] == equipe_home][required_columns_home]
    away_filtered_team = away_data[away_data["Equipe_Fora"] == equipe_away][required_columns_away]
    away_fav_filtered_team = away_fav_data[away_fav_data["Equipe_Fora"] == equipe_away_fav][required_columns_away]
    overall_filtered_team = overall_stats_data[overall_stats_data["Equipe"] == equipe_home][required_columns_overall]

    home_filtered_pih = home_data[(home_data["PIH"] >= pih_min) & (home_data["PIH"] <= pih_max)]
    away_filtered_pia = away_data[(away_data["PIA"] >= pia_min) & (away_data["PIA"] <= pia_max)]
    home_filtered_piha = home_data[(home_data["PIH_HA"] >= piha_min) & (home_data["PIH_HA"] <= piha_max)]
    away_filtered_piah = away_data[(away_data["PIA_HA"] >= piah_min) & (away_data["PIA_HA"] <= piah_max)]
    home_filtered_gf_avg = home_data[(home_data["GF_AVG_Home"] >= gf_avg_home_min) & (home_data["GF_AVG_Home"] <= gf_avg_home_max)]
    away_filtered_gf_avg = away_data[(away_data["GF_AVG_Away"] >= gf_avg_away_min) & (away_data["GF_AVG_Away"] <= gf_avg_away_max)]

    # Exibição dos dados
    st.subheader("Overall")
    st.dataframe(overall_filtered_team.reset_index(drop=True))

    st.subheader("Home")
    st.dataframe(home_filtered_team.reset_index(drop=True))

    st.subheader("Away (Zebra)")
    st.dataframe(away_filtered_team.reset_index(drop=True))

    st.subheader("Away (Favorito)")
    st.dataframe(away_fav_filtered_team.reset_index(drop=True))

    st.subheader("1x2 (Home)")
    st.dataframe(home_filtered_pih.reset_index(drop=True))

    st.subheader("1x2 (Away)")
    st.dataframe(away_filtered_pia.reset_index(drop=True))

    st.subheader("HA +0.25 (Home)")
    st.dataframe(home_filtered_piha.reset_index(drop=True))

    st.subheader("HA +0.25 (Away)")
    st.dataframe(away_filtered_piah.reset_index(drop=True))

    st.subheader("Média de Gols (Casa)")
    st.dataframe(home_filtered_gf_avg.reset_index(drop=True))

    st.subheader("Média de Gols (Away)")
    st.dataframe(away_filtered_gf_avg.reset_index(drop=True))

else:
    st.warning("Verifique os arquivos com colunas ausentes e corrija antes de continuar.")

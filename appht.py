import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
from collections import Counter
import itertools
import math
from scipy.stats import poisson

# Configuração da página
st.set_page_config(page_title="Football Stats HT", layout="wide")

# ----------------------------
# FUNÇÃO UTILITÁRIA PARA CARREGAR CSV
# ----------------------------
@st.cache_data
def load_csv(url):
    df = pd.read_csv(url, encoding="utf-8-sig")
    df = df.dropna(axis=1, how='all')  # Remove colunas totalmente vazias
    df.columns = df.columns.str.strip()  # Limpa os nomes das colunas
    return df

# ----------------------------
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ----------------------------

@st.cache_data
def load_first_goal_data():
    urls = [
        "https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_home.csv",
        "https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_away.csv"
    ]
    return [load_csv(url) for url in urls]

@st.cache_data
def load_goal_minute_data():
    urls = [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_away.csv"
    ]
    return [load_csv(url) for url in urls]

@st.cache_data
def load_goals_half_data():
    return load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Half.csv")

@st.cache_data
def goals_ht_data():
    urls = [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Away.csv"
    ]
    return [load_csv(url) for url in urls]

@st.cache_data
def goals_per_time_data():
    urls = [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Per_Time_Home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Per_Time_Away.csv"
    ]
    return [load_csv(url) for url in urls]

@st.cache_data
def ppg_ht_data():
    urls = [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/PPG_HT_Home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/PPG_HT_Away.csv"
    ]
    return [load_csv(url) for url in urls]

# ----------------------------
# NORMALIZAÇÃO DE COLUNAS
# ----------------------------
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

# ----------------------------
# CARREGAMENTO DOS DADOS
# ----------------------------

home_fg_df, away_fg_df = load_first_goal_data()
goal_minute_home_df, goal_minute_away_df = load_goal_minute_data()
goals_half_df = load_goals_half_data()
cv_home_df, cv_away_df = goals_ht_data()
goals_per_time_home_df, goals_per_time_away_df = goals_per_time_data()
ppg_ht_home_df, ppg_ht_away_df = ppg_ht_data()

# Normalizar todas as tabelas
all_dfs = [
    home_fg_df, away_fg_df, goal_minute_home_df, goal_minute_away_df, goals_half_df, cv_home_df, cv_away_df,
    goals_per_time_home_df, goals_per_time_away_df, ppg_ht_home_df, ppg_ht_away_df
]
for df in all_dfs:
    normalize_columns(df)

# ----------------------------
# Lista de times para seleção
# ----------------------------
all_teams = sorted(set(
    home_fg_df['Team_Home'].dropna().astype(str)[home_fg_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    away_fg_df['Team_Away'].dropna().astype(str)[away_fg_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goal_minute_home_df['Team_Home'].dropna().astype(str)[goal_minute_home_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goal_minute_away_df['Team_Away'].dropna().astype(str)[goal_minute_away_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goals_half_df['Team'].dropna().astype(str)[goals_half_df['Team'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goals_per_time_home_df['Team_Home'].dropna().astype(str)[goals_per_time_home_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goals_per_time_away_df['Team_Away'].dropna().astype(str)[goals_per_time_away_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    ppg_ht_home_df['Team_Home'].dropna().astype(str)[ppg_ht_home_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    ppg_ht_away_df['Team_Away'].dropna().astype(str)[ppg_ht_away_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist()
))

# Seleção dos times para a interface
equipe_home = st.sidebar.selectbox("🏠 Time da Casa:", all_teams, index=all_teams.index('Bayern Munich') if 'Bayern Munich' in all_teams else 0)
equipe_away = st.sidebar.selectbox("🛫 Time Visitante:", all_teams, index=all_teams.index('Dortmund') if 'Dortmund' in all_teams else 0)

# ----------------------------
# INTERFACE STREAMLIT
# ----------------------------
tabs = st.tabs([
    "⚠️ Analitico", "🧾 h2h", "⚽ First Goal", "⏱️ Goals_Minute", "⚡ Goals HT/FT", "📌 CV HT", "📊 Goals Per Time"
])

# ABA 1 - H2H (índice 1)
with tabs[1]:
    home_stats = ppg_ht_home_df[ppg_ht_home_df['Team_Home'] == equipe_home]
    away_stats = ppg_ht_away_df[ppg_ht_away_df['Team_Away'] == equipe_away]

    if not home_stats.empty:
        st.subheader(f"📋 Estatísticas do {equipe_home}")
        st.dataframe(home_stats[['League','Team_Home','GP','PIH','PIH_HA','PPG_HT_Home','GF_AVG_Home','Odd_Justa_MO','Rank_Home']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para o time da casa: {equipe_home}")

    if not away_stats.empty:
        st.subheader(f"📋 Estatísticas do {equipe_away}")
        st.dataframe(away_stats[['League','Team_Away','GP','PIA','PIA_HA','PPG_HT_Away','GF_AVG_Away','Odd_Justa_MO','Rank_Away']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para o time visitante: {equipe_away}")

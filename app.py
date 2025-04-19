import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise Geral e H2H - First Goal", layout="wide")

# ---------------------------- 
# FUNÇÕES DE CARREGAMENTO 
# ---------------------------- 
@st.cache_data
def load_csv(url):
    return pd.read_csv(url)

@st.cache_data
def load_all_data():
    home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
    away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"
    away_fav_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_Favorito.csv"
    overall_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/overall_stats.csv"
    return (
        load_csv(home_url),
        load_csv(away_url),
        load_csv(away_fav_url),
        load_csv(overall_url),
    )

@st.cache_data
def load_first_goal_data():
    home_url = 'https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_home.csv'
    away_url = 'https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_away.csv'
    return load_csv(home_url), load_csv(away_url)

@st.cache_data
def load_avg_minute_data():
    avg_min_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_home.csv"
    return load_csv(avg_min_url)

# ----------------------------
# INÍCIO DO APP
# ----------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Análise Home", 
    "📊 Análise Geral", 
    "🛫 Análise Away", 
    "⚽ First Goal",
    "⏱️ AVG Minute"
])

# Carregar dados
home_data, away_data, away_fav_data, overall_data = load_all_data()
avg_min_data = load_avg_minute_data()

def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)
overall_data = normalize_columns(overall_data)
avg_min_data = normalize_columns(avg_min_data)

# Seletor de equipes
equipe_home = st.sidebar.selectbox("🏠 Time da Casa:", sorted(home_data['Equipe'].dropna().unique()))
equipe_away = st.sidebar.selectbox("🛫 Time Visitante:", sorted(away_data['Equipe_Fora'].dropna().unique()))
equipe_away_fav = st.sidebar.selectbox("⭐ Visitante (Favorito):", sorted(away_fav_data['Equipe_Fora'].dropna().unique()))

# Filtrar dados
home_filtered = home_data[home_data['Equipe'] == equipe_home]
away_filtered = away_data[away_data['Equipe_Fora'] == equipe_away]
away_fav_filtered = away_fav_data[away_fav_data['Equipe_Fora'] == equipe_away_fav]
overall_filtered = overall_data[overall_data['Equipe'] == equipe_home]

# ============================================================
# ABA 1 - ANÁLISE HOME
# ============================================================
with tab1:
    
    st.markdown("### Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 2 - ANÁLISE GERAL
# ============================================================
with tab2:
    
    st.markdown("### Home")
    st.dataframe(overall_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 3 - ANÁLISE AWAY
# ============================================================
with tab3:
    
    st.markdown("### Away")
    st.dataframe(away_fav_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 4 - FIRST GOAL
# ============================================================
with tab4:
    home_first_goal_data, away_first_goal_data = load_first_goal_data()
    
    # Filtrando apenas os dados do time de casa e visitante selecionados
    home_first_goal_filtered = home_first_goal_data[home_first_goal_data['Home'] == equipe_home]
    away_first_goal_filtered = away_first_goal_data[away_first_goal_data['Away'] == equipe_away]
    
    st.markdown(f"### {equipe_home} - First Goal")
    st.dataframe(home_first_goal_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown(f"### {equipe_away} - First Goal")
    st.dataframe(away_first_goal_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 5 - AVG MINUTE
# ============================================================
with tab5:
    # Filtrando apenas os dados do time de casa e visitante selecionados
    avg_min_home_filtered = avg_min_data[avg_min_data['Home'] == equipe_home]
    avg_min_away_filtered = avg_min_data[avg_min_data['Away'] == equipe_away]
    
    # Exibindo a média de minutos para gol dos times selecionados
    if 'AVG_min_scored' in avg_min_home_filtered.columns:
        avg_min_home_df = avg_min_home_filtered[['league', 'Home', 'AVG_min_scored']]
        avg_min_home_df = avg_min_home_df.rename(columns={'league': 'Liga', 'Home': 'Equipe', 'AVG_min_scored': 'AVG Goals'})
        st.markdown(f"### Média de Minutos para Gol - {equipe_home} (Home)")
        st.dataframe(avg_min_home_df.reset_index(drop=True), use_container_width=True)

    if 'AVG_min_scored' in avg_min_away_filtered.columns:
        avg_min_away_df = avg_min_away_filtered[['league', 'Away', 'AVG_min_scored']]
        avg_min_away_df = avg_min_away_df.rename(columns={'league': 'Liga', 'Away': 'Equipe', 'AVG_min_scored': 'AVG Goals'})
        st.markdown(f"### Média de Minutos para Gol - {equipe_away} (Away)")
        st.dataframe(avg_min_away_df.reset_index(drop=True), use_container_width=True)

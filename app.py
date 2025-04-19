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

# ----------------------------
# INÍCIO DO APP
# ----------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Análise Home", 
    "📊 Análise Geral", 
    "🛫 Análise Away", 
    "⚽ First Goal"
])

# Carregar dados
home_data, away_data, away_fav_data, overall_data = load_all_data()

def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)
overall_data = normalize_columns(overall_data)

# Colunas obrigatórias
home_columns = ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"]
away_columns = ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"]
overall_columns = ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]

# Seletor de equipes
equipe_home = st.sidebar.selectbox("🏠 Time da Casa:", sorted(home_data['Equipe'].dropna().unique()))
equipe_away = st.sidebar.selectbox("🛫 Time Visitante:", sorted(away_data['Equipe_Fora'].dropna().unique()))
equipe_away_fav = st.sidebar.selectbox("⭐ Visitante (Favorito):", sorted(away_fav_data['Equipe_Fora'].dropna().unique()))

# Filtrar dados
home_filtered = home_data[home_data['Equipe'] == equipe_home][home_columns]
away_filtered = away_data[away_data['Equipe_Fora'] == equipe_away][away_columns]
away_fav_filtered = away_fav_data[away_fav_data['Equipe_Fora'] == equipe_away_fav][away_columns]
overall_filtered = overall_data[overall_data['Equipe'] == equipe_home][overall_columns]

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
# ABA 4 - AVG Min
# ============================================================
with tab4:
    # Carregar o arquivo CSV contendo os dados de "AVG_min_scored"
    avg_min_data = load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_home.csv")
    
    # Exibir as primeiras linhas do DataFrame para verificar os dados
    st.write("Primeiras linhas dos dados:", avg_min_data.head())

    # Filtrar e renomear as colunas para exibir as informações necessárias
    if 'AVG_min_scored' in avg_min_data.columns:
        avg_min_df = avg_min_data[['league', 'Home', 'AVG_min_scored']]  # Nome das colunas de acordo com os dados fornecidos
        avg_min_df = avg_min_df.rename(columns={'league': 'Liga', 'Home': 'Equipe', 'AVG_min_scored': 'AVG Goals'})
        st.dataframe(avg_min_df.reset_index(drop=True), use_container_width=True)
    else:
        st.warning("A coluna 'AVG_min_scored' não foi encontrada nos dados.")

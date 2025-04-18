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
#st.title("📈 Painel de Análise de Equipes e H2H - First Goal")

tab1, tab2 = st.tabs(["🔍 H2H", "⚽ First Goal"])

# ============================================================
# ABA 1 - ANÁLISE GERAL
# ============================================================
with tab1:
    st.subheader("H2H")

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

    # Barra de pesquisa na aba Análise Geral
    equipe_home = st.selectbox("🔍 Selecione o Time da Casa:", sorted(home_data['Equipe'].dropna().unique()))
    equipe_away = st.selectbox("🔍 Selecione o Time Visitante:", sorted(away_data['Equipe_Fora'].dropna().unique()))
    equipe_away_fav = st.selectbox("🔍 Time Visitante (Favorito):", sorted(away_fav_data['Equipe_Fora'].dropna().unique()))

    # Filtro
    home_filtered = home_data[home_data['Equipe'] == equipe_home][home_columns]
    away_filtered = away_data[away_data['Equipe_Fora'] == equipe_away][away_columns]
    away_fav_filtered = away_fav_data[away_fav_data['Equipe_Fora'] == equipe_away_fav][away_columns]
    overall_filtered = overall_data[overall_data['Equipe'] == equipe_home][overall_columns]

    # Exibindo os dados um abaixo do outro
    st.markdown("### Home/Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Home/Overall")
    st.dataframe(overall_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Away/Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Away (Favorito)")
    st.dataframe(away_fav_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 2 - H2H - FIRST GOAL
# ============================================================
with tab2:
    st.subheader("First Goal")

    home_fg_df, away_fg_df = load_first_goal_data()

    teams_home = sorted(home_fg_df['Team_Home'].dropna().unique())
    teams_away = sorted(away_fg_df['Team_Away'].dropna().unique())

    team1 = st.selectbox("Home", teams_home)
    team2 = st.selectbox("Away", teams_away)

    def show_team_stats(team_name, df, col_name, local):
        stats = df[df[col_name] == team_name]
        if not stats.empty:
            st.markdown(f"### {team_name} ({local})")
            selected_cols = ['Matches', 'First_Gol', 'Goals', 'PPG']
            display_stats = stats[selected_cols] if all(col in stats.columns for col in selected_cols) else stats
            st.dataframe(display_stats.reset_index(drop=True), use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {team_name} ({local})")

    st.markdown("### Home")
    show_team_stats(team1, home_fg_df, 'Team_Home', 'Casa')

    st.markdown("### Away")
    show_team_stats(team2, away_fg_df, 'Team_Away', 'Fora')

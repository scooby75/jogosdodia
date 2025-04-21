import streamlit as st
import pandas as pd
import os

# Configuração da página do Streamlit
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
def load_goal_minute_data():
    home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_home.csv"
    away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_away.csv"
    return load_csv(home_url), load_csv(away_url)

@st.cache_data
def load_goals_half_data():
    url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Half.csv"
    return load_csv(url)

@st.cache_data
def goals_ht_data():
    home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Home.csv"
    away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Away.csv"
    return load_csv(home_url), load_csv(away_url)

# ---------------------------- 
# INÍCIO DO APP
# ----------------------------

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🧾 Resumo",
    "🏠 Análise Home", 
    "📊 Análise Geral", 
    "🛫 Análise Away", 
    "⚽ First Goal",
    "⏱️ Goals_Minute",
    "⚡ Goals HT/FT",
    "📌 Goals HT"
    
])

# Carregar dados
home_data, away_data, away_fav_data, overall_data = load_all_data()
home_fg_df, away_fg_df = load_first_goal_data()
goal_minute_home_df, goal_minute_away_df = load_goal_minute_data()
goals_half_df = load_goals_half_data()

# Normalizar colunas
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)
overall_data = normalize_columns(overall_data)
goal_minute_home_df = normalize_columns(goal_minute_home_df)
goal_minute_away_df = normalize_columns(goal_minute_away_df)
goals_half_df = normalize_columns(goals_half_df)

# Colunas obrigatórias
home_columns = ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"]
away_columns = ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"]
overall_columns = ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]

# Coletar todos os nomes únicos das equipes
all_teams = sorted(set(home_data['Equipe'].dropna()) |
                   set(away_data['Equipe_Fora'].dropna()) |
                   set(away_fav_data['Equipe_Fora'].dropna()) |
                   set(overall_data['Equipe'].dropna()) |
                   set(home_fg_df['Team_Home'].dropna()) |
                   set(away_fg_df['Team_Away'].dropna()) |
                   set(goal_minute_home_df['Home'].dropna()) |
                   set(goal_minute_away_df['Away'].dropna()) |
                   set(goals_half_df['Team'].dropna()))

# Seletores globais
equipe_home_global = st.sidebar.selectbox("🏠 Time da Casa:", all_teams)
equipe_away_global = st.sidebar.selectbox("🛫 Time Visitante:", all_teams)

# Filtros principais
home_filtered = home_data[home_data['Equipe'] == equipe_home_global][home_columns]
away_filtered = away_data[away_data['Equipe_Fora'] == equipe_away_global][away_columns]
away_fav_filtered = away_fav_data[away_fav_data['Equipe_Fora'] == equipe_away_global][away_columns]
overall_filtered = overall_data[overall_data['Equipe'] == equipe_home_global][overall_columns]

# ABA 1
with tab1:
    st.markdown("### Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)
    st.markdown("### Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

# ABA 2
with tab2:
    st.markdown("### Home - Geral")
    st.dataframe(overall_filtered.reset_index(drop=True), use_container_width=True)
    st.markdown("### Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

# ABA 3
with tab3:
    st.markdown("### Away - Favorito")
    st.dataframe(away_fav_filtered.reset_index(drop=True), use_container_width=True)
    st.markdown("### Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

# ABA 4
with tab4:
    def show_team_stats(team_name, df, col_name, local):
        stats = df[df[col_name] == team_name]
        if not stats.empty:
            st.markdown(f"### {team_name} ({local})")
            selected_cols = ['Matches', 'First_Gol', 'Goals']
            display_stats = stats[selected_cols] if all(col in stats.columns for col in selected_cols) else stats
            st.dataframe(display_stats.reset_index(drop=True), use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {team_name} ({local})")

    show_team_stats(equipe_home_global, home_fg_df, 'Team_Home', 'Casa')
    show_team_stats(equipe_away_global, away_fg_df, 'Team_Away', 'Fora')

# ABA 5
with tab5:
    home_team_data = goal_minute_home_df[goal_minute_home_df['Home'] == equipe_home_global]
    if not home_team_data.empty:
        avg_minute_home = home_team_data['AVG_min_scored'].values[0]
        st.success(f"Jogando em casa **{equipe_home_global}** marca seu primeiro gol em média aos **{avg_minute_home:.1f} minutos**.")
    else:
        st.warning("Nenhum dado encontrado para o time da casa.")

    away_team_data = goal_minute_away_df[goal_minute_away_df['Away'] == equipe_away_global]
    if not away_team_data.empty:
        avg_minute_away = away_team_data['AVG_min_scored'].values[0]
        st.success(f"Jogando fora **{equipe_away_global}** marca seu primeiro gol em média aos **{avg_minute_away:.1f} minutos**.")
    else:
        st.warning("Nenhum dado encontrado para o time visitante.")

# ABA 6
with tab6:
    goals_half_filtered = goals_half_df[
        (goals_half_df['Team'] == equipe_home_global) | (goals_half_df['Team'] == equipe_away_global)
    ]
    if not goals_half_filtered.empty:
        st.dataframe(goals_half_filtered[['League_Name', 'Team', 'Scored', '1st half', '2nd half']].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Nenhuma estatística de Goals Half encontrada.")


# ABA 7 - Goals HT
with tab7:
    #st.markdown("## ⚡ Análise de Gols no 1º Tempo")

    # Carregar os dados específicos
    cv_home_df, cv_away_df = goals_ht_data()

    # Normalizar colunas se necessário
    cv_home_df = normalize_columns(cv_home_df)
    cv_away_df = normalize_columns(cv_away_df)

    # Filtrar dados pelo time selecionado
    home_ht_filtered = cv_home_df[cv_home_df['Team'] == equipe_home_global]
    away_ht_filtered = cv_away_df[cv_away_df['Team'] == equipe_away_global]

    # Exibir dados do time da casa
    st.subheader(f"🏠 {equipe_home_global} - CV Gols no 1º Tempo (Home)")
    home_cols = ["4+", "3", "2", "1", "0", "Avg.", "Home", "CV_Goals_HT (%)", "Classificação CV"]
    if not home_ht_filtered.empty:
        st.dataframe(home_ht_filtered[home_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Dados não encontrados para o time da casa.")

    # Exibir dados do time visitante
    st.subheader(f"🛫 {equipe_away_global} - CV Gols no 1º Tempo (Away)")
    away_cols = ["Away", "Avg..1", "0.1", "1.1", "2.1", "3.1", "4+.1", "CV_Goals_HT (%)", "Classificação CV"]
    if not away_ht_filtered.empty:
        st.dataframe(away_ht_filtered[away_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Dados não encontrados para o time visitante.")

# ABA 8 - RESUMO
with tab8:
    st.markdown("## Resumo Geral")
    
    st.subheader("🏠 Dados Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

    st.subheader("🛫 Dados Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

    st.subheader("📊 Dados Gerais (Overall)")
    st.dataframe(overall_filtered.reset_index(drop=True), use_container_width=True)

    st.subheader("⚽ First Goal")
    show_team_stats(equipe_home_global, home_fg_df, 'Team_Home', 'Casa')
    show_team_stats(equipe_away_global, away_fg_df, 'Team_Away', 'Fora')

    st.subheader("⏱️ Minuto do 1º Gol")
    if not home_team_data.empty:
        st.write(f"🏠 **{equipe_home_global}**: {avg_minute_home:.1f} min")
    if not away_team_data.empty:
        st.write(f"🛫 **{equipe_away_global}**: {avg_minute_away:.1f} min")

    st.subheader("⚡ Gols HT/FT")
    if not goals_half_filtered.empty:
        st.dataframe(goals_half_filtered[['League_Name', 'Team', 'Scored', '1st half', '2nd half']].reset_index(drop=True), use_container_width=True)

    st.subheader("📌 Goals HT")
    if not home_ht_filtered.empty:
        st.markdown(f"🏠 **{equipe_home_global}**")
        st.dataframe(home_ht_filtered.reset_index(drop=True), use_container_width=True)
    if not away_ht_filtered.empty:
        st.markdown(f"🛫 **{equipe_away_global}**")
        st.dataframe(away_ht_filtered.reset_index(drop=True), use_container_width=True)


# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

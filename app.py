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
def load_goal_half_data():
    url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Half.csv"
    return pd.read_csv(url)

# Carregar dados
home_data, away_data, away_fav_data, overall_data = load_all_data()
home_fg_df, away_fg_df = load_first_goal_data()
goal_half_df = load_goal_half_data()

# Normalizar colunas
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

home_data = normalize_columns(home_data)
away_data = normalize_columns(away_data)
away_fav_data = normalize_columns(away_fav_data)
overall_data = normalize_columns(overall_data)
goal_half_df = normalize_columns(goal_half_df)

# Coletar todos os nomes únicos das equipes
all_teams = sorted(set(home_data['Equipe'].dropna()) |
                   set(away_data['Equipe_Fora'].dropna()) |
                   set(away_fav_data['Equipe_Fora'].dropna()) |
                   set(overall_data['Equipe'].dropna()) |
                   set(home_fg_df['Team_Home'].dropna()) |
                   set(away_fg_df['Team_Away'].dropna()))

# Seletores globais
equipe_home_global = st.sidebar.selectbox("🏠 Time da Casa:", all_teams)
equipe_away_global = st.sidebar.selectbox("🛫 Time Visitante:", all_teams)

# Função para exibir as estatísticas de Goal Half
def show_goal_half_stats(team_name, df):
    team_data = df[df['Team'] == team_name]
    if not team_data.empty:
        # Exibir apenas as colunas relevantes para a estatística
        selected_cols = ['League_Name', 'Team', 'Scored', '1st half', '2nd half', 'Avg. minute']
        st.dataframe(team_data[selected_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para {team_name}.")

# ---------------------------- 
# INÍCIO DO APP
# ----------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([ 
    "🏠 Análise Home", 
    "📊 Análise Geral", 
    "🛫 Análise Away", 
    "⚽ First Goal",
    "⏱️ Goals_Minute", 
    "⚽ Goal Half"
])

# ============================================================
# ABA 1 - ANÁLISE HOME
# ============================================================
with tab1:
    st.markdown("### Home")
    home_columns = ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"]
    home_filtered = home_data[home_data['Equipe'] == equipe_home_global][home_columns]
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Away")
    away_columns = ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"]
    away_filtered = away_data[away_data['Equipe_Fora'] == equipe_away_global][away_columns]
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 2 - ANÁLISE GERAL
# ============================================================
with tab2:
    st.markdown("### Home")
    overall_columns = ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]
    overall_filtered = overall_data[overall_data['Equipe'] == equipe_home_global][overall_columns]
    st.dataframe(overall_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Away")
    st.dataframe(away_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 3 - ANÁLISE AWAY
# ============================================================
with tab3:
    st.markdown("### Away")
    away_fav_columns = ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"]
    away_fav_filtered = away_fav_data[away_fav_data['Equipe_Fora'] == equipe_away_global][away_fav_columns]
    st.dataframe(away_fav_filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Home")
    st.dataframe(home_filtered.reset_index(drop=True), use_container_width=True)

# ============================================================
# ABA 4 - FIRST GOAL
# ============================================================
with tab4:
    def show_team_stats(team_name, df, col_name, local):
        stats = df[df[col_name] == team_name]
        if not stats.empty:
            st.markdown(f"### {team_name} ({local})")
            selected_cols = ['Matches', 'First_Gol', 'Goals', 'PPG']
            display_stats = stats[selected_cols] if all(col in stats.columns for col in selected_cols) else stats
            st.dataframe(display_stats.reset_index(drop=True), use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {team_name} ({local})")

    show_team_stats(equipe_home_global, home_fg_df, 'Team_Home', 'Casa')
    show_team_stats(equipe_away_global, away_fg_df, 'Team_Away', 'Fora')

# ============================================================
# ABA 5 - GOALS_MINUTE
# ============================================================
with tab5:
    # Dados para o time da casa
    home_team_data = goal_minute_home_df[goal_minute_home_df['Home'] == equipe_home_global]
    if not home_team_data.empty:
        avg_minute_home = home_team_data['AVG_min_scored'].values[0]
        st.success(f"Jogando em casa **{equipe_home_global}** marca seu primeiro gol em média aos **{avg_minute_home:.1f} minutos**.")
    else:
        st.warning("Nenhum dado encontrado para o time da casa selecionado.")

    # Dados para o time visitante
    away_team_data = goal_minute_away_df[goal_minute_away_df['Away'] == equipe_away_global]
    if not away_team_data.empty:
        avg_minute_away = away_team_data['AVG_min_scored'].values[0]
        st.success(f"Jogando Fora **{equipe_away_global}** marca seu primeiro gol em média aos **{avg_minute_away:.1f} minutos**.")
    else:
        st.warning("Nenhum dado encontrado para o time visitante selecionado.")

# ============================================================
# ABA 6 - GOAL HALF
# ============================================================
with tab6:
    def show_goal_half_stats(team_name, df):
        team_data = df[df['Team'] == team_name]
        if not team_data.empty:
            # Exibir apenas as colunas relevantes para a estatística
            selected_cols = ['League_Name', 'Team', 'Scored', '1st half', '2nd half', 'Avg. minute']
            st.dataframe(team_data[selected_cols].reset_index(drop=True), use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {team_name}.")

    st.markdown(f"### Estatísticas de Goal Half para {equipe_home_global} (Casa)")
    show_goal_half_stats(equipe_home_global, goal_half_df)

    st.markdown(f"### Estatísticas de Goal Half para {equipe_away_global} (Visitante)")
    show_goal_half_stats(equipe_away_global, goal_half_df)

# Iniciar o servidor Streamlit com a variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Usa a variável de ambiente PORT ou 10000 por padrão
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

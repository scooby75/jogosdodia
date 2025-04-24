import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Football Stats", layout="wide")

# ----------------------------
# FUNÇÕES DE CARREGAMENTO
# ----------------------------
@st.cache_data
def load_csv(url):
    return pd.read_csv(url)

@st.cache_data
def load_all_data():
    urls = [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_Favorito.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/overall_stats.csv"
    ]
    return [load_csv(url) for url in urls]

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

# ----------------------------
# NORMALIZAÇÃO DE COLUNAS
# ----------------------------
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    return df

# ----------------------------
# CARREGAMENTO DOS DADOS
# ----------------------------
home_df, away_df, away_fav_df, overall_df = load_all_data()
home_fg_df, away_fg_df = load_first_goal_data()
goal_minute_home_df, goal_minute_away_df = load_goal_minute_data()
goals_half_df = load_goals_half_data()
cv_home_df, cv_away_df = goals_ht_data()
goals_per_time_home_df, goals_per_time_away_df = goals_per_time_data()

# Normalizar todas as tabelas
all_dfs = [
    home_df, away_df, away_fav_df, overall_df, home_fg_df, away_fg_df,
    goal_minute_home_df, goal_minute_away_df, goals_half_df, cv_home_df, cv_away_df,
    goals_per_time_home_df, goals_per_time_away_df
]
for df in all_dfs:
    normalize_columns(df)

# ----------------------------
# VARIÁVEIS GLOBAIS
# ----------------------------
home_columns = ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"]
away_columns = ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"]
overall_columns = ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]

# Combina todas as equipes de várias fontes
all_teams = sorted(set(
    home_df['Team_Home'].dropna().astype(str)) |
    set(away_df['Team_Away'].dropna().astype(str)) |
    set(away_fav_df['Team_Away_Fav'].dropna().astype(str)) |
    set(overall_df['Team_Home'].dropna().astype(str)) |
    set(home_fg_df['Team_Home'].dropna().astype(str)) |
    set(away_fg_df['Team_Away'].dropna().astype(str)) |
    set(goal_minute_home_df['Team_Home'].dropna().astype(str)) |
    set(goal_minute_away_df['Team_Away'].dropna().astype(str)) |
    set(goals_half_df['Team'].dropna().astype(str)) |
    set(goals_per_time_home_df['Team_Home'].dropna().astype(str)) |
    set(goals_per_time_away_df['Team_Away'].dropna().astype(str))
)


equipe_home = st.sidebar.selectbox("🏠 Time da Casa:", all_teams)
equipe_away = st.sidebar.selectbox("🛫 Time Visitante:", all_teams)

# ----------------------------
# APLICAR FILTROS
# ----------------------------
home_filtered = home_df[home_df['Equipe'] == equipe_home][home_columns]
away_filtered = away_df[away_df['Equipe_Fora'] == equipe_away][away_columns]
away_fav_filtered = away_fav_df[away_fav_df['Equipe_Fora'] == equipe_away][away_columns]
overall_filtered = overall_df[overall_df['Equipe'] == equipe_home][overall_columns]

# ----------------------------
# INTERFACE STREAMLIT
# ----------------------------
tabs = st.tabs([
    "🏠 Home", "📊 Overall", "🛫 Away",
    "⚽ First Goal", "⏱️ Goals_Minute", "⚡ Goals HT/FT", "📌 CV HT", "🧾 Resumo", "📊 Goals Per Time"
])

# Função para exibir stats do time
def show_team_stats(team_name, df, col_name, local):
    stats = df[df[col_name] == team_name]
    if not stats.empty:
        st.markdown(f"### {team_name} ({local})")
        cols = ['Matches', 'First_Gol', 'Goals']
        st.dataframe(stats[cols] if all(c in stats.columns for c in cols) else stats, use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para {team_name} ({local})")

# ABA 1 - Home Favorito
with tabs[7]:
    st.markdown("### Home")
    st.dataframe(home_filtered, use_container_width=True)
    st.markdown("### Away")
    st.dataframe(away_filtered, use_container_width=True)

# ABA 2 - Home Geral
with tabs[1]:
    st.markdown("### Home - Geral")
    st.dataframe(overall_filtered, use_container_width=True)
    st.markdown("### Away")
    st.dataframe(away_filtered, use_container_width=True)

# ABA 3 - Away Favorito
with tabs[2]:
    st.markdown("### Away - Favorito")
    st.dataframe(away_fav_filtered, use_container_width=True)
    st.markdown("### Home")
    st.dataframe(home_filtered, use_container_width=True)

# ABA 4 - First Goal
with tabs[3]:
    show_team_stats(equipe_home, home_fg_df, 'Team_Home', 'Casa')
    show_team_stats(equipe_away, away_fg_df, 'Team_Away', 'Fora')

# ABA 5 - Goals Minute
with tabs[4]:
    home_team_data = goal_minute_home_df[goal_minute_home_df['Home'] == equipe_home]
    away_team_data = goal_minute_away_df[goal_minute_away_df['Away'] == equipe_away]

    if not home_team_data.empty:
        st.success(f"🏠 **{equipe_home}** marca seu primeiro gol em média aos **{home_team_data['AVG_min_scored'].values[0]:.1f} min**.")
    else:
        st.warning("Nenhum dado encontrado para o time da casa.")

    if not away_team_data.empty:
        st.success(f"🛫 **{equipe_away}** marca seu primeiro gol em média aos **{away_team_data['AVG_min_scored'].values[0]:.1f} min**.")
    else:
        st.warning("Nenhum dado encontrado para o time visitante.")

# ABA 6 - Goals HT/FT
with tabs[5]:
    st.markdown("### Gols no 1º Tempo e Placar Final")
    st.dataframe(goals_half_df, use_container_width=True)

# ABA 7 - CV HT
with tabs[6]:
    st.markdown("### Goals HT - CV")
    st.dataframe(cv_home_df, use_container_width=True)

# ABA 8 - Resumo
with tabs[8]:
    st.markdown("### Resumo")
    st.write(f"**Equipe da Casa:** {equipe_home}")
    st.write(f"**Equipe Visitante:** {equipe_away}")

# ABA 9 - Goals Per Time
with tabs[9]:
    st.markdown("### Goals Per Time")
    st.dataframe(goals_per_time_home_df, use_container_width=True)
    st.dataframe(goals_per_time_away_df, use_container_width=True)
            
# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

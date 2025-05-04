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

# ABA 2 - First Goal
with tabs[2]:
    def show_team_stats(team_name, df, col_name, local):
        stats = df[df[col_name] == team_name]
        if not stats.empty:
            st.markdown(f"### {team_name} ({local})")
            cols = ['Matches', 'First_Gol', 'Goals']
            st.dataframe(stats[cols] if all(c in stats.columns for c in cols) else stats, use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {team_name} ({local})")

    show_team_stats(equipe_home, home_fg_df, 'Team_Home', 'Casa')
    show_team_stats(equipe_away, away_fg_df, 'Team_Away', 'Fora')

# ABA 3 - Goals Minute
with tabs[3]:
    home_team_data = goal_minute_home_df[goal_minute_home_df['Team_Home'] == equipe_home]
    away_team_data = goal_minute_away_df[goal_minute_away_df['Team_Away'] == equipe_away]

    if not home_team_data.empty:
        st.success(f"🏠 **{equipe_home}** marca seu primeiro gol em média aos **{home_team_data['AVG_min_scored'].values[0]:.1f} min**.")
    else:
        st.warning("Nenhum dado encontrado para o time da casa.")

    if not away_team_data.empty:
        st.success(f"🛫 **{equipe_away}** marca seu primeiro gol em média aos **{away_team_data['AVG_min_scored'].values[0]:.1f} min**.")
    else:
        st.warning("Nenhum dado encontrado para o time visitante.")
# ABA 4 - Goals HT/FT (primeiro e segundo tempo)
with tabs[4]:
    home_goals_ht = goals_half_df[goals_half_df['Team'] == equipe_home]
    away_goals_ht = goals_half_df[goals_half_df['Team'] == equipe_away]

    if not home_goals_ht.empty:
        st.subheader(f"🧑‍⚖️ Performance do {equipe_home} no primeiro e segundo tempo")
        st.dataframe(home_goals_ht[['Team', 'Goals_HT', 'Goals_FT']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para o time da casa: {equipe_home}")

    if not away_goals_ht.empty:
        st.subheader(f"🧑‍⚖️ Performance do {equipe_away} no primeiro e segundo tempo")
        st.dataframe(away_goals_ht[['Team', 'Goals_HT', 'Goals_FT']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para o time visitante: {equipe_away}")

# ABA 5 - CV HT
with tabs[5]:
    cv_home_stats = cv_home_df[cv_home_df['Team_Home'] == equipe_home]
    cv_away_stats = cv_away_df[cv_away_df['Team_Away'] == equipe_away]

    if not cv_home_stats.empty:
        st.subheader(f"📉 Estatísticas de CV HT para {equipe_home}")
        st.dataframe(cv_home_stats[['Team_Home', 'CV_HT_Home', 'CV_HT_Away']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística de CV HT encontrada para o time da casa: {equipe_home}")

    if not cv_away_stats.empty:
        st.subheader(f"📉 Estatísticas de CV HT para {equipe_away}")
        st.dataframe(cv_away_stats[['Team_Away', 'CV_HT_Home', 'CV_HT_Away']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística de CV HT encontrada para o time visitante: {equipe_away}")

# ABA 6 - Goals Per Time
with tabs[6]:
    home_goals_per_time = goals_per_time_home_df[goals_per_time_home_df['Team_Home'] == equipe_home]
    away_goals_per_time = goals_per_time_away_df[goals_per_time_away_df['Team_Away'] == equipe_away]

    if not home_goals_per_time.empty:
        st.subheader(f"⚽ Performance de gols por tempo do {equipe_home}")
        st.dataframe(home_goals_per_time[['Team_Home', 'Goals_1H', 'Goals_2H']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística de gols por tempo encontrada para o time da casa: {equipe_home}")

    if not away_goals_per_time.empty:
        st.subheader(f"⚽ Performance de gols por tempo do {equipe_away}")
        st.dataframe(away_goals_per_time[['Team_Away', 'Goals_1H', 'Goals_2H']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística de gols por tempo encontrada para o time visitante: {equipe_away}")

# ----------------------------
# Análise de Odds e Poisson
# ----------------------------

def poisson_distribution(lmbda, max_goals=6):
    x = np.arange(0, max_goals)
    pmf = poisson.pmf(x, lmbda)
    return x, pmf

# ABA 7 - Análise de Odds com Poisson
with st.expander("📊 Análise de Odds com Poisson"):
    st.write(f"📝 Análise para a partida entre **{equipe_home}** e **{equipe_away}**.")

    # Supondo que as odds para o time da casa, empate e visitante são baseadas em uma distribuição de Poisson
    odd_home = float(st.number_input(f"Insira a odd para **{equipe_home}**", min_value=1.0))
    odd_draw = float(st.number_input(f"Insira a odd para Empate", min_value=1.0))
    odd_away = float(st.number_input(f"Insira a odd para **{equipe_away}**", min_value=1.0))

    # Parâmetros para a distribuição Poisson
    lambda_home = 1.5  # Exemplo de parâmetro de Poisson para o time da casa
    lambda_away = 1.2  # Exemplo de parâmetro de Poisson para o time visitante

    # Cálculo da distribuição Poisson
    x_home, pmf_home = poisson_distribution(lambda_home)
    x_away, pmf_away = poisson_distribution(lambda_away)

    # Plotando as distribuições
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x_home, y=pmf_home,
        name=f"{equipe_home} - Probabilidade Poisson",
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=x_away, y=pmf_away,
        name=f"{equipe_away} - Probabilidade Poisson",
        marker_color='red'
    ))

    fig.update_layout(
        title=f"Distribuição Poisson de Gols: {equipe_home} vs {equipe_away}",
        xaxis_title="Número de Gols",
        yaxis_title="Probabilidade",
        barmode="stack"
    )

    st.plotly_chart(fig)

    # Análise de Valor Esperado (EV)
    st.write(f"🔮 **Valor Esperado (EV)** para cada resultado:")
    ev_home = (odd_home - 1) * pmf_home[1]  # Probabilidade de 1 gol
    ev_draw = (odd_draw - 1) * pmf_home[0]  # Probabilidade de empate
    ev_away = (odd_away - 1) * pmf_away[2]  # Probabilidade de 2 gols

    st.write(f"💰 EV para **{equipe_home}** vencer: {ev_home:.2f}")
    st.write(f"💰 EV para **Empate**: {ev_draw:.2f}")
    st.write(f"💰 EV para **{equipe_away}** vencer: {ev_away:.2f}")

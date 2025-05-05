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

#ABA 0 - Analitico
with tabs[0]:
    # Coleta de dados
    home_data = ppg_ht_home_df[ppg_ht_home_df['Team_Home'] == equipe_home]
    away_data = ppg_ht_away_df[ppg_ht_away_df['Team_Away'] == equipe_away]
    cv_home_data = cv_home_df[cv_home_df['Team_Home'] == equipe_home]
    cv_away_data = cv_away_df[cv_away_df['Team_Away'] == equipe_away]
    fg_home = home_fg_df[home_fg_df['Team_Home'] == equipe_home]
    fg_away = away_fg_df[away_fg_df['Team_Away'] == equipe_away]
    gm_home = goal_minute_home_df[goal_minute_home_df['Team_Home'] == equipe_home]
    gm_away = goal_minute_away_df[goal_minute_away_df['Team_Away'] == equipe_away]

    col_home, col_away = st.columns(2)

    with col_home:
        st.markdown(f"### 🏠 {equipe_home}")
        
        # Exibe as métricas para o time da casa
        st.metric("📅 Jogos (GP)", int(home_data['GP'].values[0]) if not home_data.empty else 0)
        st.metric("📈 PIH", round(home_data['PIH'].values[0], 2) if not home_data.empty else 0)
        st.metric("🏠 PPG HT", round(home_data['PPG_HT_Home'].values[0], 2) if not home_data.empty else 0)
        st.metric("📊 AVG GF", round(home_data['GF_AVG_Home'].values[0], 2) if not home_data.empty else 0)
        st.metric("📈 GD", round(home_data['GD_Home'].values[0], 2) if not home_data.empty else 0)
        st.metric("🏆 Rank", int(home_data['Rank_Home'].values[0]) if not home_data.empty else "—")

        # Verifica se a coluna 'Perc.' existe antes de tentar acessar
        if not fg_home.empty and 'Perc.' in fg_home.columns:
            try:
                fg_val_home = fg_home['Perc.'].values[0]  # Extraindo o valor de Perc.
                st.metric("⚽ 1º Gol", f"{fg_val_home}")
            except Exception as e:
                st.metric("⚽ 1º Gol", "Erro")
                st.write(f"Erro ao processar 1º gol: {e}")
        else:
            st.metric("⚽ 1º Gol", "—")

        # Exibe o minuto médio para o time da casa
        st.metric("⏱️ Min. Médio Gol", round(gm_home['AVG_min_scored'].values[0], 1) if not gm_home.empty else "—")

    with col_away:
        st.markdown(f"### 🛫 {equipe_away}")
        
        # Exibe as métricas para o time visitante
        st.metric("📅 Jogos (GP)", int(away_data['GP'].values[0]) if not away_data.empty else 0)
        st.metric("📉 PIA", round(away_data['PIA'].values[0], 2) if not away_data.empty else 0)
        st.metric("🛫 PPG HT", round(away_data['PPG_HT_Away'].values[0], 2) if not away_data.empty else 0)
        st.metric("📊 AVG GF", round(away_data['GF_AVG_Away'].values[0], 2) if not away_data.empty else 0)
        st.metric("📉 GD", round(away_data['GD_Away'].values[0], 2) if not away_data.empty else 0)
        st.metric("🏆 Rank", int(away_data['Rank_Away'].values[0]) if not away_data.empty else "—")

        # Verifica se a coluna 'Perc.' existe antes de tentar acessar
        if not fg_away.empty and 'Perc.' in fg_away.columns:
            try:
                fg_val_away = fg_away['Perc.'].values[0]  # Extraindo o valor de Perc.
                st.metric("⚽ 1º Gol", f"{fg_val_away}")
            except Exception as e:
                st.metric("⚽ 1º Gol", "Erro")
                st.write(f"Erro ao processar 1º gol: {e}")
        else:
            st.metric("⚽ 1º Gol", "—")

        # Exibe o minuto médio para o time visitante
        st.metric("⏱️ Min. Médio Gol", round(gm_away['AVG_min_scored'].values[0], 1) if not gm_away.empty else "—")


# ABA 1 - H2H (índice 1)
with tabs[1]:
    home_stats = ppg_ht_home_df[ppg_ht_home_df['Team_Home'] == equipe_home]
    away_stats = ppg_ht_away_df[ppg_ht_away_df['Team_Away'] == equipe_away]

    if not home_stats.empty:
        
        st.dataframe(home_stats[['League','Team_Home','GP','PIH','PPG_HT_Home','GF_AVG_Home', 'GD_Home', 'Odd_Justa_MO','Rank_Home']], use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para o time da casa: {equipe_home}")

    if not away_stats.empty:
        
        st.dataframe(away_stats[['League','Team_Away','GP','PIA','PPG_HT_Away','GF_AVG_Away','GD_Away','Odd_Justa_MO','Rank_Away']], use_container_width=True)
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

# ABA 4 - Goals Half
with tabs[4]:
    filtered = goals_half_df[goals_half_df['Team'].isin([equipe_home, equipe_away])]
    if not filtered.empty:
        st.dataframe(filtered[['League_Name', 'Team', 'Scored', '1st half', '2nd half']], use_container_width=True)
    else:
        st.warning("Nenhuma estatística de Goals Half encontrada.")

# ABA 5 - Goals HT

with tabs[5]:
    def gerar_barra_frequencia(frequencia_dict):
        cores = {
            "0": "#d9534f",  # vermelho
            "1": "#20de6e",  # verde
            "2": "#16ed48",  # azul
            "3": "#24da1e",  # laranja
            "4": "#56b72d"   # roxo
        }

        html = '<div style="display:flex; flex-wrap: wrap;">'
        for gols, freq in frequencia_dict.items():
            blocos = int(freq)  # 1 bloco por %
            for _ in range(blocos):
                html += f'<div style="width: 6px; height: 20px; background-color: {cores[gols]}; margin: 1px;"></div>'
        html += '</div>'
        return html

    # Time da casa
    home_ht = cv_home_df[cv_home_df['Team_Home'] == equipe_home]
    if not home_ht.empty:
        df_home = home_ht.rename(columns={
            "Avg.": "Avg",
            "4+": "4",
            "3": "3",
            "2": "2",
            "1": "1",
            "0": "0"
        })[["Team_Home", "Avg", "0", "1", "2", "3", "4", "Total_Jogos", "% Com Gols", "% Sem Gols", "Classificação Ofensiva"]]

        st.dataframe(df_home, use_container_width=True)

        freq_dict_home = {g: df_home[g].iloc[0] for g in ["0", "1", "2", "3", "4"]}
        st.markdown(gerar_barra_frequencia(freq_dict_home), unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)

        try:
            media = float(df_home["Avg"].iloc[0])
            com_gols = int(df_home["% Com Gols"].iloc[0])  # Exibindo sem casas decimais
            sem_gols = int(df_home["% Sem Gols"].iloc[0])  # Exibindo sem casas decimais

            col_a.metric("Média 1T", f"{media:.2f}")
            col_b.metric("Com Gols", f"{com_gols}%")
            col_c.metric("Sem Gols", f"{sem_gols}%")
        except Exception as e:
            st.error(f"Erro ao calcular métricas: {e}")

    else:
        st.warning("Dados não encontrados para o time da casa.")

    # Time visitante
    away_ht = cv_away_df[cv_away_df['Team_Away'] == equipe_away]
    if not away_ht.empty:
        df_away = away_ht.rename(columns={
            "Avg..1": "Avg",
            "0.1": "0", "1.1": "1", "2.1": "2", "3.1": "3", "4+.1": "4"
        })[["Team_Away", "Avg", "0", "1", "2", "3", "4", "Total_Jogos", "% Com Gols", "% Sem Gols", "Classificação Ofensiva"]]

        st.dataframe(df_away, use_container_width=True)

        freq_dict_away = {g: df_away[g].iloc[0] for g in ["0", "1", "2", "3", "4"]}
        st.markdown(gerar_barra_frequencia(freq_dict_away), unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)

        try:
            media = float(df_away["Avg"].iloc[0])
            com_gols = int(df_away["% Com Gols"].iloc[0])  # Exibindo sem casas decimais
            sem_gols = int(df_away["% Sem Gols"].iloc[0])  # Exibindo sem casas decimais

            col_a.metric("Média 1T", f"{media:.2f}")
            col_b.metric("Com Gols", f"{com_gols}%")
            col_c.metric("Sem Gols", f"{sem_gols}%")
        except Exception as e:
            st.error(f"Erro ao calcular métricas: {e}")

    else:
        st.warning("Dados não encontrados para o time visitante.")

# ABA 6 - Goals Per Time

with tabs[6]:
    goals_per_time_home_df, goals_per_time_away_df = goals_per_time_data()
    
    # Limpeza dos nomes de times
    goals_per_time_home_df['Team_Home'] = goals_per_time_home_df['Team_Home'].astype(str).str.strip()
    goals_per_time_away_df['Team_Away'] = goals_per_time_away_df['Team_Away'].astype(str).str.strip()
    
    # Filtrando os dados para os times selecionados
    filtered_home = goals_per_time_home_df[goals_per_time_home_df['Team_Home'] == equipe_home]
    filtered_away = goals_per_time_away_df[goals_per_time_away_df['Team_Away'] == equipe_away]
    
    # Verificando se ambos os dataframes têm dados
    if not filtered_home.empty and not filtered_away.empty:
        st.subheader("Gols por faixa de tempo (Home / Away)")
        st.dataframe(filtered_home[['League', 'Team_Home', 'GP', '0-15', '16-30', '31-45', '46-60', '61-75', '76-90']])
        st.dataframe(filtered_away[['League', 'Team_Away', 'GP', '0-15', '16-30', '31-45', '46-60', '61-75', '76-90']],
                         use_container_width=True)
    else:
        st.warning("Nenhuma estatística encontrada para os times selecionados.")


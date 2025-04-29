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
st.set_page_config(page_title="Football Stats", layout="wide")

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


# Filtrando os nomes das equipes para garantir que são apenas letras e espaços
all_teams = sorted(set(
    home_df['Team_Home'].dropna().astype(str)[home_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    away_df['Team_Away'].dropna().astype(str)[away_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    away_fav_df['Team_Away_Fav'].dropna().astype(str)[away_fav_df['Team_Away_Fav'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    overall_df['Team_Home_Overall'].dropna().astype(str)[overall_df['Team_Home_Overall'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    home_fg_df['Team_Home'].dropna().astype(str)[home_fg_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    away_fg_df['Team_Away'].dropna().astype(str)[away_fg_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goal_minute_home_df['Team_Home'].dropna().astype(str)[goal_minute_home_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goal_minute_away_df['Team_Away'].dropna().astype(str)[goal_minute_away_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goals_half_df['Team'].dropna().astype(str)[goals_half_df['Team'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goals_per_time_home_df['Team_Home'].dropna().astype(str)[goals_per_time_home_df['Team_Home'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist() +
    goals_per_time_away_df['Team_Away'].dropna().astype(str)[goals_per_time_away_df['Team_Away'].str.contains(r'^[A-Za-z\s]+$', na=False)].tolist()
))

# Seleção dos times para a interface
equipe_home = st.sidebar.selectbox("🏠 Time da Casa:", all_teams, index=all_teams.index('Bayern Munich') if 'Bayern Munich' in all_teams else 0)
equipe_away = st.sidebar.selectbox("🛫 Time Visitante:", all_teams, index=all_teams.index('Dortmund') if 'Dortmund' in all_teams else 0)


# ----------------------------
# APLICAR FILTROS
# ----------------------------
home_filtered = home_df[home_df['Team_Home'] == equipe_home][home_columns]
away_filtered = away_df[away_df['Team_Away'] == equipe_away][away_columns]
away_fav_filtered = away_fav_df[away_fav_df['Team_Away_Fav'] == equipe_away][away_columns]
overall_filtered = overall_df[overall_df['Team_Home_Overall'] == equipe_home][overall_columns]

# ----------------------------
# INTERFACE STREAMLIT
# ----------------------------
tabs = st.tabs([
    "🧾 Resumo", "🏠 Home", "📊 Overall", "🛫 Away",
    "⚽ First Goal", "⏱️ Goals_Minute", "⚡ Goals HT/FT", "📌 CV HT", "📊 Goals Per Time", "Sintese"
])

# ABA 1 - Home Favorito
with tabs[1]:
    st.markdown("### Home")
    st.dataframe(home_filtered, use_container_width=True)
    st.markdown("### Away")
    st.dataframe(away_filtered, use_container_width=True)

# ABA 2 - Home Geral
with tabs[2]:
    st.markdown("### Home - Geral")
    st.dataframe(overall_filtered, use_container_width=True)
    st.markdown("### Away")
    st.dataframe(away_filtered, use_container_width=True)

# ABA 3 - Away Favorito
with tabs[3]:
    st.markdown("### Away - Favorito")
    st.dataframe(away_fav_filtered, use_container_width=True)
    st.markdown("### Home")
    st.dataframe(home_filtered, use_container_width=True)

# ABA 4 - First Goal
with tabs[4]:
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

# ABA 5 - Goals Minute
with tabs[5]:
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

# ABA 6 - Goals Half
with tabs[6]:
    filtered = goals_half_df[goals_half_df['Team'].isin([equipe_home, equipe_away])]
    if not filtered.empty:
        st.dataframe(filtered[['League_Name', 'Team', 'Scored', '1st half', '2nd half']], use_container_width=True)
    else:
        st.warning("Nenhuma estatística de Goals Half encontrada.")

# ABA 7 - Goals HT

with tabs[7]:
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


# ABA 8 - Resumo     
# ABA 8 - Resumo     
with tabs[0]:
    # Definindo o emoji antes de usá-lo
    if not home_filtered.empty:
        row = home_filtered.iloc[0]
        
        # Atribuindo o emoji baseado no valor de PPG_Home
        ppg_home = row.get("PPG_Home", 0)
        ppg_home_emoji = "🟩" if ppg_home >= 1.8 else "🟥"

        st.markdown(f"{ppg_home_emoji} **{equipe_home} (Casa)**")

        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        col_b.metric("Média Gols", row.get("GF_AVG_Home", "N/A"))
        col_a.metric("PIH", row.get("PIH", "N/A"))
        col_c.metric("PPG Casa", row.get("PPG_Home", "N/A"))
        col_d.metric("Odd Justa", row.get("Odd_Justa_MO", "N/A"))
        col_e.metric("Rank Casa", row.get("Rank_Home", "N/A"))

        # Colocando o emoji antes do nome de PPG Casa
        #st.markdown(f"{ppg_home_emoji} **PPG Casa**: {ppg_home}")
    else:
        st.info("Informações do time da casa como favorito não disponíveis.")

    # Definindo o emoji para o time visitante
    if not away_filtered.empty:
        row = away_filtered.iloc[0]
        
        # Atribuindo o emoji baseado no valor de PPG_Away
        ppg_away = row.get("PPG_Away", 0)
        ppg_away_emoji = "🟩" if ppg_away <= 1.00 else "🟥"

        st.markdown(f"{ppg_away_emoji} **{equipe_away} (Visitante)**")

        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        col_b.metric("Média Gols", row.get("GF_AVG_Away", "N/A"))
        col_a.metric("PIA", row.get("PIA", "N/A"))
        col_c.metric("PPG Fora", row.get("PPG_Away", "N/A"))
        col_d.metric("Odd Justa", row.get("Odd_Justa_MO", "N/A"))
        col_e.metric("Rank Fora", row.get("Rank_Away", "N/A"))

        # Colocando o emoji antes do nome de PPG Fora
        #st.markdown(f"{ppg_away_emoji} **PPG Fora**: {ppg_away}")
    else:
        st.info("Informações do time visitante não disponíveis.")



    st.markdown("### ⚽ Marca Primeiro")

    col1, col2 = st.columns(2)
    
    with col1:
        # Colocando o emoji antes do nome da equipe da casa
        stats_home_fg = home_fg_df[home_fg_df['Team_Home'] == equipe_home]
        if not stats_home_fg.empty:
            row = stats_home_fg.iloc[0]
            partidas = row['Matches']
            primeiro_gol = row['First_Gol']  # Este valor tem o símbolo "%" (ex: "62%")
            total_gols = row['Goals']
    
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Partidas", partidas)
            col_b.metric("1º Gol", f"{primeiro_gol}")  # Exibindo como porcentagem
            col_c.metric("Total de Gols", total_gols)
    
            # Remover o símbolo "%" e converter para número
            try:
                primeiro_gol_num = float(primeiro_gol.replace('%', ''))  # Removendo "%" antes de converter
                # Se o time da casa marcar o 1º gol em >= 60% das vezes
                if primeiro_gol_num >= 60:
                    gol_emoji = "🟩"  # Verde
                else:
                    gol_emoji = "🟥"  # Vermelho
            except ValueError:
                gol_emoji = "🟨"  # Caso o valor não seja numérico, emoji de alerta
    
            # Exibindo o nome da equipe com o emoji antes
            st.markdown(f"{gol_emoji} **{equipe_home} (Casa)**")
        else:
            st.info("Sem dados.")
    
    with col2:
        # Colocando o emoji antes do nome da equipe visitante
        stats_away_fg = away_fg_df[away_fg_df['Team_Away'] == equipe_away]
        if not stats_away_fg.empty:
            row = stats_away_fg.iloc[0]
            partidas = row['Matches']
            primeiro_gol = row['First_Gol']  # Este valor tem o símbolo "%" (ex: "50%")
            total_gols = row['Goals']
    
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Partidas", partidas)
            col_b.metric("1º Gol", f"{primeiro_gol}")  # Exibindo como porcentagem
            col_c.metric("Total de Gols", total_gols)
    
            # Remover o símbolo "%" e converter para número
            try:
                primeiro_gol_num = float(primeiro_gol.replace('%', ''))  # Removendo "%" antes de converter
                # Se o time visitante marcar o 1º gol em <= 45% das vezes
                if primeiro_gol_num <= 45:
                    gol_emoji = "🟩"  # Verde
                else:
                    gol_emoji = "🟥"  # Vermelho
            except ValueError:
                gol_emoji = "🟨"  # Caso o valor não seja numérico, emoji de alerta
    
            # Exibindo o nome da equipe com o emoji antes
            st.markdown(f"{gol_emoji} **{equipe_away} (Fora)**")
        else:
            st.info("Sem dados.")
    

    st.markdown("### ⏱️ Frequência Gols 1º e 2º Tempo")

    goals_half_filtered = goals_half_df[goals_half_df['Team'].isin([equipe_home, equipe_away])]
    if not goals_half_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            home_1st_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_home]['1st half'].values[0] if equipe_home in goals_half_filtered['Team'].values else "Sem dados"
            if home_1st_half != "Sem dados":
                # Remove o '%' e converte para float
                home_1st_half_num = float(home_1st_half.strip('%'))  # Já está em % na base de dados
                gol_emoji_home = "🟩" if home_1st_half_num >= 50 else "🟥"  # Se >= 50% é verde, senão vermelho
                st.metric(f"{gol_emoji_home} {equipe_home} - 1º Tempo", home_1st_half)
            else:
                st.metric(f"{equipe_home} - 1º Tempo", home_1st_half)
    
        with col2:
            home_2nd_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_home]['2nd half'].values[0] if equipe_home in goals_half_filtered['Team'].values else "Sem dados"
            st.metric(f"{equipe_home} - 2º Tempo", home_2nd_half)
    
        with col3:
            away_1st_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_away]['1st half'].values[0] if equipe_away in goals_half_filtered['Team'].values else "Sem dados"
            if away_1st_half != "Sem dados":
                # Remove o '%' e converte para float
                away_1st_half_num = float(away_1st_half.strip('%'))  # Já está em % na base de dados
                gol_emoji_away = "🟥" if away_1st_half_num >= 55 else "🟩"  # Se <= 50% é vermelho, senão verde
                st.metric(f"{gol_emoji_away} {equipe_away} - 1º Tempo", away_1st_half)
            else:
                st.metric(f"{equipe_away} - 1º Tempo", away_1st_half)
    
        with col4:
            away_2nd_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_away]['2nd half'].values[0] if equipe_away in goals_half_filtered['Team'].values else "Sem dados"
            st.metric(f"{equipe_away} - 2º Tempo", away_2nd_half)
    
    else:
        st.info("Sem dados.")

    st.markdown("### 📌 Frequência Gols HT")

    def gerar_barra_frequencia(frequencia_dict):
        cores = {
            "0": "#d9534f",
            "1": "#20de6e",
            "2": "#16ed48",
            "3": "#24da1e",
            "4": "#56b72d"
        }
    
        html = '<div style="display:flex; flex-wrap: wrap;">'
        for gols, freq in frequencia_dict.items():
            try:
                blocos = int(float(str(freq).replace(',', '.')))
            except:
                blocos = 0
            for _ in range(blocos):
                html += f'<div style="width: 6px; height: 20px; background-color: {cores[gols]}; margin: 1px;"></div>'
        html += '</div>'
        return html
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_ht = cv_home_df[cv_home_df['Team_Home'] == equipe_home]
        if not home_ht.empty:
            df_home = home_ht.rename(columns={
                "Avg.": "Avg", "4+": "4", "3": "3", "2": "2", "1": "1", "0": "0"
            })[["Team_Home", "Avg", "0", "1", "2", "3", "4", "Total_Jogos", "% Com Gols", "% Sem Gols", "Classificação Ofensiva"]]
    
            row = df_home.iloc[0]
            media = float(str(row['Avg']).replace(',', '.')) if row['Avg'] else 0.0
            com_gols = f"{int(round(float(str(row.get('% Com Gols', '0')).replace('%', '').replace(',', '.'))))}%"
            sem_gols = f"{int(round(float(str(row.get('% Sem Gols', '0')).replace('%', '').replace(',', '.'))))}%"
    
            # Determinando o emoji para Média de Gols
            if media >= 0.60:
                media_emoji = "🟩"
            else:
                media_emoji = "🟥"
    
            # Determinando o emoji para Com Gols
            com_gols_percent = float(com_gols.replace('%', ''))
            if com_gols_percent >= 60:
                com_gols_emoji = "🟩"
            else:
                com_gols_emoji = "🟥"
    
            col_a, col_b, col_c = st.columns(3)
            col_a.metric(f"{media_emoji} Média Gols", media)
            col_b.metric(f"{com_gols_emoji} Com Gols", com_gols)
            col_c.metric("Sem Gols", sem_gols)
    
            freq_dict_home = {g: row[g] for g in ["0", "1", "2", "3", "4"]}
            st.markdown(gerar_barra_frequencia(freq_dict_home), unsafe_allow_html=True)
        else:
            st.warning("Dados não encontrados para o time da casa.")
    
    with col2:
        away_ht = cv_away_df[cv_away_df['Team_Away'] == equipe_away]
        if not away_ht.empty:
            df_away = away_ht.rename(columns={
                "Avg..1": "Avg", "0.1": "0", "1.1": "1", "2.1": "2", "3.1": "3", "4+.1": "4"
            })[["Team_Away", "Avg", "0", "1", "2", "3", "4", "Total_Jogos", "% Com Gols", "% Sem Gols", "Classificação Ofensiva"]]
    
            row = df_away.iloc[0]
            media = float(str(row['Avg']).replace(',', '.')) if row['Avg'] else 0.0
            com_gols = f"{int(round(float(str(row.get('% Com Gols', '0')).replace('%', '').replace(',', '.'))))}%"
            sem_gols = f"{int(round(float(str(row.get('% Sem Gols', '0')).replace('%', '').replace(',', '.'))))}%"
    
            # Determinando o emoji para Média de Gols
            if media >= 0.70:
                media_emoji_away = "🟥"
            else:
                media_emoji_away = "🟩"
    
            # Determinando o emoji para Com Gols
            com_gols_percent_away = float(com_gols.replace('%', ''))
            if com_gols_percent_away >= 50:
                com_gols_emoji_away = "🟥"
            else:
                com_gols_emoji_away = "🟩"
    
            col_a, col_b, col_c = st.columns(3)
            col_a.metric(f"{media_emoji_away} Média Gols", media)
            col_b.metric(f"{com_gols_emoji_away} Com Gols", com_gols)
            col_c.metric("Sem Gols", sem_gols)
    
            freq_dict_away = {g: row[g] for g in ["0", "1", "2", "3", "4"]}
            st.markdown(gerar_barra_frequencia(freq_dict_away), unsafe_allow_html=True)
        else:
            st.warning("Dados não encontrados para o time visitante.")


    # Gols 15min
    st.markdown("### ⏱️ Gols 15min")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtrando os dados do time da casa
        filtered_home = goals_per_time_home_df[goals_per_time_home_df['Team_Home'] == equipe_home]
        if not filtered_home.empty:
            # Remover a parte de texto (" min.") da coluna AVG_Scored e converter para numérico
            avg_scored_home = filtered_home['AVG_Scored_Home'].str.extract('(\d+)').astype(float).values[0]
            
            # Verificando se o valor é válido
            if pd.isna(avg_scored_home):
                st.warning("O valor de AVG_Scored para o time da casa é inválido.")
            else:
                # Definindo o ícone com base no valor de AVG_Scored
                home_icon = "🟩" if avg_scored_home <= 45 else "🟥"
                st.markdown(f"{home_icon} **{equipe_home} (Casa)**")
                st.dataframe(filtered_home[['League', 'GP', 'AVG_Scored_Home', '0-15', '16-30', '31-45']], use_container_width=True)
        else:
            st.info("Sem dados de gols por faixa de tempo para o time da casa.")
    
    with col2:
        # Filtrando os dados do time visitante
        filtered_away = goals_per_time_away_df[goals_per_time_away_df['Team_Away'] == equipe_away]
        if not filtered_away.empty:
            # Remover a parte de texto (" min.") da coluna AVG_Scored e converter para numérico
            avg_scored_away = filtered_away['AVG_Scored_Away'].str.extract('(\d+)').astype(float).values[0]
            
            # Verificando se o valor é válido
            if pd.isna(avg_scored_away):
                st.warning("O valor de AVG_Scored para o time visitante é inválido.")
            else:
                # Definindo o ícone com base no valor de AVG_Scored
                away_icon = "🟥" if avg_scored_away <= 45 else "🟩"
                st.markdown(f"{away_icon} **{equipe_away} (Fora)**")
                st.dataframe(filtered_away[['League', 'GP', 'AVG_Scored_Away', '0-15', '16-30', '31-45']], use_container_width=True)
        else:
            st.info("Sem dados de gols por faixa de tempo para o time visitante.")


# ABA 9 - Goals Per Time
    
    with tabs[8]:
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


# ABA 10 - Síntese Detalhada
# ABA 10 - Síntese Detalhada
    with tabs[9]:
    
        # Verificar se temos dados suficientes
        if not home_filtered.empty and not away_filtered.empty:
            home_row = home_filtered.iloc[0]
            away_row = away_filtered.iloc[0]
    
            # Coletar dados adicionais
            home_fg_data = home_fg_df[home_fg_df['Team_Home'] == equipe_home].iloc[0] if not home_fg_df.empty and equipe_home in home_fg_df['Team_Home'].values else None
            away_fg_data = away_fg_df[away_fg_df['Team_Away'] == equipe_away].iloc[0] if not away_fg_df.empty and equipe_away in away_fg_df['Team_Away'].values else None
    
            home_goals_ht = goals_half_df[goals_half_df['Team'] == equipe_home].iloc[0] if not goals_half_df.empty and equipe_home in goals_half_df['Team'].values else None
            away_goals_ht = goals_half_df[goals_half_df['Team'] == equipe_away].iloc[0] if not goals_half_df.empty and equipe_away in goals_half_df['Team'].values else None
    
            # Dados de ranking
            try:
                rank_home = int(home_row.get('Rank_Home', 999))
                rank_away = int(away_row.get('Rank_Away', 999))
                rank_diff = rank_away - rank_home
            except:
                rank_home = 999
                rank_away = 999
                rank_diff = 0
    
            # Variáveis principais
            ppg_home = home_row.get("PPG_Home", 0)
            ppg_away = away_row.get("PPG_Away", 0)
            gf_avg_home = home_row.get("GF_AVG_Home", 0)
            gf_avg_away = away_row.get("GF_AVG_Away", 0)
            odd_justa_home = home_row.get('Odd_Justa_MO', 'N/A')
            odd_justa_away = away_row.get('Odd_Justa_MO', 'N/A')
    
            # Análise qualitativa
            if ppg_home >= 1.8:
                desempenho_home = "excelente"
                vantagem_home = "alta probabilidade de vitória"
            elif ppg_home >= 1.5:
                desempenho_home = "bom"
                vantagem_home = "boas chances de vitória"
            elif ppg_home >= 1.2:
                desempenho_home = "regular"
                vantagem_home = "desempenho equilibrado"
            else:
                desempenho_home = "fraco"
                vantagem_home = "dificuldade em vencer"
    
            if ppg_away >= 1.5:
                desempenho_away = "forte"
                desempenho_fora = "bom desempenho fora de casa"
            elif ppg_away >= 1.0:
                desempenho_away = "regular"
                desempenho_fora = "resultados mistos como visitante"
            else:
                desempenho_away = "fraco"
                desempenho_fora = "dificuldade em jogos fora"
    
            # Texto de análise
            analise_home = f"""
            ### 🏠 {equipe_home} (Casa)
            O time da casa **{equipe_home}** apresenta um **{desempenho_home} desempenho** como mandante, com uma frequência de **{gf_avg_home:.2f} gols** por partida e uma média de pontos por jogo (PPG) de **{ppg_home:.2f}**. 
            """
    
            if home_fg_data is not None:
                analise_home += f"O time marca o primeiro gol em **{home_fg_data['First_Gol']}** das partidas e "
    
            if home_goals_ht is not None:
                analise_home += f"tem uma frequência de gols no primeiro tempo de **{home_goals_ht['1st half']}**. "
    
            analise_home += f"Seu ranking como mandante é **{rank_home}**, indicando {vantagem_home} contra adversários de nível similar."
    
            analise_away = f"""
            ### ✈️ {equipe_away} (Visitante)
            O time visitante **{equipe_away}** tem mostrado um desempenho **{desempenho_away}** como visitante, com média de **{gf_avg_away:.2f} gols** por partida e PPG de **{ppg_away:.2f}**. 
            """
    
            if away_fg_data is not None:
                analise_away += f"O time marca o primeiro gol em **{away_fg_data['First_Gol']}** das partidas e "
    
            if away_goals_ht is not None:
                analise_away += f"apresenta uma frequência de gols no primeiro tempo de **{away_goals_ht['1st half']}**. "
    
            analise_away += f"Seu ranking como visitante é **{rank_away}**, com {desempenho_fora}."
    
            st.markdown(analise_home)
            st.markdown(analise_away)
    
            # Sugestões de apostas           
            col1, col2 = st.columns(2)
    
            with col1:
                st.markdown("### 1X2 (Resultado Final)")
                rankings_validos = rank_home != 999 and rank_away != 999
    
                if (ppg_home >= 1.8 and (ppg_home - ppg_away) >= 1 and rankings_validos and rank_diff >= 6):
                    st.success("**✅ Aposta sugerida:** Vitória do mandante (1)")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Excelente desempenho como mandante.
                    • Superioridade clara sobre o visitante.
                    • Time melhor posicionado no ranking (posição {rank_home} vs {rank_away}).  
                    
                    """)
                elif (ppg_away >= 1.8 and (ppg_away - ppg_home) >= 1 and rankings_validos and rank_diff <= -6):
                    st.success("**✅ Aposta sugerida:** Vitória do visitante (2)")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Excelente desempenho como visitante.  
                    • Superioridade clara sobre o mandante.  
                    • Time melhor posicionado no ranking (posição {rank_away} vs {rank_home}).  
                    
                    """)
                elif abs(ppg_home - ppg_away) < 0.5:
                    st.warning("**⚖️ Aposta sugerida:** Empate (X)")
                    st.markdown("""
                    📊 **Justificativa:**  
                    • Equilíbrio entre as equipes 
                    • Nenhum time com vantagem significativa.  
                    """)
                else:
                    st.info("**🔍 Aposta não recomendada**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Nenhum critério forte atendido.  
                    • Diferença de ranking: {abs(rank_diff)} posições.  
                    • Diferença de PPG: {abs(ppg_home - ppg_away):.2f}.  
                    """)
    
                st.markdown(f"📌 **Odd Justa:** Casa {odd_justa_home} | Fora {odd_justa_away}")
    
            with col2:
                st.markdown("### Handicap Asiático (HA)")
                diff_ppg = ppg_home - ppg_away
    
                if (ppg_home >= 1.8 and diff_ppg >= 1 and rankings_validos and rank_diff >= 6):
                    st.success("**✅ HA -1.0 para o mandante**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Mandante com desempenho forte.  
                    • Vantagem significativa jogando em casa.  
                    • Superioridade no ranking (posição {rank_home} vs {rank_away}).  
                    
                    """)
                elif (ppg_home >= 1.8 and diff_ppg >= 0.5 and rankings_validos and rank_diff >= 4):
                    st.success("**✅ HA -0.75 para o mandante**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Mandante com bom desempenho.
                    • Vantagem moderada jogando em casa.  
                    • Vantagem no ranking (posição {rank_home} vs {rank_away}).  
                    
                    """)
                elif (ppg_away >= 1.8 and -diff_ppg >= 1 and rankings_validos and rank_diff <= -6):
                    st.success("**✅ HA +1.0 para o visitante**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Visitante com desempenho forte.
                    • Vantagem significativa jogando fora de casa.  
                    • Superioridade no ranking (posição {rank_away} vs {rank_home}).  
                    
                    """)
                elif abs(diff_ppg) < 0.5:
                    st.info("**🔍 HA 0.0 (Empate sem handicap)**")
                    st.markdown("""
                    📊 **Justificativa:**  
                    • Equilíbrio entre as equipes.  
                    • Diferença entre as equipes insignificante.  
                    """)
                else:
                    st.warning("**⚠️ HA não recomendado**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Nenhum critério forte atendido.  
                    • Diferença de PPG: {diff_ppg:.2f}.  
                    • Diferença de ranking: {rank_diff} posições.  
                    """)
    
                st.markdown(f"📊 **Diferença PPG:** {diff_ppg:.2f}")
                if rankings_validos:
                    st.markdown(f"📊 **Ranking:** (Casa {rank_home} vs Fora {rank_away})")
    
            # Over/Under Gols
            st.markdown("### Over/Under Gols")
            total_avg_goals = gf_avg_home + gf_avg_away
    
            if ((ppg_home >= 1.8 or ppg_away >= 1.8) and rankings_validos and abs(rank_diff) >= 6 and total_avg_goals >= 2.8):
                st.success(f"**✅ Over 2.5 Gols (Média: {total_avg_goals:.2f})**")
                st.markdown("""
                📊 **Justificativa:**  
                • Time(s) com alto desempenho ofensivo.
                • Diferença de ranking significativa.  
                • Frequência de gols esperada elevada (≥2.8).  
                """)
            elif total_avg_goals <= 2.0:
                st.warning(f"**⚠️ Under 2.5 Gols (Média: {total_avg_goals:.2f})**")
                st.markdown("""
                📊 **Justificativa:**  
                • Ambas as equipes com frequência de gols baixa.  
                • Potencial para jogo com poucos gols.  
                """)
            else:
                st.info(f"**🔍 Over/Under incerto (Média: {total_avg_goals:.2f})**")
                st.markdown("""
                📊 **Justificativa:**  
                • Frequência de gols intermediária.  
                • Sem tendências claras para gols.  
                """)
            # BTTS (Both Teams to Score)
            st.markdown("### BTTS (Ambos Marcam)")

            if gf_avg_home >= 1.2 and gf_avg_away >= 1.2 and total_avg_goals >= 2.5:
                st.success("**✅ Sugerido: Sim (Ambos Marcam)**")
                st.markdown(f"""
                📊 **Justificativa:**  
                • Ambos os times têm média de gols ≥ 1.2.  
                • Frequência total de gols elevada ({total_avg_goals:.2f}).  
                • Indicativo de jogo aberto e ofensivo.  
                """)
            elif gf_avg_home < 1.0 or gf_avg_away < 1.0:
                st.warning("**⚠️ Sugerido: Não (Apenas um ou nenhum marca)**")
                st.markdown(f"""
                📊 **Justificativa:**  
                • Um dos times apresenta baixa frequência de gols.  
                • Tendência de apenas um time marcar.  
                """)
            else:
                st.info("**🔍 Nenhuma tendência clara para BTTS**")
                st.markdown(f"""
                📊 **Justificativa:**  
                • Frequência de gols equilibradas, mas não elevadas.  
                • Jogo pode ter gols de apenas um dos lados.  
                """)

            st.markdown("### 📊 5 Placares Mais Prováveis")
            
            # Cálculo da expectativa de gols com base no PPG e na média total de gols
            if (ppg_home + ppg_away) > 0:
                exp_gols_home = (ppg_home / (ppg_home + ppg_away)) * total_avg_goals
            else:
                exp_gols_home = 0
            exp_gols_away = total_avg_goals - exp_gols_home
            
            # Gerar probabilidades de placares usando distribuição de Poisson
            max_gols = 5
            placares = []
            
            for gols_home in range(max_gols + 1):
                for gols_away in range(max_gols + 1):
                    # Usando scipy para clareza (pode usar sua fórmula se preferir)
                    prob_home = poisson.pmf(gols_home, exp_gols_home)
                    prob_away = poisson.pmf(gols_away, exp_gols_away)
                    prob_placar = prob_home * prob_away
                    placares.append(((gols_home, gols_away), prob_placar))
            
            # Ordenar pelos placares com maior probabilidade
            placares.sort(key=lambda x: x[1], reverse=True)
            
            # Exibir os 5 placares mais prováveis
            #st.markdown("**Top 5 placares estimados:**")
            for i, ((gh, ga), prob) in enumerate(placares[:5], start=1):
                st.write(f"{i}. {equipe_home} {gh} x {ga} {equipe_away} — Probabilidade: {prob:.2%}")


# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

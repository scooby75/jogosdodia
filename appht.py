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
    "⚠️ Analitico", "🧾 h2h", "⚽ First Goal", "⏱️ Goals_Minute", "⚡ Goals HT/FT", "📌 CV HT", "📊 Goals Per Time", "Descritiva"
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
        #st.metric("📅 Jogos (GP)", int(home_data['GP'].values[0]) if not home_data.empty else 0)
        st.metric("📈 PIH", round(home_data['PIH'].values[0], 2) if not home_data.empty else 0)
        st.metric("🏠 PPG HT", round(home_data['PPG_HT_Home'].values[0], 2) if not home_data.empty else 0)
        st.metric("📊 Média Gols", round(home_data['GF_AVG_Home'].values[0], 2) if not home_data.empty else 0)
        st.metric("📈 Saldo de Gols", round(home_data['GD_Home'].values[0], 2) if not home_data.empty else 0)
        st.metric("🏆 Rank", int(home_data['Rank_Home'].values[0]) if not home_data.empty else "—")

        # Verifica e extrai o primeiro gol se disponível
        if not fg_home.empty:
            row = fg_home.iloc[0]
            primeiro_gol = row['First_Gol']  # Valor como string (ex: "62%")
            partidas = row['Matches']  # Para mostrar quantas partidas o time jogou

            # Exibe o primeiro gol, removendo o símbolo de "%" caso necessário
            try:
                st.metric("⚽ 1º Gol", primeiro_gol)
            except Exception as e:
                st.metric("⚽ 1º Gol", "Erro")
                st.write(f"Erro ao processar 1º gol: {e}")
        else:
            st.metric("⚽ 1º Gol", "—")

        # Exibe o minuto médio para o time da casa
        st.metric("⏱️ Tempo Médio 1º Gol", round(gm_home['AVG_min_scored'].values[0], 1) if not gm_home.empty else "—")

    with col_away:
        st.markdown(f"### 🛫 {equipe_away}")
        
        # Exibe as métricas para o time visitante
        #st.metric("📅 Jogos (GP)", int(away_data['GP'].values[0]) if not away_data.empty else 0)
        st.metric("📉 PIA", round(away_data['PIA'].values[0], 2) if not away_data.empty else 0)
        st.metric("🛫 PPG HT", round(away_data['PPG_HT_Away'].values[0], 2) if not away_data.empty else 0)
        st.metric("📊 Média de Gols", round(away_data['GF_AVG_Away'].values[0], 2) if not away_data.empty else 0)
        st.metric("📉 Saldo de Gols", round(away_data['GD_Away'].values[0], 2) if not away_data.empty else 0)
        st.metric("🏆 Rank", int(away_data['Rank_Away'].values[0]) if not away_data.empty else "—")

        # Verifica e extrai o primeiro gol se disponível
        if not fg_away.empty:
            row = fg_away.iloc[0]
            primeiro_gol = row['First_Gol']  # Valor como string (ex: "62%")
            partidas = row['Matches']  # Para mostrar quantas partidas o time jogou

            # Exibe o primeiro gol, removendo o símbolo de "%" caso necessário
            try:
                st.metric("⚽ 1º Gol", primeiro_gol)
            except Exception as e:
                st.metric("⚽ 1º Gol", "Erro")
                st.write(f"Erro ao processar 1º gol: {e}")
        else:
            st.metric("⚽ 1º Gol", "—")

        # Exibe o minuto médio para o time visitante
        st.metric("⏱️ Tempo Médio 1º Gol", round(gm_away['AVG_min_scored'].values[0], 1) if not gm_away.empty else "—")


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

with tabs[7]:
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

# ABA 7 - Descritiva

with tabs[8]:
    st.markdown("## 📊 Análise Descritiva e Sugestões de Apostas")

    # Dados
    home_data = ppg_ht_home_df[ppg_ht_home_df['Team_Home'] == equipe_home]
    away_data = ppg_ht_away_df[ppg_ht_away_df['Team_Away'] == equipe_away]
    fg_home = home_fg_df[home_fg_df['Team_Home'] == equipe_home]
    fg_away = away_fg_df[away_fg_df['Team_Away'] == equipe_away]
    gm_home = goal_minute_home_df[goal_minute_home_df['Team_Home'] == equipe_home]
    gm_away = goal_minute_away_df[goal_minute_away_df['Team_Away'] == equipe_away]

    # Variáveis
    pih = round(home_data['PIH'].values[0], 2) if not home_data.empty else 0
    pia = round(away_data['PIA'].values[0], 2) if not away_data.empty else 0
    ppg_home = round(home_data['PPG_HT_Home'].values[0], 2) if not home_data.empty else 0
    ppg_away = round(away_data['PPG_HT_Away'].values[0], 2) if not away_data.empty else 0
    gf_home = round(home_data['GF_AVG_Home'].values[0], 2) if not home_data.empty else 0
    gf_away = round(away_data['GF_AVG_Away'].values[0], 2) if not away_data.empty else 0
    gd_home = round(home_data['GD_Home'].values[0], 2) if not home_data.empty else 0
    gd_away = round(away_data['GD_Away'].values[0], 2) if not away_data.empty else 0
    rank_home = int(home_data['Rank_Home'].values[0]) if not home_data.empty else "—"
    rank_away = int(away_data['Rank_Away'].values[0]) if not away_data.empty else "—"
    fg_percent_home = int(fg_home['First_Gol'].values[0]) if not fg_home.empty else "—"
    fg_percent_away = int(fg_away['First_Gol'].values[0]) if not fg_away.empty else "—"
    min_gol_home = round(gm_home['AVG_min_scored'].values[0], 1) if not gm_home.empty else "—"
    min_gol_away = round(gm_away['AVG_min_scored'].values[0], 1) if not gm_away.empty else "—"

    # Cabeçalho com definição
    st.markdown("✅ **Definições Chave:**")
    st.markdown("""
- PIH (Power Index Home) e PIA (Power Index Away) ≥ 0.62 → indicam equipes fortes.  
- Quanto mais próximo de 1.00, maior a força da equipe.  
- PPG HT → Pontos por jogo em casa/fora.  
- GF_AVG → Gols marcados em média.  
- GD → Saldo de gols.  
- Rank → Posição no campeonato.  
- First_Gol → % de jogos em que marcou o 1º gol.  
- AVG_min_scored → Minuto médio em que marca o primeiro gol.  
    """)

    # Time da casa
    st.markdown(f"### 🏠 Time da Casa: {equipe_home}")
    st.markdown(f"""
**PIH:** {pih} → {"Equipe forte jogando em casa." if pih >= 0.62 else "Abaixo do índice de elite."}  
**PPG HT:** {ppg_home} → {"Excelente" if ppg_home >= 2 else "Regular"} aproveitamento em casa.  
**Média de Gols:** {gf_home} → {"Ofensivamente produtivo." if gf_home >= 1.5 else "Ataque modesto."}  
**Saldo de Gols:** {gd_home:+} → {"Boa defesa e ataque eficaz." if gd_home > 0 else "Sofre mais do que marca."}  
**Rank:** {rank_home}º lugar → {"Entre os líderes." if rank_home <= 6 else "Fora do G6."}  
**1º Gol:** {fg_percent_home}% → {"Tendência alta de sair na frente." if fg_percent_home >= 60 else "Inconsistente ao iniciar vencendo."}  
**Minuto Médio 1º Gol:** {min_gol_home} min → {"Equipe inicia bem as partidas." if isinstance(min_gol_home, (int, float)) and min_gol_home < 30 else "Demora a marcar."}  
""")

    # Time visitante
    st.markdown(f"### 🛫 Time Visitante: {equipe_away}")
    st.markdown(f"""
**PIA:** {pia} → {"Equipe forte fora de casa." if pia >= 0.62 else "Fora do padrão de elite."}  
**PPG HT:** {ppg_away} → {"Bom desempenho fora." if ppg_away >= 1.5 else "Aproveitamento irregular fora de casa."}  
**Média de Gols:** {gf_away} → {"Ofensiva perigosa." if gf_away >= 1.5 else "Ofensiva mais fraca."}  
**Saldo de Gols:** {gd_away:+} → {"Boa consistência defensiva." if gd_away > 0 else "Defensivamente vulnerável fora de casa."}  
**Rank:** {rank_away}º lugar → {"Entre os líderes." if rank_away <= 6 else "Equipe de meio de tabela."}  
**1º Gol:** {fg_percent_away}% → {"Começa vencendo com frequência." if fg_percent_away >= 60 else "Dificuldade em começar vencendo."}  
**Minuto Médio 1º Gol:** {min_gol_away} min → {"Início ofensivo rápido." if isinstance(min_gol_away, (int, float)) and min_gol_away < 30 else "Demora a marcar."}  
""")

    # Análise comparativa
    st.markdown("### 💡 Análise e Sugestões de Apostas")

    st.markdown("#### ⚖️ Força das Equipes")
    if pih >= 0.62 and pia < 0.62:
        st.markdown(f"- Com **PIH {pih}** vs **PIA {pia}**, clara vantagem para o time da casa.")
        st.markdown("- O time da casa possui melhor desempenho ofensivo, defensivo e ranking.")
    elif pia >= 0.62 and pih < 0.62:
        st.markdown(f"- Com **PIH {pih}** vs **PIA {pia}**, vantagem técnica para o time visitante.")
        st.markdown("- Visitante pode surpreender, especialmente se for ofensivo.")
    elif pia >= 0.62 and pih >= 0.62:
        st.markdown(f"- Ambos os times apresentam alto nível técnico (**PIH {pih}** vs **PIA {pia}**).")
        st.markdown("- Jogo equilibrado com tendência a gols dos dois lados.")
    else:
        st.markdown("- Ambas as equipes estão abaixo do índice de força de elite (0.62).")
        st.markdown("- Jogo de difícil leitura, com menor potencial técnico.")

    # Tendência 1º gol
    st.markdown("#### 🎯 Tendência de Primeiro Gol")
    if fg_percent_home != "—" and fg_percent_home >= 60:
        st.markdown(f"- Time da casa marca o 1º gol em {fg_percent_home}% dos jogos e muito cedo ({min_gol_home} min).")
    if fg_percent_away != "—" and fg_percent_away < 60:
        st.markdown(f"- Visitante marca menos o 1º gol e demora para balançar as redes ({min_gol_away} min).")

    # Sugestões
    st.markdown("#### 📈 Sugestões de Apostas")

    if pih >= 0.62 and pia < 0.62:
        st.markdown("""
- ✅ **Vitória do time da casa (1X2)** – forte favoritismo técnico e estatístico.  
- ✅ **Time da casa marca o 1º gol** – tendência clara de abrir o placar cedo.  
- ✅ **Menos de 2.5 gols do visitante** – baixa média ofensiva e saldo negativo.  
- ✅ **Over 0.5 HT do time da casa** – boa chance de marcar no 1º tempo.  
- 🚫 **Ambas Marcam (NÃO)** – se a defesa do mandante for sólida.  
""")
    elif pia >= 0.62 and pih < 0.62:
        st.markdown("""
- ✅ **Dupla chance: X2** – visitante pode surpreender.  
- ✅ **Ambas Marcam (SIM)** – se defesa do mandante for fraca.  
- ✅ **Gols acima de 1.5** – possível jogo movimentado.  
""")
    elif pih >= 0.62 and pia >= 0.62:
        st.markdown("""
- ✅ **Ambas Marcam (SIM)** – poder ofensivo dos dois lados.  
- ✅ **Over 2.5 gols** – jogo com alto potencial ofensivo.  
- ⚠️ **Evite mercado de resultado** – equilíbrio técnico.  
""")
    else:
        st.markdown("""
- ⚠️ **Under 2.5 gols** – jogo de baixa intensidade.  
- ⚠️ **Mercados alternativos (escanteios, cartões)** – imprevisibilidade no placar.  
""")

    st.info("Análise baseada em dados estatísticos recentes e indicadores de desempenho.")




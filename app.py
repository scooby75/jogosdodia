import streamlit as st
import pandas as pd
import os
import numpy as np
from scipy.stats import poisson

# ----------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------
st.set_page_config(page_title="Football Stats", layout="wide")

# ----------------------------
# CONSTANTES
# ----------------------------
DATA_URLS = {
    "all_data": [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_Favorito.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/overall_stats.csv"
    ],
    "first_goal": [
        "https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_home.csv",
        "https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_away.csv"
    ],
    "goal_minute": [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_away.csv"
    ],
    "goals_half": "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Half.csv",
    "goals_ht": [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Away.csv"
    ],
    "goals_per_time": [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Per_Time_Home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Per_Time_Away.csv"
    ],
    "ppg_ht": [
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/PPG_HT_Home.csv",
        "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/PPG_HT_Away.csv"
    ]
}

COLUMN_MAPPING = {
    "home": ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"],
    "away": ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"],
    "overall": ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]
}

# ----------------------------
# FUNÇÕES UTILITÁRIAS
# ----------------------------
@st.cache_data
def load_data(url):
    """Carrega um DataFrame a partir de uma URL"""
    try:
        df = pd.read_csv(url, encoding="utf-8-sig")
        df = df.dropna(axis=1, how='all')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de {url}: {str(e)}")
        return pd.DataFrame()

def normalize_team_name(team_name):
    """Normaliza o nome do time para comparação"""
    return str(team_name).strip().lower()

def get_unique_teams(*dfs):
    """Obtém times únicos de vários DataFrames"""
    teams = set()
    for df in dfs:
        for col in df.columns:
            if 'team' in col.lower() or 'equipe' in col.lower():
                teams.update(df[col].dropna().astype(str).apply(normalize_team_name))
    return sorted(teams)

def convert_percentage(value):
    """Converte string percentual para float"""
    try:
        if isinstance(value, str):
            value = value.replace('%', '').replace(',', '.').strip()
        return float(value)
    except:
        return None

def generate_frequency_bar(frequency_dict):
    """Gera HTML para barras de frequência"""
    colors = {
        "0": "#d9534f",  # vermelho
        "1": "#20de6e",  # verde
        "2": "#16ed48",  # azul
        "3": "#24da1e",  # laranja
        "4": "#56b72d"   # roxo
    }

    html = '<div style="display:flex; flex-wrap: wrap;">'
    for goals, freq in frequency_dict.items():
        blocks = int(freq)
        for _ in range(blocks):
            html += f'<div style="width: 6px; height: 20px; background-color: {colors[goals]}; margin: 1px;"></div>'
    html += '</div>'
    return html

# ----------------------------
# CARREGAMENTO DE DADOS
# ----------------------------
@st.cache_data
def load_all_datasets():
    """Carrega todos os datasets necessários"""
    datasets = {}
    
    # Carrega todos os dados principais
    all_data = [load_data(url) for url in DATA_URLS["all_data"]]
    datasets.update({
        "home_df": all_data[0],
        "away_df": all_data[1],
        "away_fav_df": all_data[2],
        "overall_df": all_data[3]
    })
    
    # Carrega dados adicionais
    datasets["home_fg_df"], datasets["away_fg_df"] = [load_data(url) for url in DATA_URLS["first_goal"]]
    datasets["goal_minute_home_df"], datasets["goal_minute_away_df"] = [load_data(url) for url in DATA_URLS["goal_minute"]]
    datasets["goals_half_df"] = load_data(DATA_URLS["goals_half"])
    datasets["cv_home_df"], datasets["cv_away_df"] = [load_data(url) for url in DATA_URLS["goals_ht"]]
    datasets["goals_per_time_home_df"], datasets["goals_per_time_away_df"] = [load_data(url) for url in DATA_URLS["goals_per_time"]]
    datasets["ppg_ht_home_df"], datasets["ppg_ht_away_df"] = [load_data(url) for url in DATA_URLS["ppg_ht"]]
    
    return datasets

# Carrega todos os dados
datasets = load_all_datasets()

# ----------------------------
# INTERFACE DO USUÁRIO
# ----------------------------
def setup_sidebar(datasets):
    """Configura a barra lateral com seleção de times"""
    st.sidebar.title("Seleção de Times")
    
    # Obtém todos os times únicos
    all_teams = get_unique_teams(*datasets.values())
    
    # Seleção dos times
    default_home = 'bayern munich' if 'bayern munich' in all_teams else 0
    default_away = 'dortmund' if 'dortmund' in all_teams else 0
    
    home_team = st.sidebar.selectbox(
        "🏠 Time da Casa:", 
        all_teams, 
        index=all_teams.index(default_home) if default_home in all_teams else 0,
        format_func=lambda x: x.title()
    )
    
    away_team = st.sidebar.selectbox(
        "🛫 Time Visitante:", 
        all_teams, 
        index=all_teams.index(default_away) if default_away in all_teams else 0,
        format_func=lambda x: x.title()
    )
    
    return home_team, away_team

# Configura a barra lateral
home_team, away_team = setup_sidebar(datasets)

# ----------------------------
# FUNÇÕES DE ANÁLISE
# ----------------------------
def filter_team_data(df, team_col, team_name, columns):
    """Filtra dados de um time específico"""
    return df[df[team_col].str.lower() == team_name.lower()][columns]

def show_team_stats(team_name, df, col_name, local):
    """Mostra estatísticas de um time"""
    stats = df[df[col_name].str.lower() == team_name.lower()]
    if not stats.empty:
        st.markdown(f"### {team_name.title()} ({local})")
        cols = ['Matches', 'First_Gol', 'Goals']
        st.dataframe(stats[cols] if all(c in stats.columns for c in cols) else stats, 
                    use_container_width=True)
    else:
        st.warning(f"Nenhuma estatística encontrada para {team_name.title()} ({local})")

def analyze_team_performance(team_name, ppg, gf_avg, rank, is_home=True):
    """Analisa o desempenho de um time"""
    if is_home:
        if ppg >= 1.8:
            return "excelente", "alta probabilidade de vitória"
        elif ppg >= 1.5:
            return "bom", "boas chances de vitória"
        elif ppg >= 1.2:
            return "regular", "desempenho equilibrado"
        else:
            return "fraco", "dificuldade em vencer"
    else:
        if ppg >= 1.5:
            return "forte", "bom desempenho fora de casa"
        elif ppg >= 1.0:
            return "regular", "resultados mistos como visitante"
        else:
            return "fraco", "dificuldade em jogos fora"

def calculate_score_probabilities(home_avg, away_avg, max_goals=5):
    """Calcula probabilidades de placar usando Poisson"""
    placares = []
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            prob = poisson.pmf(home_goals, home_avg) * poisson.pmf(away_goals, away_avg)
            placares.append(((home_goals, away_goals), prob))
    
    # Ordena por probabilidade
    placares.sort(key=lambda x: x[1], reverse=True)
    return placares[:5]  # Retorna os 5 mais prováveis

# ----------------------------
# ABAS PRINCIPAIS
# ----------------------------
def render_summary_tab(home_team, away_team, datasets):
    """Renderiza a aba de resumo"""
    with tabs[0]:
        # Dados básicos
        home_data = filter_team_data(datasets["home_df"], "Team_Home", home_team, COLUMN_MAPPING["home"])
        away_data = filter_team_data(datasets["away_df"], "Team_Away", away_team, COLUMN_MAPPING["away"])
        
        if not home_data.empty:
            home_row = home_data.iloc[0]
            ppg_home = home_row.get("PPG_Home", 0)
            home_emoji = "🟩" if ppg_home >= 1.8 else "🟥"
            
            st.markdown(f"{home_emoji} **{home_team.title()} (Casa)**")
            
            cols = st.columns(5)
            cols[1].metric("Média Gols", home_row.get("GF_AVG_Home", "N/A"))
            cols[0].metric("PIH", home_row.get("PIH", "N/A"))
            cols[2].metric("PPG Casa", home_row.get("PPG_Home", "N/A"))
            cols[3].metric("Odd Justa", home_row.get("Odd_Justa_MO", "N/A"))
            cols[4].metric("Rank Casa", home_row.get("Rank_Home", "N/A"))
        
        if not away_data.empty:
            away_row = away_data.iloc[0]
            ppg_away = away_row.get("PPG_Away", 0)
            away_emoji = "🟩" if ppg_away <= 1.00 else "🟥"
            
            st.markdown(f"{away_emoji} **{away_team.title()} (Visitante)**")
            
            cols = st.columns(5)
            cols[1].metric("Média Gols", away_row.get("GF_AVG_Away", "N/A"))
            cols[0].metric("PIA", away_row.get("PIA", "N/A"))
            cols[2].metric("PPG Fora", away_row.get("PPG_Away", "N/A"))
            cols[3].metric("Odd Justa", away_row.get("Odd_Justa_MO", "N/A"))
            cols[4].metric("Rank Fora", away_row.get("Rank_Away", "N/A"))
        
        # Primeiro gol
        st.markdown("### ⚽ Marca Primeiro")
        col1, col2 = st.columns(2)
        
        with col1:
            home_fg = filter_team_data(datasets["home_fg_df"], "Team_Home", home_team, ['Matches', 'First_Gol', 'Goals'])
            if not home_fg.empty:
                row = home_fg.iloc[0]
                first_goal = convert_percentage(row['First_Gol'])
                
                cols = st.columns(3)
                cols[0].metric("Partidas", row['Matches'])
                cols[1].metric("1º Gol", row['First_Gol'])
                cols[2].metric("Total Gols", row['Goals'])
                
                emoji = "🟩" if first_goal and first_goal >= 60 else "🟥"
                st.markdown(f"{emoji} **{home_team.title()} (Casa)**")
        
        with col2:
            away_fg = filter_team_data(datasets["away_fg_df"], "Team_Away", away_team, ['Matches', 'First_Gol', 'Goals'])
            if not away_fg.empty:
                row = away_fg.iloc[0]
                first_goal = convert_percentage(row['First_Gol'])
                
                cols = st.columns(3)
                cols[0].metric("Partidas", row['Matches'])
                cols[1].metric("1º Gol", row['First_Gol'])
                cols[2].metric("Total Gols", row['Goals'])
                
                emoji = "🟩" if first_goal and first_goal <= 45 else "🟥"
                st.markdown(f"{emoji} **{away_team.title()} (Fora)**")
        
        # Frequência de gols por tempo
        st.markdown("### ⏱️ Frequência Gols 1º e 2º Tempo")
        goals_half = datasets["goals_half_df"]
        filtered = goals_half[goals_half['Team'].str.lower().isin([home_team.lower(), away_team.lower()])]
        
        if not filtered.empty:
            cols = st.columns(4)
            
            for i, team in enumerate([home_team, away_team]):
                team_data = filtered[filtered['Team'].str.lower() == team.lower()]
                if not team_data.empty:
                    first_half = team_data['1st half'].values[0]
                    second_half = team_data['2nd half'].values[0]
                    
                    first_half_num = convert_percentage(first_half)
                    emoji = "🟩" if (i == 0 and first_half_num and first_half_num >= 50) or (i == 1 and first_half_num and first_half_num < 55) else "🟥"
                    
                    cols[i*2].metric(f"{emoji} {team.title()} - 1º Tempo", first_half)
                    cols[i*2+1].metric(f"{team.title()} - 2º Tempo", second_half)
        
        # Frequência de gols HT
        st.markdown("### 📌 Frequência Gols HT")
        col1, col2 = st.columns(2)
        
        for i, (team, local, df, cols_map) in enumerate([
            (home_team, "Casa", datasets["cv_home_df"], {"Avg.": "Avg", "4+": "4"}),
            (away_team, "Fora", datasets["cv_away_df"], {"Avg..1": "Avg", "0.1": "0", "1.1": "1", "2.1": "2", "3.1": "3", "4+.1": "4"})
        ]):
            with col1 if i == 0 else col2:
                team_data = df[df[f"Team_{local}"].str.lower() == team.lower()]
                if not team_data.empty:
                    # Renomeia colunas
                    team_data = team_data.rename(columns=cols_map)
                    
                    # Extrai métricas
                    row = team_data.iloc[0]
                    avg = convert_percentage(row['Avg'])
                    with_goals = f"{int(convert_percentage(row.get('% Com Gols', 0)) or 0)}%"
                    without_goals = f"{int(convert_percentage(row.get('% Sem Gols', 0)) or 0)}%"
                    
                    # Determina emojis
                    avg_emoji = "🟩" if (i == 0 and avg and avg >= 0.60) or (i == 1 and avg and avg < 0.70) else "🟥"
                    goals_emoji = "🟩" if (i == 0 and convert_percentage(with_goals) >= 60) or (i == 1 and convert_percentage(with_goals) < 50) else "🟥"
                    
                    # Mostra métricas
                    metric_cols = st.columns(3)
                    metric_cols[0].metric(f"{avg_emoji} Média Gols", f"{avg:.2f}" if avg else "N/A")
                    metric_cols[1].metric(f"{goals_emoji} Com Gols", with_goals)
                    metric_cols[2].metric("Sem Gols", without_goals)
                    
                    # Gera barra de frequência
                    freq_dict = {str(g): row[str(g)] for g in range(5)}
                    st.markdown(generate_frequency_bar(freq_dict), unsafe_allow_html=True)
        
        # Gols por tempo
        st.markdown("### ⏱️ Gols 15min")
        col1, col2 = st.columns(2)
        
        for i, (team, local, df) in enumerate([
            (home_team, "Casa", datasets["goals_per_time_home_df"]),
            (away_team, "Fora", datasets["goals_per_time_away_df"])
        ]):
            with col1 if i == 0 else col2:
                filtered = df[df[f"Team_{local}"].str.lower() == team.lower()]
                if not filtered.empty:
                    avg_scored = filtered['AVG_Scored'].str.extract('(\d+)').astype(float).values[0]
                    icon = "🟩" if (i == 0 and avg_scored <= 45) or (i == 1 and avg_scored > 45) else "🟥"
                    st.markdown(f"{icon} **{team.title()} ({local})**")
                    st.dataframe(filtered[['League', 'GP', 'AVG_Scored', '0-15', '16-30', '31-45']], 
                               use_container_width=True)

def render_home_tab(home_team, away_team, datasets):
    """Renderiza a aba do time da casa"""
    with tabs[1]:
        st.markdown("### Home")
        home_data = filter_team_data(datasets["home_df"], "Team_Home", home_team, COLUMN_MAPPING["home"])
        st.dataframe(home_data, use_container_width=True)
        
        st.markdown("### Away")
        away_data = filter_team_data(datasets["away_df"], "Team_Away", away_team, COLUMN_MAPPING["away"])
        st.dataframe(away_data, use_container_width=True)

def render_overall_tab(home_team, away_team, datasets):
    """Renderiza a aba de dados gerais"""
    with tabs[2]:
        st.markdown("### Home - Geral")
        overall_data = filter_team_data(datasets["overall_df"], "Team_Home_Overall", home_team, COLUMN_MAPPING["overall"])
        st.dataframe(overall_data, use_container_width=True)
        
        st.markdown("### Away")
        away_data = filter_team_data(datasets["away_df"], "Team_Away", away_team, COLUMN_MAPPING["away"])
        st.dataframe(away_data, use_container_width=True)

def render_away_tab(home_team, away_team, datasets):
    """Renderiza a aba do time visitante"""
    with tabs[3]:
        st.markdown("### Away - Favorito")
        away_fav_data = filter_team_data(datasets["away_fav_df"], "Team_Away_Fav", away_team, COLUMN_MAPPING["away"])
        st.dataframe(away_fav_data, use_container_width=True)
        
        st.markdown("### Home")
        home_data = filter_team_data(datasets["home_df"], "Team_Home", home_team, COLUMN_MAPPING["home"])
        st.dataframe(home_data, use_container_width=True)

def render_first_goal_tab(home_team, away_team, datasets):
    """Renderiza a aba de primeiro gol"""
    with tabs[4]:
        show_team_stats(home_team, datasets["home_fg_df"], 'Team_Home', 'Casa')
        show_team_stats(away_team, datasets["away_fg_df"], 'Team_Away', 'Fora')

def render_goals_minute_tab(home_team, away_team, datasets):
    """Renderiza a aba de minutos dos gols"""
    with tabs[5]:
        home_data = filter_team_data(datasets["goal_minute_home_df"], "Team_Home", home_team, ['AVG_min_scored'])
        away_data = filter_team_data(datasets["goal_minute_away_df"], "Team_Away", away_team, ['AVG_min_scored'])
        
        if not home_data.empty:
            st.success(f"🏠 **{home_team.title()}** marca seu primeiro gol em média aos **{home_data['AVG_min_scored'].values[0]:.1f} min**.")
        
        if not away_data.empty:
            st.success(f"🛫 **{away_team.title()}** marca seu primeiro gol em média aos **{away_data['AVG_min_scored'].values[0]:.1f} min**.")

def render_goals_half_tab(home_team, away_team, datasets):
    """Renderiza a aba de gols por tempo"""
    with tabs[6]:
        filtered = datasets["goals_half_df"][datasets["goals_half_df"]['Team'].str.lower().isin([home_team.lower(), away_team.lower()])]
        if not filtered.empty:
            st.dataframe(filtered[['League_Name', 'Team', 'Scored', '1st half', '2nd half']], 
                        use_container_width=True)
        else:
            st.warning("Nenhuma estatística de Goals Half encontrada.")

def render_goals_ht_tab(home_team, away_team, datasets):
    """Renderiza a aba de gols no primeiro tempo"""
    with tabs[7]:
        col1, col2 = st.columns(2)
        
        for i, (team, local, df, cols_map) in enumerate([
            (home_team, "Home", datasets["cv_home_df"], {"Avg.": "Avg", "4+": "4"}),
            (away_team, "Away", datasets["cv_away_df"], {"Avg..1": "Avg", "0.1": "0", "1.1": "1", "2.1": "2", "3.1": "3", "4+.1": "4"})
        ]):
            with col1 if i == 0 else col2:
                team_data = df[df[f"Team_{local}"].str.lower() == team.lower()]
                if not team_data.empty:
                    # Renomeia colunas
                    team_data = team_data.rename(columns=cols_map)
                    
                    # Mostra dataframe
                    st.dataframe(team_data[[f"Team_{local}", "Avg", "0", "1", "2", "3", "4", "Total_Jogos", "% Com Gols", "% Sem Gols", "Classificação Ofensiva"]], 
                               use_container_width=True)
                    
                    # Gera barra de frequência
                    freq_dict = {str(g): team_data[str(g)].iloc[0] for g in range(5)}
                    st.markdown(generate_frequency_bar(freq_dict), unsafe_allow_html=True)
                    
                    # Mostra métricas
                    cols = st.columns(3)
                    avg = convert_percentage(team_data['Avg'].iloc[0])
                    with_goals = convert_percentage(team_data['% Com Gols'].iloc[0])
                    without_goals = convert_percentage(team_data['% Sem Gols'].iloc[0])
                    
                    cols[0].metric("Média 1T", f"{avg:.2f}" if avg else "N/A")
                    cols[1].metric("Com Gols", f"{int(with_goals)}%" if with_goals else "N/A")
                    cols[2].metric("Sem Gols", f"{int(without_goals)}%" if without_goals else "N/A")
                else:
                    st.warning(f"Dados não encontrados para o time {local.lower()}")

def render_goals_per_time_tab(home_team, away_team, datasets):
    """Renderiza a aba de gols por tempo"""
    with tabs[8]:
        col1, col2 = st.columns(2)
        
        for i, (team, local, df) in enumerate([
            (home_team, "Home", datasets["goals_per_time_home_df"]),
            (away_team, "Away", datasets["goals_per_time_away_df"])
        ]):
            with col1 if i == 0 else col2:
                filtered = df[df[f"Team_{local}"].str.lower() == team.lower()]
                if not filtered.empty:
                    st.subheader(f"Gols por tempo - {team.title()} ({local})")
                    st.dataframe(filtered[['League', f'Team_{local}', 'GP', '0-15', '16-30', '31-45', '46-60', '61-75', '76-90']],
                               use_container_width=True)
                else:
                    st.warning(f"Nenhum dado encontrado para {team.title()}")

def render_htf_tab(home_team, away_team, datasets):
    """Renderiza a aba HTF"""
    with tabs[9]:
        home_stats = filter_team_data(datasets["ppg_ht_home_df"], "Team_Home", home_team, 
                                    ['League','Team_Home','GP','PIH','PIH_HA','PPG_HT_Home','GF_AVG_Home','Odd_Justa_MO','Rank_Home'])
        away_stats = filter_team_data(datasets["ppg_ht_away_df"], "Team_Away", away_team,
                                    ['League','Team_Away','GP','PIA','PIA_HA','PPG_HT_Away','GF_AVG_Away','Odd_Justa_MO','Rank_Away'])
        
        if not home_stats.empty:
            st.dataframe(home_stats, use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {home_team.title()}")
        
        if not away_stats.empty:
            st.dataframe(away_stats, use_container_width=True)
        else:
            st.warning(f"Nenhuma estatística encontrada para {away_team.title()}")

def render_synthesis_tab(home_team, away_team, datasets):
    """Renderiza a aba de síntese"""
    with tabs[10]:
        home_data = filter_team_data(datasets["home_df"], "Team_Home", home_team, COLUMN_MAPPING["home"])
        away_data = filter_team_data(datasets["away_df"], "Team_Away", away_team, COLUMN_MAPPING["away"])
        
        if not home_data.empty and not away_data.empty:
            home_row = home_data.iloc[0]
            away_row = away_data.iloc[0]
            
            # Dados adicionais
            home_fg = filter_team_data(datasets["home_fg_df"], "Team_Home", home_team, ['First_Gol'])
            away_fg = filter_team_data(datasets["away_fg_df"], "Team_Away", away_team, ['First_Gol'])
            
            home_ht = filter_team_data(datasets["ppg_ht_home_df"], "Team_Home", home_team, ['PIH'])
            away_ht = filter_team_data(datasets["ppg_ht_away_df"], "Team_Away", away_team, ['PIA'])
            
            # Rankings
            rank_home = home_row.get('Rank_Home', 999)
            rank_away = away_row.get('Rank_Away', 999)
            rank_diff = rank_away - rank_home
            
            # Estatísticas básicas
            ppg_home = home_row.get("PPG_Home", 0)
            ppg_away = away_row.get("PPG_Away", 0)
            gf_avg_home = home_row.get("GF_AVG_Home", 0)
            gf_avg_away = away_row.get("GF_AVG_Away", 0)
            total_avg_goals = gf_avg_home + gf_avg_away
            
            # Análise de desempenho
            home_perf, home_adv = analyze_team_performance(home_team, ppg_home, gf_avg_home, rank_home, is_home=True)
            away_perf, away_adv = analyze_team_performance(away_team, ppg_away, gf_avg_away, rank_away, is_home=False)
            
            # PIH e PIA
            PIH = home_ht['PIH'].values[0] if not home_ht.empty else 'N/A'
            PIA = away_ht['PIA'].values[0] if not away_ht.empty else 'N/A'
            
            # Análise textual
            st.markdown(f"""
            ### 🏠 {home_team.title()} (Casa)
            O time da casa **{home_team.title()}** apresenta um **{home_perf} desempenho** como mandante, com:
            - Média de **{gf_avg_home:.2f} gols** por partida
            - PPG de **{ppg_home:.2f}**
            - Ranking como mandante: **{rank_home}**
            - Pontos no 1º tempo (PIH): **{PIH}**
            """)
            
            if not home_fg.empty:
                st.markdown(f"- Marca o primeiro gol em **{home_fg['First_Gol'].values[0]}** das partidas")
            
            st.markdown(f"""
            ### ✈️ {away_team.title()} (Visitante)
            O visitante **{away_team.title()}** tem mostrado um desempenho **{away_perf}**, com:
            - Média de **{gf_avg_away:.2f} gols** por partida
            - PPG de **{ppg_away:.2f}**
            - Ranking como visitante: **{rank_away}**
            - Pontos no 1º tempo (PIA): **{PIA}**
            """)
            
            if not away_fg.empty:
                st.markdown(f"- Marca o primeiro gol em **{away_fg['First_Gol'].values[0]}** das partidas")
            
            # Sugestões de apostas
            st.markdown("### 📊 Sugestões de Apostas")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 1X2 (Resultado Final)")
                rankings_valid = rank_home != 999 and rank_away != 999
                
                if (ppg_home >= 1.8 and (ppg_home - ppg_away) >= 1 and rankings_valid and rank_diff >= 6):
                    st.success("**✅ Vitória do mandante (1)**")
                    st.markdown(f"""
                    - Superioridade clara do mandante
                    - Diferença de ranking: +{rank_diff} posições
                    - PPG: {ppg_home:.2f} vs {ppg_away:.2f}
                    """)
                elif (ppg_away >= 1.8 and (ppg_away - ppg_home) >= 1 and rankings_valid and rank_diff <= -6):
                    st.success("**✅ Vitória do visitante (2)**")
                    st.markdown(f"""
                    - Superioridade clara do visitante
                    - Diferença de ranking: {rank_diff} posições
                    - PPG: {ppg_away:.2f} vs {ppg_home:.2f}
                    """)
                elif abs(ppg_home - ppg_away) < 0.5:
                    st.warning("**⚖️ Empate (X)**")
                    st.markdown("- Equilíbrio entre as equipes")
                else:
                    st.info("**🔍 Sem aposta clara**")
            
            with col2:
                st.markdown("#### Handicap Asiático (HA)")
                diff_ppg = ppg_home - ppg_away
                
                if (ppg_home >= 1.8 and diff_ppg >= 1 and rankings_valid and rank_diff >= 6):
                    st.success("**✅ HA -1.0 para o mandante**")
                elif (ppg_home >= 1.8 and diff_ppg >= 0.5 and rankings_valid and rank_diff >= 4):
                    st.success("**✅ HA -0.75 para o mandante**")
                elif (ppg_away >= 1.8 and -diff_ppg >= 1 and rankings_valid and rank_diff <= -6):
                    st.success("**✅ HA +1.0 para o visitante**")
                elif abs(diff_ppg) < 0.5:
                    st.info("**🔍 HA 0.0 (Empate sem handicap)**")
                else:
                    st.warning("**⚠️ HA não recomendado**")
            

# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import numpy as np
from scipy.stats import poisson

# Configuração da página
st.set_page_config(page_title="Football Stats", layout="wide")

# ----------------------------
# CONSTANTES E CONFIGURAÇÕES
# ----------------------------
DATA_URLS = {
    "main": [
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

COLUMN_NAMES = {
    "home": ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"],
    "away": ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"],
    "overall": ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]
}

# ----------------------------
# FUNÇÕES UTILITÁRIAS
# ----------------------------
@st.cache_data
def load_csv(url):
    """Carrega um arquivo CSV e realiza limpeza básica"""
    try:
        df = pd.read_csv(url, encoding="utf-8-sig")
        df = df.dropna(axis=1, how='all')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {url}: {str(e)}")
        return pd.DataFrame()

def normalize_columns(df):
    """Normaliza nomes de colunas"""
    if not df.empty:
        df.columns = df.columns.str.strip()
    return df

def convert_percentage(value):
    """Converte valores percentuais para float"""
    try:
        if isinstance(value, str):
            return float(value.replace('%', '').replace(',', '.').strip())
        return float(value)
    except:
        return None

def generate_frequency_bar(frequency_dict):
    """Gera uma barra de frequência visual"""
    colors = {
        "0": "#d9534f",
        "1": "#20de6e",
        "2": "#16ed48",
        "3": "#24da1e",
        "4": "#56b72d"
    }
    
    html = '<div style="display:flex; flex-wrap: wrap;">'
    for goals, freq in frequency_dict.items():
        try:
            blocks = int(float(str(freq).replace(',', '.')))
        except:
            blocks = 0
        for _ in range(blocks):
            html += f'<div style="width: 6px; height: 20px; background-color: {colors[goals]}; margin: 1px;"></div>'
    html += '</div>'
    return html

# ----------------------------
# CARREGAMENTO DE DADOS
# ----------------------------
@st.cache_data
def load_all_data():
    """Carrega todos os dados necessários"""
    data = {}
    
    # Carrega dados principais
    main_data = [load_csv(url) for url in DATA_URLS["main"]]
    data["home_df"], data["away_df"], data["away_fav_df"], data["overall_df"] = main_data
    
    # Carrega outros dados
    data["home_fg_df"], data["away_fg_df"] = [load_csv(url) for url in DATA_URLS["first_goal"]]
    data["goal_minute_home_df"], data["goal_minute_away_df"] = [load_csv(url) for url in DATA_URLS["goal_minute"]]
    data["goals_half_df"] = load_csv(DATA_URLS["goals_half"])
    data["cv_home_df"], data["cv_away_df"] = [load_csv(url) for url in DATA_URLS["goals_ht"]]
    data["goals_per_time_home_df"], data["goals_per_time_away_df"] = [load_csv(url) for url in DATA_URLS["goals_per_time"]]
    data["ppg_ht_home_df"], data["ppg_ht_away_df"] = [load_csv(url) for url in DATA_URLS["ppg_ht"]]
    
    # Normaliza todas as tabelas
    for key in data:
        data[key] = normalize_columns(data[key])
    
    return data

# Carrega todos os dados
data = load_all_data()

# ----------------------------
# INTERFACE DO USUÁRIO
# ----------------------------
def get_all_teams(data):
    """Obtém a lista de todos os times disponíveis"""
    team_columns = [
        ('home_df', 'Team_Home'),
        ('away_df', 'Team_Away'),
        ('away_fav_df', 'Team_Away_Fav'),
        ('overall_df', 'Team_Home_Overall'),
        ('home_fg_df', 'Team_Home'),
        ('away_fg_df', 'Team_Away'),
        ('goal_minute_home_df', 'Team_Home'),
        ('goal_minute_away_df', 'Team_Away'),
        ('goals_half_df', 'Team'),
        ('goals_per_time_home_df', 'Team_Home'),
        ('goals_per_time_away_df', 'Team_Away'),
        ('ppg_ht_home_df', 'Team_Home'),
        ('ppg_ht_away_df', 'Team_Away')
    ]
    
    teams = set()
    for df_name, col_name in team_columns:
        df = data.get(df_name, pd.DataFrame())
        if not df.empty and col_name in df.columns:
            valid_teams = df[col_name].dropna().astype(str)
            valid_teams = valid_teams[valid_teams.str.contains(r'^[A-Za-z\s]+$', na=False)]
            teams.update(valid_teams.tolist())
    
    return sorted(teams)

# Sidebar - Seleção de times
all_teams = get_all_teams(data)
default_home = 'Bayern Munich' if 'Bayern Munich' in all_teams else 0
default_away = 'Dortmund' if 'Dortmund' in all_teams else 0

equipe_home = st.sidebar.selectbox("🏠 Time da Casa:", all_teams, index=all_teams.index(default_home) if default_home in all_teams else 0)
equipe_away = st.sidebar.selectbox("🛫 Time Visitante:", all_teams, index=all_teams.index(default_away) if default_away in all_teams else 0)

# ----------------------------
# FUNÇÕES DE ANÁLISE
# ----------------------------
def display_team_performance(team_name, team_data, is_home=True):
    """Exibe o desempenho de um time"""
    if not team_data.empty:
        row = team_data.iloc[0]
        ppg = row.get("PPG_Home" if is_home else "PPG_Away", 0)
        ppg_emoji = "🟩" if (ppg >= 1.8 and is_home) or (ppg <= 1.00 and not is_home) else "🟥"
        
        st.markdown(f"{ppg_emoji} **{team_name} ({'Casa' if is_home else 'Visitante'})**")
        
        cols = st.columns(5)
        metrics = [
            ("PIH" if is_home else "PIA", row.get("PIH" if is_home else "PIA", "N/A")),
            ("Média Gols", row.get("GF_AVG_Home" if is_home else "GF_AVG_Away", "N/A")),
            (f"PPG {'Casa' if is_home else 'Fora'}", row.get("PPG_Home" if is_home else "PPG_Away", "N/A")),
            ("Odd Justa", row.get("Odd_Justa_MO", "N/A")),
            (f"Rank {'Home' if is_home else 'Away'}", row.get("Rank_Home" if is_home else "Rank_Away", "N/A"))
        ]
        
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, value)
    else:
        st.info(f"Informações do time {'da casa' if is_home else 'visitante'} não disponíveis.")

def display_first_goal_stats(team_name, fg_data, is_home=True):
    """Exibe estatísticas de primeiro gol"""
    if not fg_data.empty:
        row = fg_data.iloc[0]
        first_goal = row['First_Gol']
        
        try:
            first_goal_num = convert_percentage(first_goal)
            if is_home:
                gol_emoji = "🟩" if first_goal_num >= 60 else "🟥"
            else:
                gol_emoji = "🟩" if first_goal_num <= 45 else "🟥"
        except:
            gol_emoji = "🟨"
        
        st.markdown(f"{gol_emoji} **{team_name} ({'Casa' if is_home else 'Fora'})**")
        
        cols = st.columns(3)
        cols[0].metric("Partidas", row['Matches'])
        cols[1].metric("1º Gol", first_goal)
        cols[2].metric("Total de Gols", row['Goals'])
    else:
        st.info("Sem dados.")

def display_goals_per_half(team_name, goals_data):
    """Exibe estatísticas de gols por tempo"""
    if not goals_data.empty:
        row = goals_data.iloc[0]
        
        cols = st.columns(2)
        first_half = row.get('1st half', 'N/A')
        second_half = row.get('2nd half', 'N/A')
        
        if first_half != "N/A":
            first_half_num = convert_percentage(first_half)
            gol_emoji = "🟩" if (first_half_num >= 50 and team_name == equipe_home) or (first_half_num < 55 and team_name == equipe_away) else "🟥"
            cols[0].metric(f"{gol_emoji} 1º Tempo", first_half)
        else:
            cols[0].metric("1º Tempo", first_half)
        
        cols[1].metric("2º Tempo", second_half)
    else:
        st.info("Sem dados.")

def display_ht_frequency(team_name, ht_data, is_home=True):
    """Exibe frequência de gols no primeiro tempo"""
    if not ht_data.empty:
        row = ht_data.iloc[0]
        
        # Extrai valores com base no tipo de time (home/away)
        if is_home:
            # Home columns: 4+	3	2	1	0	Avg.	Team_Home...
            avg_goals = float(str(row['Avg.']).replace(',', '.')) if row['Avg.'] else 0.0
            goals_pct = f"{int(round(convert_percentage(row.get('% Com Gols', '0'))))}%"
            no_goals_pct = f"{int(round(convert_percentage(row.get('% Sem Gols', '0'))))}%"
            
            freq_dict = {
                "0": row['0'],
                "1": row['1'],
                "2": row['2'],
                "3": row['3'],
                "4": row['4+']  # Note que usamos 4+ aqui
            }
        else:
            # Away columns: Team_Away	Avg..1	0.1	1.1	2.1	3.1	4+.1...
            avg_goals = float(str(row['Avg..1']).replace(',', '.')) if row['Avg..1'] else 0.0
            goals_pct = f"{int(round(convert_percentage(row.get('% Com Gols', '0'))))}%"
            no_goals_pct = f"{int(round(convert_percentage(row.get('% Sem Gols', '0'))))}%"
            
            freq_dict = {
                "0": row['0.1'],
                "1": row['1.1'],
                "2": row['2.1'],
                "3": row['3.1'],
                "4": row['4+.1']  # Note que usamos 4+.1 aqui
            }
        
        # Determina emojis baseado no contexto
        if is_home:
            avg_emoji = "🟩" if avg_goals >= 0.60 else "🟥"
            goals_emoji = "🟩" if convert_percentage(row.get('% Com Gols', '0')) >= 60 else "🟥"
        else:
            avg_emoji = "🟥" if avg_goals >= 0.70 else "🟩"
            goals_emoji = "🟥" if convert_percentage(row.get('% Com Gols', '0')) >= 50 else "🟩"
        
        cols = st.columns(3)
        cols[0].metric(f"{avg_emoji} Média Gols", avg_goals)
        cols[1].metric(f"{goals_emoji} Com Gols", goals_pct)
        cols[2].metric("Sem Gols", no_goals_pct)
        
        st.markdown(generate_frequency_bar(freq_dict), unsafe_allow_html=True)
    else:
        st.warning(f"Dados não encontrados para {team_name}")

def display_goals_per_time(team_name, time_data, is_home=True):
    """Exibe gols por faixa de tempo"""
    if not time_data.empty:
        avg_scored = time_data['AVG_Scored_Home' if is_home else 'AVG_Scored_Away'].str.extract('(\d+)').astype(float).values[0]
        
        if pd.isna(avg_scored):
            st.warning(f"Valor de AVG_Scored para {team_name} é inválido.")
        else:
            icon = "🟩" if (avg_scored <= 45 and is_home) or (avg_scored > 45 and not is_home) else "🟥"
            st.markdown(f"{icon} **{team_name} ({'Casa' if is_home else 'Fora'})**")
            
            columns = ['League', 'GP', 'AVG_Scored_Home' if is_home else 'AVG_Scored_Away', '0-15', '16-30', '31-45']
            st.dataframe(time_data[columns], use_container_width=True)
    else:
        st.info(f"Sem dados de gols por faixa de tempo para {team_name}")

def display_ht_tab(data, home_team, away_team):
    """Exibe a aba de estatísticas do primeiro tempo"""
    home_data = data["ppg_ht_home_df"][data["ppg_ht_home_df"]['Team_Home'] == home_team]
    away_data = data["ppg_ht_away_df"][data["ppg_ht_away_df"]['Team_Away'] == away_team]
    cv_home_data = data["cv_home_df"][data["cv_home_df"]['Team_Home'] == home_team]
    cv_away_data = data["cv_away_df"][data["cv_away_df"]['Team_Away'] == away_team]
    fg_home = data["home_fg_df"][data["home_fg_df"]['Team_Home'] == home_team]
    fg_away = data["away_fg_df"][data["away_fg_df"]['Team_Away'] == away_team]
    gm_home = data["goal_minute_home_df"][data["goal_minute_home_df"]['Team_Home'] == home_team]
    gm_away = data["goal_minute_away_df"][data["goal_minute_away_df"]['Team_Away'] == away_team]
    
    col_home, col_away = st.columns(2)
    
    with col_home:
        st.markdown(f"### 🏠 {home_team}")
        
        if not home_data.empty:
            st.metric("📈 PIH", round(home_data['PIH'].values[0], 2))
            st.metric("🏠 PPG HT", round(home_data['PPG_HT_Home'].values[0], 2))
            st.metric("📊 Média Gols", round(home_data['GF_AVG_Home'].values[0], 2))
            st.metric("📈 Saldo de Gols", round(home_data['GD_Home'].values[0], 2))
            st.metric("🏆 Rank", int(home_data['Rank_Home'].values[0]))
        
        if not fg_home.empty:
            st.metric("⚽ 1º Gol", fg_home.iloc[0]['First_Gol'])
        
        if not gm_home.empty:
            st.metric("⏱️ Tempo Médio 1º Gol", round(gm_home['AVG_min_scored'].values[0], 1))
    
    with col_away:
        st.markdown(f"### 🛫 {away_team}")
        
        if not away_data.empty:
            st.metric("📉 PIA", round(away_data['PIA'].values[0], 2))
            st.metric("🛫 PPG HT", round(away_data['PPG_HT_Away'].values[0], 2))
            st.metric("📊 Média de Gols", round(away_data['GF_AVG_Away'].values[0], 2))
            st.metric("📉 Saldo de Gols", round(away_data['GD_Away'].values[0], 2))
            st.metric("🏆 Rank", int(away_data['Rank_Away'].values[0]))
        
        if not fg_away.empty:
            st.metric("⚽ 1º Gol", fg_away.iloc[0]['First_Gol'])
        
        if not gm_away.empty:
            st.metric("⏱️ Tempo Médio 1º Gol", round(gm_away['AVG_min_scored'].values[0], 1))

def display_analysis_tab(data, home_team, away_team):
    """Exibe a aba de análise detalhada"""
    home_filtered = data["home_df"][data["home_df"]['Team_Home'] == home_team][COLUMN_NAMES["home"]]
    away_filtered = data["away_df"][data["away_df"]['Team_Away'] == away_team][COLUMN_NAMES["away"]]
    home_fg_data = data["home_fg_df"][data["home_fg_df"]['Team_Home'] == home_team]
    away_fg_data = data["away_fg_df"][data["away_fg_df"]['Team_Away'] == away_team]
    overall_stats = data["overall_df"]
    
    if not home_filtered.empty and not away_filtered.empty:
        home_row = home_filtered.iloc[0]
        away_row = away_filtered.iloc[0]
        
        # Coletar dados principais
        ppg_home = home_row.get("PPG_Home", 0)
        ppg_away = away_row.get("PPG_Away", 0)
        gf_avg_home = home_row.get("GF_AVG_Home", 0)
        gf_avg_away = away_row.get("GF_AVG_Away", 0)
        odd_justa_home = home_row.get('Odd_Justa_MO', 'N/A')
        odd_justa_away = away_row.get('Odd_Justa_MO', 'N/A')
        
        try:
            rank_home = int(home_row.get('Rank_Home', 999))
            rank_away = int(away_row.get('Rank_Away', 999))
            rank_diff = rank_away - rank_home
            rankings_validos = rank_home != 999 and rank_away != 999
        except:
            rank_home = 999
            rank_away = 999
            rank_diff = 0
            rankings_validos = False
        
        # Rodada atual
        rodada_atual = overall_stats['GP'].max() if not overall_stats.empty else "N/A"
        
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
        ### 🏠 {home_team} (Casa)
        Estamos na **{rodada_atual}ª rodada** da competição. 
        O time da casa **{home_team}** apresenta um **{desempenho_home} desempenho** como mandante, com uma frequência de **{gf_avg_home:.2f} gols** por partida e uma média de pontos por jogo (PPG) de **{ppg_home:.2f}**. 
        """
        
        if not home_fg_data.empty:
            analise_home += f"O time marca o primeiro gol em **{home_fg_data.iloc[0]['First_Gol']}** das partidas e "
        
        analise_home += f"seu ranking como mandante é **{rank_home}**, indicando {vantagem_home} contra adversários de nível similar."
        
        analise_away = f"""
        ### ✈️ {away_team} (Visitante)
        Estamos na **{rodada_atual}ª rodada** da competição. 
        O time visitante **{away_team}** tem mostrado um desempenho **{desempenho_away}** como visitante, com média de **{gf_avg_away:.2f} gols** por partida e PPG de **{ppg_away:.2f}**. 
        """
        
        if not away_fg_data.empty:
            analise_away += f"O time marca o primeiro gol em **{away_fg_data.iloc[0]['First_Gol']}** das partidas e "
        
        analise_away += f"seu ranking como visitante é **{rank_away}**, com {desempenho_fora}."
        
        st.markdown(analise_home)
        st.markdown(analise_away)
        
        # Sugestões de apostas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 1X2 (Resultado Final)")
            
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
            
            # Sugestão adicional: Lay ao Visitante (HT)
            if not home_fg_data.empty and not away_fg_data.empty:
                home_first_goal_percentage = convert_percentage(home_fg_data.iloc[0].get('First_Gol', 0))
                away_first_goal_percentage = convert_percentage(away_fg_data.iloc[0].get('First_Gol', 0))
                
                if home_first_goal_percentage is not None and away_first_goal_percentage is not None:
                    if home_first_goal_percentage >= 60 and away_first_goal_percentage <= 30:
                        st.info("**✅ Aposta sugerida:** Lay ao Visitante (HT)")
                        st.markdown("""
                        📊 **Justificativa:**  
                        • O time da casa marca o primeiro gol em **mais de 60%** das vezes.  
                        • O time visitante marca o primeiro gol em **menos de 30%** das vezes.  
                        • A aposta deve ser feita no *Lay ao Visitante* no intervalo.  
                        """)
        
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
        
        # Tendencia 05HT               
        col1, col2 = st.columns(2)    
        
        with col1:
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
        
        with col2:
            # Over/Under Gols
            st.markdown("### Over/Under 25FT")
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
        
        col1, col2 = st.columns(2)
        
        # Coluna 1: BTTS (Ambos Marcam)
        with col1:
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
        
        # Coluna 2: 5 Placares Mais Prováveis
        with col2:
            st.markdown("### 📊 5 Placares Mais Prováveis")
            
            # Cálculo da expectativa de gols com base no PPG e na média total de gols
            if (ppg_home + ppg_away) > 0:
                exp_gols_home = (ppg_home / (ppg_home + ppg_away)) * total_avg_goals
            else:
                exp_gols_home = 0
            exp_gols_away = total_avg_goals - exp_gols_home
            
            # Probabilidade do placar 0x1 quando a casa é favorita
            if ppg_home > ppg_away:
                prob_0_home = poisson.pmf(0, exp_gols_home)
                prob_1_away = poisson.pmf(1, exp_gols_away)
                prob_placar_0x1 = prob_0_home * prob_1_away
                st.write(f"🎯 Probabilidade do placar 0x1 (casa favorita): {prob_placar_0x1:.2%}")
            else:
                st.write("⚠️ O time da casa não é favorito neste confronto.")

            # Probabilidade Lay Goleada
            if gf_avg_home >= 1.6 and gf_avg_away <= 1.2:
                st.write("💰 Lay Goleada Visitante — Odd Máxima 50")

            # Gerar probabilidades de placares usando distribuição de Poisson
            max_gols = 5
            placares = []
            
            for gols_home in range(max_gols + 1):
                for gols_away in range(max_gols + 1):
                    prob_home = poisson.pmf(gols_home, exp_gols_home)
                    prob_away = poisson.pmf(gols_away, exp_gols_away)
                    prob_placar = prob_home * prob_away
                    placares.append(((gols_home, gols_away), prob_placar))
            
            # Ordenar pelos placares com maior probabilidade
            placares.sort(key=lambda x: x[1], reverse=True)
            
            # Exibir os 5 placares mais prováveis
            for i, ((gh, ga), prob) in enumerate(placares[:5], start=1):
                st.write(f"{i}. {home_team} {gh} x {ga} {away_team} — Probabilidade: {prob:.2%}")

def display_ht_analysis_tab(data, home_team, away_team):
    """Exibe a aba de análise detalhada do primeiro tempo"""
    home_data = data["ppg_ht_home_df"][data["ppg_ht_home_df"]['Team_Home'] == home_team]
    away_data = data["ppg_ht_away_df"][data["ppg_ht_away_df"]['Team_Away'] == away_team]
    cv_home_data = data["cv_home_df"][data["cv_home_df"]['Team_Home'] == home_team]
    cv_away_data = data["cv_away_df"][data["cv_away_df"]['Team_Away'] == away_team]
    fg_home = data["home_fg_df"][data["home_fg_df"]['Team_Home'] == home_team]
    fg_away = data["away_fg_df"][data["away_fg_df"]['Team_Away'] == away_team]
    gm_home = data["goal_minute_home_df"][data["goal_minute_home_df"]['Team_Home'] == home_team]
    gm_away = data["goal_minute_away_df"][data["goal_minute_away_df"]['Team_Away'] == away_team]
    
    # Análise qualitativa
    if not home_data.empty and not away_data.empty:
        home_row = home_data.iloc[0]
        away_row = away_data.iloc[0]
        
        # Variáveis principais
        ppg_ht_home = home_row.get("PPG_HT_Home", 0)
        ppg_ht_away = away_row.get("PPG_HT_Away", 0)
        gf_avg_ht_home = home_row.get("GF_AVG_Home", 0)
        gf_avg_ht_away = away_row.get("GF_AVG_Away", 0)
        rank_home = home_row.get("Rank_Home", 999)
        rank_away = away_row.get("Rank_Away", 999)
        rank_diff = rank_away - rank_home
        
        # Análise qualitativa HT
        if ppg_ht_home >= 1.8:
            desempenho_ht_home = "excelente"
            vantagem_ht_home = "alta probabilidade de liderar no intervalo"
        elif ppg_ht_home >= 1.2:
            desempenho_ht_home = "bom"
            vantagem_ht_home = "boas chances de estar à frente no intervalo"
        elif ppg_ht_home >= 0.8:
            desempenho_ht_home = "regular"
            vantagem_ht_home = "desempenho equilibrado no 1º tempo"
        else:
            desempenho_ht_home = "fraco"
            vantagem_ht_home = "dificuldade em liderar no intervalo"

        if ppg_ht_away >= 1.2:
            desempenho_ht_away = "bom"
            desempenho_ht_fora = "bom desempenho no 1º tempo fora de casa"
        elif ppg_ht_away >= 0.8:
            desempenho_ht_away = "regular"
            desempenho_ht_fora = "resultados mistos no 1º tempo como visitante"
        else:
            desempenho_ht_away = "fraco"
            desempenho_ht_fora = "dificuldade no 1º tempo em jogos fora"

        # Texto de análise HT
        analise_ht_home = f"""
        ### 🏠 {home_team} (Casa - 1º Tempo)
        O time da casa **{home_team}** apresenta um **{desempenho_ht_home} desempenho** no primeiro tempo como mandante, 
        com média de **{gf_avg_ht_home:.2f} gols** no 1º tempo e PPG HT de **{ppg_ht_home:.2f}**. 
        """
        
        if not fg_home.empty:
            primeiro_gol_home = fg_home.iloc[0]['First_Gol']
            analise_ht_home += f"O time marca o primeiro gol em **{primeiro_gol_home}** das partidas e "
            
        if not gm_home.empty:
            avg_min_home = gm_home.iloc[0]['AVG_min_scored']
            analise_ht_home += f"o tempo médio para marcar o primeiro gol é de **{avg_min_home:.1f} minutos**. "
            
        analise_ht_home += f"Seu ranking no 1º tempo como mandante é **{rank_home}**, indicando {vantagem_ht_home}."

        analise_ht_away = f"""
        ### ✈️ {away_team} (Visitante - 1º Tempo)
        O time visitante **{away_team}** tem mostrado um desempenho **{desempenho_ht_away}** no primeiro tempo como visitante, 
        com média de **{gf_avg_ht_away:.2f} gols** no 1º tempo e PPG HT de **{ppg_ht_away:.2f}**. 
        """
        
        if not fg_away.empty:
            primeiro_gol_away = fg_away.iloc[0]['First_Gol']
            analise_ht_away += f"O time marca o primeiro gol em **{primeiro_gol_away}** das partidas e "
            
        if not gm_away.empty:
            avg_min_away = gm_away.iloc[0]['AVG_min_scored']
            analise_ht_away += f"o tempo médio para marcar o primeiro gol é de **{avg_min_away:.1f} minutos**. "
            
        analise_ht_away += f"Seu ranking no 1º tempo como visitante é **{rank_away}**, com {desempenho_ht_fora}."

        st.markdown(analise_ht_home)
        st.markdown(analise_ht_away)

        # Sugestões de apostas HT
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 1X2 HT (Resultado no Intervalo)")
            
            if (ppg_ht_home >= 1.5 and (ppg_ht_home - ppg_ht_away) >= 0.8 and rank_diff >= 6):
                st.success("**✅ Aposta sugerida:** Vitória do mandante no 1º tempo (1)")
                st.markdown(f"""
                📊 **Justificativa:**  
                • Excelente desempenho no 1º tempo como mandante.  
                • Superioridade clara sobre o visitante no 1º tempo.  
                • Time melhor posicionado no ranking HT (posição {rank_home} vs {rank_away}).  
                """)
            elif (ppg_ht_away >= 1.5 and (ppg_ht_away - ppg_ht_home) >= 0.8 and rank_diff <= -6):
                st.success("**✅ Aposta sugerida:** Vitória do visitante no 1º tempo (2)")
                st.markdown(f"""
                📊 **Justificativa:**  
                • Excelente desempenho no 1º tempo como visitante.  
                • Superioridade clara sobre o mandante no 1º tempo.  
                • Time melhor posicionado no ranking HT (posição {rank_away} vs {rank_home}).  
                """)
            elif abs(ppg_ht_home - ppg_ht_away) < 0.3:
                st.warning("**⚖️ Aposta sugerida:** Empate no intervalo (X)")
                st.markdown("""
                📊 **Justificativa:**  
                • Equilíbrio entre as equipes no 1º tempo  
                • Nenhum time com vantagem significativa no intervalo.  
                """)
            else:
                st.info("**🔍 Aposta não recomendada**")
                st.markdown(f"""
                📊 **Justificativa:**  
                • Nenhum critério forte atendido.  
                • Diferença de ranking HT: {abs(rank_diff)} posições.  
                • Diferença de PPG HT: {abs(ppg_ht_home - ppg_ht_away):.2f}.  
                """)

        with col2:
            st.markdown("### Over/Under 0.5 HT")
            
            # Dados de frequência de gols no 1º tempo
            if not cv_home_data.empty and not cv_away_data.empty:
                try:
                    home_percent_raw = cv_home_data.iloc[0]['% Com Gols']
                    away_percent_raw = cv_away_data.iloc[0]['% Com Gols']
                    
                    if pd.notna(home_percent_raw) and pd.notna(away_percent_raw):
                        home_com_gols = convert_percentage(home_percent_raw)
                        away_com_gols = convert_percentage(away_percent_raw)
                        
                        media_com_gols = (home_com_gols + away_com_gols) / 2
                        
                        if media_com_gols >= 70:
                            st.success(f"**✅ Over 0.5 HT (Média: {media_com_gols:.1f}%)**")
                            st.markdown(f"""
                            📊 **Justificativa:**
                            • {home_team}: {home_com_gols:.1f}% de jogos com gol no 1º tempo  
                            • {away_team}: {away_com_gols:.1f}% de jogos com gol no 1º tempo  
                            • Alta probabilidade de pelo menos 1 gol no intervalo
                            """)
                        elif media_com_gols <= 50:
                            st.warning(f"**⚠️ Under 0.5 HT (Média: {media_com_gols:.1f}%)**")
                            st.markdown(f"""
                            📊 **Justificativa:**
                            • {home_team}: {home_com_gols:.1f}%  
                            • {away_team}: {away_com_gols:.1f}%  
                            • Baixa probabilidade de gol no 1º tempo
                            """)
                        else:
                            st.info(f"**🔍 Sem tendência clara (Média: {media_com_gols:.1f}%)**")
                    else:
                        st.warning("Valores nulos encontrados em '% Com Gols'.")
                except Exception as e:
                    st.error(f"Erro ao processar porcentagens de gols no 1º tempo: {e}")
            else:
                st.warning("Dados de frequência de gols no 1º tempo não disponíveis")

        # Tendências adicionais HT
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Primeiro a Marcar (HT)")
            
            if not fg_home.empty and not fg_away.empty:
                home_fg_percent = convert_percentage(fg_home.iloc[0]['First_Gol'])
                away_fg_percent = convert_percentage(fg_away.iloc[0]['First_Gol'])
                
                if home_fg_percent >= 60 and away_fg_percent <= 40:
                    st.success(f"**✅ {home_team} marca primeiro (HT)**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Casa: {home_fg_percent}% de marcar primeiro  
                    • Visitante: {away_fg_percent}% de marcar primeiro  
                    • Alta vantagem para o mandante abrir o placar  
                    """)
                elif away_fg_percent >= 60 and home_fg_percent <= 40:
                    st.success(f"**✅ {away_team} marca primeiro (HT)**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • Visitante: {away_fg_percent}% de marcar primeiro  
                    • Casa: {home_fg_percent}% de marcar primeiro  
                    • Alta vantagem para o visitante abrir o placar  
                    """)
                else:
                    st.info("**🔍 Sem vantagem clara para quem marca primeiro**")
            else:
                st.warning("Dados de primeiro gol não disponíveis")

        with col2:
            st.markdown("### Tempo do Primeiro Gol")
            
            if not gm_home.empty and not gm_away.empty:
                avg_min_home = gm_home.iloc[0]['AVG_min_scored']
                avg_min_away = gm_away.iloc[0]['AVG_min_scored']
                media_avg_min = (avg_min_home + avg_min_away) / 2
                
                if media_avg_min <= 30:
                    st.success(f"**✅ Primeiro gol antes de 30' (Média: {media_avg_min:.1f}')**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • {home_team}: {avg_min_home:.1f}' (média)  
                    • {away_team}: {avg_min_away:.1f}' (média)  
                    • Tendência de gol precoce no jogo  
                    """)
                elif media_avg_min >= 40:
                    st.warning(f"**⚠️ Primeiro gol após 40' (Média: {media_avg_min:.1f}')**")
                    st.markdown(f"""
                    📊 **Justificativa:**  
                    • {home_team}: {avg_min_home:.1f}' (média)  
                    • {away_team}: {avg_min_away:.1f}' (média)  
                    • Tendência de gol tardio no jogo  
                    """)
                else:
                    st.info(f"**🔍 Sem tendência clara (Média: {media_avg_min:.1f}')**")
            else:
                st.warning("Dados de tempo médio do primeiro gol não disponíveis")



# ----------------------------
# LAYOUT PRINCIPAL
# ----------------------------
tabs = st.tabs(["🎯 FT", "🎯 HT", "🧾 Analise", "Analise HT"])

# ABA 1 - FT   
with tabs[0]:
    # Dados filtrados
    home_filtered = data["home_df"][data["home_df"]['Team_Home'] == equipe_home][COLUMN_NAMES["home"]]
    away_filtered = data["away_df"][data["away_df"]['Team_Away'] == equipe_away][COLUMN_NAMES["away"]]
    
    # Desempenho dos times
    display_team_performance(equipe_home, home_filtered, is_home=True)
    display_team_performance(equipe_away, away_filtered, is_home=False)
    
    # Primeiro gol
    st.markdown("### ⚽ Marca Primeiro")
    col1, col2 = st.columns(2)
    
    with col1:
        home_fg_filtered = data["home_fg_df"][data["home_fg_df"]['Team_Home'] == equipe_home]
        display_first_goal_stats(equipe_home, home_fg_filtered, is_home=True)
    
    with col2:
        away_fg_filtered = data["away_fg_df"][data["away_fg_df"]['Team_Away'] == equipe_away]
        display_first_goal_stats(equipe_away, away_fg_filtered, is_home=False)
    
    # Frequência de gols por tempo
    st.markdown("### ⏱️ Frequência Gols 1º e 2º Tempo")
    goals_half_filtered = data["goals_half_df"][data["goals_half_df"]['Team'].isin([equipe_home, equipe_away])]
    
    if not goals_half_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            home_1st = goals_half_filtered[goals_half_filtered['Team'] == equipe_home]
            display_goals_per_half(equipe_home, home_1st)
        
        with col2:
            home_2nd = goals_half_filtered[goals_half_filtered['Team'] == equipe_home]
            if not home_2nd.empty:
                st.metric(f"{equipe_home} - 2º Tempo", home_2nd.iloc[0]['2nd half'])
        
        with col3:
            away_1st = goals_half_filtered[goals_half_filtered['Team'] == equipe_away]
            display_goals_per_half(equipe_away, away_1st)
        
        with col4:
            away_2nd = goals_half_filtered[goals_half_filtered['Team'] == equipe_away]
            if not away_2nd.empty:
                st.metric(f"{equipe_away} - 2º Tempo", away_2nd.iloc[0]['2nd half'])
    
    # Frequência de gols HT
    st.markdown("### 📌 Frequência Gols HT")
    col1, col2 = st.columns(2)
    
    with col1:
        home_ht = data["cv_home_df"][data["cv_home_df"]['Team_Home'] == equipe_home]
        display_ht_frequency(equipe_home, home_ht, is_home=True)
    
    with col2:
        away_ht = data["cv_away_df"][data["cv_away_df"]['Team_Away'] == equipe_away]
        display_ht_frequency(equipe_away, away_ht, is_home=False)
    
    # Gols 15min
    st.markdown("### ⏱️ Gols 15min")
    col1, col2 = st.columns(2)
    
    with col1:
        home_time = data["goals_per_time_home_df"][data["goals_per_time_home_df"]['Team_Home'] == equipe_home]
        display_goals_per_time(equipe_home, home_time, is_home=True)
    
    with col2:
        away_time = data["goals_per_time_away_df"][data["goals_per_time_away_df"]['Team_Away'] == equipe_away]
        display_goals_per_time(equipe_away, away_time, is_home=False)

# ABA 2 - HT
with tabs[1]:
    display_ht_tab(data, equipe_home, equipe_away)

# ABA 3 - Análise Detalhada
with tabs[2]:
    display_analysis_tab(data, equipe_home, equipe_away)

# ABA 4 - Análise HT
with tabs[3]:
    display_ht_analysis_tab(data, equipe_home, equipe_away)

# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

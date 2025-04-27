import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go


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

# Combina todas as equipes de várias fontes
all_teams = sorted(set(
    home_df['Team_Home'].dropna().astype(str)) |
    set(away_df['Team_Away'].dropna().astype(str)) |
    set(away_fav_df['Team_Away_Fav'].dropna().astype(str)) |
    set(overall_df['Team_Home_Overall'].dropna().astype(str)) |
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
home_filtered = home_df[home_df['Team_Home'] == equipe_home][home_columns]
away_filtered = away_df[away_df['Team_Away'] == equipe_away][away_columns]
away_fav_filtered = away_fav_df[away_fav_df['Team_Away_Fav'] == equipe_away][away_columns]
overall_filtered = overall_df[overall_df['Team_Home_Overall'] == equipe_home][overall_columns]

# ----------------------------
# INTERFACE STREAMLIT
# ----------------------------
tabs = st.tabs([
    "🧾 Resumo", "🏠 Home", "📊 Overall", "🛫 Away",
    "⚽ First Goal", "⏱️ Goals_Minute", "⚡ Goals HT/FT", "📌 CV HT", "📊 Goals Per Time"
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
    st.markdown("### 🏠 Home")

    if not home_filtered.empty:
        row = home_filtered.iloc[0]
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        col_b.metric("Média Gols", row.get("GF_AVG_Home", "N/A"))
        col_a.metric("PIH", row.get("PIH", "N/A"))
        col_c.metric("PPG Casa", row.get("PPG_Home", "N/A"))
        col_d.metric("Odd Justa", row.get("Odd_Justa_MO", "N/A"))
        col_e.metric("Rank Casa", row.get("Rank_Home", "N/A"))

        # Adicionando o emoji para PPG Casa
        ppg_home = row.get("PPG_Home", 0)
        ppg_home_emoji = "🟩" if ppg_home > 1.8 else "🟥"
        st.markdown(f"PPG Casa {ppg_home_emoji}")
    else:
        st.info("Informações do time da casa como favorito não disponíveis.")

    st.markdown("### 🚌 Away")

    if not away_filtered.empty:
        row = away_filtered.iloc[0]
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        col_b.metric("Média Gols", row.get("GF_AVG_Away", "N/A"))
        col_a.metric("PIA", row.get("PIA", "N/A"))
        col_c.metric("PPG Fora", row.get("PPG_Away", "N/A"))
        col_d.metric("Odd Justa", row.get("Odd_Justa_MO", "N/A"))
        col_e.metric("Rank Fora", row.get("Rank_Away", "N/A"))

        # Adicionando o emoji para PPG Fora
        ppg_away = row.get("PPG_Away", 0)
        ppg_away_emoji = "🟩" if ppg_away < 1.00 else "🟥"
        st.markdown(f"PPG Fora {ppg_away_emoji}")
    else:
        st.info("Informações do time visitante não disponíveis.")

    st.markdown("### ⚽ Marca Primeiro")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{equipe_home} (Casa)**")
        stats_home_fg = home_fg_df[home_fg_df['Team_Home'] == equipe_home]
        if not stats_home_fg.empty:
            row = stats_home_fg.iloc[0]
            partidas = row['Matches']
            primeiro_gol = row['First_Gol']
            total_gols = row['Goals']
    
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Partidas", partidas)
            col_b.metric("1º Gol", primeiro_gol)
            col_c.metric("Total de Gols", total_gols)
    
            # Adicionando o emoji para 1º Gol
            try:
                primeiro_gol_num = float(primeiro_gol)
                # Ajuste para 60% (🟩) e 40% (🟥)
                if primeiro_gol_num > 0.60:
                    gol_emoji = "🟩"  # 60% ou mais
                elif primeiro_gol_num <= 0.40:
                    gol_emoji = "🟥"  # 40% ou menos
                else:
                    gol_emoji = "🟨"  # Entre 40% e 60%, emoji de alerta
            except ValueError:
                gol_emoji = "🟨"  # Caso o valor não seja numérico, emoji de alerta
    
            st.markdown(f"1º Gol {gol_emoji}")
        else:
            st.info("Sem dados.")
    
    with col2:
        st.markdown(f"**{equipe_away} (Fora)**")
        stats_away_fg = away_fg_df[away_fg_df['Team_Away'] == equipe_away]
        if not stats_away_fg.empty:
            row = stats_away_fg.iloc[0]
            partidas = row['Matches']
            primeiro_gol = row['First_Gol']
            total_gols = row['Goals']
    
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Partidas", partidas)
            col_b.metric("1º Gol", primeiro_gol)
            col_c.metric("Total de Gols", total_gols)
    
            # Adicionando o emoji para 1º Gol
            try:
                primeiro_gol_num = float(primeiro_gol)
                # Ajuste para 60% (🟩) e 40% (🟥)
                if primeiro_gol_num > 0.60:
                    gol_emoji = "🟩"  # 60% ou mais
                elif primeiro_gol_num <= 0.40:
                    gol_emoji = "🟥"  # 40% ou menos
                else:
                    gol_emoji = "🟨"  # Entre 40% e 60%, emoji de alerta
            except ValueError:
                gol_emoji = "🟨"  # Caso o valor não seja numérico, emoji de alerta
    
            st.markdown(f"1º Gol {gol_emoji}")
        else:
            st.info("Sem dados.")
    

    st.markdown("### ⏱️ Frequência Gols 1º e 2º Tempo")

    goals_half_filtered = goals_half_df[goals_half_df['Team'].isin([equipe_home, equipe_away])]
    if not goals_half_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            home_1st_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_home]['1st half'].values[0] if equipe_home in goals_half_filtered['Team'].values else "Sem dados"
            st.metric(f"{equipe_home} - 1º Tempo", home_1st_half)

        with col2:
            home_2nd_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_home]['2nd half'].values[0] if equipe_home in goals_half_filtered['Team'].values else "Sem dados"
            st.metric(f"{equipe_home} - 2º Tempo", home_2nd_half)

        with col3:
            away_1st_half = goals_half_filtered[goals_half_filtered['Team'] == equipe_away]['1st half'].values[0] if equipe_away in goals_half_filtered['Team'].values else "Sem dados"
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

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Média Gols", media)
            col_b.metric("Com Gols", com_gols)
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

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Média Gols", media)
            col_b.metric("Com Gols", com_gols)
            col_c.metric("Sem Gols", sem_gols)

            freq_dict_away = {g: row[g] for g in ["0", "1", "2", "3", "4"]}
            st.markdown(gerar_barra_frequencia(freq_dict_away), unsafe_allow_html=True)
        else:
            st.warning("Dados não encontrados para o time visitante.")

    # Gols 15min
    st.markdown("### ⏱️ Gols 15min")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{equipe_home} (Casa)**")
        filtered_home = goals_per_time_home_df[goals_per_time_home_df['Team_Home'] == equipe_home]
        if not filtered_home.empty:
            st.dataframe(filtered_home[['League', 'GP', 'AVG_Scored', '0-15', '16-30', '31-45']], use_container_width=True)
        else:
            st.info("Sem dados de gols por faixa de tempo para o time da casa.")

    with col2:
        st.markdown(f"**{equipe_away} (Fora)**")
        filtered_away = goals_per_time_away_df[goals_per_time_away_df['Team_Away'] == equipe_away]
        if not filtered_away.empty:
            st.dataframe(filtered_away[['League', 'GP', 'AVG_Scored', '0-15', '16-30', '31-45']], use_container_width=True)
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

        
# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

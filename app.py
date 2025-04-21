import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Análise Geral e H2H - First Goal", layout="wide")

# ----------------------------
# FUNÇÕES DE CARREGAMENTO
# ----------------------------
@st.cache_data
def load_csv(url):
    return pd.read_csv(url)

@st.cache_data
def load_all_data():
    return (
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"),
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"),
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora_Favorito.csv"),
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/overall_stats.csv")
    )

@st.cache_data
def load_first_goal_data():
    return (
        load_csv("https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_home.csv"),
        load_csv("https://raw.githubusercontent.com/scooby75/firstgoal/main/scored_first_away.csv")
    )

@st.cache_data
def load_goal_minute_data():
    return (
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_home.csv"),
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/momento_do_gol_away.csv")
    )

@st.cache_data
def load_goals_half_data():
    return load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/Goals_Half.csv")

@st.cache_data
def goals_ht_data():
    return (
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Home.csv"),
        load_csv("https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/CV_Goals_HT_Away.csv")
    )

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

# Normalizar
for df in [home_df, away_df, away_fav_df, overall_df, home_fg_df, away_fg_df,
           goal_minute_home_df, goal_minute_away_df, goals_half_df, cv_home_df, cv_away_df]:
    normalize_columns(df)

# ----------------------------
# VARIÁVEIS GLOBAIS
# ----------------------------
home_columns = ["Liga", "PIH", "PIH_HA", "GD_Home", "PPG_Home", "GF_AVG_Home", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Home"]
away_columns = ["Liga", "PIA", "PIA_HA", "GD_Away", "PPG_Away", "GF_AVG_Away", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Away"]
overall_columns = ["Liga", "PIO", "PIO_HA", "GD_Overall", "PPG_Overall", "GF_AVG_Overall", "Odd_Justa_MO", "Odd_Justa_HA", "Rank_Overall"]

all_teams = sorted(set(home_df['Equipe'].dropna()) |
                   set(away_df['Equipe_Fora'].dropna()) |
                   set(away_fav_df['Equipe_Fora'].dropna()) |
                   set(overall_df['Equipe'].dropna()) |
                   set(home_fg_df['Team_Home'].dropna()) |
                   set(away_fg_df['Team_Away'].dropna()) |
                   set(goal_minute_home_df['Home'].dropna()) |
                   set(goal_minute_away_df['Away'].dropna()) |
                   set(goals_half_df['Team'].dropna()))

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
    "🧾 Resumo", "🏠 Análise Home", "📊 Análise Geral", "🛫 Análise Away",
    "⚽ First Goal", "⏱️ Goals_Minute", "⚡ Goals HT/FT", "📌 Goals HT"
])

# ABA 1 - Resumo
with tabs[0]:
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

# ABA 6 - Goals Half
with tabs[5]:
    filtered = goals_half_df[goals_half_df['Team'].isin([equipe_home, equipe_away])]
    if not filtered.empty:
        st.dataframe(filtered[['League_Name', 'Team', 'Scored', '1st half', '2nd half']], use_container_width=True)
    else:
        st.warning("Nenhuma estatística de Goals Half encontrada.")

# ABA 7 - Goals HT
with tabs[6]:
    st.subheader(f"🏠 {equipe_home} - CV Gols no 1º Tempo (Home)")
    home_ht = cv_home_df[cv_home_df['Team'] == equipe_home]
    if not home_ht.empty:
        st.dataframe(
            home_ht.rename(columns={
                "Avg.": "Avg",
                "4+": "4+"
            })[["Team", "Avg", "0", "1", "2", "3", "4+", "CV_Goals_HT (%)", "Classificação CV"]],
            use_container_width=True
        )
    else:
        st.warning("Dados não encontrados para o time da casa.")

    st.subheader(f"🛫 {equipe_away} - CV Gols no 1º Tempo (Away)")
    away_ht = cv_away_df[cv_away_df['Team'] == equipe_away]
    if not away_ht.empty:
        st.dataframe(
            away_ht.rename(columns={
                "Avg..1": "Avg",
                "0.1": "0", "1.1": "1", "2.1": "2", "3.1": "3", "4+.1": "4+"
            })[["Team", "Avg", "0", "1", "2", "3", "4+", "CV_Goals_HT (%)", "Classificação CV"]],
            use_container_width=True
        )
    else:
        st.warning("Dados não encontrados para o time visitante.")

# ABA 8 - Resumo Final
with tabs[7]:
    st.subheader("🏠 Dados Home")
    st.dataframe(home_filtered, use_container_width=True)

    st.subheader("🛫 Dados Away")
    st.dataframe(away_filtered, use_container_width=True)


# Executar com variável de ambiente PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    os.system(f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0")

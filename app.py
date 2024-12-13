import streamlit as st
import pandas as pd

# Configurar o título do aplicativo
st.title("Consulta de Jogos - Home e Away")

# URLs dos arquivos CSV
home_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
away_url = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Carregar os dados
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

home_data = load_data(home_url)
away_data = load_data(away_url)

# Colunas específicas para filtragem
home_team_col = "Equipe"
away_team_col = "Equipe_Fora"

# Verificar se as colunas existem
if home_team_col not in home_data.columns or away_team_col not in away_data.columns:
    st.error("Erro: Não foi possível identificar a coluna de equipes nos dados carregados.")
else:
    # Sidebar para seleção de equipes
    equipe_home = st.sidebar.selectbox(
        "Selecione a equipe Home:",
        sorted(home_data[home_team_col].unique())
    )

    equipe_away = st.sidebar.selectbox(
        "Selecione a equipe Away:",
        sorted(away_data[away_team_col].unique())
    )

    # Filtrar os dados para Home e Away
    home_filtered = home_data[home_data[home_team_col] == equipe_home] if equipe_home else home_data
    away_filtered = away_data[away_data[away_team_col] == equipe_away] if equipe_away else away_data

    # Exibir os dados filtrados para Home
    st.subheader("Jogos - Home")
    st.dataframe(home_filtered)

    # Exibir os dados filtrados para Away
    st.subheader("Jogos - Away")
    st.dataframe(away_filtered)

    # Comparação de resultados
    if not home_filtered.empty and not away_filtered.empty:
        st.subheader("Comparação de Resultados")
        # Unir os dados de Home e Away para exibição em formato empilhado
        home_filtered = home_filtered.rename(columns=lambda col: f"{col}_home")
        away_filtered = away_filtered.rename(columns=lambda col: f"{col}_away")
        home_filtered["Tipo"] = "Home"
        away_filtered["Tipo"] = "Away"

        comparison = pd.concat([home_filtered, away_filtered], axis=0, ignore_index=True)
        st.dataframe(comparison)

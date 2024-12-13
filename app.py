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

# Sidebar para seleção de equipe
equipe = st.sidebar.selectbox(
    "Selecione a equipe:",
    sorted(set(home_data['team'].unique()).union(away_data['team'].unique()))
)

# Filtrar os dados para Home e Away simultaneamente
home_filtered = home_data[home_data['team'] == equipe] if equipe else home_data
away_filtered = away_data[away_data['team'] == equipe] if equipe else away_data

# Exibir os dados filtrados para Home
st.subheader("Jogos - Home")
st.dataframe(home_filtered)

# Exibir os dados filtrados para Away
st.subheader("Jogos - Away")
st.dataframe(away_filtered)

# Comparação de resultados
if not home_filtered.empty and not away_filtered.empty:
    st.subheader("Comparação de Resultados")
    comparison = pd.merge(
        home_filtered, away_filtered, 
        on=['team'], 
        suffixes=('_home', '_away'), 
        how='outer'
    )
    st.dataframe(comparison)

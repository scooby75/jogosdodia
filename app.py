import streamlit as st
import pandas as pd

# URLs dos arquivos CSV
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Ler os arquivos CSV
df_casa = pd.read_csv(url_equipes_casa)
df_fora = pd.read_csv(url_equipes_fora)

# Seleção de equipe da casa
equipe_casa = st.selectbox("Selecione a Equipe da Casa", df_casa['Equipe'].unique())

# Exibir os dados da equipe da casa
st.write(f"Dados da equipe da casa {equipe_casa}:")
df_casa_selecionada = df_casa[df_casa['Equipe'] == equipe_casa]
st.write(df_casa_selecionada)

# Seleção de equipe de fora
equipe_fora = st.selectbox("Selecione a Equipe de Fora", df_fora['Equipe'].unique())

# Exibir os dados da equipe de fora
st.write(f"Dados da equipe de fora {equipe_fora}:")
df_fora_selecionada = df_fora[df_fora['Equipe'] == equipe_fora]
st.write(df_fora_selecionada)

# Comparação de algumas estatísticas entre as equipes
compara_gols = st.checkbox("Comparar gols (GF) das equipes")

if compara_gols:
    st.write(f"Comparação de Gols (GF) entre {equipe_casa} e {equipe_fora}:")
    gols_casa = df_casa_selecionada['GF'].sum()
    gols_fora = df_fora_selecionada['GF'].sum()
    st.write(f"Gols da equipe da casa {equipe_casa}: {gols_casa}")
    st.write(f"Gols da equipe de fora {equipe_fora}: {gols_fora}")

# Exemplo de comparação de pontos
compara_pontos = st.checkbox("Comparar pontos (Pts_Home/Pts_Away) das equipes")

if compara_pontos:
    st.write(f"Comparação de Pontos entre {equipe_casa} e {equipe_fora}:")
    pontos_casa = df_casa_selecionada['Pts_Home'].sum() if 'Pts_Home' in df_casa_selecionada.columns else 0
    pontos_fora = df_fora_selecionada['Pts_Away'].sum() if 'Pts_Away' in df_fora_selecionada.columns else 0
    st.write(f"Pontos da equipe da casa {equipe_casa}: {pontos_casa}")
    st.write(f"Pontos da equipe de fora {equipe_fora}: {pontos_fora}")

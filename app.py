import streamlit as st
import pandas as pd

# Carregar os dados das URLs
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Leitura dos dados
df_casa = pd.read_csv(url_equipes_casa)
df_fora = pd.read_csv(url_equipes_fora)

# Normalizar os nomes das colunas para facilitar a manipulação
df_casa.columns = df_casa.columns.str.strip().str.lower()
df_fora.columns = df_fora.columns.str.strip().str.lower()

# Renomear as colunas para garantir que sejam consistentes entre as duas fontes
df_casa = df_casa.rename(columns={
    'pts_home': 'pts',  # Renomeando para um nome comum
    'pih': 'pi',  # Renomeando para um nome comum
    'gd_home': 'gd',
    'odd_justa_mo': 'odd_mo',
    'odd_justa_ha': 'odd_ha'
})

df_fora = df_fora.rename(columns={
    'pts_away': 'pts',  # Renomeando para um nome comum
    'pia': 'pi',  # Renomeando para um nome comum
    'gd_away': 'gd',
    'odd_justa_mo': 'odd_mo',
    'odd_justa_ha': 'odd_ha'
})

# Adicionar uma coluna para identificar se é time da casa ou fora
df_casa['tipo'] = 'casa'
df_fora['tipo'] = 'fora'

# Concatenar os dois DataFrames
df = pd.concat([df_casa, df_fora], ignore_index=True)

# Verificar as colunas do DataFrame
st.write("Colunas do DataFrame:", df.columns)

# Definir filtros
st.title("Filtro de Equipes")
equipes_casa = st.selectbox("Selecione a Equipe da Casa", df[df['tipo'] == 'casa']['equipe'].unique())
equipes_fora = st.selectbox("Selecione a Equipe de Fora", df[df['tipo'] == 'fora']['equipe'].unique())

# Filtros para outras colunas
liga = st.selectbox("Selecione a Liga", df['liga'].unique())
odd_justa_ha = st.slider("Filtrar Odd Justa HA", min_value=df['odd_ha'].min(), max_value=df['odd_ha'].max(), step=0.01)
odd_justa_mo = st.slider("Filtrar Odd Justa MO", min_value=df['odd_mo'].min(), max_value=df['odd_mo'].max(), step=0.01)

# Aplicar os filtros
filtered_df = df[
    (df['equipe'] == equipes_casa) &
    (df['equipe'] == equipes_fora) &
    (df['liga'] == liga) &
    (df['odd_ha'] >= odd_justa_ha) &
    (df['odd_mo'] >= odd_justa_mo)
]

# Mostrar o dataframe filtrado
st.write("Dados filtrados:", filtered_df)

# Exibir algumas estatísticas (opcional)
st.write("Estatísticas das colunas numéricas:")
st.write(filtered_df.describe())

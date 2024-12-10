import streamlit as st
import pandas as pd

# Carregar os dados das URLs
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Leitura dos dados
df_casa = pd.read_csv(url_equipes_casa)
df_fora = pd.read_csv(url_equipes_fora)

# Concatenar os dois DataFrames em um único DataFrame para facilitar a manipulação
df = pd.concat([df_casa, df_fora], ignore_index=True)

# Exibir as colunas disponíveis
st.write("Colunas disponíveis no dataset:", df.columns)

# Definir filtros
st.title("Filtro de Equipes")
equipes_casa = st.selectbox("Selecione a Equipe da Casa", df['Equipes_casa'].unique())
equipes_fora = st.selectbox("Selecione a Equipe de Fora", df['equipes_fora'].unique())

# Filtros para outras colunas
liga = st.selectbox("Selecione a Liga", df['Liga'].unique())
odd_justa_ha = st.slider("Filtrar Odd Justa HA", min_value=df['Odd_Justa_HA'].min(), max_value=df['Odd_Justa_HA'].max(), step=0.01)
odd_justa_mo = st.slider("Filtrar Odd Justa MO", min_value=df['Odd_Justa_MO'].min(), max_value=df['Odd_Justa_MO'].max(), step=0.01)

# Aplicar os filtros
filtered_df = df[
    (df['Equipes_casa'] == equipes_casa) &
    (df['equipes_fora'] == equipes_fora) &
    (df['Liga'] == liga) &
    (df['Odd_Justa_HA'] >= odd_justa_ha) &
    (df['Odd_Justa_MO'] >= odd_justa_mo)
]

# Mostrar o dataframe filtrado
st.write("Dados filtrados:", filtered_df)

# Exibir algumas estatísticas (opcional)
st.write("Estatísticas das colunas numéricas:")
st.write(filtered_df.describe())

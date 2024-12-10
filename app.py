import streamlit as st
import pandas as pd

# URLs dos arquivos CSV
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Ler os arquivos CSV
df_casa = pd.read_csv(url_equipes_casa)
df_fora = pd.read_csv(url_equipes_fora)

# Verificar os tipos de dados das colunas
st.write("Tipos de dados das colunas de equipes_casa:", df_casa.dtypes)
st.write("Tipos de dados das colunas de equipes_fora:", df_fora.dtypes)

# Concatenar os DataFrames
try:
    df = pd.concat([df_casa, df_fora], ignore_index=True)
    st.write("DataFrame concatenado com sucesso!")
except Exception as e:
    st.error(f"Ocorreu um erro ao concatenar os DataFrames: {e}")

# Verificar valores nulos no DataFrame concatenado
st.write("Valores nulos no DataFrame:", df.isnull().sum())

# Substituir valores nulos por um valor padrão, se necessário
df.fillna({'Odd_Justa_MO': 0, 'Odd_Justa_HA': 0, 'GD_Home': 0, 'PIH': 0, 'PIH_HA': 0}, inplace=True)

# Exibir as primeiras 10 linhas do DataFrame
st.write("Primeiras 10 linhas do DataFrame concatenado:", df.head(10))

# Seleção de equipe da casa
equipes_casa = st.selectbox("Selecione a Equipe da Casa", df['Equipe'].unique())
st.write(f"Você selecionou a equipe da casa: {equipes_casa}")

# Filtrar os dados pela equipe da casa
df_casa_selecionada = df[df['Equipe'] == equipes_casa]

# Exibir os dados filtrados da equipe da casa
st.write(f"Dados da equipe da casa {equipes_casa}:", df_casa_selecionada)

# Filtragem adicional, se necessário
# Exemplo de filtrar apenas as colunas de interesse
st.write("Primeiras 10 linhas com colunas selecionadas:", df[['Equipe', 'GP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts_Home', 'Odd_Justa_MO']].head(10))

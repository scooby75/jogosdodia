import pandas as pd

# URLs dos arquivos CSV
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Carregar os arquivos CSV
equipes_casa = pd.read_csv(url_equipes_casa)
equipes_fora = pd.read_csv(url_equipes_fora)

# Mostrar as primeiras linhas para verificar os dados
print("Equipes Casa:")
print(equipes_casa.head())

print("\nEquipes Fora:")
print(equipes_fora.head())

# Criando o DataFrame com as colunas das equipes 'Home' e 'Away'
df = pd.DataFrame({
    'Home': equipes_casa['Equipe'],  # Ajuste o nome da coluna conforme necessário
    'Away': equipes_fora['Equipe']   # Ajuste o nome da coluna conforme necessário
})

# Mostrar o DataFrame resultante
print("\nDataFrame com as equipes Home e Away:")
print(df.head())

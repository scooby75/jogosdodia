import streamlit as st
import pandas as pd

# Função para carregar os dados dos arquivos CSV
def carregar_dados():
    # Carregar o arquivo enviado pelo usuário
    arquivo = st.file_uploader("Faça o upload do arquivo com os dados das partidas", type=["csv"])
    if arquivo is not None:
        df = pd.read_csv(arquivo)
        return df
    return None

# Função para carregar os arquivos de equipes
@st.cache
def carregar_equipes():
    # URLs dos arquivos CSV
    url_casa = 'https://raw.githubusercontent.com/scooby75/jogosdodia/main/equipes_casa.csv'
    url_fora = 'https://raw.githubusercontent.com/scooby75/jogosdodia/main/equipes_fora.csv'
    
    # Carregar os dados dos arquivos de equipes
    equipes_casa = pd.read_csv(url_casa)
    equipes_fora = pd.read_csv(url_fora)
    
    return equipes_casa, equipes_fora

# Função principal para comparar e criar o dataframe
def comparar_equipes(df):
    equipes_casa, equipes_fora = carregar_equipes()
    
    # Fazer a comparação das equipes
    resultado = []
    for index, row in df.iterrows():
        home = row['Home']
        away = row['Away']
        
        if home in equipes_casa['Equipe'].values and away in equipes_fora['Equipe'].values:
            # Adicionar os dados do jogo e as estatísticas
            dados_comparados = {
                'Hora': row['Hora'],
                'Evento': row['Evento'],
                'Competição': row['Competição'],
                'Home': home,
                'Away': away,
                'GP': '',  # Exemplo de dado extra, você pode adicionar mais informações conforme necessário
                'W': '',   # Dados de vitórias
                'D': '',   # Empates
                'L': '',   # Derrotas
                'GF': '',  # Gols feitos
                'GA': '',  # Gols contra
                'GD': '',  # Saldo de gols
                'Pts_Away': '',  # Pontos
                'PIH': '',  # Exemplo de dado
                'PIH_HA': '',  # Exemplo de dado
                'GD_Home': '',  # Exemplo de dado
                'Odd_Justa_MO_Home': '',  # Odds
                'Odd_Justa_HA_Home': '',  # Odds
                'PIA': '',  # Exemplo de dado
                'PIA_HA': '',  # Exemplo de dado
                'GD_Away': '',  # Exemplo de dado
                'Odd_Justa_MO_Away': '',  # Odds
                'Odd_Justa_HA_Away': '',  # Odds
            }
            resultado.append(dados_comparados)
    
    # Criar o dataframe final
    df_resultado = pd.DataFrame(resultado)
    return df_resultado

# Streamlit interface
def main():
    st.title("Análise de Jogos e Comparação de Equipes")
    
    # Carregar os dados do usuário
    df_jogos = carregar_dados()
    
    if df_jogos is not None:
        st.write("Dados carregados:")
        st.dataframe(df_jogos)
        
        # Comparar as equipes e criar o dataframe final
        df_resultado = comparar_equipes(df_jogos)
        
        # Exibir o resultado
        st.write("Resultado da comparação das equipes:")
        st.dataframe(df_resultado)

if __name__ == "__main__":
    main()

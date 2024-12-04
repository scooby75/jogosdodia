import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Título do aplicativo
st.title("Comparação de Jogos do Dia")

# URLs dos arquivos no GitHub
url_melhores_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Casa.csv"
url_melhores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Melhores_Equipes_Fora.csv"
url_piores_away = "https://raw.githubusercontent.com/scooby75/jogosdodia/main/Piores_Equipes_Fora.csv"
url_equipes_casa = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_casa.csv"
url_equipes_fora = "https://raw.githubusercontent.com/scooby75/jogosdodia/refs/heads/main/equipes_fora.csv"

# Função para limpar e extrair odds
def extrair_odds(valor):
    if isinstance(valor, str):
        try:
            return pd.to_numeric(valor.split('(')[0].replace(",", "").strip())
        except ValueError:
            return None
    return valor

# Upload do arquivo "Jogos do Dia"
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")

if jogos_dia_file:
    # Ler o arquivo "Jogos do Dia"
    jogos_dia = pd.read_csv(jogos_dia_file)

    # Carregar os arquivos diretamente das URLs
    melhores_casa = pd.read_csv(url_melhores_casa)
    melhores_away = pd.read_csv(url_melhores_away)
    piores_away = pd.read_csv(url_piores_away)
    equipes_casa = pd.read_csv(url_equipes_casa)
    equipes_fora = pd.read_csv(url_equipes_fora)

    # Verificar e corrigir o formato da coluna Evento
    st.subheader("Verificação dos dados na coluna 'Evento'")
    problemas = jogos_dia[~jogos_dia['Evento'].str.contains(' v ', na=False)]
    if not problemas.empty:
        st.warning("Foram encontrados problemas no formato da coluna 'Evento':")
        st.dataframe(problemas)
    else:
        st.success("Todos os dados estão no formato esperado.")

    # Filtrar apenas linhas válidas
    jogos_dia_validos = jogos_dia[jogos_dia['Evento'].str.contains(' v ', na=False)]

    # Filtrar jogos que não contêm palavras-chave indesejadas
    palavras_indesejadas = (
        'UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21|English Premier League 2|Israeli Cup|Friendly Matches|Malaysian Cup|Copa de França|Copa de Inglaterra|Scottish FA Cup|U23|Sub23|Cup|Copa'
    )
    jogos_dia_validos = jogos_dia_validos[~jogos_dia_validos['Competição'].str.contains(palavras_indesejadas, case=False, na=False)]

    # Adicionar colunas Time_Casa e Time_Fora
    jogos_dia_validos['Time_Casa'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[0].strip())
    jogos_dia_validos['Time_Fora'] = jogos_dia_validos['Evento'].apply(lambda x: x.split(' v ')[1].strip())

    # Corrigir as odds para Home, Away e The Draw
    for coluna in ['Home', 'Away', 'The Draw']:
        jogos_dia_validos[coluna] = jogos_dia_validos[coluna].apply(extrair_odds)

    # Exibir os jogos válidos
    st.subheader("Jogos válidos")
    st.dataframe(jogos_dia_validos)

    # Análise: Back Home  
   
    print(jogos_dia_validos.columns)

    # Converter W para numérico
    equipes_casa['W'] = pd.to_numeric(equipes_casa['W'], errors='coerce')
    equipes_fora['W'] = pd.to_numeric(equipes_fora['W'], errors='coerce')
    
    # Filtrar as melhores equipes jogando em casa
    melhores_casa_filtrados = equipes_casa[equipes_casa['W'] >= 5]
    
    # Filtrar as piores equipes jogando fora de casa
    piores_fora_filtrados = equipes_fora[equipes_fora['W'] <= 1]
    
    # Preprocessar nomes das equipes e ligas para melhorar eficiência
    melhores_casa_nomes = melhores_casa_filtrados['Equipe'].str.strip().str.title()  # Nome das equipes com a primeira letra maiúscula
    melhores_casa_ligas = melhores_casa_filtrados['Liga'].str.strip().str.lower()  # Ligas com todas as letras minúsculas
    piores_fora_nomes = piores_fora_filtrados['Equipe'].str.strip().str.title()  # Nome das equipes com a primeira letra maiúscula
    piores_fora_ligas = piores_fora_filtrados['Liga'].str.strip().str.lower()  # Ligas com todas as letras minúsculas
    
    # Função para verificar similaridade com times bons em casa e ruins fora, além das ligas
    def verifica_criterios(time_casa, time_fora, liga_casa, liga_fora):
        # Normalizar as entradas: time da casa e fora para título, liga para minúsculo
        time_casa_normalizado = time_casa.strip().title()  # Normalizar para título (primeira letra maiúscula)
        time_fora_normalizado = time_fora.strip().title()  # Normalizar para título (primeira letra maiúscula)
        liga_casa_normalizada = liga_casa.strip().lower()  # Liga em minúscula
        liga_fora_normalizada = liga_fora.strip().lower()  # Liga em minúscula
        
        # Verificar se o time da casa é bom jogando em casa
        casa_match = any(fuzz.partial_ratio(time_casa_normalizado, equipe) > 80 for equipe in melhores_casa_nomes)
        
        # Verificar se o time fora é ruim jogando fora
        fora_match = any(fuzz.partial_ratio(time_fora_normalizado, equipe) > 80 for equipe in piores_fora_nomes)
        
        # Verificar se a liga do time da casa é similar à liga das melhores equipes em casa
        liga_casa_match = any(fuzz.partial_ratio(liga_casa_normalizada, liga) > 80 for liga in melhores_casa_ligas)
        
        # Verificar se a liga do time visitante é similar à liga das piores equipes fora
        liga_fora_match = any(fuzz.partial_ratio(liga_fora_normalizada, liga) > 80 for liga in piores_fora_ligas)
        
        return casa_match and fora_match and liga_casa_match and liga_fora_match
    
    # Aplicar filtro nos jogos do dia
    back_home_jogos = jogos_dia_validos[
        jogos_dia_validos.apply(
            lambda row: verifica_criterios(row['Time_Casa'], row['Time_Fora'], row['Liga_Casa'], row['Liga_Fora']), axis=1
        ) & (jogos_dia_validos['Home'] >= 1.45) & (jogos_dia_validos['Home'] <= 2.2)
    ]
    
    # Exibir os jogos filtrados
    st.dataframe(back_home_jogos)



    # Análise: Back Away
    st.subheader("Back Away")
    melhores_away_filtrados = melhores_away[melhores_away['W'] >= 5]
    back_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_away_filtrados['Equipe'])
        ) & (jogos_dia_validos['Away'] >= 1.45) & (jogos_dia_validos['Away'] <= 2.2)
    ]
    st.dataframe(back_away_jogos)

    # Análise: HA -0.25
    st.subheader("HA -0.25")
    piores_away_filtrados = piores_away[piores_away['L'] >= 4]
    melhores_home_filtrados = melhores_casa[melhores_casa['W'] >= 3]
    ha_negativo_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in piores_away_filtrados['Equipe'])
        )
        & (jogos_dia_validos['Home'] >= 1.80) & (jogos_dia_validos['Home'] <= 2.2)
        & jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_home_filtrados['Equipe'])
        )
    ]
    st.dataframe(ha_negativo_jogos)

    # Análise: HA +0.25
    st.subheader("HA +0.25")
    ha_pos_filtrados = melhores_casa[(melhores_casa['W'] + melhores_casa['D']) >= 6]
    ha_pos_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in ha_pos_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] >= 1.60) & (jogos_dia_validos['Home'] <= 2.3)
    ]
    st.dataframe(ha_pos_jogos)

    # Análise: HA +0.25 Away
  
    st.subheader("HA +0.25 Away")
    
    melhores_away_filtrados = melhores_away[melhores_away['W'] >= 4]  
    ha_25_away = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in melhores_away_filtrados['Equipe'])
        )
        & (jogos_dia_validos['Home'] >= 1.80) & (jogos_dia_validos['Away'] >= 1.8)
        
    ]
    st.dataframe(ha_25_away)


    # Análise: HA +1
    st.subheader("HA +1")
    ha_mais_um_filtrados = melhores_away[
        (melhores_away['W'] + melhores_away['D']) >= 6
        & (melhores_away['GD'] > 0)
    ]
    
    ha_mais_um_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.partial_ratio(x, equipe) > 80 for equipe in ha_mais_um_filtrados['Equipe'])
        ) & (jogos_dia_validos['Home'] >= 2.60) & (jogos_dia_validos['Away'] >= 2.4)
    ]
    
    st.dataframe(ha_mais_um_jogos)

else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

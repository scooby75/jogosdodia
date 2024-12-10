import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# Título do aplicativo
st.title("Comparação de Jogos do Dia")

# URLs dos arquivos no GitHub
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

# Função para calcular similaridade entre nomes completos
def similaridade_nome_completo(nome1, nome2, limiar=80):
    # Comparar os nomes completos das equipes
    return fuzz.ratio(nome1.lower(), nome2.lower()) >= limiar

# Upload do arquivo "Jogos do Dia"
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")

if jogos_dia_file:
    # Ler o arquivo "Jogos do Dia"
    jogos_dia = pd.read_csv(jogos_dia_file)

    # Carregar os arquivos diretamente das URLs
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
        'UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21|English Premier League 2|Israeli Cup|Friendly Matches|Malaysian Cup|Copa de França|Copa de Inglaterra|Scottish FA Cup|U23|Sub23|Cup|Copa|CAF Champions League|(W)|EFL Trophy'
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

    # Adicionar a lógica de filtro para a coluna 'Home'
    jogos_filtrados = jogos_dia_validos[(jogos_dia_validos['Home'] >= 1.8) & (jogos_dia_validos['Home'] <= 2.4)]
    
    # Exibir os jogos filtrados
    st.subheader("Jogos filtrados (Home entre 1.8 e 2.4)")
    st.dataframe(jogos_filtrados)

    # Verificar e ajustar os nomes das colunas
    equipes_casa.columns = equipes_casa.columns.str.strip()  # Remove espaços em branco dos nomes das colunas
    
    # Renomear as colunas para evitar conflitos e garantir consistência
    if "Equipe_Casa" in equipes_casa.columns and "PIH_HA" in equipes_casa.columns:
        equipes_casa.rename(columns={"Equipe_Casa": "Equipe_Casa_CSV", "PIH_HA": "PIH_HA_CSV"}, inplace=True)
    else:
        st.error("As colunas esperadas não foram encontradas no arquivo equipes_casa.csv.")
    
    # Confirmar se as colunas do DataFrame foram renomeadas corretamente
    st.write("Colunas após renomear:", equipes_casa.columns)
    
    # Aplicar a lógica de similaridade para fazer o merge
    jogos_merged = []
    for _, jogo in jogos_dia_validos.iterrows():
        nome_time_casa = jogo['Time_Casa']
        
        # Encontrar a linha correspondente em equipes_casa com base na similaridade de nome completo
        similar_times = equipes_casa[equipes_casa['Equipe_Casa_CSV'].apply(lambda x: similaridade_nome_completo(nome_time_casa, x))]  # Comparando nomes completos
        
        if not similar_times.empty:
            jogo_merged = pd.merge(pd.DataFrame([jogo]), similar_times, left_on='Time_Casa', right_on='Equipe_Casa_CSV', how='left')
            jogos_merged.append(jogo_merged)

    # Concatenar todos os jogos encontrados no merge
    if jogos_merged:
        jogos_merged_df = pd.concat(jogos_merged, ignore_index=True)
    else:
        jogos_merged_df = pd.DataFrame()

    # Exibir os jogos com merge realizado
    st.subheader("Jogos com informações das equipes da casa")
    st.dataframe(jogos_merged_df)

    # Aplicar o filtro de PIH_HA >= 0.75
    jogos_filtrados_pih = jogos_merged_df[
        (jogos_merged_df['PIH_HA_CSV'] >= 0.75) &
        (jogos_merged_df['Home'] >= 1.7) &
        (jogos_merged_df['Home'] <= 2.4)
    ]
    
    # Exibir os jogos filtrados com PIH_HA
    st.subheader("Jogos filtrados com PIH_HA >= 0.75")
    st.dataframe(jogos_filtrados_pih)
    
else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

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

# Upload do arquivo "Jogos do Dia"
jogos_dia_file = st.file_uploader("Envie o arquivo 'Jogos do dia Betfair.csv'", type="csv")

if jogos_dia_file:
    # Ler o arquivo "Jogos do Dia"
    jogos_dia = pd.read_csv(jogos_dia_file)

    # Carregar os arquivos diretamente das URLs com verificação de erro
    try:
        equipes_casa = pd.read_csv(url_equipes_casa)
        equipes_fora = pd.read_csv(url_equipes_fora)
    except Exception as e:
        st.error(f"Erro ao carregar os arquivos das equipes: {e}")
        equipes_casa = pd.DataFrame()  # Criação de dataframe vazio em caso de erro
        equipes_fora = pd.DataFrame()  # Criação de dataframe vazio em caso de erro

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

    # Análise: HA +0.25
    st.subheader("HA +0.25 (casa)")
    
    # Validação e conversão de colunas
    def validar_converter_coluna(df, coluna):
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
        return df.dropna(subset=[coluna])
    
    equipes_casa = validar_converter_coluna(equipes_casa, 'PIH_HA')
    equipes_fora = validar_converter_coluna(equipes_fora, 'PIA_HA')
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['PIH_HA'] >= 0.75]
    piores_fora_filtrados = equipes_fora[equipes_fora['PIA_HA'] >= 0.75]
    
    # Filtrar jogos com base nos critérios
    hahome_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Home'] >= 1.6) &
        (jogos_dia_validos['Home'] <= 2.4)
    ]
    
    # Adicionar as colunas de aproveitamento ao dataframe 'hahome_jogos'
    hahome_jogos = hahome_jogos.merge(
        equipes_casa[['Equipe_Casa', 'PIH_HA']],
        left_on='Time_Casa',
        right_on='Equipe_Casa',
        how='left'
    ).drop(columns=['Equipe_Casa'])
    
    hahome_jogos = hahome_jogos.merge(
        equipes_fora[['Equipe_Fora', 'PIA_HA']],
        left_on='Time_Fora',
        right_on='Equipe_Fora',
        how='left'
    ).drop(columns=['Equipe_Fora'])
    
    # Adicionar outras colunas relevantes
    hahome_jogos = hahome_jogos.merge(
        equipes_casa[['Equipe_Casa', 'Odd_Justa_HA', 'Pts_Home', 'GD_Home']],
        left_on='Time_Casa',
        right_on='Equipe_Casa',
        how='left'
    ).drop(columns=['Equipe_Casa'])
    
    hahome_jogos = hahome_jogos.merge(
        equipes_fora[['Equipe_Fora', 'Pts_Away', 'GD_Away']],
        left_on='Time_Fora',
        right_on='Equipe_Fora',
        how='left'
    ).drop(columns=['Equipe_Fora'])
    
    # Garantir que todos os valores necessários estão preenchidos
    hahome_jogos = hahome_jogos.dropna(subset=['PIH_HA', 'PIA_HA', 'Odd_Justa_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away'])
    
    # Verificar se há jogos válidos para exibir
    if hahome_jogos.empty:
        st.write("Nenhum jogo atende aos critérios ou possui dados suficientes!")
    else:
        # Exibir jogos válidos
        st.dataframe(hahome_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH_HA', 'PIA_HA', 'Odd_Justa_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away']])

else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

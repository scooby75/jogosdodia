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
        'UEFA|AFC Champions|Reservas|Friendlies Women\'s International|U21|English Premier League 2|Israeli Cup|Friendly Matches|Malaysian Cup|Copa de França|Copa de Inglaterra|Scottish FA Cup|U23|Sub23|Cup|Copa|CAF Champions League|(W)'
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
    st.subheader("Back Home")
    # Garantir que as colunas 'Aproveitamento' e 'Aproveitamento_Fora' estão no formato correto (numérico)
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA'] = pd.to_numeric(equipes_fora['PIA'], errors='coerce')
    
    # Remover valores nulos de 'Aproveitamento'
    equipes_casa = equipes_casa.dropna(subset=['PIH'])
    equipes_fora = equipes_fora.dropna(subset=['PIA'])
    
    # Função para filtrar sufixos das equipes
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['PIH'] >= 0.65]
    piores_fora_filtrados = equipes_fora[equipes_fora['PIA'] <= 0.20]
    
    # Filtrar jogos com base nos critérios
    back_home_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Home'] >= 1.45) &
        (jogos_dia_validos['Home'] <= 2.2)
    ]
    
    # Adicionar as colunas de aproveitamento ao dataframe 'back_home_jogos'
    back_home_jogos = back_home_jogos.merge(
        equipes_casa[['Equipe', 'PIH']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    back_home_jogos = back_home_jogos.merge(
        equipes_fora[['Equipe', 'PIA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Garantir que a coluna 'Odd_Justa_MO' do DataFrame 'equipes_casa' esteja no formato numérico
    equipes_casa['Odd_Justa_MO'] = pd.to_numeric(equipes_casa['Odd_Justa_MO'], errors='coerce')
    
    # Adicionar a coluna Odd_Justa_MO ao dataframe 'back_home_jogos'
    back_home_jogos = back_home_jogos.merge(
        equipes_casa[['Equipe', 'Odd_Justa_MO']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if back_home_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        # Exibir os jogos com a coluna 'Odd_Justa_MO'
        st.dataframe(back_home_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA', 'Odd_Justa_MO']])



    # BACK AWAY
    
    st.subheader("Back Away")
    
    # Garantir que as colunas 'Aproveitamento' e 'Aproveitamento_Fora' estão no formato correto (numérico)
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA'] = pd.to_numeric(equipes_fora['PIA'], errors='coerce')
    
    # Remover valores nulos de 'Aproveitamento'
    equipes_casa = equipes_casa.dropna(subset=['PIH'])
    equipes_fora = equipes_fora.dropna(subset=['PIA'])
    
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes fora e piores em casa
    melhores_fora_filtrados = equipes_fora[equipes_fora['PIA'] >= 0.65]
    piores_casa_filtrados = equipes_casa[equipes_casa['PIH'] <= 0.20]
    
    # Filtrar jogos com base nos critérios
    back_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_fora_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_casa_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Away'] >= 1.45) &
        (jogos_dia_validos['Away'] <= 2.2)
    ]
    
    # Adicionar as colunas de aproveitamento ao dataframe 'back_away_jogos'
    back_away_jogos = back_away_jogos.merge(
        equipes_casa[['Equipe', 'PIH']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    back_away_jogos = back_away_jogos.merge(
        equipes_fora[['Equipe', 'PIA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])

     # Adicionar a coluna Odd_Justa_MO ao dataframe 'back_home_jogos'
    back_away_jogos = back_away_jogos.merge(
        equipes_fora[['Equipe', 'Odd_Justa_MO']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if back_away_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        #st.write("Jogos filtrados para Back Away:")
        st.dataframe(back_away_jogos[['Hora','Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA', 'Odd_Justa_MO']])


    # Análise: HA -0.25
    st.subheader("HA -0.25")
    
    # Garantir que as colunas 'Aproveitamento' e 'Aproveitamento_Fora' estão no formato correto (numérico)
    equipes_casa['PIH_HA'] = pd.to_numeric(equipes_casa['PIH_HA'], errors='coerce')
    equipes_fora['PIA'] = pd.to_numeric(equipes_fora['PIA'], errors='coerce')
    
    # Remover valores nulos de 'Aproveitamento'
    equipes_casa = equipes_casa.dropna(subset=['PIH_HA'])
    equipes_fora = equipes_fora.dropna(subset=['PIA'])
    
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['PIH_HA'] >= 0.6]
    piores_fora_filtrados = equipes_fora[equipes_fora['PIA'] <= 0.1]
    
    # Filtrar jogos com base nos critérios
    hastrong_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Home'] >= 1.8) &
        (jogos_dia_validos['Home'] <= 2.4)
    ]
    
    # Adicionar as colunas de aproveitamento ao dataframe 'hahome_jogos'
    hastrong_jogos = hastrong_jogos.merge(
        equipes_casa[['Equipe', 'PIH_HA']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    hastrong_jogos = hastrong_jogos.merge(
        equipes_fora[['Equipe', 'PIA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Adicionar a coluna Odd_Justa_MO ao dataframe 'back_home_jogos'
    hastrong_jogos = hastrong_jogos.merge(
        equipes_casa[['Equipe', 'Odd_Justa_HA']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if hastrong_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        # Corrigindo a exibição das colunas no st.dataframe
        st.dataframe(hastrong_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH_HA', 'PIA', 'Odd_Justa_HA']])

    # Análise: HA +0.25
    st.subheader("HA +0.25 (casa)")
    # Garantir que as colunas 'Aproveitamento' e 'Aproveitamento_Fora' estão no formato correto (numérico)
    equipes_casa['PIH_HA'] = pd.to_numeric(equipes_casa['PIH_HA'], errors='coerce')
    equipes_fora['PIA'] = pd.to_numeric(equipes_fora['PIA'], errors='coerce')
    
    # Remover valores nulos de 'Aproveitamento'
    equipes_casa = equipes_casa.dropna(subset=['PIH_HA'])
    equipes_fora = equipes_fora.dropna(subset=['PIA'])
    
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['PIH_HA'] >= 0.75]
    piores_fora_filtrados = equipes_fora[equipes_fora['PIA'] <= 0.25]
    
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
        equipes_casa[['Equipe', 'PIH_HA']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    hahome_jogos = hahome_jogos.merge(
        equipes_fora[['Equipe', 'PIA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Adicionar a coluna Odd_Justa_MO ao dataframe 'back_home_jogos'
    hahome_jogos = hahome_jogos.merge(
        equipes_casa[['Equipe', 'Odd_Justa_HA']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if hahome_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        # Corrigindo a exibição das colunas no st.dataframe
        st.dataframe(hahome_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH_HA', 'PIA', 'Odd_Justa_HA']])


    
    # Análise: HA +0.25 Away
  
    st.subheader("HA +0.25 Away")
              
    # Garantir que as colunas 'Aproveitamento' e 'Aproveitamento_Fora' estão no formato correto (numérico)
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA_HA'] = pd.to_numeric(equipes_fora['PIA_HA'], errors='coerce')
    
    # Remover valores nulos de 'Aproveitamento'
    equipes_casa = equipes_casa.dropna(subset=['PIH'])
    equipes_fora = equipes_fora.dropna(subset=['PIA_HA'])
    
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_fora_filtrados = equipes_fora[equipes_fora['PIA_HA'] >= 0.75]
    piores_casa_filtrados = equipes_casa[equipes_casa['PIH'] <= 0.25]
    
    # Filtrar jogos com base nos critérios
    haaway_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_fora_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_casa_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Away'] >= 1.6) &
        (jogos_dia_validos['Away'] <= 2.4)
    ]

    # Adicionar as colunas de aproveitamento ao dataframe 'haaway_jogos'
    haaway_jogos = haaway_jogos.merge(
        equipes_casa[['Equipe', 'PIH']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    haaway_jogos = haaway_jogos.merge(
        equipes_fora[['Equipe', 'PIA_HA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])

    # Adicionar a coluna Odd_Justa_MO ao dataframe 'back_home_jogos'
    haaway_jogos = haaway_jogos.merge(
        equipes_fora[['Equipe', 'Odd_Justa_HA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if haaway_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        #st.write("Jogos filtrados para HA +0.25 (Fora):")
        st.dataframe(haaway_jogos[['Hora','Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA_HA','Odd_Justa_HA']])

    # Análise: HA +1
   
    st.subheader("HA +1")
   
    # Garantir que as colunas 'Aproveitamento' e 'Aproveitamento_Fora' estão no formato correto (numérico)
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA_HA'] = pd.to_numeric(equipes_fora['PIA_HA'], errors='coerce')
    
    # Remover valores nulos de 'Aproveitamento'
    equipes_casa = equipes_casa.dropna(subset=['PIH'])
    equipes_fora = equipes_fora.dropna(subset=['PIA_HA'])
    
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_fora_filtrados = equipes_fora[equipes_fora['PIA_HA'] >= 0.6]
    piores_casa_filtrados = equipes_casa[equipes_casa['PIH'] <= 0.2]
    
    # Filtrar jogos com base nos critérios
    haum_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_fora_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_casa_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Home'] >= 2.6) &
        (jogos_dia_validos['Away'] >= 2.2)
    ]

    # Adicionar as colunas de aproveitamento ao dataframe 'haum_jogos'
    haum_jogos = haum_jogos.merge(
        equipes_casa[['Equipe', 'PIH']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    haum_jogos = haum_jogos.merge(
        equipes_fora[['Equipe', 'PIA_HA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])

    haum_jogos = haum_jogos.merge(
        equipes_fora[['Equipe', 'Odd_Justa_HA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if haum_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        #st.write("Jogos filtrados para HA +1 (Fora):")
        st.dataframe(haum_jogos[['Hora','Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA_HA', 'Odd_Justa_HA']])
        
    # Análise: HA +0.25 (GD)
    
    st.subheader("HA +0.25(GD)")
    
    # Garantir que as colunas 'PIH' e 'PIA_HA' estão no formato correto (numérico)
    equipes_casa['GD'] = pd.to_numeric(equipes_casa['GD'], errors='coerce')
    equipes_fora['GD'] = pd.to_numeric(equipes_fora['GD'], errors='coerce')
    
    # Remover valores nulos de 'PIH' e 'PIA_HA'
    equipes_casa = equipes_casa.dropna(subset=['GD'])
    equipes_fora = equipes_fora.dropna(subset=['GD'])
    
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa (PIH >= 0.5) e piores fora (PIA_HA <= 0.1)
    melhores_casa_filtrados = equipes_casa[equipes_casa['GD'] >= 6]
    piores_fora_filtrados = equipes_fora[equipes_fora['GD'] <= -2.]
    
    # Filtrar jogos com base nos critérios
    hagd_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Away'] >= 3) &
        (jogos_dia_validos['Away'] <= 10)
    ]
    
    # Adicionar as colunas de aproveitamento ao dataframe 'hagd_jogos'
    hagd_jogos = hagd_jogos.merge(
        equipes_casa[['Equipe', 'PIH']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    hagd_jogos = hagd_jogos.merge(
        equipes_fora[['Equipe', 'PIA_HA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Adicionar a coluna Odd_Justa_HA ao dataframe 'hagd_jogos'
    hagd_jogos = hagd_jogos.merge(
        equipes_fora[['Equipe', 'GD']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos filtrados
    if hagd_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        st.dataframe(hagd_jogos[['Hora','Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA_HA','GD']])


else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

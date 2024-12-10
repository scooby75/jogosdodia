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

    # Análise: Back Home
    st.subheader("Back Home")
   
    # Garantir que as colunas de aproveitamento estão no formato correto (numérico)
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA'] = pd.to_numeric(equipes_fora['PIA'], errors='coerce')
    
    # Remover valores nulos nas colunas de aproveitamento
    equipes_casa = equipes_casa.dropna(subset=['PIH'])
    equipes_fora = equipes_fora.dropna(subset=['PIA'])
    
    # Função para filtrar equipes com sufixos indesejados
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['PIH'] >= 0.65]
    piores_fora_filtrados = equipes_fora[equipes_fora['PIA'] <= 0.20]
    
    # Filtrar jogos com base nos critérios definidos
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
    
    # Adicionar colunas de métricas de desempenho ao DataFrame
    metricas = [
        ('PIH', equipes_casa),
        ('PIA', equipes_fora),
        ('Pts_Home', equipes_casa),
        ('Pts_Away', equipes_fora),
        ('GD_Home', equipes_casa),
        ('GD_Away', equipes_fora),
        ('Odd_Justa_MO', equipes_casa)
    ]
    
    for coluna, dataframe in metricas:
        back_home_jogos = back_home_jogos.merge(
            dataframe[['Equipe', coluna]],
            left_on='Time_Casa' if 'Home' in coluna or 'Odd_Justa_MO' in coluna else 'Time_Fora',
            right_on='Equipe',
            how='left'
        ).drop(columns=['Equipe'])
    
    # Verificar se há jogos que atendem aos critérios
    if back_home_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        # Exibir DataFrame com as colunas selecionadas
        st.dataframe(back_home_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA', 'Odd_Justa_MO', 'GD_Home', 'GD_Away','Pts_Home', 'Pts_Away'
        ]])


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

    # Certifique-se de que as colunas de aproveitamento e pontuação não têm valores nulos
    equipes_casa = equipes_casa.dropna(subset=['GD_Home', 'PIH', 'Pts_Home', 'Odd_Justa_HA'])
    equipes_fora = equipes_fora.dropna(subset=['GD_Away', 'PIA', 'Pts_Away'])
    
    # Garantir que as colunas 'GD_Home' e 'GD_Away' estão no formato correto
    equipes_casa['GD_Home'] = pd.to_numeric(equipes_casa['GD_Home'], errors='coerce')
    equipes_fora['GD_Away'] = pd.to_numeric(equipes_fora['GD_Away'], errors='coerce')

    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["FC", "CF", "FK", "CD", "SV"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['GD_Home'] >= 1.5]
    piores_fora_filtrados = equipes_fora[equipes_fora['GD_Away'] <= 0.8]
    
    # Filtrar jogos com base nos critérios
    hastrong_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Home'] >= 1.6) &
        (jogos_dia_validos['Home'] <= 2.2)
    ]
    
    # Verificar se há jogos filtrados
    if hastrong_jogos.empty:
        st.write("Nenhum jogo atende aos critérios!")
    else:
        # Realizar os merges para adicionar colunas de aproveitamento e pontuação
        hastrong_jogos = hastrong_jogos.merge(
            equipes_casa[['Equipe', 'GD_Home', 'PIH', 'Pts_Home', 'Odd_Justa_HA']],
            left_on='Time_Casa',
            right_on='Equipe',
            how='left'
        ).drop(columns=['Equipe'])
    
        hastrong_jogos = hastrong_jogos.merge(
            equipes_fora[['Equipe', 'GD_Away', 'PIA', 'Pts_Away']],
            left_on='Time_Fora',
            right_on='Equipe',
            how='left'
        ).drop(columns=['Equipe'])
    
        # Exibir os jogos filtrados com as colunas especificadas
        st.dataframe(hastrong_jogos[[
            'Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 
            'Odd_Justa_HA', 'PIH', 'PIA', 'GD_Home', 'GD_Away', 
            'Pts_Home', 'Pts_Away'
        ]])




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
        equipes_casa[['Equipe', 'PIH_HA']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    hahome_jogos = hahome_jogos.merge(
        equipes_fora[['Equipe', 'PIA_HA']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Adicionar outras colunas relevantes
    hahome_jogos = hahome_jogos.merge(
        equipes_casa[['Equipe', 'Odd_Justa_HA', 'Pts_Home', 'GD_Home']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    hahome_jogos = hahome_jogos.merge(
        equipes_fora[['Equipe', 'Pts_Away', 'GD_Away']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Garantir que todos os valores necessários estão preenchidos
    hahome_jogos = hahome_jogos.dropna(subset=['PIH_HA', 'PIA_HA', 'Odd_Justa_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away'])
    
    # Verificar se há jogos válidos para exibir
    if hahome_jogos.empty:
        st.write("Nenhum jogo atende aos critérios ou possui dados suficientes!")
    else:
        # Exibir jogos válidos
        st.dataframe(hahome_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH_HA', 'PIA_HA', 'Odd_Justa_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away']])


    
    # Análise: HA +0.25 Away
  
    st.subheader("HA +0.25 Away")
              
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
    
    # Adicionar outras colunas relevantes
    hahome_jogos = hahome_jogos.merge(
        equipes_casa[['Equipe', 'Odd_Justa_HA', 'Pts_Home', 'GD_Home']],
        left_on='Time_Casa',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    hahome_jogos = hahome_jogos.merge(
        equipes_fora[['Equipe', 'Pts_Away', 'GD_Away']],
        left_on='Time_Fora',
        right_on='Equipe',
        how='left'
    ).drop(columns=['Equipe'])
    
    # Verificar se há jogos válidos para exibir
    if hahome_jogos.empty or hahome_jogos[['PIH_HA', 'PIA']].isnull().any(axis=None):
        st.write("Nenhum jogo atende aos critérios ou possui dados suficientes!")
    else:
        # Corrigindo a exibição das colunas no st.dataframe
        st.dataframe(hahome_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH_HA', 'PIA', 'Odd_Justa_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away']])

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
    
    st.subheader("HA +0.25(GD_Away > 5)")
    
    # Garantir que as colunas 'PIH', 'PIA_HA', 'GD_Home' e 'GD_Away' estão no formato correto (numérico)
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA_HA'] = pd.to_numeric(equipes_fora['PIA_HA'], errors='coerce')
    equipes_casa['GD_Home'] = pd.to_numeric(equipes_casa['GD_Home'], errors='coerce')
    equipes_fora['GD_Away'] = pd.to_numeric(equipes_fora['GD_Away'], errors='coerce')
    
    # Remover valores nulos nas colunas essenciais
    equipes_casa = equipes_casa.dropna(subset=['PIH', 'GD_Home'])
    equipes_fora = equipes_fora.dropna(subset=['PIA_HA', 'GD_Away'])
    
    # Filtrar equipes com base nos sufixos
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Filtrar as melhores equipes em casa (GD_Home >= 6) e piores fora (GD_Away <= -5)
    melhores_casa_filtrados = equipes_casa[equipes_casa['GD_Home'] >= 6]
    piores_fora_filtrados = equipes_fora[equipes_fora['GD_Away'] >= -5]
    
    # Filtrar jogos com base nos critérios
    hagd_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Home'] >= 1.6) &
        (jogos_dia_validos['Home'] <= 2.40)
    ]
    
    # Adicionar as colunas ao dataframe 'hagd_jogos'
    colunas_para_merge = [
        ('PIH', 'Time_Casa', equipes_casa),
        ('PIA_HA', 'Time_Fora', equipes_fora),
        ('GD_Home', 'Time_Casa', equipes_casa),
        ('GD_Away', 'Time_Fora', equipes_fora),
        ('Pts_Home', 'Time_Casa', equipes_casa),
        ('Pts_Away', 'Time_Fora', equipes_fora)
    ]
    
    for coluna, chave, df_merge in colunas_para_merge:
        hagd_jogos = hagd_jogos.merge(
            df_merge[['Equipe', coluna]],
            left_on=chave,
            right_on='Equipe',
            how='left'
        ).drop(columns=['Equipe'])
    
    # Remover linhas com valores nulos nas colunas essenciais
    hagd_jogos = hagd_jogos.dropna(subset=['PIH', 'PIA_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away'])
    
    # Verificar se há jogos filtrados
    if hagd_jogos.empty:
        st.write("Nenhum jogo atende aos critérios ou possui dados suficientes!")
    else:
        st.dataframe(hagd_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away']])

    # LAY AWAY
    
    st.subheader("Lay Away")
    
    # Garantir que as colunas de aproveitamento estão no formato correto
    equipes_casa['PIH'] = pd.to_numeric(equipes_casa['PIH'], errors='coerce')
    equipes_fora['PIA'] = pd.to_numeric(equipes_fora['PIA'], errors='coerce')
    
    # Remover valores nulos das colunas de aproveitamento
    equipes_casa = equipes_casa.dropna(subset=['PIH'])
    equipes_fora = equipes_fora.dropna(subset=['PIA'])
    
    # Função para filtrar equipes com sufixos indesejados
    def filtrar_sufixos(time, lista_sufixos):
        return not any(sufixo in time for sufixo in lista_sufixos)
    
    sufixos_diferentes = ["B", "II", "Sub-23"]
    equipes_casa = equipes_casa[equipes_casa['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    equipes_fora = equipes_fora[equipes_fora['Equipe'].apply(lambda x: filtrar_sufixos(x, sufixos_diferentes))]
    
    # Remover valores nulos após filtrar por sufixos indesejados
    equipes_casa = equipes_casa.dropna()
    equipes_fora = equipes_fora.dropna()
    
    # Filtrar melhores equipes em casa e piores fora
    melhores_casa_filtrados = equipes_casa[equipes_casa['PIH'] >= 0.5]
    piores_fora_filtrados = equipes_fora[equipes_fora['PIA'] <= 0.10]

    
    
    # Filtrar jogos do dia com base nos critérios
    lay_away_jogos = jogos_dia_validos[
        jogos_dia_validos['Time_Casa'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in melhores_casa_filtrados['Equipe'])
        ) &
        jogos_dia_validos['Time_Fora'].apply(
            lambda x: any(fuzz.token_sort_ratio(x, equipe) > 80 for equipe in piores_fora_filtrados['Equipe'])
        ) &
        (jogos_dia_validos['Away'] >= 3)
    ]
    
      # Adicionar as colunas ao dataframe 'hagd_jogos'
    colunas_para_merge = [
        ('PIH', 'Time_Casa', equipes_casa),
        ('PIA_HA', 'Time_Fora', equipes_fora),
        ('GD_Home', 'Time_Casa', equipes_casa),
        ('GD_Away', 'Time_Fora', equipes_fora),
        ('Pts_Home', 'Time_Casa', equipes_casa),
        ('Pts_Away', 'Time_Fora', equipes_fora)
    ]
    
    for coluna, chave, df_merge in colunas_para_merge:
       lay_away_jogos = lay_away_jogos.merge(
            df_merge[['Equipe', coluna]],
            left_on=chave,
            right_on='Equipe',
            how='left'
        ).drop(columns=['Equipe'])
    
    # Remover linhas com valores nulos nas colunas essenciais
    lay_away_jogos = lay_away_jogos.dropna(subset=['PIH', 'PIA_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away'])
    
    # Verificar se há jogos filtrados
    if lay_away_jogos.empty:
        st.write("Nenhum jogo atende aos critérios ou possui dados suficientes!")
    else:
        st.dataframe(lay_away_jogos[['Hora', 'Time_Casa', 'Time_Fora', 'Home', 'Away', 'PIH', 'PIA_HA', 'GD_Home', 'GD_Away', 'Pts_Home', 'Pts_Away']])

else:
    st.info("Por favor, envie o arquivo 'Jogos do dia Betfair.csv' para realizar a análise.")

import math
import pandas as pd
import numpy as np


    
def search_diameter_long(area_necessaria, diameters, variables):


    # --------- PARAMETERS --------------- #

    # area_necessaria: Área necessária de aço para o projeto
    # diameters: Diâmetros comerciais disponíveis
    # variables: Variáveis de projeto em formato de dicionário.
    # É necessário que contenha bw, diâmetro transversal e cobrimento

    def get_n_areas(d):

        def area(d):
            return math.pi*(d**2)/4

        n_areas = []
        for i in range(2, 21):
            n_areas.append(area(d)*i)

        return n_areas

    dict_steel = {}
    for diameter in diameters:
        dict_steel[str(diameter)] = get_n_areas(diameter)

    df = pd.DataFrame(dict_steel)

    for i in df.index:
        for j in df.columns:
            df.iloc[i][j] = df.iloc[i][j] - area_necessaria
            if df.iloc[i][j] < 0:
                df.iloc[i][j] = np.inf

    list_min = []
    for column in df.columns:
        list_min.append(df[column].min())

    def get_d(min_dif):

        for column in df.columns:
            try:
                print('Diâmetro: {} mm - N: {}'.format(column, str(df.loc[df[column] == min_dif].index[0]+2)))
                d = float(column)
                n = df.loc[df[column] == min_dif].index[0]+2

            except:
                print('Searching...')

        return [d, n]

    def calculate_sh(variables, r):
        bw = variables['bw']
        dt = variables['dt']
        cob = variables['Cobrimento']
        dl = r[0]
        nl = r[1]

        sh = (bw*1000 - dl*nl - 2*(cob + dt))/(nl-1)
        return sh

    min_dif = np.min(list_min)
    r = get_d(min_dif)
    sh = calculate_sh(variables, r)
    while sh < 20:
        list_min.remove(min_dif)
        min_dif = np.min(list_min)
        r = get_d(min_dif)
        sh = calculate_sh(variables, r)

    print('Espaçamento: {} > 20mm. Ok!'.format(sh))
    
    r.append(sh)

    return r


def search_diameter_trans(area_necessaria, diameters, variables):

    # --------- PARAMETERS --------------- #

    # area_necessaria: Área necessária de aço para o projeto
    # diameters: Diâmetros comerciais disponíveis
    # variables: Variáveis de projeto em formato de dicionário.
    # É necessário que contenha L

    def get_n_areas(d):

        def area(d):
            return math.pi*(d**2)/4

        n_areas = []
        for i in range(2, 1000):
            n_areas.append(area(d)*i)

        return n_areas

    dict_steel = {}
    for diameter in diameters:
        dict_steel[str(diameter)] = get_n_areas(diameter)

    df = pd.DataFrame(dict_steel)

    for i in df.index:
        for j in df.columns:
            df.iloc[i][j] = df.iloc[i][j] - area_necessaria
            if df.iloc[i][j] < 0:
                df.iloc[i][j] = np.inf

    def get_d(min_dif):

        for column in df.columns:
            try:
                print('Diâmetro: {} mm - N: {}'.format(column, str(df.loc[df[column] == min_dif].index[0]+2)))
                d = float(column)
                n = df.loc[df[column] == min_dif].index[0]+2
            except:
                print('Searching...')

        return [d, n]

    fck = variables['fck']
    bw = variables['bw']
    alpha = 1 - fck / 250
    vrd2 = 0.27 * alpha * fck/1.4 * bw * variables['d'] * (10 ** 3)
    vsd = variables['vsk']*1.4

    if vsd <= vrd2:
        st_max = np.min([0.6*variables['d'], 0.3])
    else:
        st_max = np.min([0.3*variables['d'], 0.2])

    nt_min = math.ceil(variables['L']/st_max)
    df = df.loc[df.index >= nt_min]

    list_min = []
    for column in df.columns:
        list_min.append(df[column].min())

    min_dif = np.min(list_min)

    return get_d(min_dif)

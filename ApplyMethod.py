from BeamOpt_TCC import BeamOpt
from GetDiameter import search_diameter_long, search_diameter_trans


def Otimizacao_ArmSimples(variables, bw_lim):

    results = BeamOpt(variables, bw_lim)
    variables['bw'] = results[0]
    variables['x'] = results[1]

    bw = int(variables['bw']*100)/100
    d_ = 4/100
    d = variables['h']/100 - d_
    variables['d'] = d
    fck = variables['fck']
    fcd = variables['fck'] * 1000 / 1.4
    fyd = variables['fyk'] * 1000 / 1.15
    L = variables['L']
    vsd = variables['vsk'] * 1.4
    md = variables['mk'] * 1.4
    x = variables['x']

    # Armadura Longitudinal
    Asl = (md / (fyd * (d - 0.4 * x)))  # m2

    # Armadura Transversal
    fctd = 0.7 * 0.3 * (fck ** (2 / 3)) / 1.4
    vc = 0.6 * (fctd * 1000) * bw * d
    vsw = vsd - vc
    Ast = (vsw / (0.9 * d * fyd)) * L  # m2/m

    # Calculando dt, nt
    diameters = [5.0, 6.3, 8.00]
    r_trans = search_diameter_trans(Ast * (10**6), diameters, variables)
    variables['dt'] = r_trans[0]
    variables['nt'] = r_trans[1]

    # Calculando dl_inf, nl_inf
    diameters = [5.0, 6.3, 8.00, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0]
    r_long = search_diameter_long(Asl * (10 ** 6), diameters, variables)
    variables['dl'] = r_long[0]
    variables['nl'] = r_long[1]
    variables['sh'] = r_long[2]

    print('''
    Aço Longitudinal total: {} cm2 \n
    Aço Transversal total: {} cm2 \n
    '''.format(Asl * (10 ** 4), Ast*(10**4)))

    print('''
    ----------------- VARIÁVEIS DE ENTRADA ----------------- \n
    fck: {} MPa \n
    fyk: {} MPa \n
    Comprimento do vão: {} m \n
    Altura útil: {} cm \n
    Vd: {} tf \n
    Md: {} tfm \n
          '''.format(variables['fck'], variables['fyk'], variables['L'], variables['d'] * 100,
                     round(variables['vsk'] * 1.4 * 0.10, 2), round(variables['mk'] * 1.4 * 0.10, 2)))

    print('''
    ----------------- AUTO DESIGN: RESULTS ----------------- \n
    Largura da Viga: {} cm \n
    Altura da linha neutra: {} cm \n
    Diâmetro da armadura longitudinal: {} mm \n
    Número de barras da armadura longitudinal: {} \n
    Espaçamento horizontal: {} cm \n
    Diâmetro da armadura transversal: {} mm \n
    Número de barras da armadura transversal: {} \n
    Cobrimento: {} cm \n'''.format(bw*100, round(variables['x'] * 100, 2), variables['dl'],
                                   variables['nl'], round(variables['sh'] / 10, 2),
                                   variables['dt'], variables['nt'], variables['Cobrimento'] / 10))


    return variables

from BeamOpt2_TCC import BeamOpt2
from GetDiameter import search_diameter_long, search_diameter_trans

def Otimizacao_ArmDupla(variables, bw_lim):

    while True:
        try:
            results = BeamOpt2(variables, bw_lim)
            variables['bw'] = results[0]

            bw = int(variables['bw']*100)/100
            fck = variables['fck']
            fcd = variables['fck']*1000/1.4
            fyd = variables['fyk']*1000/1.15
            L = variables['L']
            vsd = variables['vsk']*1.4
            md = variables['mk']*1.4
            d_ = 4/100
            d = variables['h']/100 - d_
            variables['d'] = d

            # Cálculo da Armadura Longitudinal
            kx34 = 0.45
            x34 = kx34 * d
            m34 = (0.68 * x34 * d - 0.272 * x34**2) * bw * fcd

            # Armadura inferior
            kz34 = 1 - kx34*0.4
            As34 = m34/(kz34 * d * fyd)  # m2

            # Armadura superior
            m2 = md - m34
            As2 = m2/((d-d_) * fyd)  # m2

            Asl = As34 + As2
            print(Asl*(10**6))

            # Cálculo da Armadura Transversal
            fctd = 0.7 * 0.3 * (fck**(2/3))/1.4
            vc = 0.6 * (fctd*1000) * bw * d
            vsw = vsd - vc
            Ast = (vsw/(0.9 * d * fyd)) * L  # m2/m

            # Calculando dt, nt
            diameters = [5.0, 6.3, 8.00]
            r_trans = search_diameter_trans(Ast*(10**6), diameters, variables)
            variables['dt'] = r_trans[0]
            variables['nt'] = r_trans[1]
            print(variables['dt'], variables['bw'], variables['Cobrimento'])

            # Calculando dl_inf, nl_inf
            diameters = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0]
            r_long_inf = search_diameter_long(Asl*(10**6), diameters, variables)
            variables['dl_inf'] = r_long_inf[0]
            variables['nl_inf'] = r_long_inf[1]
            variables['sh_inf'] = r_long_inf[2]

            # Calculando dl_sup, nl_sup
            diameters = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0]
            r_long_sup = search_diameter_long(As2*(10**6), diameters, variables)
            variables['dl_sup'] = r_long_sup[0]
            variables['nl_sup'] = r_long_sup[1]
            variables['sh_sup'] = r_long_sup[2]

            print('''
        
            Aço Inferior: {} cm2 \n
            Aço Superior: {} cm2 \n
            Aço Transversal: {} cm2 \n
            '''.format(Asl*(10**4), As2*(10**4), Ast*(10**4)))

            print('''
            ----------------- VARIÁVEIS DE ENTRADA ----------------- \n
            fck: {} MPa \n
            fyk: {} MPa \n
            Comprimento do vão: {} m \n
            Altura útil: {} cm \n
            Vd: {} tf \n
            Md: {} tfm \n
                  '''.format(variables['fck'], variables['fyk'], variables['L'], variables['d']*100,
                             round(variables['vsk']*1.4*0.10, 2), round(variables['mk']*1.4*0.10, 2)))

            print('''
            ----------------- AUTO DESIGN: RESULTS ----------------- \n
            Largura da Viga: {} cm \n
            Diâmetro da armadura longitudinal inferior: {} mm \n
            Número de barras da armadura longitudinal inferior: {} \n
            Espaçamento horizontal inferior: {} cm \n
            Diâmetro da armadura longitudinal superior: {} mm \n
            Número de barras da armadura longitudinal superior: {} \n
            Espaçamento horizontal superior: {} cm \n
            Diâmetro da armadura transversal: {} mm \n
            Número de barras da armadura transversal: {} \n
            Cobrimento: {} cm \n'''.format(round(bw*100, 2), variables['dl_inf'],
                                           variables['nl_inf'], round(variables['sh_inf']/10, 2),
                                           variables['dl_sup'], variables['nl_sup'], round(variables['sh_sup']/10, 2),
                                           variables['dt'], variables['nt'], variables['Cobrimento']/10))

        except ValueError:
            print('bw não suficiente para a armadura, buscando bw maior...')
            bw_lim = bw_lim + 0.01

        else:
            return variables


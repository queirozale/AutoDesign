from gekko import GEKKO
import math
import numpy as np


def BeamOpt2(variables, bw_lim):

    # ---------------------- BeamOpt2 ---------------------- #
    # Recebe os parâmetros do projeto "variables"
    # Realiza a Otimização e retorna a Largura da Viga(bw) e
    # o valor da Linha Neutra encontrado.
    # ----------------------------------------------------- #

    m = GEKKO()

    # Coletando as informações das variáveis
    fck = variables['fck']
    fcd = variables['fck'] * 1000 / 1.4  # MPa -> KPa
    fyk = variables['fyk']
    fyd = variables['fyk'] * 1000 / 1.15  # MPa -> KPa
    md = variables['mk'] * 1.4  # KNm
    vsd = variables['vsk'] * 1.4  # KN
    h = variables['h'] / 100  # cm -> m
    L = variables['L']  # m
    d_ = 4/100
    d = variables['h']/100 - d_

    #  Cálculo da massa específica média das barras de ferro
    def calc_peso_aco():
        D = [6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0, 40.0]
        P = [0.248, 0.393, 0.624, 0.988, 1.570, 2.480, 3.930, 6.240, 9.880]

        def area(d):
            return math.pi * (d ** 2) * (10**-6) / 4

        pesos = []
        for (d, p) in zip(D, P):
            pesos.append(p / area(d))

        return np.mean(pesos)

    p = calc_peso_aco()  # Massa específica média

    # Preço dos materiais R$/kg e R$/m3
    preco_CA5060 = 8.86
    preco_concreto = 295.46

    # Armadura Longitudinal
    bw = m.Var(lb=bw_lim, ub=1.00)  # m
    kx34 = 0.45
    x34 = kx34 * d
    m34 = (0.68 * x34 * d - 0.272 * x34**2) * bw * fcd

    # Armadura inferior
    kz34 = 1 - kx34
    As34 = m34/(kz34 * d * fyd)  # m2

    # Armadura superior
    m2 = md - m34
    As2 = m2/((d-d_) * fyd)  # m2

    Asl = As34 + As2

    # Armadura Transversal
    alpha = 1 - fck / 250
    vrd2 = 0.27 * alpha * fck/1.4 * bw * d * (10 ** 3)
    fctm = 0.3 * (fck**(2/3))
    fctd = 0.7 * 0.3 * (fck ** (2 / 3)) / 1.4
    vc = 0.6 * (fctd * 1000) * bw * d
    vsw = vsd - vc
    Ast = (vsw / (0.9 * d * fyd)) * L

    # Volume Concreto
    Volume_Concreto = bw * h * L

    # Formulação dos preços dos componentes
    Preco_acolong = preco_CA5060 * p * (L + 0.4) * Asl
    Preco_acotrans = preco_CA5060 * p * (2 * (bw + h)) * Ast
    Preco_concreto = preco_concreto * Volume_Concreto

    # Função objetivo e equações de restrição
    m.Obj(Preco_acolong + Preco_acotrans + Preco_concreto)
    m.Equations([vsd <= vrd2, vsw > 0, md > m34, (vsw / (0.9 * d * fyd))/bw >= 0.2*(fctm/fyk),
                 Asl + As2 <= 0.04*bw*h])

    m.solve(display=True)
    
    print('''Otimização Concluída! \n
    Largura encontrada (m): {}'''.format(bw.value[0]))
    
    return [bw.value[0]]



